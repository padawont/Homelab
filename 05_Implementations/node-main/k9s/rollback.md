---
title: "k9s terminal cluster UI — rollback"
status: active
author: "padawont"
date: 2026-08-23
tags: [kubernetes, k9s, rollback]
technologies: [k9s]
related_docs:
  - "./overview.md"
references:
  online: []
  repo: []
node: node-main
---

# k9s terminal cluster UI — Rollback

## Prerequisites

- None — k9s is a stateless TUI reading a kubeconfig.

## Rollback steps

k9s has no state to roll back. To remove it (or revert to a previous version):

```bash
# Remove the package from home.nix (configs/home.nix) and redeploy:
cd 05_Implementations/node-main/nixos
nix run github:serokell/deploy-rs -- .#node-main

# Or manually drop the config cache:
rm -rf ~/.config/k9s ~/.local/state/k9s
```

## Verification

- `which k9s` no longer resolves (after removal) or returns the expected version.
