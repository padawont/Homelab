---
title: "RunicEngine"
status: active
date: 2025-07-09
tags: [desktop, workstation]
machine: runic-engine
---

# RunicEngine

Primary desktop and homelab host. Runs CachyOS with Docker.

## Storage Layout

| Mount | Device | Size | Purpose |
|---|---|---|---|
| / | /dev/sdd2 | 465G | OS + home (btrfs) |
| /mnt/games | /dev/sdc1 | 447G | Games |
| /mnt/projects | /dev/sdb1 | 112G | Projects |
| /mnt/videos | /dev/sda1 | 224G | Videos |

## Notes

- BTRFS subvolumes for /home, /var/log, /var/tmp, /srv, /root, /var/cache
- ZRAM swap (31G)
- Wayland + KDE Plasma 6
- Docker installed (no active containers yet)
