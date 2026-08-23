---
name: loop-validation
description: >
  Validates and fixes Homelab PKM content by looping four role-based subagents
  — Researcher (fact-check online + local), Editor (applies confirmed fixes
  with source/rule justification), Overview (context & homelab-fit review), and
  Compliance (AGENTS.md missed-rules check) — until clean or a user-chosen loop
  count. For VALIDATION ONLY: fixing issues in existing files/issues, never
  creating new notes or content from scratch.
---

# loop-validation

## When to use

- A user asks to validate/fix an existing PKM file or a set of files.
- A PKM issue needs fact-checking against online sources and repo notes.
- Content needs a section-fit and homelab-fit review before acceptance.

## When NOT to use

- Capturing a new idea, writing a new note, or drafting research from scratch
  (use the normal capture pipeline).
- Non-PKM content (application code, infra configs) — PKM content only.

## Loop model

Fixed order, never skipped:

```
Researcher → Editor → Overview → Compliance   (repeat, max 10)
```

| Agent | Subagent | Focus |
|---|---|---|
| Researcher | `pkm-researcher` | URLs live, claims correct, ≤250-line report |
| Editor | `pkm-editor` | Confirmed fixes only, each citing source/rule |
| Overview | `pkm-overview` | Section + homelab fit |
| Compliance | `pkm-compliance` | Missed AGENTS.md rules |

Every agent posts its findings to the main chat; the main AI aggregates and
reports them per loop and in the final consolidated report.

## Agent detail

### 1. Researcher (`pkm-researcher`)

- Fetch and confirm every external `sources[]` / `references[]` URL is live
  and returns relevant content (`webfetch`).
- Cross-check claims against authoritative sources and existing repo notes
  (read/glob/grep across `01_Ideas/` – `06_Archive/`).
- Flag statuses: `dead | live | wrong | superseded | unverifiable`.
- Ambiguous or conflicting sources → mark `needs_recheck` for the Editor's
  targeted recheck — never guess.
- May launch parallel subagents to cover many URLs/claims at once.
- Output: `{url_or_claim, status, issue, recommended_action}`.
- Report ≤250 lines (including grouped/multi-file findings); consolidate.

### 2. Editor (`pkm-editor`)

- The only agent in the loop that edits files (`edit: allow`).
- Apply fixes for **confirmed** issues from the Researcher's findings only.
- Every single change cites its justification: a **source** (URL or `./`
  repo-relative path) or a **rule** from the relevant AGENTS.md — never
  silently.
- Output status: `applied | deferred | needs_input`.
- **Ambiguous changes are never applied directly:**
  1. Send the ambiguity back to the Researcher for a targeted recheck.
  2. Apply if the recheck resolves it.
  3. Still ambiguous → ask the user via the `question` tool before touching
     the file.
- Question policy: the only agent with `question: allow`; ask one bounded
  question per ambiguity, never batch unrelated questions.
- No `webfetch` — verification is the Researcher's job.

### 3. Overview (`pkm-overview`)

- Check the file sits in the correct section/folder for its topic
  (`01_Ideas/`, `02_Knowledge/`, `03_Research/`, `04_ADRs/`,
  `05_Implementations/`, `06_Archive/`).
- Assess whether content belongs as a Knowledge note, in Research, or only in
  a specific Implementation.
- Flag misplaced, homelab-irrelevant, or not-worth-keeping content; confirm
  the file is coherent, complete, and actionable for its section.
- Output: `section_fit` (`correct|misplaced|unsure`), `homelab_fit`
  (`relevant|out-of-scope|unsure`), `concerns[]`.
### 4. Compliance (`pkm-compliance`)

- Re-read the relevant section AGENTS.md
  (`./01_Ideas/AGENTS.md` … `./06_Archive/AGENTS.md`) plus root `AGENTS.md`.
- Check missed conventions: required frontmatter fields, allowed status
  values, lowercase kebab-case tags, ISO 8601 dates, the 150-line atomic file
  rule, `./`-relative cross-links, section structure, template usage.
- Report only issues the other agents missed — do not re-report what they
  already caught.
- Output: `{rule, missed_by: researcher | editor | overview, fix_needed}`.

## Workflow

### 1. Gather targets

- Take target file path(s) from the user: a **single** file or a **batch**
  (list or glob).
- If no targets are given or the paths don't exist, stop and ask the user —
  do not invent targets.
- Batch mode: launch a loop per file **in parallel** for speed.

### 2. Loop (per file)

- Run all four agents in order: Researcher → Editor → Overview → Compliance.
  Never skip an agent. Post each agent's findings to the main chat.
- **Max loop count:** 10 per file.
- **Early stop:** after **7 consecutive clean loops** (no edits made and the
  compliance agent found nothing), ask the user via the `question` tool:
  **Keep looping** (continue to max 10) / **Stop all** (end every file's loop)
  / **Just this file** (stop only this file's loop).

### 3. Ambiguity handling

When the Editor cannot confirm a change (wrong URL, unclear claim, conflict):

1. Send it back to the Researcher for a targeted recheck.
2. Apply if resolved.
3. Still ambiguous → ask the user via the `question` tool. Never guess.

## Edge cases

| Case | Behavior |
|---|---|
| Empty / invalid target list | Stop and ask the user — never invent targets |
| URL can't be fetched | Researcher marks it `unverifiable`, not `live` — no fabrication |
| Editor blocked on a fix | Recheck → `question` tool → stay `deferred` until answered |
| All-clean from loop 1 | Still run to the 7-loop early-stop question |

## Report

After the final loop, print a consolidated report per file:

- applied changes with their sources/rules
- remaining issues (incl. any deferred as ambiguous / answered by the user)
- section/homelab fit concerns
- missed-rule findings from the compliance agent
- per-loop progress (what changed in each loop)

## Guardrails

- **Validation only** — fix issues in existing files; never create new notes
  or write content from scratch.
- Never guess (ambiguous → recheck → `question` tool) or fabricate
  verification results/citations.
