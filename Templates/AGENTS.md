---
title: "AGENTS.md — Templates"
status: accepted
author: "padawont"
date: 2026-11-03
tags: []
sources: []
last_audit_date: 2026-11-03
related_docs: []
---

# AGENTS.md — Templates

Reusable document templates for the pipeline sections. `06_Archive/` has none — see
`./06_Archive/AGENTS.md`.

## Template inventory

| Template | Path | For |
|---|---|---|
| Idea | `./Templates/ideas/idea.md` | `./01_Ideas/` |
| Knowledge note | `./Templates/knowledge/note.md` | `./02_Knowledge/` |
| Research overview | `./Templates/research/overview.md` | `./03_Research/` |
| Research alternatives index | `./Templates/research/alternatives.md` | `./03_Research/` |
| Research alternative | `./Templates/research/alternative.md` | `./03_Research/` |
| ADR | `./Templates/adr/adr.md` | `./04_ADRs/` |
| Implementation overview | `./Templates/implementations/service.md` | `./05_Implementations/` |
| Implementation rollback | `./Templates/implementations/rollback.md` | `./05_Implementations/` |
| GitHub Issue | `./Templates/tasks/issue.md` | Creating new GitHub issues |
| Cluster spec | `./Templates/specs/cluster.md` | `./05_Implementations/` as `spec-cluster.md` |
| Service stack spec | `./Templates/specs/service-stack.md` | `./05_Implementations/` as `spec-service-stack.md` |
| Topology spec | `./Templates/specs/topology.md` | `./05_Implementations/` as `spec-topology.md` |

## Conventions

- Templates use YAML frontmatter with placeholder values (`""`, `[]`, `YYYY-MM-DD`, `NNNN`, `{number}`)
- Use `<!-- comment -->` blocks as instructions — strip these when copying
- Copy, don't edit — see `./AGENTS.md` § General Conventions
- Keep templates in sync with AGENTS.md conventions
- Archive does not need a template — files are moved there, not copied, with archival
  frontmatter added; see `./AGENTS.md` § General Conventions and `./06_Archive/AGENTS.md`
