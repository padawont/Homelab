---
title: "Alternative: NixOps"
status: draft
author: "padawont"
date: 2026-08-20
tags: [nixos, deployment, nixops, flakes]
sources:
  - knowledge: "./02_Knowledge/technologies/tools/nixos/flakes.md"
references:
  - url: "https://nixops.dev/"
    title: "NixOps"
  - url: "https://github.com/NixOS/nixops"
    title: "NixOS/nixops"
  - url: "https://github.com/nixops4/nixops4-nixos"
    title: "nixops4-nixos"
last_audit_date: 2026-08-20
---

# Alternative: NixOps

## Overview

NixOps is NixOS's own deployment tool, mid-rewrite and effectively two products. See `./overview.md` for the deployment comparison and the flake foundation in the [K1 flakes note](./02_Knowledge/technologies/tools/nixos/flakes.md).

- **NixOps 2.x** (`NixOS/nixops`, Python): mature but in low-maintenance mode — maintainers say it is "probably not suited for new projects". Last release v1.7. Not flake-native: plain `.nix` network expressions plus a local state file. Deploys to existing hardware via `deployment.targetHost` with `targetEnv` unset (no backend). Multi-node through the "network" abstraction with parallel operations. Opt-in rollback (`network.enableRollback` + `nixops rollback`). Ships its own `/run/keys` secret mechanism — no agenix/sops-nix integration.
- **NixOps4** (`nixops4/nixops4`, Rust rewrite): flake-native — root expression comes from the flake `nixops4` output, applied with `nixops4 apply <member>`, with a flake-parts module. Deploys to existing hosts over SSH (`nix copy --to ssh-ng://` + apply switch; host keys declared in the expression). Status: "in development", zero releases; the nixops4-nixos provider is explicitly "pre-release — features subject to change". No rollback UX, no documented secrets integration, no multi-node/parallel docs. Resource definitions are hand-written; the README admits they are "not representative of the final product".

## Pros

- **NixOps 2.x**
  - Proven tool with years of production history
  - Deploys to existing hosts via `deployment.targetHost` — no reinstall needed
  - Real multi-node "network" abstraction with parallel ops across machines
  - Opt-in rollback (`network.enableRollback` / `nixops rollback`)
  - Own `/run/keys` secret-handling mechanism
- **NixOps4**
  - Flake-native — root expression from the flake `nixops4` output matches homelab flake configs
  - Rust rewrite on a sustainable architecture
  - Actively developed

## Cons

- **NixOps 2.x**
  - Low-maintenance mode; last release v1.7; maintainers point new users to NixOps4
  - Not flake-native (plain `.nix` network expressions, local state file)
  - No agenix/sops-nix integration — only its own `/run/keys` mechanism
  - Likely a dead-end line
- **NixOps4**
  - In development, zero releases, pre-release provider
  - Manual host-key and resource plumbing
  - No rollback UX
  - No documented secrets integration
  - Churn risk mid-rewrite (API/format not stable)

## Evaluation

- **Portability to any node**: both deploy over SSH to existing hosts — but NixOps 2.x is non-flake and NixOps4 is unreleased
- **Flake-native**: NixOps 2.x no; NixOps4 yes
- **Multi-node**: NixOps 2.x strong (network abstraction, parallel ops); NixOps4 undocumented
- **Rollback**: NixOps 2.x opt-in; NixOps4 none
- **Secrets wiring**: NixOps 2.x own `/run/keys`; NixOps4 none documented
- **Maturity/stability**: NixOps 2.x stable but abandoned; NixOps4 actively developed but unreleased
- **Maintenance burden**: NixOps 2.x moderate but on an abandoned codebase; NixOps4 high — must track main

## Verdict

**Rejected.** The stable line (NixOps 2.x) is abandoned and not flake-native; the maintained line (NixOps4) is unreleased pre-production software with no rollback or secrets story. Not viable as the homelab's primary deploy path. NixOps4 is worth revisiting when it ships a stable release.
