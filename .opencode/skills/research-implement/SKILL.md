---
name: research-implement
description: >
  Per-stage builder. For each planned file, launches a pkm-researcher to
  verify THAT file's candidate sources (official docs + GitHub), then
  launches a pkm-editor as Writer for the SAME file citing only the verified
  sources — one researcher→writer pair per file, all pairs IN PARALLEL.
  Merges the old research + implement skills. Idea/S1 stages skip research
  and write straight from the plan. After all writers finish, marks TODOs
  done and reports to RuneSmith for the separate loop-validation step.
---

# research-implement

Stage builder executed by RuneSmith. Produces the actual PKM files from the
plan's big chunk by pairing one Researcher and one Writer per planned file,
so verification and writing are coupled per file instead of chained as two
whole-stage passes.

## When to use

- After foundation wrote the stage big chunk, before loop-validation.
- A stage's files need their candidate sources verified and written.

## When NOT to use

- No plan for this stage in the session (run foundation first).
- Validating written content (loop-validation is a separate RuneSmith step).

## Inputs (from RuneSmith in the main chat)

- Stage big chunk: deliverable, concept per file, dependencies.
- Per-file candidate sources (official docs + GitHub only).
- Matching template path from `Templates/`.
- Section AGENTS.md for the target folder (frontmatter spec, structure).

## Workflow

### Phase A — Verify (skip entirely for Idea/S1)

1. For each planned file, launch ONE `pkm-researcher` subagent in parallel:
   - webfetch every candidate source for that file (official docs + GitHub)
   - classify each: `live | dead | wrong | unverifiable`
   - if a candidate URL is dead/wrong, note the working replacement if one
     is found while fetching
   - return `{file, sources[{url, status, notes}], flags[]}`
2. Wait for ALL researchers before moving to Phase B.
3. Aggregate per-file: keep `live`; drop `dead` and `wrong`; keep
   `unverifiable` marked so Writers never cite it as verified.

### Phase B — Write

1. For each planned file, launch ONE Writer subagent (`pkm-editor`
   instructed as Writer) in parallel. Each Writer receives ONLY its own
   file's verified source list plus the plan references:
   - copies the matching template from `Templates/`
   - sets frontmatter per the section AGENTS.md
   - labels anything not-yet-deployed `Example — abstract`
   - cross-links with `./`-relative paths
   - keeps every file ≤150 lines
   - cites verified sources or plan references only — no fabrication
   - touches ONLY files within the current stage scope
2. Wait for ALL writers to finish before proceeding.
3. Mark the stage's main TODO and its `[Sx-name]` side TODOs done.
4. Report files written to RuneSmith, then STOP. Do NOT run loop-validation
   yourself — RuneSmith launches it as a separate step.

## Per-file pairing contract

- Writer N is launched with Researcher N's verified source list directly —
  the orchestrator never aggregates sources across files before handing them
  over. This is what lets research and implement agents work together per
  file instead of as two sequential passes.
- Writers wait for their file's verified sources; they never draft before
  verification completes.
- If a file has zero verified sources, the Writer:
  1. writes the file using only plan references, each marked `unverified`
  2. notes every unverified claim in its report so loop-validation can
     re-check them
  3. never cites a dead, wrong, or unverifiable URL as if it were live
- Cross-file consistency: Writers may read sibling files from earlier stages
  to match wording and link targets, but only edit files within the current
  stage scope.

## Role contracts (no new agent files — bind existing subagents)

### Researcher (`pkm-researcher`)

- Behavior: webfetch-verify ONE file's candidate sources and classify them.
- Permissions: read/glob/grep/webfetch; read-only — never edits.
- Never fabricates a result: unreachable URLs are `unverifiable`, not `live`.
- Output: `{file, sources[{url, status, notes}], flags[]}`.

### Writer (`pkm-editor` instructed as Writer)

- Behavior: creates the stage file per the plan + its own file's verified
  sources + Templates/ + section AGENTS.md.
- Permissions when launched: read/edit/glob/grep; instructed NOT to use the
  question tool — unresolved ambiguity goes into the report, never a
  mid-write prompt.
- Every claim cites a verified source, plan reference, or AGENTS.md rule.
- Output: `{file, status, claims_unverified[], flags[]}`.

## Edge cases

| Case | Behavior |
|---|---|
| All candidate sources dead | Researcher reports `dead`; Writer writes from plan refs marked `unverified` |
| Candidate URL moved | Researcher records the working replacement during fetch |
| Idea/S1 stage | Phase A skipped; Writers use plan references only |
| One writer fails | Wait for the rest, report the failure to RuneSmith — do not relaunch silently |
| Source verified but content irrelevant | Researcher marks `wrong` and flags it — Writer must not cite it |

## Guardrails

- Do NOT load or chain foundation or loop-validation — RuneSmith drives.
- Do NOT load rs-* skills.
- Idea/S1: skip Phase A; Writers cite plan references only.
- Researchers are read-only; only Writers edit files.
- Never fabricate a verification result — unverifiable stays marked.
- Writers are launched in parallel, one per file; never one writer for the
  whole stage.
- The plan is session-scoped in the main chat — no file is written or
  deleted; RuneSmith carries it between stages.
