---
title: "AGENTS.md — 06_Archive"
status: accepted
author: "padawont"
date: 2026-11-03
tags: []
sources: []
last_audit_date: 2026-11-03
related_docs: []
---

# AGENTS.md — 06_Archive

Terminal storage for failed experiments, rejected proposals, retired services, and deprecated decisions.
No new content originates here. Content is purged 31 days after archiving.

## Directory structure

Example:

```
06_Archive/
├── ideas/
│   └── ingress-overhaul/
│       └── idea-upgrade-ingress.md
├── knowledge/
├── research/
│   └── ingress-comparison/
│       ├── overview.md
│       ├── alternatives.md
│       ├── alternative-traefik.md
│       ├── alternative-nginx.md
│       └── alternative-haproxy.md
├── adrs/
├── implementations/
│   └── node-main/
│       └── old-service/
│           ├── overview.md
│           ├── rollback.md
│           ├── spec-service-stack.md
│           └── configs/
```

Naming follows `./AGENTS.md` § General Conventions; each subfolder mirrors the
source section's internal structure — see `./03_Research/AGENTS.md` § Conventions and
`./05_Implementations/AGENTS.md` § Conventions.

## Frontmatter (required)

Example:

```yaml
---
title: "Deploy Traefik as ingress"
original_location: "./04_ADRs/42-deploy-traefik-ingress.md"
archived_date: 2026-08-13
reason: "Replaced by Caddy ingress"
superseded_by: "./04_ADRs/43-deploy-caddy-ingress.md"   # optional
---
```

`superseded_by` is optional — include it only when a successor exists.

## Conventions

- Move (not copy) — original file is deleted from the source section
- Preserve original content verbatim; add archival frontmatter on top
- Preserve directory structure (e.g. `./06_Archive/implementations/node-main/traefik/`)
- **Purge after 31 days** — files older than 31 days are deleted
- Link to superseding content via `superseded_by` when applicable
