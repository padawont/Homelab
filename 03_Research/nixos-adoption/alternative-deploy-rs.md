---
title: "Alternative: deploy-rs"
status: draft
author: "padawont"
date: 2026-08-20
tags: [nixos, deployment, deploy-rs, flakes]
sources:
  - knowledge: "./02_Knowledge/technologies/tools/nixos/flakes.md"
references:
  - url: "https://github.com/serokell/deploy-rs"
    title: "deploy-rs"
last_audit_date: 2026-08-20
---

# Alternative: deploy-rs

## Overview

A Rust CLI by Serokell that deploys NixOS configurations from a flake. It evaluates the flake's `deploy.nodes` output, builds each profile, copies the closure to targets over SSH, and runs the NixOS activation script. Handles NixOS, home-manager, nix-darwin, and custom profiles. See `./overview.md` for the deployment comparison and the flake foundation in the [K1 flakes note](./02_Knowledge/technologies/tools/nixos/flakes.md).

## Pros

- **Flake-native**: nodes are declared in the flake, e.g. `deploy.nodes.<name>.profiles.system.path = deploy-rs.lib.<system>.activate.nixos self.nixosConfigurations.<name>`; `deployChecks` integrates with `nix flake check`
- **One command deploys all nodes** (`deploy .`); builds run in parallel, activation runs sequentially
- **Automatic rollback on activation failure** via `autoRollback` (default on); `magicRollback` makes a node self-roll-back if unreachable within `confirmTimeout` (default 30s) — protects against breaking SSH
- **Zero server-side state**: a single binary, no agent, DB, or daemon; only SSH and Nix on targets
- **Runtime overrides**: `--hostname` / `--ssh-user` / `--sudo` per run — deploy the same profile to any node without editing config; `--groups` filters node sets
- **Secrets transparent**: sops-nix/agenix decryption happens at build/activation time
- **Active maintenance**: commits through Aug 10 2026, ~385 commits, 2.3k stars

## Cons

- Hosts declared statically in the flake — no inventory file
- No formal releases/tags — rides master or a nixpkgs pin
- Activation phase is sequential (fine for small fleets)
- magicRollback can silently revert configs that change SSH networking — must be disabled for such changes
- Bootstrap gap — cannot install NixOS on an existing Ubuntu host; needs a separate conversion step (e.g. nixos-anywhere or manual install)
- Thin docs — no dedicated docs site; README + examples
- No native secret handling — relies on sops-nix/agenix at build time

## Evaluation

- **Portability to any node**: strong — runtime `--hostname` override deploys the same profile to any host
- **Flake-native**: yes — nodes, profiles, and `deployChecks` all live in the flake
- **Multi-node**: one command, parallel builds, sequential activation
- **Rollback**: excellent — autoRollback on activation failure plus magicRollback for unreachable nodes
- **Secrets wiring**: transparent via sops-nix
- **Maturity/stability**: actively maintained, but no release tags to pin to
- **Maintenance burden**: low-moderate — no server-side state

## Verdict

**Selected** — the best fit for the homelab's hard portability requirement (runtime host override) and rollback safety for unattended node updates, backed by active maintenance. Caveats to record in the ADR: pin via nixpkgs, and disable magicRollback when changing SSH-related networking.
