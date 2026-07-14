# Configs Section

Configuration for each node in the Kubernetes cluster. Each node has its own directory split by configuration domain.

## Node-Role Structure

Configs are grouped by node role:

```
configs/<node-{role}>/
```

### Current Roles

| Role | Node(s) | Purpose |
|---|---|---|
| `node-main` | node-1 | K3s server, Longhorn storage, Rancher management |
| `node-extra` | — | Future worker / extra nodes |

### Per-Node Layout

Each node folder contains:

| Directory | Purpose |
|---|---|
| `kubernetes/` | Kubernetes manifests (actual YAML) — deployments, services, configmaps, etc. |
| `OS/` | OS-level configuration — NixOS configs, network settings, installed packages |

## Cross-Linking

Use frontmatter fields to link to knowledge topics:
- `related_knowledge: []` — links to knowledge/ topics relevant to this node's config

## Adding a New Node

1. Create `configs/node-<role>/` with `kubernetes/` and `OS/` subdirectories
2. Add a `README.md` describing the node's hardware, network, and services
3. Populate config files under the appropriate subdirectory
4. Link to any relevant knowledge topics via `related_knowledge`
