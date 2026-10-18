---
name: loop-validation
description: >
  Validates and fixes Homelab PKM content by looping the Flow D lane — worker
  (producer, skipped when the file already exists), reviewer (one JSON report
  across all five types: source, accuracy, scope, structure, overlap), and
  editor (applies confirmed fixes with source/rule justification) — until clean
  or a user-chosen loop count. For VALIDATION ONLY: fixing issues in existing
  files/issues, never creating new notes or content from scratch.
---

# loop-validation

> Agent handoff model: this loop is Flow D (parallel batch) — see
> `./.opencode/WORKFLOW.md`. Each lane is `worker -> reviewer -> editor`,
> hub-owned; no spoke ever calls another spoke.

## When to use

- A user asks to validate/fix an existing PKM file or a set of files.
- A PKM issue needs fact-checking against online sources and repo notes.
- Content needs a section-fit and homelab-fit review before acceptance.

## When NOT to use

- Capturing a new idea, writing a new note, or drafting research from scratch
  (use the normal capture pipeline).
- Non-PKM content (application code, infra configs) — PKM content only.

## Loop model

One lane per file, fixed order, never skipped:

```
worker -> reviewer (JSON) -> editor   (repeat, max 10)
```

| Step | Subagent | Focus |
|---|---|---|
| Producer | `worker` | Drafts/repairs the file from the hub's brief — **skipped in validation** (the file already exists; `N = 1` review) |
| Reviewer | `reviewer` | All five types → one JSON report, S1–S4 |
| Editor | `editor` | Confirmed findings only, each citing source/rule |

The **producer step is skipped**: validation works on existing files, so the
repeating loop is `reviewer -> editor`. `worker` runs only if the hub decides a
document must be produced — outside validation-only scope. The hub (main agent /
RuneSmith) owns the loop, aggregates the reports, and posts them per loop and in
the final report. No spoke launches another spoke.

## Agent detail

### Reviewer (`reviewer`)

- One invocation covers all five types; they are **sections of one JSON
  object**, not separate agents. The hub supplies the folder, target, and
  sibling drafts (for `overlap` only).
- Fetch and confirm every external `sources[]` / `references[]` URL is live
  (`webfetch`).

| type | question it answers | severity band |
|---|---|---|
| `source` | Is every cited URL live, authoritative, and does it actually say what's claimed? | S1–S2 |
| `accuracy` | Are commands, keys, defaults, ports and versions correct for *this* homelab? | S1–S2 |
| `scope` | Homelab-relevant, correct folder, right depth, no history/marketing? | S3 |
| `structure` | Frontmatter, status, kebab-case tags, ISO dates, 150-line rule, `./` links, heading order | S3–S4 |
| `overlap` | Duplicates or contradicts another note/ADR — link instead of repeat? | S4 |

- The five types absorb the former review passes: `source` (fact-check),
  `accuracy` (homelab correctness), `scope` (fit), `structure` (AGENTS.md
  rules), `overlap` (duplication).
- All five type keys are **always present**, even when empty. Every finding
  carries `severity`, `issue`, `evidence`, and `fix_hint`.
- `verdict` is `clean` (all types empty), `issues` (any finding), or
  `needs_recheck` (a finding that cannot be resolved without a guess).
- Judge `overlap` only against the sibling drafts the hub supplies — never
  reach across lanes, batches, or the wider repo.
- Read-only (`edit: deny`); never edits, never delegates, never asks the human.
- Ambiguous or conflicting sources → `needs_recheck`; never guess.

### Editor (`editor`)

- The only agent in the loop that edits files (`edit: allow`).
- Apply fixes for **confirmed** issues from the reviewer's JSON only.
- Every single change cites its justification: a **source** (URL or `./`
  repo-relative path) or a **rule** from the relevant AGENTS.md — never
  silently.
- Output status: `applied | deferred | unresolved`.
- A finding without evidence is not confirmed: report it as `unresolved` with
  `source_or_rule: "none — no citable source"`, never apply it.
- No `webfetch` — verification is the reviewer's job.
- **Ambiguity is reported, never resolved by guessing.** `question` is denied
  for the editor; escalation is the hub's call, not the editor's.

## Workflow

### 1. Gather targets

- Take target file path(s) from the user: a **single** file or a **batch**
  (list or glob).
- If no targets are given or the paths don't exist, stop and ask the user —
  do not invent targets.
- Batch mode: run one lane per file **in parallel** for speed.

### 2. Loop (per file)

- Run the lane in order: producer (**skipped** — the file exists) → reviewer →
  editor. Post the reviewer's JSON and the editor's change report to the main
  chat.
- **Max loop count:** 10 per file.
- **Early stop:** after **7 consecutive clean loops** (every type empty, verdict
  `clean`, no edits made), the hub asks the user via the `question` tool:
  **Keep looping** (continue to max 10) / **Stop all** (end every file's loop)
  / **Just this file** (stop only this file's loop).

### 3. Ambiguity handling

When the reviewer returns `needs_recheck`, or the editor cannot cite a finding
(wrong URL, unclear claim, conflict):

1. The editor reports it as `unresolved` (or `deferred`) — never a silent edit.
2. The hub decides: re-run the reviewer with a tighter brief, or escalate.
3. Still unresolved → the hub asks the user via the `question` tool. Never
   guess. (The editor cannot ask — `question: deny`.)

## Edge cases

| Case | Behavior |
|---|---|
| Empty / invalid target list | Stop and ask the user — never invent targets |
| URL can't be fetched | Reviewer marks the `source` finding `unverifiable`, not `live` — no fabrication |
| Editor can't cite a fix | Report `unresolved`/`deferred` → hub decides → hub asks the user |
| All-clean from loop 1 | Still run to the 7-loop early-stop question |

## Report

After the final loop, print a consolidated report per file:

- applied changes with their sources/rules
- remaining issues (incl. any deferred as ambiguous / answered by the user)
- scope/structure concerns from the reviewer's JSON
- per-loop progress (what changed in each loop)

## Guardrails

- **Validation only** — fix issues in existing files; never create new content.
- Never guess (ambiguous → `unresolved` → hub escalates) or fabricate results.
- **The editor never asks the human** — `question` is denied; the hub escalates.
- Keep the 10-loop cap and the 7-consecutive-clean early stop.
