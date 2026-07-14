---
title: "Architect Orchestration and Phase Gates"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - architect
  - orchestration
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/orchestration-patterns.md"
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-07
---

# Architect Orchestration and Phase Gates

> **Status:** Draft — deep analysis of the RuneSmith architect's orchestration mechanics, phase-gating logic, task delegation patterns, and error recovery strategies.
> **Audience:** Developers building or extending the `@runicengines/opencode-runesmith` plugin.
> **Prerequisite:** `agents/architect.md` — this document covers *how* the architect orchestrates; that document covers *what* the architect is and its agent file configuration.

## 1. Orchestration Flow

The RuneSmith architect executes a six-phase, strictly sequential pipeline. Each phase maps to a single specialist agent and terminates in a gate that must pass before the next phase begins.

```
 User Request
      |
      v
 +----------+       +------------------+
 | Architect| --->  | rs-spec-writer   |
 | (Hub)    |       | (Planning Phase) |
 +----------+       +------------------+
      |                      |
      |               [Plan Gate]
      |                 approve?
      |                   |
      |              (yes)|           (no, max 3x)
      |                   v              |
      |            +-------------+       |
      |            | rs-developer| <-----+ back to spec-writer
      |            | (Implement) |
      |            +-------------+
      |                   |
      |            [Implementation Gate]
      |                 compile/lint?
      |                   |
      |              (yes)|           (no, max 3x)
      |                   v              |
      |            +-------------+       |
      |            | rs-reviewer | <-----+ back to developer
      |            | (Review)    |
      |            +-------------+
      |                   |
      |              [Review Gate]
      |                 findings OK?
      |                   |
      |              (yes)|           (no, max 3x)
      |                   v              |
      |            +---------------+     |
      |            | rs-test-writer| <---+ back to developer
      |            | (Tests)       |
      |            +---------------+
      |                   |
      |              [Test Gate]
      |                 100% pass?
      |                   |
      |              (yes)|           (no, max 3x)
      |                   v              |
      |            +--------------+      |
      |            | rs-tech-writer| <---+ back to dev or test-writer
      |            | (Docs)       |
      |            +--------------+
      |                   |
      |              (done?)
      |                   v
      |            +-------------+
      |            | rs-devops   |
      |            | (Deploy)    |
      |            +-------------+
      |                   |
      |              [Deploy Gate]
      |                 health OK?
      |                   |
      |              (yes)|           (no)
      |                   v              v
      |            +-----------+   Rollback +
      |            | Architect |   + Diagnose
      |            | Report    |
      v            | to User   |
 Final Response <--+-----------+
```

Each box in this diagram is invoked via the `task()` tool. The architect never performs the work itself — it validates, gates, and reports.

## 2. Phase Gates in Detail

Each gate is a structured checkpoint. The architect evaluates the gate condition, decides pass or fail, and either advances the pipeline or triggers recovery.

### 2.1 Plan Gate

**Pass Condition:** The spec written by `rs-spec-writer` contains all required sections: title, context, acceptance criteria, implementation plan, open questions. The architect reads the spec file, verifies each section is populated, and confirms the approach is sound against the original request.

**Fail Action:** Return the spec to `rs-spec-writer` with specific feedback (e.g., "Missing acceptance criterion for rate-limiting"). Maximum 3 retries. On the 4th failure, escalate to the user — the request may be underspecified or infeasible.

### 2.2 Implementation Gate

**Pass Condition:** The code compiles without errors and passes lint. The architect runs `git status`, `git diff`, and relevant build commands (e.g., `go build ./...`, `npm run lint`) to confirm. No functional testing — that comes later.

**Fail Action:** Return to `rs-developer` with the compiler/lint output. Max 3 retries. If the same error persists across retries, the architect re-routes to `rs-spec-writer` for re-planning — the approach itself may be flawed.

### 2.3 Review Gate

**Pass Condition:** The `rs-reviewer` agent produces a review report with no S1 (critical) or S2 (major) findings, and at most 2 S3 (minor) findings. The architect checks the report against these thresholds.

**Fail Action:** Return the review findings to `rs-developer` for fixes. Max 3 retries. If findings persist after 3 rounds, the architect may request a fresh review from a different reviewer invocation to eliminate reviewer bias.

### 2.4 Test Gate

**Pass Condition:** All tests pass at 100% success rate. No S1 coverage gaps (critical paths without tests). The architect reads the test output and coverage report.

**Fail Action:** If a test failure is a genuine code issue, route to `rs-developer`. If it is a test correctness issue (flaky or wrong assertion), route to `rs-test-writer`. The architect distinguishes these by reading the failure stack trace.

### 2.5 Deploy Gate

**Pass Condition:** Deployment completes and a health check endpoint returns 200 within 30 seconds. The architect waits for the health probe, then confirms.

**Fail Action:** Instruct `rs-devops` to rollback to the previous known-good version. Then diagnose — was it a config issue, a missing dependency, or a runtime error? The architect reports the rollback and findings to the user.

### Gate Summary Table

| Gate | Check | Pass Condition | Fail Action | Max Retries |
|---|---|---|---|---|
| Plan Gate | Spec is complete and approved | All required sections present, approach validated | Back to spec-writer with feedback | 3 |
| Implementation Gate | Code compiles, lints pass | No build/lint errors | Back to developer with error output | 3 |
| Review Gate | Code review passes | No S1/S2 findings, max 2 S3 | Back to developer with review comments | 3 |
| Test Gate | All tests pass | 100% pass rate, no S1 coverage gaps | Back to developer (code) or test-writer (test) | 3 |
| Deploy Gate | Deploy succeeds | Health check passes within 30s | Rollback + diagnose | 1 (rollback is final) |

## 3. Task Delegation Pattern

The architect uses OpenCode's `task()` function to invoke subagents. Each invocation targets a specific agent by name and provides a prompt with precise context.

### 3.1 Standard Invocation Shape

```typescript
const spec = await task({
  name: "rs-spec-writer",
  prompt: `Write a spec for ${feature}.
Context: ${architectContext}
Acceptance criteria: ${criteria}
Output to: .runesmith/{date}-{branch}/specs/${feature}-spec.md`
});
```

The architect's prompt to each subagent includes:

1. **What to do** — the specific task (write a spec, implement a function, review a diff).
2. **Context** — relevant excerpts from the original request, prior phase outputs, or knowledge notes.
3. **Output location** — where to write files. This lets the architect read the results for gate validation.
4. **Constraints** — e.g., "do not modify files outside `src/auth/`".

### 3.2 Context Passing

The architect passes context forward through phases but never dumps raw conversation history. It synthesises:

- From the **Plan** phase: the approved spec filename and key decisions.
- From the **Implement** phase: the diff summary and commit SHA.
- From the **Review** phase: the finding list and pass/fail verdict.
- From the **Test** phase: the test output summary and coverage gaps.

This keeps each subagent's prompt focused and within the model's context window. Context is additive — each phase enriches the next without repeating verbatim transcripts.

### 3.3 Result Collection

After each `task()` call, the architect reads the subagent's output (spec file, code files, review report, test output). It does not trust the subagent's self-reported "done" signal — it verifies by reading files and running validation commands (compile, lint, health check) independently.

## 4. Error Recovery Strategy

Errors fall into four categories. Each has a specific recovery ladder.

### 4.1 Agent Failure or Timeout

The `task()` call itself fails — the subagent did not respond, timed out, or returned an error.

**Recovery:**
1. Retry the same agent with the same prompt (max 2x). The agent may have hit a transient infrastructure issue.
2. If both retries fail, reduce the scope: break the phase into smaller chunks and delegate each chunk separately.
3. If chunking also fails, escalate to the user: "The developer agent was unable to implement this feature after 3 attempts. Possible causes: [list]. Options: [retry with different model, implement manually, abort]."

### 4.2 Repeated Gate Failure

The subagent completes, but the gate validation fails repeatedly (e.g., 3 retries of developer still produces lint errors).

**Recovery:**
1. Change strategy — re-route to `rs-spec-writer` for re-planning. The approach may be fundamentally incompatible with the codebase.
2. If re-planning also fails the implementation gate, escalate to the user with the full failure log.

### 4.3 Gate Not Passable

A gate condition cannot be met no matter the retries. For example, a 100% test pass rate is impossible because the codebase has pre-existing test infrastructure issues.

**Recovery:**
1. Present options to the user: relax the gate condition, skip the gate with justification, or fix the underlying infrastructure issue.
2. The architect must never bypass a gate unilaterally — the user makes the call.

### 4.4 Unexpected Error

An exception in the architect's own reasoning loop — a malformed `task()` call, a file read error, a permission denial.

**Recovery:**
1. Log the error to `.runesmith/{date}-{branch}/logs/error-{timestamp}.log`.
2. Report to the user with the error context.
3. Offer to retry from the last known-good checkpoint.

### Error Recovery Matrix

| Failure Mode | Recovery Step 1 | Recovery Step 2 | Recovery Step 3 | Escalation |
|---|---|---|---|---|
| Agent times out | Retry same agent (1x) | Retry same agent (2x) | Re-plan with smaller phases | Escalate to user |
| Implementation lint fails | Back to dev (1x) | Back to dev (2x) | Back to dev (3x) | Re-plan spec |
| Review finds S1 bug | Back to dev (1x) | Back to dev (2x) | Fresh reviewer | Escalate to user |
| Test fails (code issue) | Back to dev (1x) | Back to dev (2x) | Back to dev (3x) | Re-plan or escalate |
| Test fails (test issue) | Back to test-writer (1x) | Back to test-writer (2x) | Escalate to user | — |
| Deploy health check fails | Rollback | Diagnose | Report findings | Escalate to user |
| task() call error | Retry (1x) | Retry (2x) | Re-plan smaller phase | Escalate to user |

## 5. When NOT to Delegate

Delegation has overhead. Each `task()` call consumes a model invocation, thinking tokens, and context window space. The architect should skip the pipeline for changes that are too small to justify the cost.

### 5.1 Threshold Rules

The architect checks the request against these heuristics before entering the pipeline:

| Condition | Action |
|---|---|
| Single file, < 20 lines changed (typo, rename, config tweak) | Do not delegate — handle directly if permitted, or route to developer directly |
| Single file, > 20 lines but only formatting/style changes | Route to developer, skip spec-writer and reviewer |
| Multi-file change with clear, well-scoped requirements | Full pipeline |
| Ambiguous or multi-domain request that needs decomposition | Full pipeline starting with spec-writer |

### 5.2 Cost-Benefit Check

Before invoking the pipeline, the architect performs an implicit cost-benefit check:

- **Pipeline cost:** ~5-8 model invocations (spec, code, review, test, docs, deploy) × thinking tokens each.
- **Bypass cost:** 1 developer invocation + manual user review.

If the bypass cost is lower and the risk of error is acceptable, the architect should bypass. This is a judgement call: a typo fix that goes through the full pipeline wastes tokens and time; a security-sensitive config change should never bypass review, even if the diff is small.

The architect documents its bypass decision in the response to the user: "This change is simple enough to skip the spec and review phases. I delegated directly to the developer."

## 6. Comparison with opencode-swarm

The `opencode-swarm` plugin pioneered the hub-and-spoke pattern in OpenCode. RuneSmith's orchestration diverges in several important ways:

| Dimension | opencode-swarm | RuneSmith | Implication |
|---|---|---|---|
| **Architect role** | `primary` agent | `subagent` agent | Swarm's architect is user-facing; RuneSmith's is a backplane service. |
| **Phases** | Scripted in agent prompt | Explicit gates with circuit breakers | RuneSmith's gates are auditable and have configurable retry limits. |
| **Delegation tool** | `task()` with agent names | `task()` with agent names | Same tooling, different agent allowlists. |
| **Leaf agent rule** | Enforced via convention | Enforced via permission deny-all | RuneSmith hard-blocks delegation from leaf agents in the agent file. |
| **Error recovery** | Ad-hoc model judgement | Structured ladder (retry → re-plan → escalate) | RuneSmith's recovery path is deterministic and testable. |
| **Gate bypass** | Model decides | Architect decides, logs reason | RuneSmith's bypass is explicit and documented in the response. |
| **Context passing** | Raw conversation history | Synthesised summaries per phase | RuneSmith conserves context windows for large codebases. |

### 6.1 Key Divergence: Explicit Gates

Swarm's architect relies on the model's inherent chain-of-thought to gate phases. This works well for straightforward flows but is vulnerable to context window pressure — a long conversation may cause the model to skip steps. RuneSmith's architect has named gates with hard pass conditions, retry limits, and fallback routes. This makes the pipeline's behaviour predictable regardless of conversation length.

### 6.2 Key Divergence: Bypass Logic

Swarm does not define when to bypass the pipeline — the model routes every request through the full flow. RuneSmith's architect explicitly checks whether a change is simple enough to skip delegation overhead. This saves tokens on trivial changes but adds complexity to the architect's decision logic.

## 7. Open Questions

1. Should the pipeline be configurable? Some projects may want to skip the docs or deploy phase. A `runesmith.json` config could specify which phases are active.
2. Should the architect persist delegation history to disk (e.g., `.runesmith/{date}-{branch}/logs/pipeline-{session}.json`)? This would enable post-mortem analysis of failed pipelines.
3. How should the architect handle pre-existing test failures? If the codebase already has failing tests, the "100% pass rate" gate can never be met.
4. Should the bypass logic itself be configurable? A `conservative` mode could force full pipeline on every change; an `aggressive` mode could skip tests for trivial changes.

## See Also

- Architect role and configuration: `agents/architect.md`
- Orchestration flow diagram: (this document)
- Phase gate validation patterns: `knowledge/tooling/opencode/agents/orchestration-patterns`
- Agent file configuration reference: `knowledge/tooling/opencode/agents/agent-file-reference`
- OpenCode task() API: `knowledge/tooling/opencode/agents/interactions.md`
