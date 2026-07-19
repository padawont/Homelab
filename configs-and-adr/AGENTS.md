# Configs-and-ADR Section

Configuration for each node in the Kubernetes cluster, plus homelab-specific Architecture Decision Records. Each node has its own directory split by configuration domain. ADRs are co-located with configs to keep decisions close to the configurations they inform.

## Node-Role Structure

Configs are grouped by node role:

```
configs-and-adr/<node-{role}>/
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

## ADR Conventions

Architecture Decision Records live in `configs-and-adr/adr/` and follow the [MADR](https://adr.github.io/madr/) format:

```
configs-and-adr/adr/{NNNN}-{title-with-kebab-case}.md
```

Each ADR must include:
- `status` frontmatter field (proposed, accepted, deprecated, superseded)
- `date` frontmatter field (ISO date)
- Context section — why the decision was needed
- Decision section — what was decided
- Consequences section — trade-offs and implications

## Cross-Linking

Use frontmatter fields to link between sections:
- `related_knowledge: []` — links to knowledge/ topics relevant to this node's config
- `related_configs: []` — links to other config paths within configs-and-adr/

## Adding a New Node

1. Create `configs-and-adr/node-<role>/` with `kubernetes/` and `OS/` subdirectories
2. Add a `README.md` describing the node's hardware, network, and services
3. Populate config files under the appropriate subdirectory
4. Link to any relevant knowledge topics via `related_knowledge`
