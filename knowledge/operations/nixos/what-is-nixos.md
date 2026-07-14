---
title: "What is NixOS"
status: draft
author: "padawont"
date: 2026-07-14
tags:
  - nixos
  - nix
  - declarative-configuration
sources:
  - url: "https://nixos.org/manual/nixos/stable/"
    title: "NixOS Manual (stable)"
  - url: "https://nixos.org/manual/nix/stable/"
    title: "Nix Reference Manual (stable)"
  - url: "https://zero-to-nix.com/"
    title: "Zero to Nix"
last_audit_date: 2026-07-14
---

# What is NixOS

NixOS is a Linux distribution built on the Nix package manager. It extends Nix's purely functional model to the entire operating system — the kernel, drivers, services, packages, and configuration files are all declared in Nix expressions and managed atomically.

## Declarative OS model

Instead of configuring a system by running imperative commands (e.g. `apt install`, editing files in `/etc`), NixOS uses a single declarative configuration file (`/etc/nixos/configuration.nix`) as the source of truth. Running `nixos-rebuild switch` applies that configuration to the running system.

Key properties of the declarative model:

- **Reproducible** — the same configuration produces the same system state (modulo hardware differences).
- **Self-documenting** — the configuration file serves as the canonical reference for what is installed and configured.
- **Atomic upgrades** — system state is never partially updated; either the full switch succeeds or nothing changes.
- **Rollback** — every `nixos-rebuild switch` creates a new bootable generation; the previous generation remains available in the boot menu.

## Nix language

NixOS configurations are written in the Nix language, a purely functional, lazy, domain-specific language. Key Nix language concepts used in NixOS configurations:

| Concept | Description | Example |
|---|---|---|
| Attribute sets | Key-value maps, the core data structure | `{ services.openssh.enable = true; }` |
| Let-in | Bind variables in scope | `let pkgs = import <nixpkgs> {}; in ...` |
| With | Bring attribute set keys into scope | `with pkgs; [ hello git ]` |
| Functions | Lambdas for parameterization | `{ config, pkgs, ... }: { ... }` |
| Imports | Load other Nix files | `imports = [ ./hardware-configuration.nix ];` |
| String interpolation | Embed expressions in strings | `"${pkgs.hello}/bin/hello"` |

Nix expressions evaluate to **derivations** — build recipes that describe how to produce a package. Derivations are stored in the Nix store under unique content-addressed paths.

## Generations

Every time `nixos-rebuild switch` is run, NixOS creates a new **generation** — a complete, self-contained snapshot of the system configuration and all its packages. Generations appear as boot menu entries (in systemd-boot or GRUB).

```console
# List all generations
$ nix-env --list-generations -p /nix/var/nix/profiles/system

# Switch to a specific generation at next boot
$ sudo nixos-rebuild switch --rollback

# Delete old generations
$ sudo nix-env --delete-generations -p /nix/var/nix/profiles/system 7d
$ sudo nix-collect-garbage
```

## Nix store

All packages and configurations live under `/nix/store` in paths like:

```
/nix/store/q06x3jll2yfzckz2bzqak089p43ixkkq-firefox-33.1/
```

The hash (`q06x3jll...`) is a cryptographic digest of the build inputs — dependencies, source code, and build scripts. This means:

- Different versions of the same package can coexist (no DLL hell).
- Upgrades never overwrite existing packages — they add new store paths.
- Unused packages are removed by garbage collection.

## Comparison to imperative distributions

| Aspect | NixOS | Traditional (Debian/Ubuntu) |
|---|---|---|
| Configuration | Declarative (`configuration.nix`) | Imperative (editing files, running commands) |
| Package installation | Add to `environment.systemPackages`, rebuild | `apt install` |
| Upgrades | Atomic, new generation created | In-place, can leave partial state |
| Rollback | Boot into previous generation | Difficult, often requires restore |
| Reproducibility | Same config = same system | Depends on package versions and manual state |
| Multi-user installs | Users can install software safely without root | Requires `sudo` or package manager |
