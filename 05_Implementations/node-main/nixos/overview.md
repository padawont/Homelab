---
title: "NixOS host on node-main"
status: active
author: "padawont"
date: 2026-08-23
tags: [nixos, k3s, deploy-rs, nixos-anywhere, disko, provisioning]
technologies: [nixos, nixos-anywhere, disko, deploy-rs, k3s, sops-nix, home-manager]
related_docs:
  - "./04_ADRs/26-adopt-nixos-on-node-main.md"
  - "./02_Knowledge/technologies/tools/nixos/overview.md"
  - "./02_Knowledge/technologies/tools/nixos-anywhere/overview.md"
  - "./02_Knowledge/technologies/tools/nixos-anywhere/usage.md"
  - "./02_Knowledge/technologies/kubernetes/k3s/installation.md"
references:
  online:
    - url: "https://nix-community.github.io/nixos-anywhere/"
      title: "nixos-anywhere docs"
    - url: "https://github.com/serokell/deploy-rs"
      title: "deploy-rs"
  repo:
    - "./05_Implementations/node-main/nixos/flake.nix"
node: node-main
---

# NixOS host on node-main

## Prerequisites

- Target machine reachable on the LAN (here `192.168.111.7`), running either a
  NixOS installer (direct boot) or any Linux with kexec.
- A machine with Nix + flakes (the admin workstation).
- `SSHPASS` set for the installer's `nixos` user password during bootstrap.

## Deployment

### Pre-deploy checks

- `nix flake check` and `nix build .#nixosConfigurations.node-main.config.system.build.toplevel` pass.
- `lsblk` on the target confirms the disk devices match `disk-config.nix`.

### Deploy (bootstrap, destructive — wipes nvme0n1 + sda)

```bash
cd 05_Implementations/node-main/nixos
export SSHPASS=nixos
nix run github:nix-community/nixos-anywhere -- \
  --generate-hardware-config nixos-generate-config ./hardware-configuration.nix \
  --flake .#node-main \
  --target-host nixos@192.168.111.7 --env-password
```

If the machine reboots into the installer USB afterwards, fix firmware boot order
(`sudo efibootmgr -o <boot0>,...` putting "Linux Boot Manager" first) or remove the USB.

### Post-deploy verification

```bash
ssh -i ~/.ssh/id_ed25519 runic@192.168.111.7 'hostname; sudo k3s kubectl get nodes'
```

### Ongoing updates (deploy-rs)

```bash
cd 05_Implementations/node-main/nixos
nix run github:serokell/deploy-rs -- .#node-main
```

## Configuration

| File | Purpose |
|---|---|
| `flake.nix` | Inputs (nixpkgs 26.05, disko, home-manager, deploy-rs, sops-nix), `nixosConfigurations.node-main`, `deploy.nodes.node-main` |
| `disk-config.nix` | disko layout: nvme0n1 EFI+swap+ext4 root; sda ext4 at `/var/lib/rancher/k3s` |
| `configuration.nix` | hostname, users (runic/root), key-only SSH, k3s server, firewall (6443/10250/8472), sops skeleton |
| `home.nix` | runic home: kubectl, k9s, kubernetes-helm, kubectx |
| `hardware-configuration.nix` | Generated at install (`nixos-generate-config`), AMD CPU/modules |

## Operations

- **k3s**: `systemctl status k3s`, `sudo k3s kubectl get nodes`, logs `journalctl -u k3s -f`.
- **kubectl as runic**: `KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl ...`.
- **deploy-rs**: `nix run github:serokell/deploy-rs -- .#node-main`; disable
  `magicRollback` when intentionally changing SSH-relevant config.
- **Secrets**: sops-nix skeleton only; add `sops.secrets.*` in configuration.nix + a
  `secrets.yaml` when the first secret lands (k3s token, Rancher bootstrap).
- **Rollback**: see `./rollback.md`.
