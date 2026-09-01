---
name: research
description: >
  Per-stage source verification. For each planned file, launches one
  pkm-researcher subagent IN PARALLEL to webfetch-verify every candidate
  source (official docs + GitHub), classifies live|dead|wrong|unverifiable,
  drops dead/wrong/unofficial, and records the final per-file URL list in
  the plan file. READ-ONLY on content. Use after foundation, before
  implement, per stage. (Idea/S1 stages skip research.)
---

# research

Source verifier executed by RuneSmith. Pins reliable sources for every
planned file so `implement` writers can cite them.

## When to use

- Immediately after foundation wrote the stage big chunk, before implement.
- A stage's planned files need their candidate sources verified and pinned.

## When NOT to use

- No plan file for this stage (run foundation first).
- Writing content (implement).
- Validating written content (loop-validation).

## Workflow

1. Load the plan file; read THIS stage's big chunk + candidate source list.
2. For each planned file, launch ONE `pkm-researcher` subagent in parallel:
   - webfetch every candidate source (official docs + GitHub only)
   - classify each: `live | dead | wrong | unverifiable`
   - return `{file, sources[{url, status, notes}]}`
3. Aggregate all results; drop dead, wrong, and unofficial; keep the rest.
4. Update the plan file — final per-file source list + status.
5. Report source counts + dropped sources to RuneSmith, then STOP. Do NOT
   load implement — RuneSmith drives the next step.

> [!NOTE]
> The recorded source list per file is the hand-off contract for
> `implement` — writers cite only these.

## Guardrails

- Do NOT load or chain implement — RuneSmith drives.
- Do NOT load rs-* skills.
- Do NOT edit or write any content file — only the plan file.
- Allowed: read, glob, grep, task (parallel researchers), plan-file edits.
- Never fabricate a verification result — unverifiable stays marked.
