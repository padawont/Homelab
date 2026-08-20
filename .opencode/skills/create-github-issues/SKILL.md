---
name: create-github-issues
description: Creates GitHub issues and epics for the Homelab PKM pipeline. Use when creating an epic, a pipeline issue (idea / knowledge / research / adr / proposal / projects / implementation), or native sub-issues, using the gh CLI and the Templates/tasks/issue.md skeleton. Use ONLY when creating GitHub issues, not for writing notes.
---

# create-github-issues

Plan and create GitHub epics and pipeline sub-issues on `RunicEngines/knowledge-base` using the `gh` CLI. Native parent/child links are created with `gh issue create --parent <number>` (gh >= 2.94). Every sub-issue is drafted from `Templates/tasks/issue.md` and filled from the per-topic spec below.

## The content pipeline

```
Idea → Knowledge → Research → ADR → Implementation
                                  └──► Archive
Proposal = how-we-work; Projects/Tasks = registry/index updates
```

### Per-topic spec

| Topic | Label | Template(s) | Frontmatter | Review pipeline |
|---|---|---|---|---|
| Idea | `idea` | `Templates/ideas/idea.md` | title, status, author, date, tags, technologies, related_ideas | none (draft → accepted) |
| Knowledge | `knowledge` | `Templates/knowledge/note.md` | title, status, author, date, tags, sources[{url,title}], last_audit_date | knowledge-agent → kb-editor/kb-tech-lead/kb-architect |
| Research | `research` | `Templates/research/overview.md` + `alternatives.md` + `alternative-*.md` | title, status, author, date, tags, sources[{knowledge}], references[{url,title}], last_audit_date | research review |
| ADR | `adr` | `Templates/adr/adr.md` | adr, title, author, status, topic, technology, date, date-proposed, replaces, replaced-by, history, sources, references | architect review |
| Proposal | `proposal` | — | change-log style | proposal review |
| Projects | — | projects registry index | chore template | — |
| Implementation | — | `Templates/implementations/service.md` + `rollback.md` | title, status, author, date, tags, technologies, related_docs, references{online,repo}, node | implementation review |

### Topic detail

- **Idea** — freeform capture. No review for draft→accepted; no stale timeout.
- **Knowledge** — atomic single-concept notes, 100–250 body lines. Frontmatter needs `sources` + `last_audit_date`. Folder ≤3 levels deep, kebab-case.
- **Research** — overview + one file per alternative. Must reference ≥1 knowledge note or online source; must be detailed enough to write the ADR directly.
- **ADR** — MADR format, sequential number, ≥2 mermaid diagrams (internal working + homelab fit). Requires an accepted Research.
- **Proposal** — how-we-work change log.
- **Projects/Tasks** — registry index updates via chore template (non-pipeline bookkeeping).
- **Implementation** — requires accepted ADR + knowledge; every folder ships `overview.md` + `rollback.md` (+ `configs/`).

### Per-topic acceptance criteria

| Topic | Core acceptance criteria |
|---|---|
| Idea | status `accepted`; ready to promote to Knowledge |
| Knowledge | atomic note(s) ≤150 lines; valid frontmatter; every `sources[]` URL live; `last_audit_date` set; passes knowledge review |
| Research | `overview.md` + ≥3 `alternative-*.md` files; ≥1 knowledge/online source; detailed enough to write the ADR directly; passes research review |
| ADR | filename `{issue}-{kebab}.md`; `adr` = issue number; ≥2 mermaid diagrams; links to Research; `draft → accepted` gated on review; passes architect review |
| Proposal | change-log entry recorded; passes proposal review |
| Implementation | `overview.md` + `rollback.md` + `configs/`; flake with `nixosConfigurations` + deploy target; rollback verified; passes implementation review |

## Sources and Acceptance Criteria rules

- **Sources**: every issue must cite real links — absolute URLs for online sources, `./` repo-relative paths for KB docs. No prose-only sources.
- **Acceptance Criteria**: always topic-specific and verifiable per the Per-topic acceptance criteria table above — never generic boilerplate.

## Epic issue template

```markdown
## Objective
<!-- one-paragraph: what decision/artefact this epic produces, and why -->

## Description
<!-- pipeline coverage: which stages this epic delivers (idea/knowledge/research/adr/proposal/project). Enumerate sub-tasks with short IDs (K1..Kn, R1.., etc.) and one line each. State explicitly what the epic DOES and DOES NOT include. -->

## KB sections covered
<!-- checklist: ideas / knowledge / research / proposals / adr / projects / tasks -->

## Out of Scope

## Sources
<!-- Real links the epic builds on: official docs, KB notes (./ relative). Never prose-only. -->

## Acceptance Criteria
- [ ] Sub-issues created as native GitHub sub-issues of this epic
- [ ] Every sub-issue created from its corresponding issue form template
- [ ] Each sub-issue carries topic-specific acceptance criteria per the Per-topic table and passes its section's review pipeline
```

## Sub-issue template (from Templates/tasks/issue.md)

```markdown
## Objective
## Description
<!-- "Closes gap-cluster {ID} for umbrella epic #{N}". -->
## In Scope
<!-- bullet list; if not here, not required -->
## Out of Scope
<!-- reference sibling sub-tasks of the same epic -->
## Provenance
## Assumptions
## Good Examples
## Bad Examples
## Topic Hierarchy
```
{folder/path/}
```
## Sources
<!-- Links to source documents, specifications, or reference materials this task is based on.
Use real URLs (absolute for online, ./ for repo-relative). Never plain prose without links. -->
## Summary
## Instructions
<!-- per-topic: which agent produces it, template to follow, frontmatter rules, line range, review pipeline -->
## Acceptance Criteria
<!-- Per-issue, specific, verifiable; must be relevant to the topic's actual deliverable
(see Per-topic acceptance criteria). -->
## Parent
#{epic-number}
```

## Workflow (single flow)

1. Ask the user for the epic objective and scope; map it onto the pipeline (which stages are in scope → which topics → which labels).
2. Draft the epic body from the epic template; confirm the `KB sections covered` checklist.
3. Create the epic: `gh issue create --title "Epic: {Title}" --body-file epic.md --label epic`.
4. For each in-scope stage, draft a sub-issue body from the sub-issue template, filled per the per-topic spec (label, template, frontmatter, review pipeline). Sources must be links (URLs or `./` repo-relative); acceptance criteria must be topic-specific per the Per-topic table.
5. Create each sub-issue: `gh issue create --title "{Topic}: {Title}" --body-file {id}.md --label {label} --parent {epic-number}`.
6. Verify: `gh issue view {epic-number} --json sub_issues`.

## gh CLI reference

- Create epic: `gh issue create --title "Epic: …" --body-file epic.md --label epic --repo RunicEngines/knowledge-base`
- Create sub-issue: `gh issue create --title "Knowledge: …" --body-file k1.md --label knowledge --parent {epic-number} --repo RunicEngines/knowledge-base`
- Link existing issue as sub-issue: `gh issue edit {epic} --add-sub-issue {issue}`
- Read structure: `gh issue view {n} --json number,title,labels,parent,sub_issues,body`
- Labels: `gh label list --repo RunicEngines/knowledge-base`
- Author from `git config user.name`; dates ISO 8601 (`YYYY-MM-DD`); kebab-case titles.
