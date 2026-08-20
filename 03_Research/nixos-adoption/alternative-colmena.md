---
title: "Alternative: colmena"
status: accepted
author: "padawont"
date: 2026-08-20
tags: [nixos, deployment, colmena, flakes]
sources:
  - knowledge: "./02_Knowledge/technologies/tools/nixos/flakes.md"
references:
  - url: "https://colmena.cli.rs/"
    title: "colmena manual"
last_audit_date: 2026-08-20
---

# Alternative: colmena

## Overview

Stateless NixOS deployment tool written in Rust, modeled after NixOps and morph. It is a thin wrapper over the underlying Nix commands and is built specifically for parallel multi-host deployment. The project now lives under the nix-community umbrella.

## Pros

- Single binary, stateless, zero extra infrastructure to run.
- True parallel multi-node deploys: `colmena apply` targets all nodes, with default parallelism of 10, tunable via `-p`; `--on` filters nodes with globs and `@tag` groups.
- Native flake support via the `colmenaHive` output (`colmena.lib.makeHive`).
- Reuses existing NixOS modules — no separate module language to learn.
- Ships out-of-band `deployment.keys` and works unchanged with sops-nix/agenix.
- `apply-local` lets a fresh NixOS box pull its own config — useful for Ubuntu→NixOS migration.
- Packaged in nixpkgs, well-documented manual, nix-community backed (~2.3k stars).

## Cons

- Hosts must be declared in config via `deployment.targetHost`; there is no runtime hostname override — weak for ad-hoc "deploy to any node" flows.
- Requires a dedicated `colmenaHive` output; a flake exposing only plain `nixosConfigurations` needs a wrapper.
- No automatic rollback — relies on NixOS generations and manual rollback.
- Known-limited error reporting.
- Slow release cadence (last stable v0.4.0, 2023-05-15) and "0.x" versioning.
- Static target mapping means nodes must be pre-declared before they can be deployed to.

## Evaluation

- **Portability to any node**: weaker — target mapping is static config; nodes must be pre-declared in `deployment.targetHost`.
- **Flake-native**: yes, but via a dedicated `colmenaHive` output, not plain `nixosConfigurations`.
- **Multi-node**: excellent — parallel deploys, `--on` glob filters, and `@tag` groups that mirror k3s role groups.
- **Rollback**: none automatic; recovery depends on manual generation rollback.
- **Secrets wiring**: compatible with sops-nix.
- **Maturity/stability**: mature and battle-tested, but the release cadence is slow.
- **Maintenance burden**: low — stateless, minimal config surface.

## Verdict

**Rejected — runner-up.** Strong for a declared, known fleet and parallel k3s role-group updates, but no automatic rollback and the static node mapping weakens the hard portability requirement. Kept as a close second if deploy-rs is later deemed unsuitable. See `./overview.md` for the recommendation and plan for the ADR.
