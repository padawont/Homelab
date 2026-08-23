---
title: "NixOS host on node-main — rollback"
status: active
author: "padawont"
date: 2026-08-23
tags: [nixos, rollback, nixos-anywhere]
technologies: [nixos, nixos-anywhere, disko]
related_docs:
  - "./overview.md"
references:
  online:
    - url: "https://nix-community.github.io/nixos-anywhere/"
      title: "nixos-anywhere docs"
  repo: []
node: node-main
---

# NixOS host on node-main — Rollback

## Prerequisites

- Bootable NixOS installer USB for the target machine.
- The flake at `configs/` and `SSHPASS` for the installer's `nixos` user.
- Boot menu access (or `efibootmgr`) to boot the installer.

## Rollback steps

A broken NixOS host on node-main is restored by reinstalling declaratively — the
flake is the single source of truth, so "rollback" == "reinstall to known-good".

1. Boot the NixOS installer USB (pick it in the firmware boot menu).
2. Confirm the node is reachable via SSH (`nixos` user, `SSHPASS`).
3. Re-run the bootstrap install (wipes both disks):

```bash
cd 05_Implementations/node-main/nixos
export SSHPASS=nixos
nix run github:nix-community/nixos-anywhere -- \
  --generate-hardware-config nixos-generate-config ./hardware-configuration.nix \
  --flake .#node-main \
  --target-host nixos@192.168.111.7 --env-password
```

4. Fix firmware boot order if it reboots into the USB
   (`sudo efibootmgr -o 0000,...`).

Alternative for config-only breakage (system still boots, SSH works):

```bash
# revert to the previous system generation at the boot menu (systemd-boot),
# or rebuild with deploy-rs:
cd 05_Implementations/node-main/nixos
nix run github:serokell/deploy-rs -- .#node-main
```

## Verification

- `ssh -i ~/.ssh/id_ed25519 runic@192.168.111.7 'hostname'` returns `node-main`.
- `sudo k3s kubectl get nodes` shows `node-main` Ready.
- `df -h /var/lib/rancher/k3s` shows the sda data disk mounted.
