---
title: "Forgejo adoption — self-hosted Git hosting comparison"
status: draft
author: "padawont"
date: 2026-08-30
tags: [forgejo, gitea, gitlab, gogs, git, self-hosted, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/forgejo/overview.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/install-config.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/operations.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/migration.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/security.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/ci-act-runners.md"
references:
  - url: "https://forgejo.org/docs/latest/"
    title: "Forgejo v16 documentation"
  - url: "https://codeberg.org/forgejo/forgejo"
    title: "Forgejo source repository"
  - url: "https://forgejo.org/compare-to-gitea/"
    title: "Forgejo comparison with Gitea"
  - url: "https://docs.gitea.com/"
    title: "Gitea documentation"
  - url: "https://about.gitlab.com/install/"
    title: "GitLab install options"
  - url: "https://gogs.io/"
    title: "Gogs"
last_audit_date: 2026-08-30
---

# Forgejo adoption — self-hosted Git hosting comparison

## Goal

Goal: decide which self-hosted Git server the homelab adopts — Forgejo vs Gitea vs GitLab CE vs Gogs. Research is required before an ADR per the PKM pipeline (Research → ADR). Sparked by the desire to remove SaaS dependency for private Git hosting.

## Alternatives

See `./alternatives.md` for the full index; each alternative has its own evaluation file (`./alternative-forgejo.md`, `./alternative-gitea.md`, `./alternative-gitlab-ce.md`, `./alternative-gogs.md`).

- Forgejo — **Selected** — community-governed fork, lightweight, GitHub-Actions-compatible CI.
- Gitea — Rejected — near-parity but for-profit corporate governance.
- GitLab CE — Rejected — heavy footprint, overkill for homelab.
- Gogs — Rejected — too minimal, no CI/packages.

## Plan for ADR

### Recommended technology and why

Forgejo — a community-run fork of Gitea under Codeberg e.V., created Oct 2022 as a soft-fork and a hard fork since early 2024 (per https://forgejo.org/compare-to-gitea/). It is a lightweight single-Go-binary service where SQLite is enough for a personal instance, with repository hosting plus issues, PRs, a package registry, and GitHub-Actions-style CI (per `./02_Knowledge/technologies/services/forgejo/overview.md`).

### How it fits into the existing homelab

Namespace `forgejo` on the k3s cluster (node-main), reached at `git.homelab.local` through a Traefik Ingress, service port 3000, repository data on a Longhorn PVC (per `./02_Knowledge/technologies/services/forgejo/overview.md` and `./02_Knowledge/technologies/services/forgejo/install-config.md`).

Deployment is not live yet — all config-ish references below are **Example — abstract**, not running config.

### Architecture overview

A single Forgejo process serves the web UI, git over HTTP, and git over SSH; Traefik terminates TLS in front (the `forgejo-ingress` example in `./02_Knowledge/technologies/kubernetes/concepts/ingress.md`). Database: SQLite by default — enough for a single-owner homelab — with PostgreSQL as the option for heavier instances (per `./02_Knowledge/technologies/services/forgejo/install-config.md`). Repository data, LFS, and uploads live on the Longhorn PVC (ReadWriteOnce is fine on one node). Forgejo Actions CI runs via forgejo-runner(s) deployed alongside in the `forgejo` namespace; runner provisioning is deferred to the Implementation stage (per `./02_Knowledge/technologies/services/forgejo/ci-act-runners.md`).

### Dependencies and integration points

k3s on node-main, Traefik Ingress controller, Longhorn StorageClass, cert-manager for TLS if present, k8s Secrets for `SECRET_KEY`/DB password/runner tokens (per `./02_Knowledge/technologies/services/forgejo/security.md`), and the GitHub repositories to migrate in (per `./02_Knowledge/technologies/services/forgejo/migration.md`).

### Risks and mitigation

- Migration loss — wiki and packages do not always migrate cleanly, and LFS objects are not mirrored over SSH push mirrors (per `./02_Knowledge/technologies/services/forgejo/migration.md`). Mitigation: verify LFS transfer, export/import wiki and packages separately, keep GitHub mirrors or DNS redirects for old URLs.
- Actions maturity — workflow syntax is familiar to GitHub Actions but not guaranteed compatible (per `./02_Knowledge/technologies/services/forgejo/ci-act-runners.md`). Mitigation: pin third-party actions to commit SHAs, keep runners isolated from cluster/host secrets, prefer ephemeral runners.
- Upgrade cadence — semantic versioning since 7.0.0; only major bumps (e.g. 15 → 16) may contain breaking changes, and stable releases get ~3 months of bugfix/security fixes (per `./02_Knowledge/technologies/services/forgejo/operations.md`). Mitigation: back up before upgrades, run `forgejo doctor check --all` after, follow the upgrade guide.

## Recommendation

**approve** — adopt Forgejo as the self-hosted Git server. It is the community-governed (Codeberg e.V.) hard fork of Gitea since early 2024, lightweight enough for a single-node homelab with SQLite, fits the existing k3s/Traefik/Longhorn stack, and provides GitHub-Actions-style CI through Forgejo Runner. Gitea is at near-parity but rejected on corporate governance; GitLab CE is too heavy and Gogs too minimal for this homelab.
