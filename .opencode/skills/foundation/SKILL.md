---
name: foundation
description: >
  Entry-point skill for ONE GitHub issue and ONE pipeline stage. Lays
  groundwork only: audits the current stage, checks its GitHub sub-issue,
  writes the .opencode/plans/ plan file with a big-chunk section, emits a
  structured brief to RuneSmith, then STOPS. Never writes stage content,
  never auto-chains, never plans downstream stages. Use when starting (or
  re-entering) a single issue's next stage before any content exists.
---

# foundation

Read-only groundwork layer executed by RuneSmith. Sets up ONE stage of ONE
issue so `research` and `implement` can consume the plan file.

## When to use

- Starting or re-entering a single GitHub issue's next stage.
- No plan file exists yet for this issue + stage.
- The user asks "set up groundwork for issue #N, stage Sx".

## When NOT to use

- Writing/verifying stage content (research, implement, loop-validation).
- More than one issue or more than one stage in scope — stop and ask.
- A plan file for this stage already exists (mid-pipeline re-entry goes
  straight to research or implement).
- rs-* software tasks — foundation is PKM-only.

## Workflow

1. Confirm scope — ONE issue + ONE stage (user-specified, or auto-detect
   the first unstarted stage for the issue). If scope includes multiple
   issues or stages, stop and ask the user via `question` — never fan out.
2. Stage audit — for THIS stage only, list existing artifacts
   (repo-relative paths) and gaps in a status table. Downstream stages get
   a single `follow-up` line each — no TODOs, no plan sections.
3. Missing sub-issue check — if this stage lacks its GitHub issue, WAIT-ONLY:
   print ready-to-paste sub-issue info (title, body, parent epic, dependency
   order — load create-github-issues for structure only, never run gh), then
   pause until the user confirms filing in another session.
4. Candidate sources — list official docs + GitHub repo URLs per planned
   file. Do NOT webfetch — verification is research's job.
5. Broad TODO — one main todo for this stage.
6. Write plan file `.opencode/plans/{issue}-{topic}.md`:
   - one big-chunk section for THIS stage: deliverable, file list, concept
     per file, dependencies, candidate sources.
   - inline `Skills:` line — `research → implement → loop-validation`
     (Idea/S1: `implement → loop-validation`).
   - one row in the top-of-file execution table (Sx | topic | skills chain).
   - downstream stages as `follow-up` lines only.
7. Emit the brief to RuneSmith and STOP. Report as structured YAML (stage,
   file list, plan-file path, next skill to load). Do NOT load research
   yourself — RuneSmith decides and drives.

> [!IMPORTANT]
> Never create GitHub issues yourself. If the stage lacks one, the pipeline
> pauses until the user files it in another session — no skip path.

> [!NOTE]
> The plan file is the hand-off contract: foundation writes the big chunk,
> `research` appends verified sources, `implement` consumes both. All
> chaining is done by RuneSmith, never by this skill.

## Guardrails

- Do NOT load or chain research/implement — RuneSmith drives.
- Do NOT load rs-* skills.
- Do NOT edit or write any file EXCEPT the plan file. Allowed: read, glob,
  grep, todowrite, question.
- Do NOT create GitHub issues — wait for the user.
- Do NOT create stage content — that is research → implement's job.
- Do NOT webfetch — source verification moved to research.
- Downstream stages are follow-up lines only; re-run foundation later for
  the next stage.
