# Configs

Per-node configuration for the Kubernetes cluster, organized by node role.

## Structure

```
configs/
├── node-main/       # Main node (K3s server, Longhorn storage)
│   ├── kubernetes/  # K8s manifests
│   └── OS/          # NixOS config, network, packages
├── node-extra/      # Extra / worker nodes
│   ├── kubernetes/
│   └── OS/
├── AGENTS.md        # Detailed rules for this section
└── README.md        # This file
```

## Roles

- **node-main** — K3s server + Longhorn storage (node-1)
- **node-extra** — future worker nodes

See `AGENTS.md` for full rules.
