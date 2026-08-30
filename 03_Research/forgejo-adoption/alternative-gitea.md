---
title: "Alternative: Gitea"
status: draft
author: "padawont"
date: 2026-08-30
tags: [gitea, git, self-hosted, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/forgejo/overview.md"
  - knowledge: "./02_Knowledge/technologies/services/forgejo/migration.md"
references:
  - url: "https://docs.gitea.com/"
    title: "Gitea documentation"
  - url: "https://forgejo.org/compare-to-gitea/"
    title: "Forgejo comparison with Gitea"
last_audit_date: 2026-08-30
---

# Alternative: Gitea

## Overview

Gitea is a lightweight, self-hosted Git service (2016, forked from Gogs) released under MIT — the codebase ancestor of Forgejo. Since 2022 its development has been controlled by Gitea Ltd, a for-profit company, after the domains/trademark were transferred without community approval (https://forgejo.org/compare-to-gitea/). The feature surface is nearly identical to Forgejo — repositories, issues, PRs, packages, and Gitea Actions (GitHub-Actions-compatible CI) — because both share the same codebase lineage (per `./02_Knowledge/technologies/services/forgejo/overview.md`).

## Pros

- **Mature and large ecosystem**: project history since 2016 with a broad install base, integrations, and community content (https://forgejo.org/compare-to-gitea/)
- **Gitea Actions is GitHub-Actions-compatible**: workflow CI follows the same model Forgejo uses (per `./02_Knowledge/technologies/services/forgejo/overview.md`)
- **Extensive docs + Helm chart + many third-party integrations**: official documentation site includes install options and a Helm chart for k3s-style deployment (https://docs.gitea.com/)
- **Very lightweight resource profile**: single Go binary with SQLite enough for a personal instance — the same homelab-scale footprint as Forgejo (per `./02_Knowledge/technologies/services/forgejo/overview.md`)

## Cons

- **For-profit corporate governance**: domain and trademark controlled by Gitea Ltd after transfer without community approval (https://forgejo.org/compare-to-gitea/)
- **Open-core with non-free features**: parts of the product are reserved for paying customers, unlike Forgejo's fully free scope (https://forgejo.org/compare-to-gitea/)
- **Migration is one-way Gitea → Forgejo**: Forgejo documents instance upgrades from Gitea (≤ v1.22 → v10.0.x → newer), but no reverse path from Forgejo to Gitea is documented (per `./02_Knowledge/technologies/services/forgejo/migration.md`)
- **No advantage over Forgejo for a homelab valuing community governance**: near-identical feature surface, but the governance model is the opposite of what this homelab wants (https://forgejo.org/compare-to-gitea/)

## Evaluation

- **Resource footprint**: excellent — single Go binary, SQLite is enough for a personal instance (per `./02_Knowledge/technologies/services/forgejo/overview.md`)
- **k3s deploy effort**: low — official Helm chart and container images documented (https://docs.gitea.com/)
- **CI (Gitea Actions)**: GitHub-Actions-compatible workflows, same model as Forgejo Actions (per `./02_Knowledge/technologies/services/forgejo/overview.md`)
- **GitHub parity**: repositories, issues, PRs, packages, Actions — near-identical surface to Forgejo (per `./02_Knowledge/technologies/services/forgejo/overview.md`)
- **Upgrade path**: Gitea → Forgejo documented one-way only; nothing back (per `./02_Knowledge/technologies/services/forgejo/migration.md`)
- **Maintenance burden (corporate governance risk)**: for-profit controller can shift licensing/features — open-core with non-free features already (https://forgejo.org/compare-to-gitea/)

## Verdict

**Rejected** — near-parity with Forgejo on features, footprint, and CI, but for-profit corporate governance and a one-way migration path only (Gitea → Forgejo, never back) make it a governance risk for a homelab that values community control. Forgejo is the community-governed continuation of the same codebase with the same feature surface — see `./overview.md` and `./alternative-forgejo.md`.
