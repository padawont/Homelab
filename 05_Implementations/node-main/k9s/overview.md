---
title: "k9s terminal cluster UI"
status: active
author: "padawont"
date: 2026-08-23
tags: [kubernetes, k9s, tui, operations]
technologies: [k9s, kubernetes]
related_docs:
  - "./02_Knowledge/technologies/kubernetes/k9s/overview.md"
  - "./05_Implementations/node-main/nixos/overview.md"
references:
  online:
    - url: "https://k9scli.io/"
      title: "k9s documentation"
  repo: []
node: node-main
---

# k9s terminal cluster UI

## Prerequisites

- Installed for `runic` via home-manager (`configs/home.nix` in the nixos flake).
- A kubeconfig that the user can read — `/etc/rancher/k3s/k3s.yaml` (mode 644,
  set by k3s `--write-kubeconfig-mode 644`).

## Deployment

Installed declaratively through the flake — nothing manual:

```nix
# 05_Implementations/node-main/nixos/home.nix
packages = [ pkgs.kubectl pkgs.k9s pkgs.kubernetes-helm pkgs.kubectx ];
```

Apply with deploy-rs:

```bash
cd 05_Implementations/node-main/nixos
nix run github:serokell/deploy-rs -- .#node-main
```

## Configuration

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
k9s
```

Key bindings: `:` command bar (pods/nodes/deployments…), `d` describe, `s` shell,
`x` logs, `?` help. Config lives at `~/.config/k9s/`.

## Operations

- **Switch contexts**: `k9s --context <name>` or `kubectx`.
- **Logs**: select a pod → `l`.
- **Rollback**: see `./rollback.md`.
