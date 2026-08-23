---
name: rs-human-responds
description: >
  RuneSmith's faithful-answer contract: parse a specialist's needs_input,
  present each question to the human verbatim via the question tool, capture
  answers without paraphrase, and relaunch the source specialist with answers.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: chained
---

## Purpose

`rs-human-responds` is the orchestrator-side contract that keeps the human
the single decision-maker. When any specialist returns a `needs_input`
payload, RuneSmith loads this skill to relay the questions to the human —
verbatim, without paraphrase or agent opinion — capture the answers exactly
as given, and relaunch the requesting specialist with the answers appended.

This is the counterpart of `rs-ask-human` (specialist-side emit).

## When to Invoke

Triggered when RuneSmith receives a `needs_input` payload from any
specialist (rs-spec-writer, rs-developer, rs-reviewer, rs-test-writer,
rs-tech-writer, rs-devops, rs-debugger, rs-architect).

## Workflow Steps

### Step 1: Parse the payload

Read the `needs_input` YAML:

```yaml
needs_input:
  recipient: runesmith
  source: rs-spec-writer
  questions:
    - id: q1
      question: "Should the auth token live in a cookie or header?"
      context: "Blocking spec stage; affects rs-spec-writer output"
      blocking: true
```

Extract: `source` (which specialist to relaunch) and `questions[]`.

### Step 2: Present each question verbatim

For each question, present it to the human via the `question` tool:

- Include the question **verbatim** — no rewording, no simplification.
- Include the `context` as-is.
- If `blocking: true`, frame it as halting the pipeline until answered.
- Ask all questions in one gate where practical; per-question gates if they
  need separate decisions.

### Step 3: Capture answers exactly

Record the human's answers **verbatim** — no paraphrase, no reordering, no
summary, no agent interpretation. Map each answer to its question `id`.

### Step 4: Relaunch the source specialist

Relaunch the `source` specialist as a **fresh subagent** (no `task_id`
reuse) with:

1. The specialist's original context (stage, config, prior outputs)
2. A `human_answers` block mapping question ids to verbatim answers:

```yaml
human_answers:
  - id: q1
    answer: "cookie"
  - id: q2
    answer: "S3"
```

### Step 5: Loop until resolved

After relaunch, check the specialist's return:

- If it returns another `needs_input` → repeat from Step 1.
- If it returns a normal structured result → resume the pipeline stage.
- If `blocking: true` questions remain unanswered → do NOT proceed; block.

## Guardrails

- Never substitute RuneSmith's own answer for the human's.
- Never reinterpret, reorder, or summarize the human's answers.
- Never answer on the human's behalf to "keep the pipeline moving."
- Never modify the `source` — the relaunch target is exactly the specialist
  that asked.
- Block on `blocking: true`; proceed only when answered.
- Record answers for the pipeline transcript and `pipeline-state.yaml`
  `human_decisions` (binding for subsequent cycles).

## Required Permissions

| Tool     | Required | Scope                     | Purpose                                  |
| -------- | -------- | ------------------------- | ---------------------------------------- |
| question | Yes      | —                         | Present the human's questions and capture answers |
| task     | Yes      | `rs-*` (all specialists)  | Relaunch the source specialist with answers |
| read     | Yes      | `.runesmith/`             | Parse state and specialist output        |
| write    | Yes      | `.runesmith/`             | Record `human_decisions` in state        |

## Chained Skills

| Skill | When to Chain | Purpose |
| ----- | ------------- | ------- |
| rs-ask-human | Upstream producer | Specialists emit `needs_input` payloads |
| rs-scratchpad | On answer capture | Persist `human_decisions` in the session path |

## See Also

- `rs-ask-human` — specialist-side structured question emit (the producer)
- RuneSmith agent — owns this contract; the only agent with `question: allow`
- Human Gate Patterns — AskQuestion strategies and decision binding
  (sibling knowledge-base repo at `knowledge/tooling/opencode/skills/human-gate/overview.md`)
- Session–Subagent Boundary — subagents never decide; the session relays
  (sibling knowledge-base repo at `knowledge/tooling/opencode/skills/session-subagent-boundary.md`)
