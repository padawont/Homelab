---
title: "Forgejo Comparison"
status: draft
tags:
  - git
  - forge
  - comparison
  - gitea
  - github
  - gitlab
  - gogs
sources:
  - url: "https://forgejo.org/compare/"
    title: "Forgejo vs Other Forges"
  - url: "https://forgejo.org"
    title: "Forgejo Official Site"
  - url: "https://codeberg.org/forgejo/governance"
    title: "Forgejo Governance"
last_audit_date: 2026-07-22
related_configs:
  - "configs-and-adr/node-main/kubernetes/forgejo.yaml"
---

# Forgejo Comparison

Feature comparison of Forgejo against other software forges.

## Feature Matrix

| Feature | Forgejo | Gitea | GitHub | GitLab CE | Gogs |
|---|---|---|---|---|---|
| **Git hosting** | Yes | Yes | Yes | Yes | Yes |
| **Repository mirroring** | Yes | Yes | Yes | Yes | Limited |
| **CI/CD (built-in)** | Forgejo Actions | Gitea Actions | GitHub Actions | GitLab CI | No |
| **CI/CD compat with GitHub** | High | High | Native | Low | N/A |
| **Container registry** | Yes | Yes | Yes | Yes | No |
| **Package registry** | 20+ formats | 20+ formats | Yes | Yes | No |
| **Issue tracking** | Yes | Yes | Yes | Yes | Yes |
| **Pull/Merge requests** | Yes | Yes | Yes | Yes | Yes |
| **Code review** | Inline comments | Inline comments | Required reviews | Approvals | Basic |
| **Wiki** | Yes | Yes | Yes | Yes | Yes |
| **Projects (Kanban)** | Yes | Yes | Yes | Yes | No |
| **OAuth2 provider** | Yes | Yes | Yes | Yes | No |
| **Federation** | In development | No | No | No | No |
| **Single binary** | Yes | Yes | No | No | Yes |
| **Resource usage** | Very low | Very low | High | High | Very low |
| **Governance** | Codeberg e.V. (nonprofit) | For-profit (2022+) | Microsoft | GitLab B.V. | Individual |
| **License** | MIT | MIT | Proprietary | MIT (CE) | MIT |
| **Self-hostable** | Yes | Yes | No | Yes | Yes |

## Governance Comparison

| Aspect | Forgejo | Gitea |
|---|---|---|
| **Umbrella org** | Codeberg e.V. (German nonprofit) | Gitea Ltd (for-profit company) |
| **Decision-making** | Community-driven via governance team | Corporate-controlled after 2022 |
| **Funding** | Donations via Liberapay | Commercial support + donations |
| **Vendor lock-in risk** | None (open governance) | Moderate (corporate governance) |

This governance difference was the primary motivation for the Gitea fork in late 2022.

## Resource Usage Comparison

| Metric | Forgejo/Gitea | GitLab CE |
|---|---|---|
| **Minimum RAM** | 512MB — 1GB | 4GB+ |
| **Storage (base)** | ~500MB | ~3GB |
| **Installation** | Single binary | Multiple services |
| **Dependencies** | Optional DB + optional reverse proxy | Postgres, Redis, Sidekiq, etc. |

Forgejo's low resource profile makes it ideal for homelab deployments, especially on resource-constrained nodes like SBCs.

## Homelab Decision

Forgejo was chosen over:
- **GitHub.com** — Must stay online, vendor lock-in
- **GitLab CE** — Too resource-heavy for homelab (requires 4GB+ RAM, Postgres, Redis)
- **Gitea** — Corporate governance concerns after 2022 takeover
- **Gogs** — Single maintainer risk, less feature-complete, no CI/CD
- **Gitea (self-hosted)** — Functionally identical but governed by for-profit
