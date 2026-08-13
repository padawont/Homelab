# AGENTS.md — Homelab PKM

Personal Knowledge Management system for my homelab.

## Repository Structure

| Folder | Purpose | AGENTS.md |
|---|---|---|
| `01_Ideas/` | Raw concepts, wishlist items, new tech spottings | ./01_Ideas/AGENTS.md |
| `02_Knowledge/` | General tech concepts, syntax guides, theory | ./02_Knowledge/AGENTS.md |
| `03_Research/` | Deep dives combining ideas + knowledge into an ADR plan | ./03_Research/AGENTS.md |
| `04_ADRs/` | Architectural Decision Records with mermaid diagrams | ./04_ADRs/AGENTS.md |
| `05_Implementations/` | Live running setups — configs and overview | ./05_Implementations/AGENTS.md |
| `06_Archive/` | Failed experiments, rejected proposals, retired services | ./06_Archive/AGENTS.md |
| `Templates/` | Reusable document templates | ./Templates/AGENTS.md |

## When to Load Subfolder AGENTS.md

Load on a need-to-know basis — do not load all at once.

- Capturing a new idea? → `./01_Ideas/AGENTS.md`
- Writing a reference note? → `./02_Knowledge/AGENTS.md`
- Running a deep-dive? → `./03_Research/AGENTS.md`
- Making an architectural decision? → `./04_ADRs/AGENTS.md`
- Deploying a service? → `./05_Implementations/AGENTS.md`
- Archiving retired/rejected content? → `./06_Archive/AGENTS.md`
- Creating a document from a template? → `./Templates/AGENTS.md`

## Content Pipeline

```
Idea → Knowledge → Research → ADR → Implementation
                                    └──► Archive
```

Each step refines the concept further. At any point, if rejected or abandoned, it goes to Archive.

| Step | Input | Output |
|---|---|---|
| **Idea → Knowledge** | Raw concept | Structured reference note |
| **Knowledge → Research** | Knowledge + Ideas + online docs | Plan for ADR, with alternatives |
| **Research → ADR** | Research doc | Decision record with mermaid diagrams |
| **ADR → Implementation** | ADR | Live service (overview + configs) |
| **Any → Archive** | Archived content | Moved, purged after 31 days |

### Dependency Rules

- Ideas: stand alone
- Knowledge: stand alone
- Research: requires at least one Knowledge note or online documentation
- ADR: requires a Research doc
- Implementation: requires an ADR + Knowledge note(s)

## Frontmatter by Section

Each section defines its own frontmatter. See the individual AGENTS.md for exact field specs.

| Section | Key fields |
|---|---|
| `01_Ideas/` | `title, status, author, date, tags, technologies, related_ideas` |
| `02_Knowledge/` | `title, status, author, date, tags, sources[{url,title}], last_audit_date` |
| `03_Research/` | `title, status, author, date, tags, sources[{knowledge:""}], references[{url,title}], last_audit_date` |
| `04_ADRs/` | `adr, title, author, status, topic, technology, date, date-proposed, replaces, replaced-by, history, sources, references` |
| `05_Implementations/` | `title, status, author, date, tags, technologies, related_docs, references, node` |
| `06_Archive/` | `title, original_location, archived_date, reason, superseded_by` |

## Atomic File Rule

- Maximum **150 lines** per file (including frontmatter and blank lines)
- When a file exceeds 150 lines, split it into multiple files
- Splitting strategies:
  - **By concept**: one concept per file (e.g. `deploy.md`, `configure.md`, `operate.md` instead of one giant file)
  - **By section**: move subsections into separate files linked via `related_docs`
  - **By date**: split notes/changelogs into dated files
- This applies to all sections: Ideas, Knowledge, Research, ADRs, Implementations
- Archive records are exempt (they are copies of originals)

## Status Lifecycle (all sections)

```
draft → accepted
  L__> archived
```

## Git Guidelines

| Practice | Rule |
|---|---|
| Branch naming | `{type}/{issue-number}-{kebab-description}` — e.g. `feat/42-user-auth`, `knowledge/39-worktrunk` |
| Commit messages | Conventional Commits — `type(scope): description` |
| PR workflow | draft → CI passes → review → merge |
| Merge strategy | Squash merge (default); merge commits or rebase merge by exception |
| Code review | At least 1 approving review; resolve all threads before merge |
| Labels | Shared org-wide taxonomy: type (bug/enhancement/docs/chore), area, scope/priority |
| CI | Required checks must pass; default branch protected |
| Fast-track | Mutual consent + fast-track label for trivial/urgent changes |

## General Conventions

- **Naming**: kebab-case for all files and folders (`topic-name/file-name.md`)
- **Frontmatter**: YAML between `---` delimiters
- **Tags**: lowercase kebab-case — `^[a-z0-9]+(-[a-z0-9]+)*$`
- **Dates**: ISO 8601 — `YYYY-MM-DD`
- **Cross-linking**: use relative paths from repo root (e.g. `./02_Knowledge/technologies/kubernetes/ingress.md`)
- **Templates**: always copy from `Templates/` — never edit in place
- **Archive**: moved content is purged after 31 days
