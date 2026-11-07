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

Section purpose is owned by `./AGENTS.md` § Repository Structure (row `Templates/`).
`06_Archive/` has none — see `./06_Archive/AGENTS.md`.

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
| A new idea | `./Templates/ideas/idea.md` | `./01_Ideas/<topic>/idea-<name>.md` |
| A reference note | `./Templates/knowledge/note.md` | `./02_Knowledge/technologies/<category>/<topic>/<slug>.md` |
| A research question | `./Templates/research/overview.md` | `./03_Research/<topic>/overview.md` |
| The list of options considered | `./Templates/research/alternatives.md` | `./03_Research/<topic>/alternatives.md` |
| One option's write-up | `./Templates/research/alternative.md` | `./03_Research/<topic>/alternative-<name>.md` |
| A decision | `./Templates/adr/adr.md` | `./04_ADRs/<NNNN>-<slug>.md` |
| A deployable service | `./Templates/implementations/service.md` | `./05_Implementations/<node>/<service>/overview.md` |
| How to undo that deploy | `./Templates/implementations/rollback.md` | `./05_Implementations/<node>/<service>/rollback.md` |
| A GitHub sub-task | `./Templates/tasks/issue.md` | Issue body |
| Observed cluster state | `./Templates/specs/cluster.md` | `./05_Implementations/<node>/<service>/spec-cluster.md` |
| Observed topology | `./Templates/specs/topology.md` | `./05_Implementations/<node>/<service>/spec-topology.md` |
| Observed service stack | `./Templates/specs/service-stack.md` | `./05_Implementations/<node>/<service>/spec-service-stack.md` |

Paths, and the division of labour between `overview.md`/`rollback.md` and `spec-*.md`:
`./05_Implementations/AGENTS.md` § File system layout and § Spec files.

## Frontmatter by section

Each template bound to a pipeline section takes that section's frontmatter as specified in
the section's own AGENTS.md § Frontmatter (required); this file does not restate the field
lists. The section → AGENTS.md mapping is owned by `./AGENTS.md` § Repository Structure.

### Issue template frontmatter

`./Templates/tasks/issue.md` belongs to no section — it fills a GitHub issue body, so its
fields are not derived from a section AGENTS.md:

| Template | Fields |
|---|---|
| `./Templates/tasks/issue.md` | `title`, `issue_number`, `status`, `labels`, `created_at`, `epic` |

## Conventions

- Templates use YAML frontmatter with placeholder values — for example `""` (empty field),
  `[]` (empty list), `YYYY-MM-DD` (date), `NNNN` (ADR number) and `{number}` (issue number),
  plus body placeholders such as `{Title}`, `{name}`, `{topic}`, `{type}`,
  `{Service Name}`, `{Cluster Name}` and `{Selected / Rejected — reason}`
- Exception: `./Templates/research/alternatives.md` and
  `./Templates/research/alternative.md` are body-only snippets with no frontmatter — when
  copied into the `./03_Research/<topic>/` folder beside `overview.md`, wrap each one in the
  topic frontmatter specified by `./03_Research/AGENTS.md` § Frontmatter (required), as the
  live research topics do
- Use `<!-- comment -->` blocks as instructions — strip these when copying
- Editing rules: `./AGENTS.md` § General Conventions
- Archive handling: `./06_Archive/AGENTS.md` § Conventions
- Keep templates in sync with AGENTS.md conventions
