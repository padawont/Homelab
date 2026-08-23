---
name: rs-ask-human
description: >
  Leaf meta-skill for specialists needing human input: decide whether the
  gap truly requires the human, craft one precise bounded question per gap,
  and emit a structured needs_input payload for RuneSmith to relay verbatim.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: manual+chained
---

## Purpose

`rs-ask-human` is the specialist-side contract for routing human questions
to the orchestrator. When a specialist cannot resolve a gap through its own
analysis or `rs-consult`, it uses this skill to emit a structured
`needs_input` payload. RuneSmith relays the questions to the human and
relaunches the specialist with the answers.

It exists because specialists NEVER use the `question` tool (their
`question` permission is `deny`). Only RuneSmith talks to the human.

## When to Invoke

Triggered reactively when a specialist hits a gap that only a human can
resolve:

1. **Ambiguous requirement** — the request can be read multiple ways and the
   choice materially changes the output.
2. **Missing decision** — a choice the human must own (e.g., "cookie or
   header?", "S3 or GCS?").
3. **Conflicting requirements** — two requirements cannot both be satisfied;
   the human must arbitrate.
4. **Blocked by policy/taste** — a preference, constraint, or trade-off the
   specialist is not authorized to choose.

Do NOT invoke when:

- The gap is a knowledge gap resolvable via `rs-consult` or webfetch.
- The gap is derivable from the codebase (read/grep/glob).
- The specialist can proceed with a documented, safe default (state the
  assumption instead).

## Workflow Steps

### Step 1: Confirm the human-gap

Verify the gap genuinely needs a human:

1. Can it be answered from the codebase, docs, or web? → No payload; resolve it.
2. Can `rs-consult` resolve it? → Try consult first; fall back here if not.
3. Is a safe documented default acceptable? → Use the default and record it.

If none of these apply, the gap is a human-gap. Proceed.

### Step 2: Craft one precise question per gap

Decompose a vague gap into specific, answerable sub-questions:

- One question per gap — no compound or multi-part questions.
- State the decision surface: the options and what each implies.
- Include enough context for a human to answer without rereading your whole
  session.

### Step 3: Emit the `needs_input` payload

Return structured YAML and STOP. Do not continue working while blocked.

```yaml
needs_input:
  recipient: runesmith
  source: <this agent name>
  questions:
    - id: q1
      question: "Should the auth token live in a cookie or header?"
      context: "Blocking spec stage; affects rs-spec-writer output"
      blocking: true
    - id: q2
      question: "Which cloud storage backend should the new feature target?"
      context: "Affects rs-devops deployment config"
      blocking: false
```

## Output Format

The `needs_input` payload is the ONLY output of this skill. Fields:

| Field      | Required | Meaning                                                       |
| ---------- | -------- | ------------------------------------------------------------- |
| `recipient`| Yes      | `runesmith`                                                   |
| `source`   | Yes      | The agent emitting the payload (e.g. `rs-spec-writer`)        |
| `questions[].id`      | Yes      | Unique identifier per question (`q1`, `q2`, ...)   |
| `questions[].question`| Yes      | Precise, bounded, single question                    |
| `questions[].context` | Yes      | Why it is needed and what it blocks                  |
| `questions[].blocking`| Yes      | `true` = pipeline halts until answered; `false` = can proceed |

## Rules

- Never ask what can be derived from the codebase, docs, or web.
- Never guess or fabricate a fallback answer when blocked.
- Always attach `source` so RuneSmith knows which specialist to relaunch.
- One question per gap; cap questions per payload (typically ≤ 3).
- Mark genuinely blocking questions `blocking: true`; optional clarifications
  `blocking: false`.
- Do NOT use the `question` tool — ever. Only emit the payload.

## Required Permissions

| Tool | Required | Scope                  | Purpose                                   |
| ---- | -------- | ---------------------- | ----------------------------------------- |
| read | No       | —                      | Re-reading context to confirm the gap (optional) |
| question | No   | —                      | NEVER used — the payload routes through RuneSmith |

The skill itself needs no special permissions; it only produces a YAML
return value. The consuming specialist's existing read/analysis permissions
suffice.

## Chained Skills

| Skill | When to Chain | Purpose |
| ----- | ------------- | ------- |
| rs-consult      | Before emitting, if the gap is a knowledge gap | Resolve without the human if possible |
| rs-human-responds | Downstream, consumed by RuneSmith          | RuneSmith relays the payload verbatim and relaunches |

## See Also

- `rs-human-responds` — RuneSmith-side faithful-answer contract (the consumer)
- `rs-consult` — Try this first for knowledge gaps
- RuneSmith agent — the orchestrator that routes questions to the human
- Session–Subagent Boundary — subagents never interact with the user directly
  (sibling knowledge-base repo at `knowledge/tooling/opencode/skills/session-subagent-boundary.md`)
