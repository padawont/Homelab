---
title: "Evaluate Open Knowledge Format for the PKM"
status: draft
author: "padawont"
date: 2026-08-23
tags: [pkm, knowledge-management, metadata]
technologies: [okf]
related_ideas: []
---

# Evaluate Open Knowledge Format for the PKM

## Objective

Evaluate the Open Knowledge Format (OKF) as validation and inspiration for the
Homelab PKM's own format design. OKF stores knowledge as plain markdown files
with YAML frontmatter in a git-versioned directory hierarchy — the same core
design this repo already uses (see `AGENTS.md`).

## Possibilities

- **Borrow OKF's trust/provenance signals in frontmatter**: `sources` with
  per-source credibility, `verified`/`generated`, `status` + `stale_after` so
  an agent-maintained corpus stays trustable without a runtime.
- **Auto-generated `index.md` per directory** for progressive disclosure — an
  agent or human navigates one level at a time instead of loading everything
  into context.
- **Graph-shaped cross-linking** beyond the folder tree: concepts link to each
  other via normal markdown links, not just parent/child directories.
- **Secondary tooling idea**: `kcmd` (Metadata-as-Code, from the
  knowledge-catalog repo) manages metadata as source artifacts with pull/push
  sync and ships an MCP server — a possible pattern for homelab metadata
  management.

## Open Questions

- Is the OKF v0.2 spec stable/mature enough to depend on, or still moving?
- Does adopting OKF-style fields conflict with the frontmatter conventions
  already defined per-section in the AGENTS.md files?
- Is the OKF reference agent practical to run in a homelab (BigQuery + Gemini
  dependencies), or is the format the only useful part?
- Is `stale_after` freshness worth adding to this PKM's knowledge notes, or
  does the existing `last_audit_date` convention suffice?

## Sources

- OKF canonical repo (the `knowledge-catalog` copy is a frozen snapshot):
  <https://github.com/GoogleCloudPlatform/open-knowledge-format>
- OKF spec v0.2 snapshot and tooling:
  <https://github.com/GoogleCloudPlatform/knowledge-catalog>
