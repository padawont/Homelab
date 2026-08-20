---
title: "NixOS declarative configuration"
status: accepted
author: "padawont"
date: 2026-08-20
tags: [nixos, declarative-config, configuration]
sources:
  - url: "https://nixos.org/manual/nixos/stable/"
    title: "NixOS manual"
last_audit_date: 2026-08-20
related_docs:
  - "./02_Knowledge/technologies/tools/nixos/flakes.md"
  - "./02_Knowledge/technologies/tools/nixos/home-manager.md"
  - "./02_Knowledge/technologies/tools/nixos/services-secrets.md"
  - "./05_Implementations/node-main/nixos/"
---

# NixOS declarative configuration

## Overview

NixOS is a Linux distribution whose entire system — packages, services, users, kernel, network — is described declaratively in Nix expressions and built reproducibly. Changing the system means editing config and rebuilding; the old configuration remains bootable, giving atomic upgrades and easy rollback. This is the foundation the homelab migration (#26 cluster, epic #25) builds on.

## Details

### configuration.nix

The main entry point. It is a NixOS *module*: a function taking `{ config, pkgs, ... }` and returning attribute sets of *options* that configure the system.

Example — abstract:

```nix
{ config, pkgs, ... }:
{
  boot.loader.systemd-boot.enable = true;
  networking.hostName = "node-main";
  environment.systemPackages = [ pkgs.git pkgs.tmux ];
  system.stateVersion = "26.05";
}
```

### Options

Every aspect of the system is set through options like `boot.loader.*`, `networking.*`, `environment.systemPackages`, and `services.<name>.*`. The full set is documented in the manual's option reference.

### Modules

Example — abstract: A module is the unit of configuration. It declares options and provides their values:

```nix
{ config, lib, pkgs, ... }:
{
  options.myService.enable = lib.mkEnableOption "myService";
  config = lib.mkIf config.myService.enable {
    # settings derived from the option
  };
}
```

Modules are composed via `imports`, letting a flake assemble `configuration.nix`, `home-manager`, and custom host modules into one system.

### Rebuilding

- `nixos-rebuild switch` — build and activate the new config
- `nixos-rebuild boot` — build and set as default boot entry, activate on reboot
- `nixos-rebuild build` — build only, no activation, output in `./result`

Rollback: on next boot the previous generation can be selected from the bootloader menu, so a failed change never bricks the host.

### Channels vs flakes

Channels (`nix-channel`, `nixos-<version>`) are the legacy way to select nixpkgs. Flakes (`flake.nix` + `flake.lock`) replace them with pinned, reproducible inputs. The homelab targets flakes — see `./02_Knowledge/technologies/tools/nixos/flakes.md`.

## Sources / Further Reading

- [NixOS manual](https://nixos.org/manual/nixos/stable/)
- See `./02_Knowledge/technologies/tools/nixos/flakes.md` for flake-based system definitions and `./02_Knowledge/technologies/tools/nixos/services-secrets.md` for declaring services and secrets.
