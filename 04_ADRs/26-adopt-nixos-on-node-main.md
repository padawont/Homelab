---
adr: 26
title: "Adopt NixOS as the host OS on node-main"
author: "padawont"
status: accepted
topic: "platform"
technology: "nixos, nixos-anywhere, deploy-rs, k3s, sops-nix"
date: 2026-08-23
date-proposed: 2026-08-20
replaces: ""
replaced-by: ""
history: "Research 03_Research/nixos-adoption accepted 2026-08-22"
sources:
  - url: "https://nixos.org/manual/nixos/stable/"
    title: "NixOS manual"
  - url: "https://github.com/serokell/deploy-rs"
    title: "deploy-rs"
  - url: "https://github.com/Mic92/sops-nix"
    title: "sops-nix"
references:
  - url: "https://nix-community.github.io/nixos-anywhere/"
    title: "nixos-anywhere docs"
related_docs:
  - "./03_Research/nixos-adoption/overview.md"
  - "./02_Knowledge/technologies/tools/nixos/overview.md"
  - "./02_Knowledge/technologies/tools/nixos-anywhere/overview.md"
  - "./02_Knowledge/technologies/kubernetes/k3s/installation.md"
  - "./05_Implementations/node-main/nixos/overview.md"
---

# ADR-26: Adopt NixOS as the host OS on node-main

## Context and Problem Statement

node-main runs Ubuntu with a k3s cluster installed via the curl script. Configuration
drifted across manual edits; reinstalling the host meant repeating undocumented steps,
and secrets lived in world-readable places. The homelab wants a declarative, reproducible
host OS that keeps the existing k3s workloads running unchanged.

Research `03_Research/nixos-adoption/overview.md` evaluated deployment tooling and
selected deploy-rs (flake-native, automatic rollback) with sops-nix for secrets,
and confirmed the in-tree nixpkgs k3s module (nix-community/k3s-nix is dead).

## Decision

Adopt **NixOS 26.05** as the host OS on node-main:

- **Bootstrap**: `nixos-anywhere` (direct-boot against the NixOS installer) with a disko
  layout — nvme0n1 (EFI + swap + ext4 root) and sda (ext4 mounted at
  `/var/lib/rancher/k3s` for k3s data).
- **Ongoing deployment**: `deploy-rs` from a single flake at
  `05_Implementations/node-main/nixos/` (`autoRollback` + `magicRollback`).
- **Workloads**: k3s single-node server via the in-tree module (`services.k3s`),
  SQLite datastore, auto-generated token, `--write-kubeconfig-mode 644`.
- **Secrets**: sops-nix skeleton (`sops.age.sshKeyPaths`), no secrets yet.
- **Access**: admin user `runic` + root, key-only SSH
  (`PasswordAuthentication false`), passwordless sudo via wheel.
- **Observability/ops UI**: Rancher Manager deployed on the k3s cluster at
  `https://rancher.local`; k9s for terminal cluster ops.

```mermaid
graph TD
    A[Flake inputs: nixpkgs 26.05, disko, home-manager, deploy-rs, sops-nix] --> B[nixosConfigurations.node-main]
    B --> C[disko: nvme0n1 root/swap/EFI + sda k3s-data]
    B --> D[services.k3s server, single-node SQLite]
    B --> E[users runic + root, key-only SSH]
    B --> F[sops-nix skeleton]
    D --> G[Rancher Manager / rancher.local]
    D --> H[k9s + kubectl + helm for runic]
```

## Fit into Homelab

```mermaid
graph TD
    Admin[Admin workstation 192.168.111.12] -->|deploy-rs over SSH| N[node-main 192.168.111.7]
    N -->|services.k3s| K3S[k3s cluster]
    K3S -->|traefik ingress| R[Rancher https://rancher.local]
    K3S -->|local-path on sda| PV[(/var/lib/rancher/k3s on sda 954G)]
    Admin -->|browser| R
```

node-main keeps the existing homelab services role (ingress, workloads, storage) while
the host OS becomes fully declarative. Ongoing changes flow through the flake via
deploy-rs; the same flake can later target additional nodes.
