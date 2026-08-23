---
name: rs-implementation-pipeline
description: >
  Planning aid for pipeline design. Conducts a 3-round, 9-question
  interview to produce pipeline-config.yaml. Defines stage ordering
  (TDD/non-TDD), gate placement, review cycle limits, severity
  thresholds, and artifact paths. RuneSmith orchestrates the interview,
  launches specialist agents directly per stage, runs gates and
  escalation, and maintains pipeline state.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: chained
---

## Purpose

The rs-implementation-pipeline skill is a planning aid for pipeline-based
development. It conducts a structured 3-round, 9-question interview with
the user to capture their project's implementation preferences, then
generates a `pipeline-config.yaml` that defines how RuneSmith executes the
pipeline.

Key characteristics:

- **Interview-driven**: Asks up to 9 questions across 3 rounds (Q1–Q4
  auto-detected by rs-discover, asked only as fallbacks). Each question maps
  directly to a field in `pipeline-config.yaml`.
- **Config-generating**: Produces a single YAML artifact —
  `pipeline-config.yaml` — that RuneSmith reads to determine stage
  order, gate placement, review cycle limits, and artifact paths.
- **Auto-detecting**: Chains rs-discover before Round 1 to detect
  language/framework, test/lint/build commands from the codebase. Q1–Q4
  are presented only as fallbacks when rs-discover cannot determine the
  answer.
- **TDD-aware**: Supports both TDD (test-first: spec → test → implement →
  review → docs) and non-TDD (implement-first: spec → implement → test →
  review → docs) stage orderings.
- **RuneSmith-orchestrated and RuneSmith-executed**: RuneSmith (the
  orchestrator / primary agent) owns interview flow, stage execution, human
  gate presentation, and escalation handling. It launches the drafter
  specialist and two independent reviewers directly per stage, runs the fix
  loop, validates gate conditions, and updates pipeline state. There is no
  intermediate orchestrator subagent — flat delegation only.
- **Human-gated**: Supports three gate strategies (`every_stage`,
  `end_only`, `custom`) that determine where human approval is required
  during pipeline execution. After each stage's gate validation, RuneSmith
  presents the human gate.
- **Question routing**: Specialists never talk to the human. If a specialist
  needs input it returns a `needs_input` payload (via `rs-ask-human`);
  RuneSmith presents it via the question tool and relaunches the specialist
  with verbatim answers (via `rs-human-responds`).

## When to Invoke

Trigger conditions:

- A new implementation session starts on a feature branch and RuneSmith
  needs a pipeline config before dispatching specialists.
- The user explicitly requests pipeline setup (e.g., "Set up an
  implementation pipeline for this feature").
- The active session lacks a `pipeline-config.yaml` and RuneSmith
  determines one is needed.
- After a significant change to project structure (new language, test
  framework, build system) invalidating an existing pipeline config.

Do NOT invoke when:

- A valid `pipeline-config.yaml` already exists for the current session
  and no project changes have occurred. RuneSmith should not auto-invoke
  when config exists. If the user explicitly requests reconfiguration,
  the skill detects the existing config and prompts for re-interview
  confirmation.
- The task is purely research or documentation with no implementation
  stages.
- The pipeline is already mid-flight.
- The user needs to modify a running pipeline mid-execution.

## Workflow Steps

### Interview Template — 3 Rounds, 9 Questions

The interview proceeds in 3 sequential rounds. RuneSmith presents questions
one at a time, records answers, and advances to the next round after all
questions in the current round are answered.

**Flow**: Round 1: Project Setup (Q1–Q4) → Round 2: Workflow Preference
(Q5–Q6) → Round 3: Pipeline Configuration (Q7–Q9) → Generate config →
Confirm with user.

| Q#  | Category                 | Question                                                                                                                                                                                       | Maps To                                                         | Type / Constraints                                                                                                                                                                |
| --- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q1  | Language & Framework     | "What language and framework does your project use? (e.g., Python/FastAPI, TypeScript/React, Rust/Axum) (Auto-detected via rs-discover; question is fallback only)"                                                                                       | Agent selection, tool configuration (auto-detected)                             | free-text string, must be non-empty                                                                                                                                               |
| Q2  | Test Framework & Command | "What test framework and command does your project use? (e.g., pytest tests/, bun test, cargo test) (Auto-detected via rs-discover; question is fallback only)"                                                                                           | Gate conditions (test gate), review_cycles (auto-detected)                      | free-text string, must be non-empty                                                                                                                                               |
| Q3  | Lint Command             | "What command do you use to run the linter? (e.g., ruff check ., eslint src/, cargo clippy) (Auto-detected via rs-discover; question is fallback only)"                                                                                                   | Gate conditions (implementation gate) (auto-detected)                           | free-text string, optional (empty = skip lint gate)                                                                                                                               |
| Q4  | Build/Compile Command    | "What command do you use to build or compile the project? (e.g., npm run build, cargo build, tsc) (Auto-detected via rs-discover; question is fallback only)"                                                                                             | Gate conditions (implementation gate) (auto-detected)                           | free-text string, optional (empty = skip build gate)                                                                                                                              |
| Q5  | TDD or Non-TDD           | "Do you want to use Test-Driven Development (TDD)? In TDD mode, tests are written before implementation."                                                                                      | `pipeline.strategy.tdd`                                         | boolean, default: `false` (non-tdd). Accepted values: `yes`/`no`, `true`/`false`, `tdd`/`non-tdd`, `y`/`n`, and suffixed forms like `yes (tdd)`/`no (non-tdd)`. Case-insensitive. |
| Q6  | Stage Selection          | "Which stages should be included in the pipeline? Choose from: spec, implement, test, review, docs, deploy. Select at least 3."                                                                | `stages[]` membership                                           | multi-select, must include `spec`, ≥3 stages. If TDD=true, `test` must precede `implement`. See TDD vs Non-TDD Paths.                                                             |
| Q7  | Human Gate Placement     | "Where should human approval gates be placed? Options: every_stage (approval after each stage), end_only (approval only after all stages complete), or custom (you select specific stages)."   | `pipeline.gates.human.placement`                                | enum: `every_stage`, `end_only`, `custom`; default: `every_stage`. If custom: follow-up prompt lists selected stages for multi-select.                                                                                                                 |
| Q8  | Max Review Cycles        | "What is the maximum number of review cycles allowed before escalation? (1–20, default 10)"                                                                                                    | `pipeline.review.max_cycles`                                    | integer 1–20, default: 10                                                                                                                                                         |
| Q9  | Severity Thresholds      | "Which severity levels should the agent auto-fix, and which require human review? Default: S1–S3 auto-fix, S4–S5 human check. Accept or specify custom split (e.g., S1–S2 auto, S3–S5 human)." | `pipeline.review.auto_fix_severities`, `human_check_severities` | range expression, default: S1–S3 auto, S4–S5 human. Auto and human sets must be disjoint and cover all S1–S5.                                                                     |
#### Round 1: Project Setup (Q1–Q4 — Auto-Detected, Fallback-Only)

Captures the project's toolchain: language/framework, test runner, linter,
and build command. Before presenting any questions, RuneSmith chains
rs-discover to auto-detect answers from the codebase. Questions are only
presented as fallbacks when rs-discover returns `unknown` for the
corresponding field. If all four fields are detected, Round 1 may complete
without presenting any questions.

#### Round 2: Workflow Preference (Q5–Q6)

Determines TDD mode and which stages to include. TDD selection affects
stage ordering (see TDD vs Non-TDD Paths below). Stage selection determines
which agents are invoked and which gates apply.

#### Round 3: Pipeline Configuration (Q7–Q9)

Configures gate placement strategy, review cycle limits, severity
thresholds for auto-fix vs. human review, and the artifact storage path.

#### Post-Interview Confirmation

After all 9 questions are answered, present a summary of all responses
and ask for confirmation:

```
## Pipeline Configuration Summary

- **Language/Framework**: Python/FastAPI
- **Test Command**: pytest tests/ -v
- **Lint Command**: ruff check .
- **Build Command**: (none)
- **TDD**: No (implement first)
- **Stages**: spec → implement → test → review → docs
- **Gate Placement**: every_stage
- **Max Review Cycles**: 10
- **Severity Thresholds**: S1–S3 auto-fix, S4–S5 human check

Does this look correct? (yes/no)
```

If the user rejects, allow re-answering specific questions without
restarting the full interview.

### Pipeline Config Schema

The generated `pipeline-config.yaml` follows this annotated schema:

```yaml
schema_version: "1.0"
metadata:
  generated_at: "ISO 8601 timestamp"
  generator: "rs-implementation-pipeline@1.0.0"
  session: "{rs-scratchpad-session}/" # derived from rs-scratchpad session path convention

stages: # Ordered list from Q6, respecting TDD ordering
  - spec
  - implement # (or test if TDD)
  - test # (or implement if TDD)
  - review
  - docs

pipeline:
  strategy:
    tdd: false # boolean, from Q5

  gates:
    human:
      placement: "every_stage" # from Q7: every_stage | end_only | custom
      stages: [] # populated only when placement=custom

    conditions:
      pre:
        spec:
          requires_config: true
        implement:
          has_spec: true
        test:
          has_spec: true
          has_implementation: true
        review:
          has_all_outputs: true
        docs:
          has_all_outputs: true
        deploy:
          has_all_outputs: true
      post:
        spec:
          output_exists: true
        implement:
          output_exists: true
          lint_command: "" # from Q3, optional
          build_command: "" # from Q4, optional
          lint_on_fail: "warn"
          build_on_fail: "fail"
        test:
          output_exists: true
          test_command: "" # from Q2
          test_on_fail: "fail"
          coverage_threshold: 0.0 # float 0.0-1.0; 0.0 disables coverage checks
          coverage_on_fail: "warn"
        review:
          output_exists: true
          max_findings_s1: 0
          max_findings_s2: 5
        docs:
          output_exists: true

  review:
    max_cycles: 10 # from Q8
    auto_fix_severities: # from Q9
      - S1
      - S2
      - S3
    human_check_severities: # from Q9
      - S4
      - S5
    fresh_invocation: true # each cycle uses fresh subagent
    recurrence:
      max_count: 3 # appearances before escalation
      window: "all" # "all" = across all cycles within the current stage; also supports "sliding-N"

  analysis:
    plan_review: "on_demand" # on_demand | off. RuneSmith launches rs-architect
                             # for plan review on complex stages and escalation.

  artifacts:
    root: "{rs-scratchpad-session}/pipeline/" # derived from rs-scratchpad session path
    subdirectories:
      stages: "stages/"

stage_agent_map:
  spec:
    agent: "rs-spec-writer"
  implement:
    agent: "rs-developer"
    language: "" # from Q1
    framework: "" # from Q1
  test:
    agent: "rs-test-writer"
    test_framework: "" # from Q2
  review:
    agent: "rs-reviewer"
  docs:
    agent: "rs-tech-writer"
  deploy:
    agent: "rs-devops"

escalation:
  triggers:
    - type: conflict
      description: "Two review cycles produce contradictory findings about the same content area"
      action: ask_question # RuneSmith-handled: presents to human
    - type: recurrence
      description: "Same finding appears in 3+ cycles within a single stage"
      action: return_failed # RuneSmith-handled: returns failed to user
    - type: adjudication
      description: "Reviewer conflict or a trade-off beyond reviewer scope; needs-discussion status"
      action: ask_question # RuneSmith-handled: presents to human
    - type: cycle-exhaustion
      description: "A stage exhausts its maximum review cycles without passing all gates"
      action: return_failed # RuneSmith-handled: returns failed to user
  question: true # global enable flag for RuneSmith-handled AskQuestion triggers (conflict, adjudication). When false, all escalations use return_failed and no AskQuestion is presented.
```

### TDD vs Non-TDD Paths

**TDD Path** (`pipeline.strategy.tdd: true`):

```
spec → test → implement → review → docs
```

Tests written **before** implementation (red → green → refactor).

| Stage     | Pre-condition                      | Post-condition                                |
| --------- | ---------------------------------- | --------------------------------------------- |
| spec      | Config exists                      | spec/output.md exists                         |
| test      | spec/output.md exists              | tests written and failing appropriately (red) |
| implement | spec/output.md exists, tests exist | all tests pass (green), lint/build pass       |
| review    | all prior outputs exist            | findings within thresholds                    |
| docs      | all prior outputs exist            | docs/output.md exists                         |

**Non-TDD Path** (`pipeline.strategy.tdd: false`, default):

```
spec → implement → test → review → docs
```

Tests written **after** implementation.

| Stage     | Pre-condition                              | Post-condition                         |
| --------- | ------------------------------------------ | -------------------------------------- |
| spec      | Config exists                              | spec/output.md exists                  |
| implement | spec/output.md exists                      | code compiles/builds, lint passes      |
| test      | spec/output.md + implement/output.md exist | all tests pass, coverage threshold met |
| review    | all prior outputs exist                    | findings within thresholds             |
| docs      | all prior outputs exist                    | docs/output.md exists                  |

`deploy` is always appended after `docs` if selected in Q6.

### Review Cycle Loop

Severity classification used across all review stages. The pipeline inherits
severity definitions from `rs-review-severity`; this table describes pipeline
handling behaviour per severity level. The default split shown below can be
customised via Q9.

| Severity | Definition                                          | Auto-Fix         | Merge-Blocking |
| -------- | --------------------------------------------------- | ---------------- | -------------- |
| S1       | Critical: security vulnerability, data loss, crash  | Yes              | Yes            |
| S2       | Major: incorrect behaviour, logic error             | Yes              | Yes            |
| S3       | Moderate: maintainability concern, minor logic gap  | Yes              | No             |
| S4       | Minor: style violation, naming nit, formatting      | No — human check | No             |
| S5       | Nitpick: suggestion, preference, future improvement | No — human check | No             |

Cycle rules:

1. **Max cycles**: Configurable via Q8 (default 10). When `cycle_count >=
max_cycles`, escalation triggers.
2. **Fresh subagents**: Each cycle invokes a fresh subagent. No `task_id`
   reuse.
3. **Auto-fix (S1–S3)**: RuneSmith re-launches the drafter agent to apply
   fixes without human intervention.
4. **Human check (S4–S5)**: Presented via `AskQuestion`. Pipeline pauses
   until human responds.
5. **Recurrence tracking**: Finding tracked across cycles. Appearance in
   3+ cycles triggers recurrence escalation.
6. **Input accumulation**: Each cycle receives the original spec, the
   latest code, all previous review findings, and the cycle number —
   so the reviewer can check whether earlier findings were addressed.

7. **Human decision binding**: Every decision a human makes through a gate
   or escalation is appended to all subsequent reviewer prompts as a
   `human_decisions` block. Reviewers must not re-flag settled findings;
   RuneSmith filters re-flagged findings from the fix list (logged as
   `already-decided-by-human`, does not increment recurrence).

The state file (`pipeline-state.yaml`) tracks each finding across cycles:

```yaml
findings:
  - id: "find-001"
    description: "SQL injection risk in user query"
    severity: S1
    first_seen_cycle: 0
    last_seen_cycle: 2
    appearance_count: 3
    status: "recurring"
```

When `appearance_count >= recurrence.max_count` (default 3), escalation triggers.

### Question Routing

Specialists never use the `question` tool. If a specialist needs human input
it returns a `needs_input` payload (per `rs-ask-human`):

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

RuneSmith loads `rs-human-responds`, presents each question to the human
via the question tool **verbatim**, captures answers, and relaunches the
`source` specialist (fresh subagent) with the answers appended. It loops
until no further `needs_input` remains and blocks on `blocking: true`.

### Plan Review (Deep Analysis)

When `pipeline.analysis.plan_review: on_demand`, RuneSmith launches
`rs-architect` (the deep-analysis / plan-review specialist) to review a
plan/spec before a complex stage executes, or as a second opinion during
escalation. `rs-architect` returns a verdict (`approve` / `revise` /
`reject`) + findings, which RuneSmith consumes like any gate input. A
per-stage `requires_analysis` flag can force review for specific stages.

### Gate Strategies

Three strategies control where human approval is required:

**`every_stage`** — Human gate after every stage. Pipeline pauses at each
stage boundary and presents a summary before proceeding.

AskQuestion example:

```json
{
  "question": "Gate: Stage 2 — implement complete",
  "context": "rs-developer has completed the implementation stage. Output: src/auth/login.ts (142 lines), tests/stage-2-implement/output.md.",
  "details": {
    "stage": "implement",
    "agent": "rs-developer",
    "files_changed": 3,
    "lint_passed": true,
    "build_passed": true
  },
  "options": [
    "Approve — proceed to test stage",
    "Reject — return to implement for revision",
    "Cancel pipeline"
  ]
}
```

**`end_only`** — Single human gate after the final stage. All stages run
autonomously; a final summary is presented for human sign-off.

AskQuestion example:

```json
{
  "question": "Gate: Pipeline complete — final review",
  "context": "All 5 stages completed. 0 S1 findings, 2 S2 findings (resolved), 4 S3 findings (auto-fixed), 1 S4 finding (pending).",
  "details": {
    "stages_completed": ["spec", "implement", "test", "review", "docs"],
    "total_cycles": 3,
    "unresolved_s4": 1,
    "unresolved_s5": 0
  },
  "options": [
    "Approve all — accept pipeline output",
    "Reject pipeline — discard all outputs",
    "Review individual stages"
  ]
}
```

**`custom`** — User selects which stages have human gates during Q7.
`pipeline.gates.human.stages` is populated with the selected stage names.

AskQuestion example (user selected gates at spec and review):

```json
{
  "question": "Gate: Stage 4 — review complete",
  "context": "rs-reviewer has completed the review stage. 0 S1 findings, 1 S2 finding, 3 S3 findings (auto-fixed), 2 S4 findings.",
  "details": {
    "stage": "review",
    "agent": "rs-reviewer",
    "s1_count": 0,
    "s2_count": 1,
    "s3_count": 3,
    "s4_count": 2,
    "s5_count": 0
  },
  "options": [
    "Approve — proceed to docs stage",
    "Reject — return to review for re-evaluation",
    "Accept S2, escalate S4 findings to human",
    "Cancel pipeline"
  ]
}
```

### Escalation Triggers

Escalation follows a **RuneSmith-handled model**: all triggers are processed
by RuneSmith, either by presenting to the human via `AskQuestion` or by
returning a structured `failed` summary.

| #   | Trigger          | Description                                                                          | Handled By    | Escalation Action                                                                 |
| --- | ---------------- | ------------------------------------------------------------------------------------ | ------------- | --------------------------------------------------------------------------------- |
| 1   | Conflict         | Two review cycles produce contradictory findings about the same content area.        | RuneSmith     | RuneSmith presents side-by-side comparison via `AskQuestion`.                     |
| 2   | Recurrence       | Same finding appears in 3+ cycles within a single stage.                             | RuneSmith     | RuneSmith returns `failed` status with recurrence details. May re-launch.         |
| 3   | Adjudication     | A trade-off beyond reviewer scope, or needs-discussion from a reviewer/rs-architect. | RuneSmith     | RuneSmith presents trade-off analysis via `AskQuestion`.                          |
| 4   | Cycle-Exhaustion | `cycle_count >= max_cycles` with unresolved S1–S3 findings.                          | RuneSmith     | RuneSmith returns `failed` status with summary of unresolved findings.            |

When RuneSmith detects recurrence or cycle-exhaustion, it writes the full
context to `gate-report.json`, sets the stage status to `failed`, and
presents the failure to the human (per gate placement strategy) or aborts
the pipeline.

### Artifact Layout

Pipeline artifacts are stored under the rs-scratchpad session path, within a
`pipeline/` subdirectory (i.e., `{rs-scratchpad-session}/pipeline/`):

```
{rs-scratchpad-session}/pipeline/
├── pipeline-config.yaml
├── pipeline-state.yaml
└── stages/
    ├── stage-1-spec/
    │   ├── output.md
    │   ├── gate-report.json
    │   └── findings.json
    ├── stage-2-implement/
    │   ├── output.md
    │   ├── gate-report.json
    │   └── findings.json
    ├── stage-3-test/
    │   ├── output.md
    │   ├── gate-report.json
    │   └── findings.json
    ├── stage-4-review/
    │   ├── output.md
    │   ├── gate-report.json
    │   └── findings.json
    └── stage-5-docs/
        ├── output.md
        ├── gate-report.json
        └── findings.json
    └── stage-6-deploy/         # Optional — only if deploy selected in Q6
        ├── output.md
        ├── gate-report.json
        └── findings.json
```

File purposes:

| File                            | Purpose                                            |
| ------------------------------- | -------------------------------------------------- |
| `pipeline-config.yaml`          | Immutable config from interview (this skill)       |
| `pipeline-state.yaml`           | Runtime state tracking (RuneSmith updates per event) |
| `stage-N-name/output.md`        | Stage output (stage executor)                      |
| `stage-N-name/gate-report.json` | Structured gate validation (RuneSmith)             |
| `stage-N-name/findings.json`    | Review findings (rs-reviewer)                      |

### RuneSmith Responsibility Boundary

| Responsibility                                         | Owner     |
| ------------------------------------------------------ | --------- |
| Interview, config generation                           | RuneSmith |
| Launch specialist agents per stage                     | RuneSmith |
| Present human gates, await response                    | RuneSmith |
| Human-required escalation (conflict, adjudication)     | RuneSmith (via question tool) |
| Execute a single stage                                 | RuneSmith |
| Read config for current stage                          | RuneSmith |
| Delegate to specialist agents (drafter, reviewers)     | RuneSmith |
| Validate gate conditions                               | RuneSmith |
| Apply auto-fixes (S1–S3)                               | RuneSmith (re-launch drafter) |
| Write `gate-report.json`, update `pipeline-state.yaml` | RuneSmith |
| Monitor `max_cycles`, detect recurrence                | RuneSmith |
| Auto-fix escalation (recurrence, cycle-exhaustion)     | RuneSmith (returns `failed`) |
| Question routing (specialist → human → relaunch)       | RuneSmith (via rs-human-responds) |
| Plan review / deep analysis                            | rs-architect (launched by RuneSmith) |
| Writing code, specs, docs, tests, or configs           | Specialist agents (launched by RuneSmith) |
| Direct invocation of specialist agents                 | RuneSmith only (flat delegation) |
| Orchestrator role contract                             | See AGENTS.md |

### Stage Dispatch Loop

After the interview is confirmed and `pipeline-config.yaml` is generated,
RuneSmith iterates through stages in the order defined by the TDD or
non-TDD path. For each stage:

```
for each stage in pipeline.stages (ordered):
  1. RuneSmith launches the drafter specialist directly (per stage_agent_map):
     rs-spec-writer | rs-developer | rs-test-writer | rs-reviewer |
     rs-tech-writer | rs-devops
  2. Drafter produces output to {artifacts-root}/stages/stage-N-{name}/output.md
  3. If the drafter returns needs_input → question routing (rs-ask-human /
     rs-human-responds) → relaunch drafter with answers
  4. RuneSmith launches Reviewer A + Reviewer B (fresh rs-reviewer subagents,
     parallel, no task_id reuse) on the drafter output
  5. If findings exceed thresholds (S1 > 0 or S2 > 5 from config; S3–S5 do
     not trigger threshold rework): fix loop → re-launch drafter (≤ max_cycles)
  6. If Reviewer A and Reviewer B findings conflict on the same file/line
     range → escalate as adjudication (needs-discussion to human)
  7. If recurrence or cycle-exhaustion → escalate per escalation model
  8. If plan_review is on_demand and the stage is complex (or requires_analysis
     set) → launch rs-architect for plan review / deep analysis
  9. RuneSmith validates gate conditions; writes gate-report.json; updates
     pipeline-state.yaml
 10. RuneSmith presents human gate per placement strategy
 11. If human rejects → re-launch stage for rework
 12. If human approves → next stage
```

Specialist invocation is always fresh — no `task_id` reuse across stages.
Each drafter/reviewer invocation receives:
- The stage name and config (`pipeline-config.yaml`)
- All prior stage outputs (spec, implementation, etc.)
- The current `pipeline-state.yaml`
- Prior `human_decisions` blocks relevant to the stage
- An empty review findings context (no cross-contamination)

Stage dispatch is strictly sequential — RuneSmith waits for each stage to
complete before launching the next. No parallel stage execution.

## Required Permissions

| Tool     | Required | Scope                         | Purpose                                        |
| -------- | -------- | ----------------------------- | ---------------------------------------------- |
| read     | Yes      | `.runesmith/`, project source | Read existing config, detect project structure |
| write    | Yes      | `.runesmith/` directory       | Write `pipeline-config.yaml`                   |
| edit     | Yes      | `.runesmith/` directory       | Update `pipeline-state.yaml`, gate reports     |
| glob     | Yes      | `.runesmith/` directory       | Discover existing artifacts                    |
| grep     | Yes      | `.runesmith/` directory       | Search state files                             |
| bash     | Yes      | `git rev-parse`               | Determine branch for artifact path             |
| question | Yes      | —                             | Conduct interview, present gates, route questions |
| skill    | Yes      | `rs-*`                        | Chain related skills                           |
| task     | Yes      | `rs-*` (all specialists)      | Launch specialist agents per stage             |

## Chained Skills

| Skill                  | When to Chain                               | Purpose                                      |
| ---------------------- | ------------------------------------------- | -------------------------------------------- |
| rs-scratchpad          | During interview, confirming session path | Initialize/validate session scratchpad for artifact storage |
| rs-discover            | Before Round 1, required — auto-detect project setup | Detect language/framework, test/lint/build commands; results suppress Q1–Q4 when known |
| rs-consult             | During interview if user is uncertain       | Guidance on technology choices               |
| rs-ask-human           | When a specialist needs human input         | Emit structured `needs_input` payload        |
| rs-human-responds      | When RuneSmith receives `needs_input`       | Faithful verbatim presentation + relaunch    |
| rs-review-methodology  | During review execution (by rs-reviewer)    | 7-step review checklist                      |
| rs-review-severity     | During review classification (by rs-reviewer) | S1–S5 severity classification              |
| rs-review-architecture | During review cycle (by rs-reviewer)        | WAF 5-pillar review                          |
| rs-review-security     | During review cycle (by rs-reviewer)        | Deep security domain analysis                |

**Fallback**: If rs-scratchpad `init` fails or returns no session path,
RuneSmith falls back to `.runesmith/{date}-{sanitized-branch}/pipeline/` as
the artifact root and notifies the user.

## See Also

- runesmith — The orchestrator that consumes `pipeline-config.yaml` and
  executes stages directly
- rs-architect — Deep-knowledge / deep-code-analysis / plan-review
  specialist (optional, on demand)
- rs-ask-human — Specialist-side structured question emit contract
- rs-human-responds — RuneSmith-side faithful verbatim answer contract
- rs-discover — Codebase scanner for automated interview answers
- rs-consult — Domain guidance during interview
- rs-scratchpad — Session path management for artifacts
- Orchestration Patterns — Session-as-Orchestrator design rationale
  (sibling knowledge-base repo at `knowledge/tooling/opencode/skills/orchestration-patterns.md`)
- Human Gate Patterns — AskQuestion strategies for gates and escalation
  (sibling knowledge-base repo at `knowledge/tooling/opencode/skills/human-gate/overview.md`)
- Pipeline Config & State Schema — Full schema reference
  (sibling knowledge-base repo at `research/opencode-runesmith/operations/pipeline-config-and-state.md`)
- Review Cycle Escalation — 4 escalation triggers in detail
  (sibling knowledge-base repo at `research/opencode-runesmith/operations/review-cycle-escalation.md`)
- Session–Subagent Boundary — structured returns, subagents never decide
  (sibling knowledge-base repo at `knowledge/tooling/opencode/skills/session-subagent-boundary.md`)
