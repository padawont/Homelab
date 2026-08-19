---
name: validate-pkm
description: Validates Homelab PKM content by orchestrating five standard-prompt runs of the general subagent (linting, online fact-check, knowledge-base fact-check, depth check, status change), looping up to a user-chosen count, on one file or a batch. Use ONLY when validating files or issues (e.g. "validate this file/issue", "lint", "fact-check", "audit", "verify conventions"). Do NOT use for creating notes, writing content, or general questions.
---

# validate-pkm

Validate one or more Homelab PKM files against AGENTS.md conventions by orchestrating
five standard-prompt runs of the built-in `general` subagent, looped a user-chosen
number of times. This skill is for validating existing files and issues only.

## Workflow

### 1. Gather targets
- Take the target file path(s) from the user.
- Ask the user for the scope:
  - **single** — one file, or
  - **batch** — multiple files (accept a list or glob).
- Ask the user for the max loop count (**default 5**).

### 2. Loop
Run the **full** loop count every time (never early-stop). For each file in scope, each
loop launches the built-in `general` subagent via the Task tool with each of the five
standard prompts below, then aggregates the results.

Use the per-section frontmatter/status tables and root rules below as the shared spec
all five prompts operate against.

## Shared spec

### Root / global rules (apply to every section)
- At most **150 lines** per file (including frontmatter and blank lines).
- **kebab-case** filenames and folders.
- **tags**: lowercase kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`).
- **dates**: ISO 8601 (`YYYY-MM-DD`).
- **cross-links**: relative paths from repo root (e.g. `./02_Knowledge/...`).

### Per-section required frontmatter + allowed status

| Section | Required fields | Status values |
|---|---|---|
| `01_Ideas` | title, status, author, date, tags, technologies, related_ideas | draft / accepted / archived |
| `02_Knowledge` | title, status, author, date, tags, sources[{url,title}], last_audit_date | draft / accepted / archived |
| `03_Research` | title, status, author, date, tags, sources[{knowledge}], references[{url,title}], last_audit_date | draft / accepted / archived |
| `04_ADRs` | adr, title, author, status, topic, technology, date, date-proposed, replaces, replaced-by, history, sources, references | draft / accepted / archived |
| `05_Implementations` | title, status, author, date, tags, technologies, related_docs, references{online,repo}, node | draft / active / retired |
| `06_Archive` | title, original_location, archived_date, reason, superseded_by | — |

### Section-specific structure
- **ADR** (`04_ADRs`): filename `{issue-number}-{kebab-description}.md`; `adr` = issue
  number; at least **two mermaid diagrams** (internal working + fit into homelab).
- **Implementation** (`05_Implementations`): every folder ships `overview.md` +
  `rollback.md` (+ `configs/` where applicable).
- **Archive** (`06_Archive`): preserve original content verbatim, add archival
  frontmatter on top; content is purged after 31 days.

## The five standard prompts

Launch each as the built-in `general` subagent via the Task tool.

### P1 — Linter
Verify required frontmatter per section (table above) and allowed status values; check
global rules (150-line limit, kebab-case filenames, lowercase kebab-case tags, ISO
dates, relative repo-root cross-links); check section structure (ADR mermaid diagrams
and `{issue}-{kebab}.md` naming; Implementations `overview.md`+`rollback.md`+`configs/`).
Auto-fix unambiguous issues (case, date formatting, line-splits, filenames); report
everything else. Return a `{file, line, issue, fixed}` list.

### P2 — Fact-check online
- Fetch every external `references[]` / `sources[]` URL and confirm each is live and
  returns expected content (`webfetch` / `websearch`).
- Cross-check cited facts and claims against authoritative sources; flag dead links,
  wrong URLs, superseded/outdated claims, and unsupported assertions.
- Verify the file's general info is **written correctly**: code blocks are valid and
  syntactically sound, configs match the documented tooling, and prose paragraphs are
  accurate and coherent against the source.
- Do **not** report confidence scores — state findings plainly with a concrete
  recommended action.
- Return `{url_or_item, status, issue, recommended_action}`.

### P3 — Fact-check knowledge base
- Resolve all `related_docs` / `related_ideas` / Knowledge / Research / ADR cross-links;
  confirm they exist and match the referenced topic.
- Compare claims against existing notes; flag contradictions or duplication.
- Enforce dependency rules: Research requires ≥1 Knowledge note or online source; ADR
  requires a Research doc; Implementation requires an ADR + Knowledge note(s).
- Return `{link, exists, matches, issue}`.

### P4 — Depth check (generalized)
- Assess whether the file is substantive enough for its section using **generic depth
  criteria** (not per-section checklists): clear purpose, adequate detail and examples,
  complete and consistent sections, and enough context to be actionable — versus being a
  thin stub or bare outline.
- Flag thin/stub files and state which areas are underdeveloped or need expansion.
- Return `{file, depth_rating, missing_areas}`.

### P5 — Status change
- Review P1–P4 outputs. Determine the correct status transition per lifecycle:
  `draft → accepted → archived` (Implementations: `draft → active → retired`).
- Apply the transition **only** when the file passes lint + depth and both fact-checks
  clear; otherwise keep `draft` and state why.
- Set `last_audit_date` (and archive frontmatter where applicable).
- Return `{from, to, applied, reason}`.

## Output

After the final loop, print a consolidated report per file:
- fixed items
- remaining violations
- depth gaps
- dead / incorrect links
- status change applied
