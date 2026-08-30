---
title: "Alternative: Gogs"
status: draft
author: "padawont"
date: 2026-08-30
tags: [gogs, git, self-hosted, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/forgejo/overview.md"
references:
  - url: "https://gogs.io/"
    title: "Gogs"
  - url: "https://github.com/gogs/gogs"
    title: "Gogs source repository"
last_audit_date: 2026-08-30
---

# Alternative: Gogs

## Overview

Gogs (Go Git Service) is a minimalist self-hosted Git server written in Go, MIT-licensed, positioned for extremely light resource use — gogs.io targets as little as 64 MiB RAM and a quarter vCPU (per [gogs.io](https://gogs.io/)). Covers core Git hosting: repositories, issues, pull requests, wiki, webhooks, deploy keys, Git LFS, and LDAP/SMTP/GitHub auth (per [Gogs README](https://github.com/gogs/gogs)).

## Pros

- **Extremely lightweight**: runs in as little as 64 MiB RAM and a quarter vCPU (source: [gogs.io](https://gogs.io/)) — the smallest resource profile of the Forgejo-family forks (author assessment).
- **Simple install**: ships as a single cross-platform binary or Docker image, with installers for Windows/macOS/Linux (source: [Gogs README](https://github.com/gogs/gogs)).
- **Still actively maintained**: 47.8k stars on GitHub (source: [GitHub](https://github.com/gogs/gogs)).
- **Rich database backend support**: SQLite, PostgreSQL, MySQL/MariaDB (source: [gogs.io](https://gogs.io/)).

## Cons

- **No built-in CI/CD**: no integrated pipeline; Jenkins integration exists but requires an external Jenkins server (source: [gogs.io](https://gogs.io/)).
- **No package registry**: unlike Forgejo's built-in registry (source: [Forgejo overview](./02_Knowledge/technologies/services/forgejo/overview.md)).
- **Issues/PRs/wiki exist but are simpler** than Forgejo/Gitea (author assessment based on the feature-list comparison) — no Actions, no package surface, fewer project-management tools (source: [gogs.io](https://gogs.io/)).
- **Slow development cadence and single-maintainer bus factor** (author assessment based on the [GitHub](https://github.com/gogs/gogs) repository): long gaps between releases with effectively one primary maintainer.
- **No GitHub Actions compatibility**: no Actions-style CI runner, so GitHub-parity workflows cannot run (assessment: Actions is absent from the [Gogs README](https://github.com/gogs/gogs) feature list).
- **Would not meet the homelab's GitHub-parity needs**: CI and a package registry are required (source: [./overview.md](./overview.md)), and Gogs cannot deliver either natively.

## Evaluation

- **Resource footprint**: smallest of the family (author assessment) — 64 MiB RAM / quarter vCPU class (source: [gogs.io](https://gogs.io/)) — but the rest of the profile suffers for it.
- **k3s deploy effort**: trivial — a single container on a Longhorn PVC; deployment would mirror Forgejo's (`./overview.md`) minus runner setup.
- **CI**: none built-in — only external Jenkins integration (source: [gogs.io](https://gogs.io/)).
- **GitHub parity**: low — no packages, no Actions, simplified issues/PRs/wiki (source: [gogs.io](https://gogs.io/)).
- **Upgrade path**: slow cadence and single-maintainer bus factor raise upgrade risk (author assessment based on the [GitHub](https://github.com/gogs/gogs) repository).
- **Maintenance burden**: low to run (single lightweight binary), but project-risk burden is high.

## Verdict

**Rejected** — too minimal for the homelab's needs: no built-in CI and no package registry, which are required for GitHub parity (source: [./overview.md](./overview.md)). Forgejo delivers the same lightweight profile with a full feature surface — see `./overview.md` and `./alternative-forgejo.md`.
