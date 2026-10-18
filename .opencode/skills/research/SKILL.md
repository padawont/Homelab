---
name: research
description: >
  Per-stage source verification that runs independently of implement. Checks
  the local KB first (target file + its own folder only); if the KB already
  covers a claim it uses that and skips the web. Otherwise fetches exactly
  ONE authoritative source per planned file (official docs or GitHub) and
  reports the confirmed per-file list back to RuneSmith. READ-ONLY. Use after
  foundation, standalone or before implement. Skipped for Idea/S1 and when
  the user declines implementation in a pipeline run.
---

# research

Source verifier executed by RuneSmith. Pins reliable sources for every
planned file so `implement` writers can cite them. `research` and `implement`
are modular — each can run without the other.

> Agent handoff model: `reviewer` (`source`) returns JSON to the hub — see
> `./.opencode/WORKFLOW.md`.

## When to use

- After foundation assembled the stage big chunk, when a stage's planned
  files need their sources verified and pinned.
- Standalone, to pin sources for files without writing them.

## When NOT to use

- The user has declined implementation in this pipeline run — skip research
  for the run (it stays runnable standalone if the user asks for sources).
- Idea/S1 stages — no external sources.
- No plan for this stage in the session (run foundation first).
- Writing content (implement), or validating written content (loop-validation).

## Modularity

- `research` never requires `implement` to follow.
- `implement` can run from plan references alone when research has not run.
- Default pipeline order is `research → implement`; neither hard-depends on
  the other.

## Related skill — knowledge-gap-research

This skill pins sources; it does not judge whether the Knowledge needed to
build, change, or operate the service is complete. While working this topic,
load `knowledge-gap-research` to turn every fact that had to be sourced online
into a standardized Knowledge gap (and, on confirmation, an epic or single
issue). It is not a standalone Knowledge-base audit.

## Inputs (from RuneSmith in the main chat)

- Stage big chunk: deliverable, concept per file, dependencies.
- Per-file candidate: ONE authoritative link per file (official docs or GitHub).

## Workflow

### Phase 1 — KB first (always)

1. For each planned file, check the local knowledge base BEFORE any webfetch.
2. KB scope is tight: the target file itself plus sibling files in the same
   folder. Do NOT search the wider repo, other sections, or other folders.
3. If the KB already covers the file's needed facts, pin those KB paths as
   the sources and skip the web for that file.

### Phase 2 — One online source (only if the KB is insufficient)

1. For each file the KB did not fully cover, fetch its ONE candidate source.
2. Classify it: `live | dead | wrong | unverifiable`.
3. If dead/wrong, record a working replacement only if the SAME website
   yields one — do not open a second website.
4. Return `{file, source {url, status, notes}, kb_refs[], flags[]}`.

### Report

Aggregate per file: source origin (`kb | online | plan-only`), status, and
the pinned references. Report to RuneSmith, then STOP. Do NOT load implement
— RuneSmith drives the next step.

> [!NOTE]
> The reported per-file reference list is the hand-off contract for
> `implement` — writers cite only these, never a dead, wrong, or
> unverifiable URL.

## Role contract (no new agent file — bind existing subagent)

### Reviewer (`reviewer`, `source` type)

- Behavior: check the KB (target file + same folder) first; fetch ONE source
  per file only when the KB does not fully cover it.
- Permissions: read/glob/grep/webfetch; read-only (`edit: deny`) — never edits.
- Never fabricates a result: unreachable URLs are `unverifiable`, not `live`.
- Bound to the `source` type only: the reviewer's JSON `source` findings
  (`severity`, `issue`, `evidence`, `fix_hint`) are this skill's verification
  result; the other four type keys come back empty.
- Output: `{file, source {url, status, notes}, kb_refs[], flags[]}`.

## Edge cases

| Case | Behavior |
|---|---|
| KB fully covers the file | Pin KB paths as sources; no web lookup |
| KB partially covers the file | Use KB for covered facts; ONE online source for the rest |
| All sources dead | Report `dead`; implement writes from plan refs marked `unverified` |
| One online source irrelevant | Mark `wrong`; do NOT open a second website — fall back to plan refs |
| Candidate URL moved | Record a replacement only from the same website |
| No candidate source for a file | KB-only; otherwise plan refs |

## Guardrails

- Modular: runnable alone; never requires `implement` to follow.
- Skip research in a pipeline run when the user declines implementation.
- Default successor is `implement`.
- KB first — never webfetch before checking the local KB.
- KB scope = target file + its own folder; never search the wider repo.
- At most ONE external link/website per planned file.
- Never open a second website to replace a dead/wrong source.
- READ-ONLY: never edit or write any content file.
- Do NOT load or chain foundation, implement, or loop-validation — RuneSmith drives.
- Do NOT load rs-* skills.
- Idea/S1: skip research entirely.
- Never fabricate a verification result — unverifiable stays marked.
- The plan is session-scoped in the main chat — no file is written or deleted.
