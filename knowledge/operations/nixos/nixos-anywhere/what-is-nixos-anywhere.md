---
title: "What is nixos-anywhere"
status: draft
author: "padawont"
date: 2026-07-14
tags:
  - nixos-anywhere
  - nixos
  - provisioning
  - ssh
sources:
  - url: "https://github.com/nix-community/nixos-anywhere"
    title: "nix-community/nixos-anywhere — Install NixOS everywhere via SSH"
  - url: "https://nixos.org/manual/nixos/stable/#sec-installation"
    title: "NixOS Manual — Installation"
last_audit_date: 2026-07-14
---

# What is nixos-anywhere

nixos-anywhere is a tool for installing NixOS on any SSH-accessible machine without requiring physical access or ISO boot. It handles the full installation workflow: kexec into a temporary NixOS environment, run [disko](https://github.com/nix-community/disko) for partitioning, and perform `nixos-install` — all from a single CLI command.

## When to use it

nixos-anywhere is ideal when:

| Scenario | Example |
|---|---|
| Remote servers | VPS, bare metal, cloud instances where you cannot boot an ISO |
| No physical access | Machines in a datacenter, remote offices |
| Automated provisioning | CI/CD pipeline deploying NixOS to new hosts |
| Fleet deployment | Provisioning multiple identical servers from a shared config |
| Existing Linux migration | Replace Debian/Ubuntu on a running server with NixOS |

When NOT to use it:

| Scenario | Alternative |
|---|---|
| You have physical access and can boot an ISO | [ISO installation](../installation.md) — simpler |
| Air-gapped machine | Pre-download nixpkgs, use local binary cache |
| No SSH root access | Use a live ISO and manual steps |
| ARM with unsupported kexec | Boot from a NixOS installer image instead |

## How it works

1. **SSH connection** — connects to the target machine over SSH
2. **kexec** — if no NixOS installer is detected, uses `kexec` to boot a temporary NixOS environment in memory
3. **disko** — partitions and formats disks according to your `disko-config.nix`
4. **nixos-install** — installs NixOS using your flake configuration
5. **Cleanup** — optionally reboots into the new system

The entire process is unattended after the initial command.

## Prerequisites

**Source machine** (where you run the command):

- Nix installed (any Linux/macOS with Nix works)
- SSH access to the target

**Target machine** (where NixOS will be installed):

- SSH server running with root or sudo access
- x86_64-linux with kexec support (most x86_64 Linux systems qualify)
- At least 1 GB RAM (excluding swap) when using kexec
- Reachable over network (public internet or LAN)
- Supported base OS: Debian, Ubuntu, Fedora, CentOS, or any Linux with kexec support

For aarch64 or other architectures, provide a custom kexec image.

## Basic command

```console
# Minimal usage with flakes
$ nix run github:nix-community/nixos-anywhere -- --flake .#host root@server.ip

# With disko config (explicit mode, though disko runs by default)
$ nix run github:nix-community/nixos-anywhere -- --flake .#host root@server.ip --disko-mode disko

# Using a specific kexec image
$ nix run github:nix-community/nixos-anywhere -- \
  --flake .#host \
  --kexec "$(nix build --print-out-paths github:nix-community/nixos-images#packages.x86_64-linux.kexec-installer-nixos-unstable-noninteractive)/nixos-kexec-installer-noninteractive-x86_64-linux.tar.gz" \
  root@server.ip
```

## See also

- [basic-usage.md](basic-usage.md) — CLI flags, flake setup, end-to-end example
- [disko-integration.md](disko-integration.md) — Declarative disk partitioning configurations

## Important warning

nixos-anywhere **completely overwrites** the target machine's disks. All existing data is lost. Never run this against a production server.

Deprecated name notice: This project was previously hosted in the `numtide` organization but now lives at `github:nix-community/nixos-anywhere`.
