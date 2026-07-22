---
status: proposed
date: 2026-07-22
related_configs:
  - configs-and-adr/node-main/kubernetes/forgejo.yaml
  - configs-and-adr/node-main/OS/forgejo.nix
  - deployment/procedures/deploy-forgejo.md
  - deployment/pipelines/deploy-forgejo.yml
related_knowledge:
  - knowledge/technology/forgejo/
---

# ADR 0002 — Deploy Forgejo for Self-Hosted Git Hosting and CI Trigger

## Context

The homelab currently relies entirely on GitHub.com for Git hosting and CI/CD (GitHub Actions). This creates two problems:

1. **Single point of failure** — if GitHub is unreachable, no code can be pushed, no CI runs, and no deployments happen
2. **Vendor lock-in** — all CI/CD logic is coupled to GitHub Actions syntax and ecosystem

The homelab needs a self-hosted Git platform that can:
- Host internal repositories
- Trigger Dagger pipelines (the homelab's future CI/CD engine, tracked in Issue #6)
- Provide a testing environment before code reaches GitHub (Issue #3 or similar)

Forgejo is a community-governed fork of Gitea hosted under Codeberg e.V. It provides GitHub Actions-compatible CI/CD (Forgejo Actions), built-in OCI container and package registries, issue tracking, and code review. It runs as a single Go binary against SQLite or Postgres and fits within the homelab's resource constraints.

## Decision

Deploy Forgejo as a K3s workload on node-1, backed by the existing in-cluster Postgres database.

Key details:
- **Image**: `codeberg.org/forgejo/forgejo:10`
- **Database**: existing in-cluster Postgres (not SQLite — supports future multi-user scale)
- **Storage**: 10Gi Longhorn PVC for `/data`
- **Networking**: ClusterIP on port 3000 (HTTP) + NodePort on port 22 (SSH)
- **Ingress**: `git.homelab.internal` with TLS via the cluster's ingress controller
- **Secret management**: SealedSecrets for the Postgres password
- **CI role**: Forgejo Actions will be enabled to serve as the CI trigger platform for Dagger pipelines (Issue #6)
- **Installation lock**: `INSTALL_LOCK = true` after initial setup to prevent re-configuration

Forgejo will coexist with GitHub.com during a transition period. No migration from GitHub repositories is planned at this time — Forgejo hosts internal/test repositories first.

## Consequences

**Positive:**
- Eliminates single point of failure for Git hosting and CI
- Enables local development and testing without internet connectivity
- Forgejo Actions provides GitHub Actions-compatible workflows, easing transition
- Built-in OCI registry reduces dependency on Docker Hub / GitHub Container Registry
- Community governance (Codeberg e.V.) provides long-term project stability

**Negative:**
- Operational overhead — must maintain and upgrade the Forgejo instance
- Storage cost — 10Gi PVC plus registry/images storage over time
- Security surface — self-hosted Git server requires regular patching and monitoring

**Risks:**
- SealedSecrets controller must be deployed in the cluster before Forgejo can be applied
- Postgres database must be reachable from the `forgejo` namespace
- DNS record for `git.homelab.internal` must exist before ingress works
