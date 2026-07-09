---
title: "nixos"
status: active
date: 2026-07-09
tags: [server, nixos, longhorn]
machine: nixos
related_services: [longhorn]
---

# nixos

NixOS server node for Longhorn storage cluster.

## Storage Layout

| Mount | Device | Size | FSType | Purpose |
|---|---|---|---|---|
| / | tmpfs | 16G | tmpfs | Root (ephemeral) |
| /nix/.ro-store | /dev/loop0 | 1.5G | squashfs | Nix read-only store |
| /mnt/longhorn-nvme | /dev/nvme0n1 | 447G | ext4 | Longhorn storage (fast) |
| /mnt/longhorn-sda | /dev/sda | 954G | ext4 | Longhorn storage (bulk) |

## Notes

- NixOS 26.05 on kernel 6.18.34
- Root is tmpfs — NixOS ephemeral config
- /dev/sdb (466G) present but not mounted
- No swap configured
- Longhorn storage backend
- Docker + flannel networking active
- WiFi interface (wlp5s0) is down; only wired enp6s0 in use
