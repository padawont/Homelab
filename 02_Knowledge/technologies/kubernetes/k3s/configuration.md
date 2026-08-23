---
title: "k3s configuration"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, k3s, configuration]
sources:
  - url: "https://docs.k3s.io/installation/configuration"
    title: "k3s configuration"
  - url: "https://docs.k3s.io/cli/server"
    title: "k3s server config reference"
last_audit_date: 2026-08-22
related_docs:
  - "./03_Research/nixos-adoption/overview.md"
---

# k3s configuration

## Overview

k3s configuration comes from three layers with fixed precedence: config file `/etc/rancher/k3s/config.yaml`, `K3S_*` environment variables, and CLI flags (highest). The same file path is used on servers and agents.

## Details

### Precedence and merging

1. `/etc/rancher/k3s/config.yaml` — lowest
2. `K3S_*` env vars — override config file values
3. CLI flags — highest

Config keys mirror the CLI flags with dashes (`--disable=traefik` → `disable: - traefik`). Repeated flags become YAML lists.

### config.yaml — single-node homelab server

Example — abstract (single-node server):

```yaml
write-kubeconfig-mode: "644"
node-ip: 192.168.1.10
node-name: node-main
disable:
  - traefik        # if a different ingress is preferred
token-file: /run/secrets/k3s-token   # prefer token-file over token
```

### config.yaml — multi-node HA

Example — abstract (HA server with embedded etcd):

```yaml
write-kubeconfig-mode: "644"
token-file: /run/secrets/k3s-token
tls-san:
  - k3s.homelab.local
cluster-init: true               # first HA server: start embedded etcd
server: https://10.0.0.1:6443    # subsequent HA servers join the cluster
```

`cluster-init: true` on the first server, then later servers point `server:` at the existing cluster — the datastore becomes etcd (see `./02_Knowledge/technologies/kubernetes/k3s/architecture.md`). For a single node, omit `cluster-init` and stay on SQLite.

### CLI flags and env vars

Every config key has a flag equivalent and most have a `K3S_*` env var. Common ones:

| Flag | Env var | Purpose |
|---|---|---|
| `--token-file` | `K3S_TOKEN_FILE` | Server token from file (preferred) |
| `--token` | `K3S_TOKEN` | Server token inline |
| `--node-ip` | `K3S_NODE_IP` | Advertised node IP |
| `--disable` | `K3S_DISABLE` | Disable a bundled component |
| `--flannel-backend` | — | flannel mode (vxlan default) |
| `--data-dir` | `K3S_DATA_DIR` | Data location (default `/var/lib/rancher/k3s`) |

### token vs tokenFile

- `token` / `K3S_TOKEN`: the value sits in config or env — easily leaked into shell history or world-readable files.
- `tokenFile` / `K3S_TOKEN_FILE`: k3s reads the token from a file at start. In the NixOS migration, point it at a sops-nix-managed secret under `/run/secrets` (see `./03_Research/nixos-adoption/overview.md`) so the token never lands in the Nix store.

The NixOS module exposes the same options as `services.k3s.token` / `services.k3s.tokenFile`, plus `services.k3s.extraFlags` for anything not natively wrapped.

## Sources / Further Reading

- [k3s configuration](https://docs.k3s.io/installation/configuration)
- [k3s server config reference](https://docs.k3s.io/cli/server)
- [k3s agent config reference](https://docs.k3s.io/cli/agent)
