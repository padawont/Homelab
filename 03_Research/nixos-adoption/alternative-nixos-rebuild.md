---
title: "Alternative: nixos-rebuild"
status: draft
author: "padawont"
date: 2026-08-20
tags: [nixos, deployment, nixos-rebuild, flakes]
sources:
  - knowledge: "./02_Knowledge/technologies/tools/nixos/overview.md"
references:
  - url: "https://nixos.org/manual/nixos/stable/"
    title: "NixOS manual"
last_audit_date: 2026-08-20
---

# Alternative: nixos-rebuild

## Overview

The standard, first-party NixOS tool for rebuilding a system. It builds a system configuration — from a channel or a flake — into a new Nix store closure and applies it. Ships with NixOS, requires root. Everything is three operations: build, set boot default, activate. Subcommands: `switch` (build + set boot default + activate now), `boot` (build + set boot default, activate on reboot), `build` (build only), `test` (activate without setting boot default), `build-vm`, `repl`. See `./overview.md` for the deployment comparison and the flake foundation in the [K1 overview note](./02_Knowledge/technologies/tools/nixos/overview.md) and [K1 flakes note](./02_Knowledge/technologies/tools/nixos/flakes.md).

## Pros

- **Zero external dependencies**: ships with NixOS and works on every node from day one — no extra tool to install.
- **Same flake, any node**: `nixos-rebuild switch --flake .#hostname` expresses one flake driving many hosts directly.
- **Rollback baked into the boot system**: prior generations are selectable from the boot menu; `nixos-rebuild switch --rollback` reverts.
- **Secrets work transparently**: sops-nix/agenix decrypt at activation time — tool-agnostic.
- **Safe staging ladder**: `build` / `test` / `boot` / `build-vm` let a change be validated before it is activated.
- **Reproducible**: inputs pinned via `flake.lock`.
- **Self-sufficient nodes**: runs on the target itself, so each node needs nothing else present.

## Cons

- **No multi-node support**: every host is a separate manual command — no inventory, no "deploy everything".
- **No automatic rollback** on failed activation; manual intervention required.
- **Remote mode is rough**: `--target-host` has known rough edges (workaround `--fast`).
- **Manual SSH bootstrap** per node.
- **Flake must be reachable on the target** (git clone/fetch).
- **No drift detection**.
- **No secret-key distribution automation**.

## Evaluation

- **Portability to any node**: excellent — per-host flake attribute plus `--target-host` SSH.
- **Flake-native**: yes — `--flake .#host`.
- **Multi-node**: none built-in; only manual loops over hosts.
- **Rollback**: manual only — boot menu or `--rollback`.
- **Secrets wiring**: transparent, tool-agnostic.
- **Maturity/stability**: the standard tool, extremely widely exercised; flakes support stable for years.
- **Maintenance burden**: minimal tooling, but a manual-orchestration cost per host.

## Verdict

**Rejected as standalone — acceptable baseline fallback.** Fully satisfies portability and keeps tooling minimal, ideal for a 1–2 node fleet, but lacks multi-node orchestration and automatic rollback exactly when the fleet grows (node-main + future nodes + k3s). Any future tool (deploy-rs/colmena) layers on the same flake without change. See `./overview.md` for the recommendation and plan for the ADR.
