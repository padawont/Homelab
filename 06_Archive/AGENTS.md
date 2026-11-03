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

Section purpose is owned by `./AGENTS.md` § Repository Structure (row `06_Archive/`).
No new content originates here. Content here is time-limited — see § Conventions for the
purge rule.

## Directory structure

Example:

```
06_Archive/
├── ideas/
│   └── ingress-overhaul/
│       └── idea-upgrade-ingress.md
├── knowledge/
├── research/
├── adrs/
└── implementations/
```

Inside `research/`, a topic folder keeps the shape owned by `./03_Research/AGENTS.md`
§ File system layout; inside `implementations/`, a service folder keeps the shape owned
by `./05_Implementations/AGENTS.md` § File system layout. Naming follows
`./AGENTS.md` § General Conventions, and each source section states its own archival
transition in § Status Lifecycle, or in § Conventions where that section carries it.

## Frontmatter (required)

Example:

```yaml
---
title: "Deploy NetBox as IPAM"
status: archived          # the source section's terminal value, unchanged
original_location: "./04_ADRs/<issue-number>-<kebab-description>.md"
archived_date: 2026-08-13
reason: "Replaced by NetBox on its own VLAN"
superseded_by: "./04_ADRs/<successor-issue-number>-<kebab-description>.md"
---
```

`status` carries the source section's terminal value unchanged — the archival block
records that value rather than re-deriving it. The value itself is owned by each section:
see § Status Lifecycle in `./01_Ideas/AGENTS.md`, `./02_Knowledge/AGENTS.md`,
`./03_Research/AGENTS.md`, `./04_ADRs/AGENTS.md`, and `./05_Implementations/AGENTS.md`.
The rest of the source content is preserved verbatim per § Conventions.

`superseded_by` is optional — include it only when a successor exists. For an archived ADR
it mirrors that ADR's own `replaced-by` (`./04_ADRs/AGENTS.md` § Frontmatter (required));
the ADR record is authoritative, so on disagreement `superseded_by` is corrected to match
it, never the reverse.

## Conventions

- Move (not copy) — original file is deleted from the source section
- Preserve original content verbatim; add archival frontmatter on top
- Preserve directory structure (e.g. `./06_Archive/implementations/node-main/traefik/`)
- **Purge after 31 days** — files older than 31 days are deleted
- Link to superseding content via `superseded_by` — its presence rule lives in
  § Frontmatter (required)
