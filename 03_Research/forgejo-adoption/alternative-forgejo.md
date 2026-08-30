---
title: "Alternative: Forgejo"
status: draft
author: "padawont"
date: 2026-08-30
tags: [forgejo, git, self-hosted, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/forgejo/overview.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/install-config.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/ci-act-runners.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/migration.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/operations.md"
references:
  - url: "https://forgejo.org/docs/latest/"
    title: "Forgejo v16 documentation"
  - url: "https://codeberg.org/forgejo/forgejo"
    title: "Forgejo source repository"
  - url: "https://forgejo.org/compare-to-gitea/"
    title: "Forgejo comparison with Gitea"
last_audit_date: 2026-08-30
---

# Alternative: Forgejo

## Overview

Forgejo is a community-governed hard fork of Gitea under the Codeberg e.V. non-profit ([comparison with Gitea](https://forgejo.org/compare-to-gitea/)). It runs as a single Go binary — web UI, git over HTTP, and git over SSH all come from one process — with SQLite as the default database, enough for a personal instance ([install-config](./02_Knowledge/technologies/services/forgejo/install-config.md)). It provides repositories, issues, pull requests, a package registry, and Forgejo Actions (GitHub-Actions-compatible CI) executed by `forgejo-runner` ([overview](./02_Knowledge/technologies/services/forgejo/overview.md), [ci-act-runners](./02_Knowledge/technologies/services/forgejo/ci-act-runners.md)).

## Pros

- **Lightweight**: a single Go binary plus a database; SQLite is enough for a single-owner homelab instance ([install-config](./02_Knowledge/technologies/services/forgejo/install-config.md))
- **Community governance**: developed under the Codeberg e.V. non-profit umbrella rather than a single vendor ([comparison with Gitea](https://forgejo.org/compare-to-gitea/))
- **GitHub-Actions-compatible CI**: Forgejo Actions runs `.forgejo/workflows/*.yml` via `forgejo-runner`, registered at instance/org/user/repo scope ([ci-act-runners](./02_Knowledge/technologies/services/forgejo/ci-act-runners.md))
- **Full forge feature surface**: package registry, pull/push repo mirrors, webhooks, and an OAuth2 provider alongside PRs and issues ([overview](./02_Knowledge/technologies/services/forgejo/overview.md))
- **Documented from-Gitea upgrade path**: Gitea ≤ v1.22 → Forgejo v10.0.x → newer Forgejo is an official two-step route ([migration](./02_Knowledge/technologies/services/forgejo/migration.md), [operations](./02_Knowledge/technologies/services/forgejo/operations.md))
- **Active project**: v16 is current stable, v15 is LTS, and the Codeberg repository is actively maintained ([overview](./02_Knowledge/technologies/services/forgejo/overview.md), [source repository](https://codeberg.org/forgejo/forgejo))

## Cons

- **Younger project**: docs and release cadence still churn, and Actions workflow compatibility is "familiar but not guaranteed" — third-party actions should be pinned ([ci-act-runners](./02_Knowledge/technologies/services/forgejo/ci-act-runners.md))
- **Hard-fork divergence from Gitea**: the projects have split since early 2024, so not all Gitea PRs land in Forgejo ([comparison with Gitea](https://forgejo.org/compare-to-gitea/))
- **Operator-managed operations**: upgrades and maintenance are the operator's responsibility — no managed upgrade service; back up with `forgejo dump` before upgrades ([operations](./02_Knowledge/technologies/services/forgejo/operations.md))

## Evaluation

- **Resource footprint**: minimal — a single Go binary plus SQLite fits a single-node k3s cluster ([overview](./02_Knowledge/technologies/services/forgejo/overview.md), [install-config](./02_Knowledge/technologies/services/forgejo/install-config.md))
- **k3s deploy effort**: low — one Deployment with a Longhorn PVC, a Service on port 3000, and a Traefik Ingress at `git.homelab.local` ([install-config](./02_Knowledge/technologies/services/forgejo/install-config.md))
- **CI (Forgejo Actions / ACT runner)**: GitHub-Actions-compatible workflows executed by a registered `forgejo-runner`; runner provisioning deferred to Implementation ([ci-act-runners](./02_Knowledge/technologies/services/forgejo/ci-act-runners.md))
- **GitHub parity (PRs, issues, packages, mirrors)**: high — PRs, issues, labels/milestones, package registry, pull/push mirrors, and OAuth2 cover typical GitHub usage ([overview](./02_Knowledge/technologies/services/forgejo/overview.md), [migration](./02_Knowledge/technologies/services/forgejo/migration.md))
- **Upgrade path (semver, LTS, from-Gitea)**: semantic versioning since 7.0.0 with stable + LTS channels and an official from-Gitea two-step route ([operations](./02_Knowledge/technologies/services/forgejo/operations.md), [migration](./02_Knowledge/technologies/services/forgejo/migration.md))
- **Maintenance burden**: low-moderate — backups via `forgejo dump` or Longhorn snapshots; upgrades swap the image tag plus `forgejo doctor` verification ([operations](./02_Knowledge/technologies/services/forgejo/operations.md))

## Verdict

**Selected** — the best homelab fit: lightweight enough for a single-node k3s cluster with SQLite, slots into the existing Traefik/Longhorn stack, backed by Codeberg's community governance, and ships GitHub-Actions-compatible CI. See the [overview](./overview.md) for the full adoption plan.
