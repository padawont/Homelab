---
title: "AGENTS.md — Homelab PKM"
status: accepted
author: "padawont"
date: 2026-11-03
tags: []
sources: []
last_audit_date: 2026-11-03
related_docs: []
---

# AGENTS.md — Homelab PKM

Personal Knowledge Management system for my homelab.

## Repository Structure (PKM content)

| Folder | Purpose | AGENTS.md |
|---|---|---|
| `01_Ideas/` | Raw concepts, wishlist items, new tech spottings | ./01_Ideas/AGENTS.md |
| `02_Knowledge/` | General tech concepts, syntax guides, theory | ./02_Knowledge/AGENTS.md |
| `03_Research/` | Deep dives combining ideas + knowledge into an ADR plan | ./03_Research/AGENTS.md |
| `04_ADRs/` | Architectural Decision Records with mermaid diagrams | ./04_ADRs/AGENTS.md |
| `05_Implementations/` | Live running setups: `overview.md`, `rollback.md`, `configs/` | ./05_Implementations/AGENTS.md |
| `06_Archive/` | Failed experiments, rejected proposals, retired services | ./06_Archive/AGENTS.md |
| `Templates/` | Reusable document templates | ./Templates/AGENTS.md |

Tooling lives at the repo root and is not PKM content: `devbox.json` (dev shell and
`test` script), `pyproject.toml` (pytest configuration), `tests/` (roster conformance
harness), and `./.opencode/` (agent definitions and workflow).

## When to Load Subfolder AGENTS.md

Load on a need-to-know basis — do not load all at once. The folder → `AGENTS.md` map is
in § Repository Structure; this list only says which folder a task belongs to.

- Capturing a new idea? → `01_Ideas/`
- Writing a reference note? → `02_Knowledge/`
- Running a deep-dive? → `03_Research/`
- Making an architectural decision? → `04_ADRs/`
- Deploying a service? → `05_Implementations/`
- Archiving retired/rejected content? → `06_Archive/`
- Creating a document from a template? → `Templates/`

## Content Pipeline

```
Idea → Knowledge → Research → ADR → Implementation
  └──────┴──────────┴────────┴────────┴──► Archive
```

Each step refines the concept further. At any point, if rejected or abandoned, it goes to Archive.

| Step | Input | Output |
|---|---|---|
| **Idea → Knowledge** | Raw concept | Structured reference note |
| **Knowledge → Research** | Knowledge + Ideas + online docs | Plan for ADR, with alternatives |
| **Research → ADR** | Research doc | Decision record with mermaid diagrams |
| **ADR → Implementation** | ADR | Live service: `overview.md` + `rollback.md` (+ `configs/` where applicable) |
| **Any → Archive** | Content of any stage | See `./06_Archive/AGENTS.md` § Conventions |

### Dependency Rules

- Ideas: stand alone
- Knowledge: stand alone
- Research: requires at least one Knowledge note or online documentation
- ADR: requires a Research doc
- Implementation: requires an ADR + Knowledge note(s)

## Frontmatter by Section

Each section defines its own frontmatter — the field specs live in the section file named
in § Repository Structure (its `AGENTS.md` column). `Templates/` files use placeholder
values; see `./Templates/AGENTS.md` § Conventions.

## Atomic File Rule

- Maximum **150 lines** per file (including frontmatter and blank lines) — this applies to
  PKM content in Ideas, Knowledge, Research, ADRs, and Implementations
- When a file exceeds 150 lines, split it into multiple files
- Splitting strategies:
  - **By concept**: one concept per file (e.g. `deploy.md`, `configure.md`, `operate.md` instead of one giant file)
  - **By section**: move subsections into separate files linked via `related_docs`
  - **By date**: split notes/changelogs into dated files
- `Templates/` files follow their own conventions — see `./Templates/AGENTS.md`
- Archive records are exempt from the line limit — see `./06_Archive/AGENTS.md` § Conventions
- `AGENTS.md` files and `./.opencode/agents/*.md` take the 50–250 line range instead of
  150, counted the same way
- `./.opencode/WORKFLOW.md` and `./.opencode/REVIEW.md` are exempt from the line limit

## Status Lifecycle

Each section owns its status values and transitions — see the section's AGENTS.md
(e.g. `./01_Ideas/AGENTS.md`, `./05_Implementations/AGENTS.md`).

## Git Guidelines

| Practice | Rule |
|---|---|
| Branch naming | `{type}/{issue-number}-{kebab-description}` — e.g. `feat/42-user-auth`, `knowledge/39-worktrunk` |
| Commit messages | Conventional Commits — `type(scope): description` |
| PR workflow | draft → tests pass → review → merge |
| Merge strategy | Squash merge (default); merge commits or rebase merge by exception |
| Code review | Code/tooling changes: at least 1 approving review, all threads resolved. PKM notes: their section's convention (e.g. `./01_Ideas/AGENTS.md`) |
| Labels | `bug`, `enhancement`, `documentation`, `area: <topic>`, `knowledge`, `research`, `adr`, `implementation` |
| Tests | `devbox run test` (pytest) must pass before merge; no hosted CI is configured |

## General Conventions

- **Naming**: kebab-case for all files and folders (`topic-name/file-name.md`)
- **Frontmatter**: YAML between `---` delimiters
- **Tags**: lowercase kebab-case — `^[a-z0-9]+(-[a-z0-9]+)*$`
- **Dates**: ISO 8601 — `YYYY-MM-DD`
- **Cross-linking**: use relative paths from repo root (e.g. `./02_Knowledge/technologies/kubernetes/concepts/ingress.md`)
- **Templates**: always copy from `Templates/` — never edit in place
- **Archive**: see `./06_Archive/AGENTS.md` § Conventions
- **Relevance over completeness**: include only information relevant to running it in a homelab. Do not include technology history, origin stories, or sales/marketing points
