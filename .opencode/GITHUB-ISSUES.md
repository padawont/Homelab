---
title: "GITHUB-ISSUES.md — Issue contract"
status: accepted
author: "padawont"
date: 2026-11-17
tags: []
sources: []
last_audit_date: 2026-11-17
related_docs: []
---

# GITHUB-ISSUES.md — Issue contract

The canonical structure for every issue in `RunicEngines/knowledge-base`. Issues
describe work on **this** repo (`padawont/Homelab`); the tracker lives elsewhere,
the content does not.

**Precedence.** This file owns issue structure. The filing skill
(`./.opencode/skills/create-github-issues/SKILL.md`) owns the `gh` plumbing and
nothing else. A GitHub issue form that disagrees with this file is a defect to
be fixed in `knowledge-base`, never a licence to improvise. No agent, skill, or
template restates these rules — they link here.

## Why an issue is shaped this way

An agent handed an issue number must answer four questions without asking a
human: **why** the work exists, **how** it should be done, **where** the files
land, and **what proves it done**. Each question has one fixed home, so a reader
never has to understand the topic before finding the answer.

| Question | Home | Rule |
|---|---|---|
| Why | `## Objective` | never empty, never marketing |
| How | `## Instructions` | template, line rule, review lane, branch |
| Where | `issue-spec.outputs` | `./`-rooted paths in this repo |
| Done | `## Acceptance Criteria` | at least one item checkable by a command or a file state |

## Slot order

Every issue body is the `issue-spec` block followed by H2 headings in this
order. A topic uses the slots it needs; the relative order never changes.

```text
## Objective
## Description
## In Scope
## Out of Scope
## Instructions
## KB sections covered
## Provenance
## Assumptions
## Coverage
## Good Examples
## Bad Examples
## Topic Hierarchy
## Related Research
## Related ADRs
## Sources
## References
## Consequences
## Considered Options
## Files affected
## Summary
## Execution roster
## Acceptance Criteria
## Parent
```

`## Summary` and `## Execution roster` are optional extras kept for house
consistency. `## Parent` always repeats the native parent number, or `—` for an
epic.

## The `issue-spec` block

First thing in the body, before any H2:

````markdown
```yaml issue-spec
topic: knowledge
stage: knowledge
epic: 825
labels: [knowledge, "area: databases"]
outputs:
  - ./02_Knowledge/technologies/multi-model-databases/litegraph/overview.md
sources:
  - https://litegraphdb.com/
```
````

| Key | Type | Rule |
|---|---|---|
| `topic` | enum | one of the nine topics in § Topic anatomy |
| `stage` | enum | `idea`, `knowledge`, `research`, `adr`, `implementation`, or `epic` when the issue spans several stages |
| `epic` | int or `null` | must equal the native parent; `null` only for an epic |
| `labels` | list | topic label first, then `area: *`; every value from `./AGENTS.md` § Git Guidelines |
| `outputs` | list | `./`-rooted paths under `01_Ideas/`–`05_Implementations/` or `Templates/`; `[]` is legal only for an epic; `<placeholder>` segments allowed |
| `sources` | list | absolute URLs or `./` repo paths; never prose; `[]` only for an epic with no cited basis |

ADR outputs use the issue number: `./04_ADRs/<issue>-<slug>.md`
(`./04_ADRs/AGENTS.md` § Frontmatter — the number is the issue number).

## Topic anatomy

| Topic | Title prefix | Label | Outputs |
|---|---|---|---|
| `epic` | `Epic:` | `epic` | `[]` — children are native sub-issues |
| `idea` | `Idea:` | `idea` | `./01_Ideas/<topic>/idea-<name>.md` |
| `knowledge` | `Knowledge:` | `knowledge` | 1–8 atomic notes under `./02_Knowledge/technologies/<category>/<topic>/` |
| `knowledge-audit` | `Knowledge Audit:` | `knowledge` | the split targets plus the folder index |
| `research` | `Research:` | `research` | `./03_Research/<topic>/overview.md`, `alternatives.md`, `alternative-<name>.md` |
| `proposal` | `Proposal:` | `proposal` | none — flagged, see § Out of scope |
| `adr` | `ADR:` | `adr` | `./04_ADRs/<issue>-<slug>.md` |
| `implementation` | `Implementation:` | `implementation` | `overview.md`, `rollback.md`, `configs/*` under `./05_Implementations/node-main/<service>/` |
| `chore` | `Chore:` | `documentation` | exactly the files it reconciles |

## Skeletons

Copy the topic's skeleton, replace `{placeholder}` values, delete unused
optional extras. Keep the block first and the heading order intact.

### epic

````markdown
```yaml issue-spec
topic: epic
stage: {stage-or-epic}
epic: null
labels: [epic]
outputs: []
sources: []
```
# Epic: {name}

## Objective
## Description
## Out of Scope
## Instructions
## KB sections covered
## Acceptance Criteria
````

### idea

````markdown
```yaml issue-spec
topic: idea
stage: idea
epic: {epic-number}
labels: [idea]
outputs:
  - ./01_Ideas/{topic}/idea-{name}.md
sources:
  - {absolute-url-or-repo-path}
```
# Idea: {name}

## Objective
## Description
## In Scope
## Out of Scope
## Instructions
## Provenance
## Assumptions
## Good Examples
## Bad Examples
## Topic Hierarchy
## Sources
## Summary
## Execution roster
## Acceptance Criteria
## Parent
````

### knowledge

````markdown
```yaml issue-spec
topic: knowledge
stage: knowledge
epic: {epic-number}
labels: [knowledge]
outputs:
  - ./02_Knowledge/technologies/{category}/{topic}/{concept}.md
sources:
  - {absolute-url-or-repo-path}
```
# Knowledge: {name}

## Objective
## Description
## In Scope
## Out of Scope
## Instructions
## Provenance
## Assumptions
## Coverage
## Good Examples
## Bad Examples
## Topic Hierarchy
## Acceptance Criteria
## Parent
````

### knowledge-audit

````markdown
```yaml issue-spec
topic: knowledge-audit
stage: knowledge
epic: {epic-number}
labels: [knowledge]
outputs:
  - ./02_Knowledge/technologies/{category}/{topic}/{split-concept}.md
  - ./02_Knowledge/technologies/{category}/{topic}/overview.md
sources:
  - ./02_Knowledge/technologies/{category}/{topic}/{oversized-note}.md
```
# Knowledge Audit: {name}

## Objective
## Description
## In Scope
## Out of Scope
## Instructions
## Provenance
## Assumptions
## Good Examples
## Bad Examples
## Topic Hierarchy
## Acceptance Criteria
## Parent
````

### research

````markdown
```yaml issue-spec
topic: research
stage: research
epic: {epic-number}
labels: [research]
outputs:
  - ./03_Research/{topic}/overview.md
  - ./03_Research/{topic}/alternatives.md
  - ./03_Research/{topic}/alternative-{name}.md
sources:
  - {absolute-url-or-repo-path}
```
# Research: {name}

## Objective
## Description
## In Scope
## Out of Scope
## Instructions
## Provenance
## Assumptions
## Good Examples
## Bad Examples
## Topic Hierarchy
## Sources
## Summary
## Execution roster
## Acceptance Criteria
## Parent
````

### proposal

````markdown
```yaml issue-spec
topic: proposal
stage: proposal
epic: {epic-number}
labels: [proposal]
outputs: []
sources:
  - {absolute-url-or-repo-path}
```
# Proposal: {name}

## Objective
## Description
## In Scope
## Out of Scope
## Instructions
## Acceptance Criteria
## Parent
````

`outputs: []` is deliberate: a proposal has no Homelab folder. See § Out of scope.

### adr

````markdown
```yaml issue-spec
topic: adr
stage: adr
epic: {epic-number}
labels: [adr]
outputs:
  - ./04_ADRs/{issue-number}-{kebab-slug}.md
sources:
  - ./03_Research/{topic}/overview.md
```
# ADR: {name}

## Objective
## Description
## In Scope
## Out of Scope
## Instructions
## Provenance
## Assumptions
## Good Examples
## Bad Examples
## Summary
## Execution roster
## Acceptance Criteria
## Parent
````

### implementation

````markdown
```yaml issue-spec
topic: implementation
stage: implementation
epic: {epic-number}
labels: [implementation]
outputs:
  - ./05_Implementations/node-main/{service}/overview.md
  - ./05_Implementations/node-main/{service}/rollback.md
  - ./05_Implementations/node-main/{service}/configs/{manifest}.yaml
sources:
  - ./04_ADRs/{issue-number}-{kebab-slug}.md
```
# Implementation: {name}

## Objective
## Description
## In Scope
## Out of Scope
## Instructions
## Provenance
## Assumptions
## Good Examples
## Bad Examples
## Topic Hierarchy
## Sources
## Summary
## Execution roster
## Acceptance Criteria
## Parent
````

### chore

````markdown
```yaml issue-spec
topic: chore
stage: {stage-of-the-files}
epic: {epic-number-or-null}
labels: [documentation]
outputs:
  - ./{path/the/chore/edits}.md
sources:
  - ./{path/the/chore/edits}.md
```
# Chore: {name}

## Objective
## Description
## In Scope
## Out of Scope
## Instructions
## Files affected
## Acceptance Criteria
## Parent
````

## Read protocol

Given an issue number:

1. `gh issue view {n} --json number,title,labels,parent,body`.
2. Parse the `issue-spec` fence. Validate `epic` against `parent.number`, each
   label against `./AGENTS.md`, and each `outputs` root against this repo.
3. **No fence** — reconstruct the four answers from the topic anatomy and the
   heading order, and report `spec: missing`. Never invent a path the body does
   not state; a missing output list is a finding, not a gap to fill silently.
4. Resolve `outputs` against the working tree: which files exist, which folders
   are missing. That difference is the work.

## Write protocol

1. Draft the body from the topic skeleton, with real `outputs` and `sources`.
2. Self-check: block keys present, title prefix matches the topic, labels valid,
   every `./` path inside an allowed root, every acceptance item checkable.
3. File:
   `gh issue create --title "{Prefix}: {name}" --body-file {path} --label {label} --parent {epic} --repo RunicEngines/knowledge-base`
   with the body written under `.runesmith/*/pipeline/`.
4. Verify: `gh issue view {n} --json body,labels,parent` — re-parse the fence and
   confirm the parent.

## Sources and naming

- `sources` entries are absolute URLs or `./` repo paths. Prose such as
  "ADR 0033 and ADR 0044 D1" is a defect: convert it to the files it names.
- Dates are ISO 8601. Titles are kebab-case after the prefix. Author from
  `git config user.name`.
- Acceptance criteria are topic-specific and verifiable. "Passes the review
  pipeline" is never the only item — name the check that runs.

## Legacy mapping

Bodies written before this contract use another repo's layout. Map, do not
guess:

| Legacy path | Homelab path |
|---|---|
| `knowledge/technology/<a>/<b>/x.md` | `./02_Knowledge/technologies/<a>/<b>/x.md` |
| `knowledge/tooling/<a>/<b>/x.md` | `./02_Knowledge/technologies/tools/<a>/<b>/x.md` |
| `knowledge/.../README.md` | `.../overview.md` |
| `ideas/<topic>/` | `./01_Ideas/<topic>/` |
| `research/<topic>/` | `./03_Research/<topic>/` |
| `adr/<NNNN>-<slug>/overview.md` | `./04_ADRs/<issue>-<slug>.md` |
| `templates/<path>` | `./Templates/<path>` |

`knowledge/design/`, `knowledge/operations/`, `proposals/`, `projects/`,
`tasks/` have no Homelab equivalent.

## Out of scope

An issue is in scope only if its `outputs` land in this repo. Issues about
another repo's content — the `#847` runehammer tree, NeutralWaste ADRs, and any
`proposal` issue — are **out-of-scope records**: leave the body byte-for-byte
untouched, list them in the retrofit report with a recommendation, and let the
human decide whether to close, move, or add a section. Never rewrite them into
Homelab terms.

## Retrofit

Old bodies reach this contract in two reviewable batches, drafted under
`.runesmith/*/pipeline/` and applied by the human:

1. **Mechanical** — paths map by § Legacy mapping, `outputs` derive from the
   body, headings reorder. Emits `body/{n}.md`, a report, `apply.sh`, and
   `revert.sh`.
2. **Agent read** — bodies that never name their files: a worker names real
   Homelab outputs or flags the issue.

Nothing is posted by an agent: `gh issue edit` is human-run. A batch is done
when every re-fetched body parses and the exception list is explicit.

## Drift

The contract, the issue forms in `knowledge-base`, and
`tests/test_issue_contract.py` must agree. A disagreement is a failing test or a
filed defect, in that order — never a silent local exception.
