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

## Which template for which file

| Writing | Start from | Lands as |
|---|---|---|
| A new idea | `./Templates/ideas/idea.md` | `01_Ideas/<topic>/idea-<name>.md` |
| A reference note | `./Templates/knowledge/note.md` | `02_Knowledge/technologies/<topic>/<slug>.md` |
| A research question | `./Templates/research/overview.md` | `03_Research/<topic>/overview.md` |
| The list of options considered | `./Templates/research/alternatives.md` | `03_Research/<topic>/alternatives.md` |
| One option's write-up | `./Templates/research/alternative.md` | `03_Research/<topic>/alternative-<name>.md` |
| A decision | `./Templates/adr/adr.md` | `04_ADRs/<NNNN>-<slug>.md` |
| A deployable service | `./Templates/implementations/service.md` | `05_Implementations/<service>/overview.md` |
| How to undo that deploy | `./Templates/implementations/rollback.md` | `05_Implementations/<service>/rollback.md` |
| A GitHub sub-task | `./Templates/tasks/issue.md` | Issue body |
| Observed cluster state | `./Templates/specs/cluster.md` | `05_Implementations/<service>/spec-cluster.md` |
| Observed topology | `./Templates/specs/topology.md` | `05_Implementations/<service>/spec-topology.md` |
| Observed service stack | `./Templates/specs/service-stack.md` | `05_Implementations/<service>/spec-service-stack.md` |

`overview.md` and `rollback.md` describe intent and procedure; `spec-*.md` files describe
observed state and are append-only once created — see `./05_Implementations/AGENTS.md`
§ Spec files.

## Frontmatter by section

Each template's frontmatter mirrors its destination section. The fields that differ:

| Section | Template fields |
|---|---|
| `01_Ideas/` | `title`, `status`, `author`, `date`, `tags`, `technologies`, `related_ideas` |
| `02_Knowledge/` | `title`, `status`, `author`, `date`, `tags`, `sources` (`url`/`title`), `last_audit_date`, `related_docs` |
| `03_Research/` | `title`, `status`, `author`, `date`, `tags`, `sources` (`knowledge`), `references` (`url`/`title`), `last_audit_date` |
| `04_ADRs/` | `adr`, `title`, `author`, `status`, `topic`, `technology`, `date`, `date-proposed`, `replaces`, `replaced-by`, `history`, `sources`, `references`, `related_docs` |
| `05_Implementations/` | `title`, `status`, `author`, `date`, `tags`, `technologies`, `related_docs`, `references.online`/`references.repo`, `node` |
| `Templates/tasks/` | `title`, `issue_number`, `status`, `labels`, `created_at`, `epic` |

The authoritative field specs are in each section's AGENTS.md (`./01_Ideas/AGENTS.md`,
`./02_Knowledge/AGENTS.md`, `./03_Research/AGENTS.md`, `./04_ADRs/AGENTS.md`,
`./05_Implementations/AGENTS.md`); the templates track them.

## Conventions

- Templates use YAML frontmatter with placeholder values — for example `""` (empty field),
  `[]` (empty list), `YYYY-MM-DD` (date), `NNNN` (ADR number) and `{number}` (issue number),
  plus body placeholders such as `{Title}`, `{name}`, `{topic}`, `{type}`,
  `{Service Name}`, `{Cluster Name}` and `{Selected / Rejected — reason}`
- Exception: `./Templates/research/alternatives.md` and
  `./Templates/research/alternative.md` are body-only fragments with no frontmatter —
  they are appended inside the `03_Research/<topic>/` folder beside `overview.md`
- Use `<!-- comment -->` blocks as instructions — strip these when copying
- Copy, don't edit — see `./AGENTS.md` § General Conventions
- Keep templates in sync with AGENTS.md conventions
- Archive does not need a template — files are moved there, not copied, with archival
  frontmatter added; see `./AGENTS.md` § General Conventions and `./06_Archive/AGENTS.md`
