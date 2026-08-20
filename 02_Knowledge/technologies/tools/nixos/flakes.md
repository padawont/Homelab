---
title: "Nix Flakes"
status: accepted
author: "padawont"
date: 2026-08-20
tags: [nix, flakes, reproducible-builds]
sources:
  - url: "https://wiki.nixos.org/wiki/Flakes"
    title: "Flakes wiki"
last_audit_date: 2026-08-20
related_docs:
  - "./02_Knowledge/technologies/tools/nixos/overview.md"
  - "./02_Knowledge/technologies/tools/nixos/home-manager.md"
---

# Nix Flakes

## Overview

Flakes are the standard, experimental-but-de-facto format for Nix projects. A flake pins all dependencies in a `flake.lock` file, making builds and system configs reproducible across machines and over time. They are the mechanism that lets one homelab configuration be deployed to any node (`nixosConfigurations` per host), satisfying the portability requirement of the NixOS migration (#26 cluster).

## Details

### flake.nix structure

A flake has `inputs` (locked dependencies) and `outputs` (a function of those inputs):

Example — abstract:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    home-manager = {
      url = "github:nix-community/home-manager/release-26.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, home-manager, ... }: {
    nixosConfigurations.node-main = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./hosts/node-main/configuration.nix
        home-manager.nixosModules.home-manager
      ];
    };
  };
}
```

### Inputs and pinning

Each `inputs.<name>` is fetched and recorded in `flake.lock` with a content hash. `nix flake lock` pins inputs; `nix flake update` bumps them. The lockfile guarantees the same inputs resolve on any machine, which is what makes deployments to fresh nodes reproducible.

`inputs.nixpkgs.follows = "nixpkgs"` makes home-manager (or other inputs) use the same nixpkgs rev, avoiding version skew between inputs.

### Outputs relevant to a homelab

- `nixosConfigurations.<host>` — a complete NixOS system definition per node
- `nixosModules.<name>` — reusable module (e.g. a shared base module for all hosts)

Example — abstract:

```nix
{ config, lib, ... }: {
  imports = [ ./users.nix ./services-base.nix ];
  networking.firewall.enable = lib.mkDefault true;
}
```

- `packages.<system>.<name>` — buildable artifacts
- `devShells.<system>.default` — a dev environment for working on the config

### Commands

- `nix flake show` — list a flake's outputs
- `nix flake lock` / `nix flake update` — pin / bump inputs
- `nix flake check` — evaluates all outputs and builds the flake's checks (tests)

### Building a host

`nixos-rebuild switch --flake .#node-main` builds and activates the host named `node-main` from the current flake — the same invocation works for any host, on any machine.

## Sources / Further Reading

- [Flakes wiki](https://wiki.nixos.org/wiki/Flakes)
- See `./02_Knowledge/technologies/tools/nixos/overview.md` for how flakes replace channels, and `./02_Knowledge/technologies/tools/nixos/home-manager.md` for integrating home-manager as a module.
