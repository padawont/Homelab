---
name: create-github-issues
description: >
  Creates GitHub epics and pipeline sub-issues for the Homelab PKM using the gh
  CLI. Use when creating an epic, a pipeline issue (idea / knowledge / research
  / adr / proposal / projects / implementation), or native sub-issues on the
  RunicEngines/knowledge-base repo. Use ONLY when creating GitHub issues, never
  for writing notes.
---

# create-github-issues

Plan and create GitHub epics and pipeline sub-issues on
`RunicEngines/knowledge-base` using the `gh` CLI. Native parent/child links use
`gh issue create --parent <number>` (requires gh >= 2.94). Every sub-issue is
drafted from `Templates/tasks/issue.md` and filled from the per-topic spec
below.

> [!IMPORTANT]
> Issues and epics live in `RunicEngines/knowledge-base`. The `padawont/Homelab`
> repo holds only notes. Every `gh` command below MUST include
> `--repo RunicEngines/knowledge-base`.

## The content pipeline

```
Idea → Knowledge → Research → ADR → Implementation
                                  └──► Archive
Proposal = how-we-work; Projects/Tasks = registry index updates
```

## Per-topic spec

| Topic | Label | Template(s) | Frontmatter | Review pipeline |
|---|---|---|---|---|
| Idea | `idea` | `Templates/ideas/idea.md` | title, status, author, date, tags, technologies, related_ideas | none (draft → accepted) |
| Knowledge | `knowledge` | `Templates/knowledge/note.md` | title, status, author, date, tags, sources[{url,title}], last_audit_date, related_docs | pkm-researcher → pkm-editor |
| Research | `research` | `Templates/research/overview.md` + `alternatives.md` + `alternative.md` | title, status, author, date, tags, sources[{knowledge}], references[{url,title}], last_audit_date | pkm-researcher → pkm-overview |
| ADR | `adr` | `Templates/adr/adr.md` | adr, title, author, status, topic, technology, date, date-proposed, replaces, replaced-by, history, sources, references, related_docs | pkm-overview + pkm-compliance |
| Proposal | `proposal` | — | change-log style | pkm-compliance |
| Projects | — | projects registry index | chore template | — |
| Implementation | — | `Templates/implementations/service.md` + `rollback.md` | title, status, author, date, tags, technologies, related_docs, references, node | pkm-editor + pkm-compliance |

> [!NOTE]
> The review pipeline column lists the minimum/primary reviewers for the
> issue's drafted content. When files already exist and need validation, the
> full `loop-validation` pipeline always runs all four agents (Researcher →
> Editor → Overview → Compliance), regardless of topic.

### Knowledge atomic breakdown (required)

Knowledge sub-issues MUST decompose the topic into multiple single-concept
notes before drafting — never a single "mega note" or 2-3 broad files.

- One concept per file (e.g. install, operations, secrets, upgrades, migration
  each get their own note).
- Target 3–8 notes per sub-issue; each ≤150 lines (frontmatter included).
- List EVERY planned note file in the sub-issue body: Topic Hierarchy section
  with a one-line concept next to each file, plus In Scope bullets.
- Follow-up concept not fitting an existing note → its own new file, never
  appended to a near-limit one.

## Workflow

1. Ask the user for the epic objective and scope; map it onto the pipeline
   (which stages are in scope → which topics → which labels).
2. Draft the epic body from the epic template; confirm the `KB sections
   covered` checklist.
3. Create the epic:
   `gh issue create --title "Epic: {Title}" --body-file epic.md --label epic --repo RunicEngines/knowledge-base`.
4. For each in-scope stage, draft a sub-issue body from the sub-issue template,
   filled per the per-topic spec. Sources must be links (absolute URLs or `./`
   repo-relative paths); acceptance criteria must be topic-specific per the
   per-topic acceptance table below. For Knowledge sub-issues, decompose the
   topic into single-concept atomic notes first and enumerate each in In Scope
   + Topic Hierarchy (per the Knowledge atomic breakdown rule).
5. Create each sub-issue:
   `gh issue create --title "{Topic}: {Title}" --body-file {id}.md --label {label} --parent {epic-number} --repo RunicEngines/knowledge-base`.
6. Verify the epic nests the sub-issues:
   `gh issue view {epic-number} --json subIssues --repo RunicEngines/knowledge-base`.

## Epic template

```markdown
## Objective
## Description
## KB sections covered
## Out of Scope
## Sources
## Acceptance Criteria
```

## Sub-issue template (from Templates/tasks/issue.md)

```markdown
## Objective
## Description
## In Scope
## Out of Scope
## Provenance
## Assumptions
## Good Examples
## Bad Examples
## Topic Hierarchy
## Sources
## Summary
## Instructions
## Acceptance Criteria
## Parent
#{epic-number}
```

## Per-topic acceptance criteria

| Topic | Core acceptance criteria |
|---|---|
| Idea | status `accepted`; ready to promote to Knowledge |
| Knowledge | 3–8 atomic notes, one concept per file, each ≤150 lines (frontmatter included); every planned note enumerated in the issue (In Scope + Topic Hierarchy); valid frontmatter; every `sources[]` URL live; `last_audit_date` set; passes knowledge review |
| Research | `overview.md` + ≥3 `alternative.md` files; ≥1 knowledge/online source; detailed enough to write the ADR directly |
| ADR | filename `{issue}-{kebab}.md`; `adr` = issue number; ≥2 mermaid diagrams; links to Research; `draft → accepted` gated on review |
| Proposal | change-log entry recorded |
| Implementation | `overview.md` + `rollback.md` + nixos flake dir (`05_Implementations/node-main/nixos/`); flake with `nixosConfigurations` + deploy target; rollback verified |

## Source rules

- Every issue must cite real links — absolute URLs for online sources, `./`
  repo-relative paths for KB docs. Never prose-only sources.
- Acceptance criteria are always topic-specific and verifiable — never generic
  boilerplate.
- A Knowledge sub-issue bundling multiple concepts into one file, or listing
  notes without per-file concepts, must be revised before creation.

## gh CLI reference

| Command | Purpose |
|---|---|
| `gh issue create --title "Epic: …" --body-file epic.md --label epic --repo RunicEngines/knowledge-base` | Create epic |
| `gh issue create --title "Knowledge: …" --body-file k1.md --label knowledge --parent {epic-number} --repo RunicEngines/knowledge-base` | Create sub-issue |
| `gh issue edit {epic} --add-sub-issue {issue} --repo RunicEngines/knowledge-base` | Link existing issue as sub-issue |
| `gh issue view {n} --json number,title,labels,parent,subIssues,body --repo RunicEngines/knowledge-base` | Read structure |
| `gh label list --repo RunicEngines/knowledge-base` | List labels |

Author from `git config user.name`; dates ISO 8601 (`YYYY-MM-DD`); kebab-case
titles.
