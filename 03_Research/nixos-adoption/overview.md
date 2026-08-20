---
title: "NixOS adoption and deployment tooling"
status: accepted
author: "padawont"
date: 2026-08-20
tags: [nixos, deployment, k8s, portability, homelab]
sources:
  - knowledge: "./02_Knowledge/technologies/tools/nixos/overview.md"
  - knowledge: "./02_Knowledge/technologies/tools/nixos/flakes.md"
  - knowledge: "./02_Knowledge/technologies/tools/nixos/home-manager.md"
  - knowledge: "./02_Knowledge/technologies/tools/nixos/services-secrets.md"
references:
  - url: "https://nixos.org/manual/nixos/stable/"
    title: "NixOS manual"
  - url: "https://github.com/serokell/deploy-rs"
    title: "deploy-rs"
  - url: "https://colmena.cli.rs/"
    title: "colmena manual"
  - url: "https://nixops.dev/"
    title: "NixOps"
  - url: "https://github.com/Mic92/sops-nix"
    title: "sops-nix"
last_audit_date: 2026-08-20
---

# NixOS adoption and deployment tooling

## Goal

Can NixOS replace the Ubuntu host OS while the existing k3s cluster keeps running on top, and which deployment tool makes the same flake portable to any node (not just node-main)?

## Alternatives

See `./alternatives.md` for full evaluations of each tool.

- deploy-rs — **Selected** — flake-native, parallel builds / sequential activation, automatic rollback, runtime host overrides.
- colmena — Rejected (runner-up) — parallel multi-node, but no automatic rollback, no runtime hostname override, slow release cadence.
- NixOps — Rejected — 2.x abandoned and not flake-native; NixOps4 rewrite unreleased, no rollback or secrets story.
- nixos-rebuild — Rejected as standalone (baseline) — ships with NixOS but no multi-node orchestration and manual rollback only.

Sub-decision: secrets manager — **sops-nix Selected** over agenix (reuses the existing k8s SOPS toolchain).

## Plan for ADR

### Feasibility (approve)

k3s runs on NixOS via the in-tree `services.k3s.enable` nixpkgs module: first-class, systemd-managed (`Type=notify`, `Delegate=yes`), with its own containerd. NixOS manages the host; k3s stays the workload manager; existing workloads and manifests remain untouched. Migration path: back up `/var/lib/rancher/k3s` + `/etc/rancher/k3s`, reinstall the host, restore, keep the node IP. Open firewall ports 6443, 8472/UDP (flannel), 10250 (kubelet); 2379/2380 if HA etcd. Use `tokenFile` not `token` to avoid world-readable store secrets. Note: nix-community/k3s-nix is dead (404) — use the in-tree module.

### Deployment tool (recommended: deploy-rs)

Flake-native Rust tool by Serokell (`deploy.nodes.<name>` declared in the flake), builds in parallel, activation sequential, automatic rollback on activation failure (`autoRollback`) plus `magicRollback` — the node self-rolls-back if it can't be reached within `confirmTimeout`, protecting against breaking SSH. Zero server-side state (single binary + SSH, no agent/DB/daemon) and works transparently with sops-nix (activation-time decrypt). Portability: target hosts are static in the flake, but `hostname`/`ssh-user`/`sudo` are overridable at runtime with `--hostname`, so the same flake pushes the same profile to any node without editing config. Caveats: no formal releases (CLI reports 1.0, packaged in nixpkgs — ride master / pin the packaged version), thin docs, and a bootstrap gap — deploy-rs needs NixOS already installed, so Ubuntu→NixOS conversion is a separate step (nixos-anywhere or manual install). `magicRollback` must be disabled when intentionally changing SSH-relevant config.

### Secrets (recommended: sops-nix)

Reuses the existing k8s SOPS toolchain — one binary, one key base, one `.sops.yaml`. Decryption happens at activation into `/run/secrets`; per-secret owner/group/mode and `sops.templates.*` placeholders; MAC-authenticated files with cleartext git diffs; CNCF-maintained sops core. Key handling via `sops.age.sshKeyPaths` derives keys from host SSH keys — same convenience as agenix. agenix rejected: adds a disjoint second secret toolchain (age-only, no k8s story).

### Architecture overview

A single portable flake holding `nixosConfigurations` per host plus shared modules and `deploy.nodes` per host; k3s via `services.k3s` with role server/agent set per node; secrets via sops-nix; home-manager for the admin user. See `./02_Knowledge/technologies/tools/nixos/flakes.md` for the flake structure this builds on.

### Dependencies and integration points

nixpkgs (pinned flake input), deploy-rs input, sops-nix, the in-tree k3s module, home-manager. Requires SSH access (root or sudo) to target hosts.

### Risks and mitigation

- (a) Ride-master deploy-rs — pin via the nixpkgs-packaged version.
- (b) `magicRollback` footgun — disable for SSH-networking changes.
- (c) Firewall misconfig breaks k3s — explicit port rules for 6443, 8472/UDP, 10250.
- (d) Store-world-readable secrets — use `tokenFile` / sops-nix.
- (e) Bootstrap gap — nixos-anywhere or manual install before deploy-rs takes over.

## Recommendation

**approve** — adopt NixOS as the host OS: feasible because k3s keeps running on top via the in-tree module while existing workloads are untouched. Use deploy-rs as the deployment tool for its automatic rollback (autoRollback + magicRollback) and runtime host portability. Use sops-nix for secrets to reuse the existing k8s SOPS toolchain.
