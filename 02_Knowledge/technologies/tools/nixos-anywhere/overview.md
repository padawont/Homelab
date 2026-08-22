---
title: "NixOS Anywhere"
status: accepted
author: "padawont"
date: 2026-08-22
tags: [nixos, nixos-anywhere, provisioning, deployment, disko, kexec]
sources:
  - url: "https://github.com/nix-community/nixos-anywhere"
    title: "nixos-anywhere GitHub README"
  - url: "https://nix-community.github.io/nixos-anywhere/"
    title: "nixos-anywhere docs"
  - url: "https://nix-community.github.io/nixos-anywhere/requirements.html"
    title: "nixos-anywhere system requirements"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/tools/nixos/flakes.md"
  - "./02_Knowledge/technologies/tools/nixos/overview.md"
  - "./02_Knowledge/technologies/tools/nixos-anywhere/usage.md"
  - "./02_Knowledge/technologies/tools/nixos-anywhere/install-methods.md"
  - "./03_Research/nixos-adoption/overview.md"
  - "./03_Research/nixos-adoption/alternative-deploy-rs.md"
---

# NixOS Anywhere

## Overview

nixos-anywhere is a nix-community tool (MIT licensed, maintained by @Mic92, @Lassulus, @phaer, @Enzime, @a-kenji) that installs NixOS on a remote machine over SSH. The whole install — disk partitioning and formatting, NixOS configuration and installation, and optional extra software/files — is pre-configured, so a single command performs an unattended install with no babysitting. The same stored configuration can be reused to create identical servers anywhere: cloud VMs, bare metal (e.g. Hetzner), or LAN machines.

In this homelab it is the missing bootstrap step of the NixOS migration (#26 cluster): deploy-rs updates an already-installed NixOS, while nixos-anywhere performs the initial Ubuntu→NixOS conversion on a new node.

## Details

### Installation pipeline

Given a flake with a host configuration and a disko disk layout, a single run:

1. Connects to the target via SSH
2. Detects whether a NixOS installer is already running; if not, boots one using Linux `kexec`
3. Partitions and formats the disks with the `disko` tool
4. Installs NixOS
5. Optionally installs extra Nix packages/software
6. Optionally copies additional files to the new machine

### Two boot modes

- **kexec path** — the target is running any Linux with kexec support; nixos-anywhere kexecs into a NixOS installer and continues unattended
- **Direct boot path** — the target has no OS (or you boot it yourself from a NixOS installer image); nixos-anywhere detects the running installer and skips kexec

See `./02_Knowledge/technologies/tools/nixos-anywhere/install-methods.md` for the full breakdown.

### Requirements

| Machine | Requirement |
|---|---|
| Source | Any machine with Nix installed — Linux, macOS, or Windows via WSL2 |
| Target (kexec) | x86-64 or aarch64 Linux with kexec support; at least 1.5 GB RAM (excluding swap) |
| Target (direct boot) | Already running a NixOS installer |
| Network | Reachable over public internet or local network; wifi is not supported (VPN needs a custom `--kexec` installer) |

### Safety

Never run nixos-anywhere against a production server — the target is completely overwritten and all data lost. Use it only to commission a new machine or repurpose an old one after migrating important data.

### Related tools

- `disko` — the partitioning/formatting engine nixos-anywhere drives; disk layout is declared as a disko config
- After install, ongoing updates use `nixos-rebuild switch --flake` or a deployment tool such as deploy-rs (selected in the NixOS adoption research) or colmena — see `./03_Research/nixos-adoption/overview.md`

## Sources / Further Reading

- [nixos-anywhere GitHub](https://github.com/nix-community/nixos-anywhere) · [docs](https://nix-community.github.io/nixos-anywhere/)
- [System requirements](https://nix-community.github.io/nixos-anywhere/requirements.html)
- [disko](https://github.com/nix-community/disko)
- See `./02_Knowledge/technologies/tools/nixos-anywhere/usage.md` for the CLI workflow and `./02_Knowledge/technologies/tools/nixos-anywhere/install-methods.md` for kexec/hardware-config details. Flake foundations are in `./02_Knowledge/technologies/tools/nixos/flakes.md`.
