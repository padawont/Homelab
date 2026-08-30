---
title: "Forgejo — self-hosted Git hosting service"
status: accepted
author: "padawont"
date: 2026-08-23
tags: [git, forgejo, gitea, self-hosted, code-hosting]
sources:
  - url: "https://codeberg.org/forgejo/forgejo"
    title: "Forgejo source repository"
  - url: "https://forgejo.org/compare-to-gitea/"
    title: "Forgejo comparison with Gitea"
  - url: "https://forgejo.org/docs/latest/"
    title: "Forgejo v16 documentation"
  - url: "https://forgejo.org/docs/latest/user/actions/github-actions/"
    title: "Forgejo Actions — GitHub Actions"
last_audit_date: 2026-08-23
related_docs:
  - "./02_Knowledge/technologies/services/forgejo/install-config.md"
  - "./02_Knowledge/technologies/services/forgejo/operations.md"
  - "./02_Knowledge/technologies/services/forgejo/migration.md"
  - "./02_Knowledge/technologies/services/forgejo/security.md"
  - "./02_Knowledge/technologies/services/forgejo/ci-act-runners.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/ingress.md"
---

# Forgejo — self-hosted Git hosting service

## Overview

Forgejo is a community-run fork of Gitea developed under the Codeberg e.V.
umbrella — a soft-fork in 2022 that became a hard-fork in early 2024. It is a
lightweight, self-hosted Git forge that provides repository hosting plus issue
tracking, pull requests, a package registry, and GitHub-Actions-style CI. It
runs as a single Go application
with a small resource footprint, which makes it a natural fit for a homelab
that wants private Git hosting without a SaaS dependency.

## Details

### Why self-host Git hosting

- **Privacy and control**: repositories, issues, and CI stay on local hardware.
- **No SaaS dependency**: no vendor lock-in, rate limits, or per-user cost.
- **Homelab-scale footprint**: a single binary plus a database (SQLite is
  enough for a personal instance) keeps the resource cost low.

### Feature surface

- Repositories with protected branches, tags, and releases
- Issue tracking, labels, milestones, projects, and wiki
- Pull requests and reviews with merge-message and PR templates
- Package registry (container, npm, PyPI, Go, Maven, and more)
- Forgejo Actions — GitHub-Actions-style CI executed by `forgejo-runner`
- Repository mirrors (pull/push), webhooks, and an OAuth2 provider
- Fine-grained access tokens, 2FA, and instance moderation tools

### Architecture

```
┌──────────┐   HTTPS   ┌──────────┐   port 3000   ┌────────────────────┐
│ Traefik  │ ────────► │ Forgejo  │ ────────────► │ SQLite / PostgreSQL │
│ (ingress)│           │ (web +   │   git over    │ / MySQL            │
└──────────┘           │  git)    │   SSH/HTTP    └────────────────────┘
                       └──────────┘       │
                              Longhorn PVC │  (repos + data)
                                           ▼
                                  ┌──────────────────┐
                                  │ forgejo-runner(s) │  ← Forgejo Actions
                                  └──────────────────┘
```

- The web UI, git HTTP endpoints, and the git SSH server all come from the
  single Forgejo process; a reverse proxy (Traefik in this homelab) terminates
  TLS in front of it.
- Supported databases: SQLite (default), PostgreSQL, MySQL/MariaDB.
- Repository data lives on the filesystem — in k3s, a Longhorn PVC
  (`./02_Knowledge/technologies/kubernetes/longhorn/storage.md`).

### Releases

- Current stable line is **v16.0** (latest patch v16.0.3); LTS is **v15.0.7**.
- Forgejo has followed semantic versioning since 7.0.0 — only a major version
  bump (e.g. 15 → 16) may contain breaking changes.
- Upgrade procedures are documented in `./02_Knowledge/technologies/services/forgejo/operations.md`.

### Homelab placement

- Target namespace `forgejo` on the k3s cluster (node-main).
- Reached at `git.homelab.local` through a Traefik Ingress; the service port is
  3000. The `forgejo-ingress` example already appears in
  `./02_Knowledge/technologies/kubernetes/concepts/ingress.md`.
- Deployment is not live yet — the ADR and Implementation stages are follow-ups
  in the pipeline; see `./02_Knowledge/technologies/services/forgejo/install-config.md`.

## Sources / Further Reading

- Forgejo v16 documentation: https://forgejo.org/docs/latest/
- Forgejo source repository: https://codeberg.org/forgejo/forgejo
- Install: `./02_Knowledge/technologies/services/forgejo/install-config.md`
- Operations (backup/upgrades): `./02_Knowledge/technologies/services/forgejo/operations.md`
