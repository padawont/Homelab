---
title: "NixOS Anywhere install methods"
status: accepted
author: "padawont"
date: 2026-08-22
tags: [nixos, nixos-anywhere, kexec, disko, provisioning]
sources:
  - url: "https://nix-community.github.io/nixos-anywhere/requirements.html"
    title: "nixos-anywhere system requirements"
  - url: "https://nix-community.github.io/nixos-anywhere/howtos/INDEX.html"
    title: "nixos-anywhere how-to guide index"
  - url: "https://github.com/nix-community/nixos-facter"
    title: "nixos-facter"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/tools/nixos-anywhere/overview.md"
  - "./02_Knowledge/technologies/tools/nixos-anywhere/usage.md"
---

# NixOS Anywhere install methods

## Overview

Before nixos-anywhere can run the disko/install steps, the target must be running a NixOS installer. There are two ways to get there — `kexec` (from an existing Linux system) or direct boot (from an installer image on an OS-less machine). This note also covers hardware-configuration generation, which happens during the same run.

## Details

### kexec mode

`kexec` is a Linux syscall that boots a new kernel directly from the running system without a full hardware reboot. nixos-anywhere uses it to load a NixOS installer kernel/initrd over the network, switch to it, and continue the install over the same SSH connection.

- Requires an x86-64 or aarch64 Linux system with kexec support (most x86-64 systems support it)
- Requires at least 1.5 GB of RAM (excluding swap)
- Wifi-only machines are not supported; if the target needs a VPN to be reachable, provide a custom installer via `--kexec` that connects to the VPN

### Custom kexec images

The `--kexec <path-or-url>` flag supplies a custom kexec image that boots the NixOS installer, and `--kexec-extra-flags <flags>` passes extra flags to the kexec call (e.g. `--no-sync`). Use a custom image when:

- The target architecture is not covered by the default images
- The installer must join a VPN to continue
- You want to control exactly which installer is booted

### Direct boot mode

For a machine with no current operating system, boot it from a NixOS installer image first (USB, IPMI/KVM virtual media, etc.). nixos-anywhere detects that a NixOS installer is already running and skips the kexec step, then proceeds with disko partitioning and installation. Useful because you still get the fully pre-configured, single-command install.

### Hardware-configuration generation

A fresh machine's hardware (drivers, disk layout, kernel modules) differs from the source machine, so nixos-anywhere can generate the hardware config during install with `--generate-hardware-config <tool> <output>`:

- **nixos-generate-config** — writes `hardware-configuration.nix`; the flake must import it (add `./hardware-configuration.nix` to the modules list). This is the classic NixOS approach.
- **nixos-facter** — writes `facter.json`; the flake sets `{ hardware.facter.reportPath = ./facter.json; }` in its modules. More comprehensive hardware reports: configures drivers, kernel modules, and firmware based on detected hardware.

Both options avoid manually crafting hardware config for each new node — relevant when commissioning multiple nodes from one portable flake.

### VM testing

Before installing on real hardware, `--vm-test` builds the flake config and runs the disko layout inside a virtual machine. Use it to validate the disk config and NixOS modules without touching the target. Requires that the flake does not import a non-existent `hardware-configuration.nix`/`facter.json` (skip it if the hardware config is not generated yet).

## Sources / Further Reading

- [System requirements](https://nix-community.github.io/nixos-anywhere/requirements.html)
- [How-to guide index](https://nix-community.github.io/nixos-anywhere/howtos/INDEX.html)
- [nixos-facter](https://github.com/nix-community/nixos-facter)
- See `./02_Knowledge/technologies/tools/nixos-anywhere/overview.md` for the install pipeline and `./02_Knowledge/technologies/tools/nixos-anywhere/usage.md` for the CLI flags that select these methods.
