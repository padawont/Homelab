# Homelab

Documentation and configuration for my homelab infrastructure. Primary use: backup and recovery if something goes wrong, and tracking changes over time.

## 4-Phase Pipeline

Content flows through a defined pipeline: research and reference → configuration and decisions → deployment → live ADR and config registry.

| Phase | Directory | Purpose |
|---|---|---|
| 1 — Knowledge | `knowledge/` | Homelab-relevant reference docs, hardware specs, design patterns |
| 2 — Configs + ADR | `configs-and-adr/` | Node configs, K8s manifests, architecture decisions |
| 3 — Deployment | `deployment/` | CI/CD pipelines, deployment procedures, Helm values |
| 4 — Status | `status/` | Live ADR and config registry, hardware, versions |

## How Content Flows

```
Knowledge ──informs──► Configs + ADR ──deploys──► Deployment ──reports──► Status
```

- **Knowledge** entries about a tool lead to creating or updating **configs**
- **ADRs** document why a particular config or technology was chosen
- **Deployment** procedures reference configs and produce status snapshots
- **Status** registers what ADRs and configs are currently deployed; feeds back into knowledge (e.g., "version X has a bug, upgrade to Y")

## Quick Start

| You want to... | Go to |
|---|---|
| Understand a technology | `knowledge/<category>/<topic>/` |
| Find or update configs | `configs-and-adr/node-<role>/` |
| See how something is deployed | `deployment/procedures/` or `deployment/pipelines/` |
| Check what's currently deployed | `status/current-adr/` and `status/current-config/` |
| Know why a decision was made | `configs-and-adr/adr/` |
