---
name: implement
description: >
  Per-stage writer that runs independently of research. For each planned file,
  launches ONE Writer subagent (pkm-editor as Writer) IN PARALLEL to create
  the stage files from the stage big chunk + available references + Templates/
  + section AGENTS.md. When research ran, each writer cites only its own
  file's verified list; otherwise it falls back to plan references marked
  unverified. Marks stage TODOs done and reports to RuneSmith for the
  separate loop-validation step. Idea/S1 writes straight from the plan.
---

# implement

Stage writer executed by RuneSmith. Produces the actual PKM files from the
plan's big chunk and, when available, the reference list `research` verified
for each file. `implement` and `research` are modular — each can run without
the other.

> Agent handoff model: the Writer fan-out is Flow D (parallel batch) — see
> `./.opencode/WORKFLOW.md`.

## When to use

- After research verified a stage's sources, before loop-validation.
- Standalone, to write a stage from plan references when research did not run.
- Idea/S1 stages: immediately after foundation (research is skipped).

## When NOT to use

- The user has declined implementation — do not run.
- No plan for this stage in the session (run foundation first).
- Verifying sources (research) or validating written content (loop-validation).

## Modularity

- `implement` never requires `research` to have run — it can write from plan
  references alone (marked `unverified`).
- When research ran, writers cite only the verified list it produced.
- Default pipeline order is `research → implement`; neither hard-depends on
  the other.

## Inputs (from RuneSmith in the main chat)

- Stage big chunk: deliverable, concept per file, dependencies.
- The verified per-file reference list from research (`kb | online | plan-only`)
  — optional; if research did not run, use plan references only.
- Matching template path from `Templates/`.
- Section AGENTS.md for the target folder (frontmatter spec, structure).

## Workflow

1. For each planned file, launch ONE Writer subagent (`pkm-editor`
   instructed as Writer) in parallel. Each Writer receives ONLY its own
   file's verified reference list (or plan references if research did not
   run) plus the plan:
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

## Per-file writer contract

- Writer N is launched with research's verified list for file N directly —
  the orchestrator never aggregates references across files before handing
  them over.
- If research is running, writers never draft a file whose verification has
  not completed.
- If a file has no verified sources (research skipped, or all sources dead),
  the Writer:
  1. writes the file using only plan references, each marked `unverified`
  2. notes every unverified claim in its report so loop-validation can
     re-check them
  3. never cites a dead, wrong, or unverifiable URL as if it were live
- Cross-file consistency: Writers may read sibling files from earlier stages
  to match wording and link targets, but only edit files within the current
  stage scope.

## Role contract (no new agent file — bind existing subagent)

### Writer (`pkm-editor` instructed as Writer)

- Behavior: creates the stage file per the plan + its own file's verified
  references + Templates/ + section AGENTS.md.
- Permissions when launched: read/edit/glob/grep; instructed NOT to use the
  question tool — unresolved ambiguity goes into the report, never a
  mid-write prompt.
- Every claim cites a verified source, plan reference, or AGENTS.md rule.
- Output: `{file, status, claims_unverified[], flags[]}`.

## Edge cases

| Case | Behavior |
|---|---|
| Research did not run | Write from plan references only, each marked `unverified` |
| All candidate sources dead | Research reported `dead`; Writer writes from plan refs marked `unverified` |
| Idea/S1 stage | No research step; Writers use plan references only |
| One writer fails | Wait for the rest, report the failure to RuneSmith — do not relaunch silently |
| Source verified but content irrelevant | Research marked it `wrong`; Writer must not cite it |

## Guardrails

- Modular: runnable alone from plan references; never requires research.
- Do NOT run when the user declines implementation.
- Do NOT load or chain foundation, research, or loop-validation — RuneSmith drives.
- Do NOT load rs-* skills.
- Only edit files within the current stage scope.
- Every claim must cite a verified source, plan reference, or AGENTS.md rule — no fabrication.
- Writers are launched in parallel, one per file; never one writer for the whole stage.
- The plan is session-scoped in the main chat — no file is written or deleted.
