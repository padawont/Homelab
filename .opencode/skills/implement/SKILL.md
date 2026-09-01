---
name: implement
description: >
  Per-stage writer. Launches ONE Writer subagent (pkm-editor as Writer) per
  planned file IN PARALLEL to create the stage files from the plan file's
  file list + verified sources + Templates/ + section AGENTS.md. After all
  writers finish, marks TODOs done and reports to RuneSmith for the separate
  loop-validation step. Use for creating Knowledge, Research, ADR, and
  Implementation files.
---

# implement

Stage writer executed by RuneSmith. Produces the actual PKM files from the
plan's big chunk and verified sources, in parallel.

## When to use

- After research verified a stage's sources (or for Idea/S1, after
  foundation).
- When stage files need to be created or edited from the plan.

## When NOT to use

- Stage not researched (run research first — except Idea/S1).
- No plan file (run foundation first).
- Validating content (loop-validation is a separate RuneSmith step).

## Workflow

1. Load the plan file; read THIS stage's file list + verified sources.
2. For each planned file, launch ONE Writer subagent in parallel:
   - copies the matching template from `Templates/`
   - sets frontmatter per the section AGENTS.md
   - labels anything not-yet-deployed `Example — abstract`
   - cross-links with `./`-relative paths
   - keeps every file ≤150 lines
   - cites verified sources or plan references only — no fabrication
   - touches ONLY files within the current stage scope
3. Wait for ALL writers to finish before proceeding.
4. Mark the stage's main TODO and its `[Sx-name]` side TODOs done.
5. Report files written to RuneSmith, then STOP. Do NOT run loop-validation
   yourself — RuneSmith launches it as a separate step. Delete the plan file
   only when RuneSmith confirms the FINAL stage is done.

## Writer role contract (no new agent file — bind existing subagent)

- Behavior: creates/edits the stage file(s) exactly per the plan file +
  verified sources + Templates/ + section AGENTS.md (see workflow step 2).
- Permissions when launched: read/edit/glob/grep allow; question deny.
- Map to: `pkm-editor` (edit-capable) instructed as Writer for new content,
  or any edit-capable subagent RuneSmith prefers.

> [!IMPORTANT]
> Writers only touch files within the current stage scope, and every claim
> must cite a verified source or plan reference — no fabrication.

## Guardrails

- Do NOT load or chain loop-validation or research — RuneSmith drives.
- Do NOT load rs-* skills.
- Only edit files within the current stage scope.
- Every claim must cite a source or plan reference — no fabrication.
- Writers are launched in parallel, one per file; never one writer for the
  whole stage.
- The plan file is session-scoped: deleted only when RuneSmith confirms the
  pipeline fully completes.
