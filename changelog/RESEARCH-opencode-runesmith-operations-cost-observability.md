---
title: "RuneSmith Cost and Observability"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-09
tags:
  - opencode
  - runesmith
  - cost
  - observability
  - monitoring
sources:
  - knowledge: "knowledge/tooling/opencode/sdk/types.md"
  - knowledge: "knowledge/tooling/opencode/sdk/api-misc.md"
  - knowledge: "knowledge/tooling/opencode/plugins/event-session.md"
  - knowledge: "knowledge/tooling/opencode/plugins/event-compaction.md"
  - knowledge: "knowledge/tooling/opencode/plugins/event-patterns.md"
  - knowledge: "knowledge/tooling/opencode/plugins/examples.md"
  - knowledge: "knowledge/tooling/opencode/agents/lifecycle.md"
  - knowledge: "knowledge/tooling/opencode/agents/orchestration-patterns.md"
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/ecosystem/plugins.md"
references:
  - url: "https://opencode.ai/docs/sdk"
    title: "OpenCode SDK Documentation"
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://api-docs.deepseek.com/quick_start/pricing"
    title: "DeepSeek API Pricing"
last_audit_date: 2026-06-09
---

# RuneSmith Cost and Observability

> **Status:** Exploring — cost projections, token budgets, logging, monitoring, and debugging approach for the `@runicengines/opencode-runesmith` multi-agent plugin.
> **Builds on:** [architect.md](../agents/architect.md) (token config), [architect-orchestration.md](../agents/architect-orchestration.md) (pipeline cost), [rollout-strategy.md](./rollout-strategy.md) (telemetry design)

## Context

The `@runicengines/opencode-runesmith` plugin deploys seven subagents across a hub-and-spoke topology. Each agent invocation consumes model tokens at provider-specific rates, with Pro models costing significantly more than Flash models and thinking tokens adding an additional cost layer. As the plugin rolls out from pilot (5 devs) to team (25 devs) to org-wide (100+ devs), cumulative costs become a material concern for the cooperative.

This document provides cost projections at each rollout tier, token budget strategies, a logging and tracing design, monitoring and alerting recommendations, and a debugging guide for common pipeline failures. It is the companion to [rollout-strategy.md](./rollout-strategy.md) on the operations side — that document covers **when** we roll out; this one covers **how much it costs** and **how we observe it**.

---

## 1. Cost Projections

### 1.1 Model Tier Assignments

The RuneSmith agents map to two model tiers based on the analysis in each agent design document:

| Agent | Model | Thinking Tokens | Tier | Rationale |
|---|---|---|---|---|
| Architect | Pro | 16,000 | High-cost | Multi-step planning, gate validation, error recovery |
| Developer | Pro | N/A (default) | High-cost | Code generation requires deep reasoning |
| Reviewer | Flash | None (Flash defaults to thinking-enabled; requires `thinking: {type: "disabled"}` to opt out) | Low-cost | Pattern matching and classification |
| Spec-Writer | Flash | None (Flash defaults to thinking-enabled; requires `thinking: {type: "disabled"}` to opt out) | Low-cost | Structured plan generation, not deep reasoning |
| Test-Writer | Pro | N/A (default) | High-cost | Test generation and failure diagnosis |
| Tech-Writer | Flash | None (Flash defaults to thinking-enabled; requires `thinking: {type: "disabled"}` to opt out) | Low-cost | Natural language prose, no reasoning overhead |
| DevOps | Pro | N/A (default) | High-cost | Infrastructure scripts, deployment logic |

**Summary:** 4 Pro-tier agents (architect, developer, test-writer, devops) and 3 Flash-tier agents (reviewer, spec-writer, tech-writer). The architect is the single most expensive agent per-invocation due to its 16K thinking token budget.

### 1.2 Estimated Per-Invocation Token Consumption

Estimates are based on typical sessions observed during RuneSmith research development. Actual consumption varies significantly by task complexity.

| Agent | Typical Input Tokens | Typical Output Tokens | Thinking Tokens | Total Tokens (approx) |
|---|---|---|---|---|
| Architect (plan + validate) | 8,000 | 2,000 | 16,000 | 26,000 |
| Developer (implement feature) | 12,000 | 8,000 | — | 20,000 |
| Reviewer (review 500-line diff) | 15,000 | 3,000 | — | 18,000 |
| Spec-Writer (decompose issue) | 10,000 | 4,000 | — | 14,000 |
| Test-Writer (write + run tests) | 10,000 | 6,000 | — | 16,000 |
| Tech-Writer (write docs) | 8,000 | 4,000 | — | 12,000 |
| DevOps (deploy + health check) | 6,000 | 2,000 | — | 8,000 |

**Full pipeline total** (all 7 agents invoked): ~114,000 tokens per end-to-end workflow.

**Architect-only session** (simple request, no delegation): ~26,000 tokens.

### 1.3 Estimated Per-Invocation Dollar Cost

Using actual [DeepSeek API pricing](https://api-docs.deepseek.com/quick_start/pricing) as the provider backend (the `opencode-go/deepseek-v4-*` models route through DeepSeek infrastructure). Cache hit pricing reflects context caching discounts. Thinking tokens are billed at the output token rate.

| Model | Input Cost / 1K tokens (cache miss) | Input Cost / 1K tokens (cache hit) | Output Cost / 1K tokens |
|---|---|---|---|
| Pro (`deepseek-v4-pro`) | $0.000435 | $0.000003625 | $0.00087 |
| Flash (`deepseek-v4-flash`) | $0.00014 | $0.0000028 | $0.00028 |

**Per-agent cost per invocation (cache miss — worst case):**

| Agent | Tier | Input Cost | Output Cost | Thinking Cost | Total (approx) |
|---|---|---|---|---|---|
| Architect | Pro | $0.00348 | $0.00174 | $0.01392 | **$0.0191** |
| Developer | Pro | $0.00522 | $0.00696 | — | **$0.0122** |
| Reviewer | Flash | $0.00210 | $0.00084 | — | **$0.0029** |
| Spec-Writer | Flash | $0.00140 | $0.00112 | — | **$0.0025** |
| Test-Writer | Pro | $0.00435 | $0.00522 | — | **$0.0096** |
| Tech-Writer | Flash | $0.00112 | $0.00112 | — | **$0.0022** |
| DevOps | Pro | $0.00261 | $0.00174 | — | **$0.0044** |

**Per-agent cost per invocation (cache hit — best case, up to 99% discount on inputs):**

| Agent | Tier | Input Cost | Output Cost | Thinking Cost | Total (approx) |
|---|---|---|---|---|---|
| Architect | Pro | $0.000029 | $0.00174 | $0.01392 | **$0.0157** |
| Developer | Pro | $0.000044 | $0.00696 | — | **$0.0070** |
| Reviewer | Flash | $0.000042 | $0.00084 | — | **$0.00088** |
| Spec-Writer | Flash | $0.000028 | $0.00112 | — | **$0.00115** |
| Test-Writer | Pro | $0.000036 | $0.00522 | — | **$0.00526** |
| Tech-Writer | Flash | $0.000022 | $0.00112 | — | **$0.00114** |
| DevOps | Pro | $0.000022 | $0.00174 | — | **$0.00176** |

**Full pipeline (cache miss):** ~**$0.053** per end-to-end workflow.
**Architect-only (cache miss):** ~**$0.019** per architect session.
**Full pipeline (cache hit):** ~**$0.033** per end-to-end workflow.

The architect dominates at 36% of the full pipeline cost due to its thinking token budget. The three Flash agents together cost $0.0076 — roughly 14% of the pipeline total. Cache hits reduce input costs by up to 99%, which has a modest effect on total cost since output and thinking tokens dominate.

### 1.4 Per-Workflow Cost Estimates

Different task types involve different pipeline depths. The architect's cost-benefit logic (defined in [architect-orchestration.md](../agents/architect-orchestration.md) §5) determines which agents are invoked.

#### Simple Bug Fix (single file, < 20 lines)

Bypasses the pipeline — architect delegates directly to developer or handles inline.

| Invocation | Agents | Est. Cost (cache miss) |
|---|---|---|
| Developer only | 1 | $0.0122 |
| **Total** | **1** | **$0.012** |

#### Moderate Feature (multi-file, well-scoped)

Full pipeline minus DevOps.

| Invocation | Agents | Est. Cost (cache miss) |
|---|---|---|
| Architect | 1 | $0.0191 |
| Spec-Writer | 1 | $0.0025 |
| Developer | 1 | $0.0122 |
| Reviewer | 1 | $0.0029 |
| Test-Writer | 1 | $0.0096 |
| Tech-Writer | 1 | $0.0022 |
| **Total** | **6** | **~$0.049** |

#### Complex Feature with Deployment

Full pipeline, all 7 agents.

| Phase | Agent | Est. Cost (cache miss) |
|---|---|---|
| Planning | Architect + Spec-Writer | $0.0216 |
| Implementation | Developer | $0.0122 |
| Review | Reviewer | $0.0029 |
| Testing | Test-Writer | $0.0096 |
| Documentation | Tech-Writer | $0.0022 |
| Deployment | DevOps | $0.0044 |
| **Total** | **7 agents, ~5-8 task() calls** | **~$0.053** |

#### Failed Pipeline (gate failure + retries)

Each retry multiplies the cost of the failing phase. A 3-retry developer phase costs $0.0366 (3 × $0.0122) instead of $0.0122. A full pipeline that fails at the implementation gate three times then escalates:

| Phase | Est. Cost (cache miss) |
|---|---|
| Architect (initial) | $0.0191 |
| Spec-Writer | $0.0025 |
| Developer (3 retries) | $0.0366 |
| Architect (re-plan) | $0.0191 |
| Spec-Writer (re-plan) | $0.0025 |
| Developer (3 retries again) | $0.0366 |
| **Total (failed pipeline)** | **~$0.12** |

Failed pipelines cost 2–3× a successful one. The circuit breaker (max 3 retries followed by escalation) limits the damage — without it, retries could burn tokens indefinitely. At current DeepSeek pricing, even a worst-case failed pipeline is under $0.15.

### 1.5 Monthly Burn Estimates by Usage Tier

Assumptions:
- **Per-developer workflows:** 5 sessions per week × 4 weeks = 20 sessions/month
- **Simple/complex split:** 60% simple (bug fix), 30% moderate (feature), 10% complex (full pipeline)
- **Failure rate:** 10% of full pipelines fail and require re-run (conservative)
- **22 working days/month, 4.33 weeks/month**

#### Tier 1: Pilot (5 developers)

| Workflow Type | Per Developer / Month | Cost per Workflow | Subtotal (5 devs) |
|---|---|---|---|
| Simple (60%) | 12 | $0.012 | $0.72 |
| Moderate (30%) | 6 | $0.049 | $1.47 |
| Complex (10%) | 2 | $0.053 | $0.53 |
| Failed pipelines | 10% of complex | $0.12 | $0.12 |
| **Total** | **20 sessions/dev** | | **~$2.84/month** |

Pilot cost: ~**$2.84/month** or **$0.57/dev/month**.

#### Tier 2: Team Expansion (25 developers)

| Workflow Type | Per Developer / Month | Cost per Workflow | Subtotal (25 devs) |
|---|---|---|---|
| Simple (60%) | 12 | $0.012 | $3.60 |
| Moderate (30%) | 6 | $0.049 | $7.35 |
| Complex (10%) | 2 | $0.053 | $2.65 |
| Failed pipelines | 10% of complex | $0.12 | $0.60 |
| Architect-only research (extra) | 5 extra sessions | $0.019 | $2.38 |
| **Total** | **25 sessions/dev** | | **~$16.58/month** |

Team cost: ~**$16.58/month** or **$0.66/dev/month**.

#### Tier 3: Org-Wide (100+ developers)

| Workflow Type | Per Developer / Month | Cost per Workflow | Subtotal (100 devs) |
|---|---|---|---|
| Simple (60%) | 12 | $0.012 | $14.40 |
| Moderate (30%) | 6 | $0.049 | $29.40 |
| Complex (10%) | 2 | $0.053 | $10.60 |
| Failed pipelines | 10% of complex | $0.12 | $2.40 |
| Architect-only research (extra) | 10 extra sessions | $0.019 | $19.00 |
| **Total** | **30 sessions/dev** | | **~$75.80/month** |

Org-wide cost: ~**$76/month** or **$0.76/dev/month**.

With cache hits (assuming 50% cache hit rate on inputs), costs drop further:

| Scenario | Pilot (5 devs) | Team (25 devs) | Org-wide (100 devs) |
|---|---|---|---|
| Cache miss (worst case) | $2.84 | $16.58 | $75.80 |
| 50% cache hit rate | $2.36 | $14.00 | $63.40 |
| Cache hit (best case) | $1.88 | $11.42 | $51.00 |

The per-developer cost rises slightly with scale because heavier users (architect-only research sessions) become more common as the plugin becomes standard infrastructure.

### 1.6 Cost Breakdown by Agent Type

Across all workflows at org-wide scale (100 devs, ~3000 total monthly workflow executions):

| Agent | Monthly Invocations | Cost per Invocation | Monthly Cost | % of Total |
|---|---|---|---|---|---|
| Architect | 3,000 (plan) + 900 (re-validate) = 3,900 | $0.0191 | $74.49 | 68% |
| Developer | 1,200 (impl) + 360 (retry) = 1,560 | $0.0122 | $19.03 | 17% |
| Reviewer | 900 | $0.0029 | $2.61 | 2% |
| Spec-Writer | 900 | $0.0025 | $2.25 | 2% |
| Test-Writer | 900 | $0.0096 | $8.64 | 8% |
| Tech-Writer | 600 | $0.0022 | $1.32 | 1% |
| DevOps | 300 | $0.0044 | $1.32 | 1% |
| **Total** | | | **~$109.66** | 100% |

The architect accounts for **68% of total cost** — far more than any other agent. This is the single most important lever for cost optimisation. The three Flash agents (reviewer, spec-writer, tech-writer) together account for about 6% of total cost.

> **Note on §1.5 vs §1.6 discrepancy:** The §1.5 org-wide total (~$75.80/mo) is a simplified estimate derived from per-workflow cost averages (simple ~$0.012, moderate ~$0.049, complex ~$0.053). These averages are rounded approximations and do not perfectly capture the actual per-agent invocation distribution. The §1.6 per-agent breakdown (~$109.66/mo) uses precise invocation counts multiplied by per-invocation costs and is the authoritative figure for per-agent cost analysis.

### 1.7 Cost Optimisation Levers

| Lever | Impact | Effort | Notes |
|---|---|---|---|
| Reduce architect thinking tokens | High | Low | 16K thinking tokens drive 73% of architect cost. Consider `max_thinking_tokens` config per session. Note: `max_thinking_tokens` is an OpenCode pass-through field — it is forwarded to the provider without interpretation. DeepSeek's documented API uses `thinking: {type: "enabled/disabled"}` and `reasoning_effort` for thinking control; whether the pass-through field is honoured should be tested during Phase 1. |
| Pipeline bypass for simple tasks | Medium | Already implemented | The architect already skips the pipeline for < 20 line changes. |
| Increase Flash model use | Low | High | Only 3 of 7 agents can use Flash. Converting Pro agents to Flash would degrade quality. |
| Session compaction to reduce context | Low | Medium | Input costs are small relative to thinking tokens. Compaction matters more for context window limits than cost. |
| Cache prompt prefixes | Low | Low | DeepSeek offers up to 99% discount on cached inputs, but output/thinking tokens dominate total cost. |
| Aggregate small changes | Low | Low | Batch multiple small fixes into one pipeline run instead of separate invocations. |
| Retry budget tuning | Low | Low | Reduce max retries from 3 to 2 for non-critical gates. |

---

## 2. Token Budgets

### 2.1 Current Token Configurations

The architect is the only agent with an explicitly configured `max_thinking_tokens`. The remaining Pro agents (developer, test-writer, devops) use the provider default without an explicit thinking token limit.

> **Note on `max_thinking_tokens`:** This is a pass-through field in OpenCode agent configs — it is forwarded to the provider without interpretation (see [knowledge/tooling/opencode/agents/agent-file-reference.md](../../../knowledge/tooling/opencode/agents/agent-file-reference.md) § `max_thinking_tokens`). DeepSeek's documented API controls thinking via `thinking: {type: "enabled/disabled"}` and `reasoning_effort`; whether the pass-through `max_thinking_tokens` field is honoured is unverified. The effectiveness of this parameter should be confirmed during Phase 1 testing. If DeepSeek does not support it, alternative mechanisms include using `reasoning_effort` or model selection (e.g. switching to Flash for simple tasks that need no reasoning).

| Agent | max_thinking_tokens | Model | Source |
|---|---|---|---|
| Architect | 16,000 | Pro | [architect.md](../agents/architect.md) §3 |
| Developer | Not set (default) | Pro | [developer.md](../agents/developer.md) |
| Reviewer | N/A (Flash defaults to thinking-enabled; requires `thinking: {type: "disabled"}` to opt out) | Flash | [reviewer.md](../agents/reviewer.md) |
| Spec-Writer | N/A (Flash defaults to thinking-enabled; requires `thinking: {type: "disabled"}` to opt out) | Flash | [spec-writer.md](../agents/spec-writer.md) |
| Test-Writer | Not set (default) | Pro | [test-writer.md](../agents/test-writer.md) |
| Tech-Writer | N/A (Flash defaults to thinking-enabled; requires `thinking: {type: "disabled"}` to opt out) | Flash | [tech-writer.md](../agents/tech-writer.md) §3 |
| DevOps | Not set (default) | Pro | [devops.md](../agents/devops.md) |

### 2.2 Thinking Token Cost Impact

Thinking tokens are billed at the output token rate (2× the input rate on DeepSeek, at $0.00087/1K for Pro). The architect's 16K thinking budget is the dominant cost factor:

- Without thinking: architect costs ~$0.0052/invocation (input + output only, cache miss).
- With thinking at 16K: architect costs ~$0.0191/invocation (3.7× increase).
- With thinking at 8K (half budget): architect costs ~$0.0123/invocation (2.4× increase).

**Note:** DeepSeek V4 Flash defaults to thinking-enabled. The zero-thinking-token assumption for Flash agents requires `thinking: {type: "disabled"}` in their agent file configurations. Without this, Flash agents will consume thinking tokens at $0.00028/1K, increasing costs beyond the projections above.

**Info:** DeepSeek notes that for complex agent requests (including OpenCode), `reasoning_effort` is automatically set to `max`. This may cause the architect to generate more thinking tokens than the 16K budget anticipates. Validate `max_thinking_tokens` behavior during Phase 1 testing.

Open Question: Should the architect's `max_thinking_tokens` be configurable per-session? A simple bug-fix delegation does not need 16K of reasoning. This was raised as an open question in [architect.md](../agents/architect.md) §10 and remains unresolved. A per-request thinking budget override in the architect's prompt could reduce cost by 40-60% for simple tasks. (See the note in §2.1 regarding the unverified status of `max_thinking_tokens` as a pass-through field to DeepSeek.)

### 2.3 Context Window Management

Without active management, developer and architect sessions accumulate large context windows over multiple turns, driving up input token costs for every subsequent model invocation.

#### Session Compaction

OpenCode provides session compaction via the `session.summarize()` SDK method and the `experimental.session.compacting` plugin hook (see [OpenCode Plugins Documentation](https://opencode.ai/docs/plugins#compaction-hooks)). When the context window approaches capacity, the session is compacted: the conversation history is summarised into a continuation prompt, and older messages are discarded.

The RuneSmith plugin should implement a compaction hook that preserves critical pipeline state:

```typescript
export const CompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Preserve pipeline status across compaction
      output.context.push(`## RuneSmith Pipeline State
- Current phase: [phase name]
- Approved spec: [spec filename]
- Gate status: [passed/failed gates]
- Active errors: [list of unresolved errors]
- Next action: [what to do next]`);
    },
  };
};
```

#### Compaction Triggers

| Trigger | When | Action |
|---|---|---|
| Context window > 80% of model limit | Automatic (OpenCode default) | Session is compacted before next model invocation |
| After gate completion | Custom (RuneSmith plugin) | Explicit compaction to flush per-phase context |
| On architect re-delegation | Custom (RuneSmith plugin) | Compact previous phase context before next `task()` call |
| On error recovery | Custom (RuneSmith plugin) | Compact before retry to remove error context that may confuse the model |

#### Context Budget per Phase

| Phase | Estimated Turns | Estimated Context Size | Compaction Recommended |
|---|---|---|---|
| Planning | 5-10 | 15-30K tokens | After spec approval |
| Implementation | 10-30 | 30-80K tokens | After implementation gate passes |
| Review | 3-8 | 20-50K tokens | After review gate passes |
| Testing | 5-15 | 25-60K tokens | After test gate passes |
| Documentation | 3-8 | 15-30K tokens | After documentation completes |

Without compaction, a full pipeline could accumulate 100-250K tokens of context by the DevOps phase. With per-phase compaction, each phase starts with 5-15K tokens of carryover context.

### 2.4 Token Consumption Reduction Strategies

#### Strategy 1: Skill Chaining vs Separate Sessions

The architect uses `task()` to invoke subagents within the same session. This means the full conversation history is available to the architect, but context grows with each delegation. An alternative is separate sessions per phase:

| Approach | Pros | Cons |
|---|---|---|
| **Skill chaining** (current design) | Full context available to architect; single audit trail | Context grows with each phase; higher input token cost |
| **Separate sessions** | Each phase starts with a clean context; lower per-phase token cost | Architect must re-establish context; no cross-phase traceability; multiple session overhead |

**Recommendation:** Use skill chaining with per-phase compaction. The audit trail of a single session is critical for debugging pipeline failures. Separate sessions would lose the cause-effect chain across phases.

#### Strategy 2: Automatic Summarisation via Lifecycle Hooks

The compaction hook is the primary mechanism for automated summarisation. The RuneSmith plugin should register a compaction hook that:

1. Extracts the current pipeline state (phase, gate status, errors).
2. Preserves only the most recent 3 turns of conversation per phase.
3. Drops tool call details (file diffs, bash output) from prior phases.
4. Maintains the spec approval decision and any user-provided constraints.

#### Strategy 3: Cache Hit Rates

Provider-level prompt caching (available on DeepSeek and most major providers) caches repeated prompt prefixes. If the architect's system prompt (approximately 800 tokens) is identical across invocations, the provider caches it after the first request and subsequent invocations pay only for the unique portion.

| Component | Tokens | Cacheable? | Saving (per Pro invocation) |
|---|---|---|---|
| System prompt | ~800 | Yes | ~$0.00035 (input cache miss → cache hit) |
| Agent file prompt | ~1,200 | Yes | ~$0.00052 (input cache miss → cache hit) |
| Spec context | Variable | No | — |
| Diff content | Variable | No | — |

DeepSeek offers up to 99% discount on cached input tokens ($0.435/1M → $0.003625/1M for Pro). However, since output and thinking tokens dominate total cost, the net impact of caching is smaller than it appears:

- **Pro agent, cached system prompt (2K tokens):** saves ~$0.00086 per invocation.
- **Flash agent, cached system prompt (2K tokens):** saves ~$0.00027 per invocation.
- **Org-wide monthly saving (assuming 50% cache hit rate):** ~$5-10/month.

---

## 3. Logging and Tracing

### 3.1 OpenCode SDK Logging API

The OpenCode SDK provides `client.app.log()` for structured logging from plugins. The RuneSmith plugin uses this as its primary logging mechanism, replacing `console.log` entirely.

**API Signature:**

```typescript
await client.app.log({
  body: {
    service: string,    // Plugin or agent name
    level: "debug" | "info" | "warn" | "error",
    message: string,    // Human-readable description
    extra?: object,     // Structured metadata
  },
});
```

**Log Level Usage in RuneSmith:**

| Level | Usage | Example |
|---|---|---|
| `debug` | Agent-session internals: tool calls, token counts, gate evaluations | `"Architect gate check: Implementation gate passed (lint: OK, build: OK)"` |
| `info` | Normal lifecycle events: session start/end, delegation, gate pass | `"Developer agent completed implementation of auth-flow feature"` |
| `warn` | Recoverable issues: retries, permission denials, slow sessions | `"Developer agent retry 2/3: lint error still present"` |
| `error` | Unrecoverable failures: escalation, plugin init failure, task() timeout | `"Architect escalation: developer agent failed after 3 retries, escalated to user"` |

**Logging Implementation Example:**

```typescript
// Inside the init hook or a lifecycle handler
await client.app.log({
  body: {
    service: "rs-architect",
    level: "info",
    message: "Phase gate passed",
    extra: {
      phase: "Implementation",
      agent: "rs-developer",
      duration: 45200, // ms
      result: "pass",
      retries: 0,
    },
  },
});
```

### 3.2 Session Events for Observability

The OpenCode event system (`client.event.subscribe()`) provides real-time session events that the RuneSmith plugin can consume for observability. See [OpenCode Plugins Documentation](https://opencode.ai/docs/plugins#events) for the full event list.

**Relevant Session Events:**

| Event | Fires When | Data Available | Observability Use |
|---|---|---|---|
| `session.created` | A new session is created | Session ID, title, project | Track session start; count total sessions per developer |
| `session.error` | A session encounters an error | Error message, stack, session ID | Alert on error rate spikes; correlate with agent failures |
| `session.deleted` | A session is deleted | Session ID | Track session lifetime; compute average session duration |
| `session.status` | Session status changes | Status value (active/idle/error) | Monitor session health; detect hung sessions |
| `session.compacted` | Session is compacted | Pre-compaction token count, post-compaction token count | Track context pressure; compute compaction efficacy |
| `session.updated` | Session metadata changes | Changed fields | General session activity monitoring |

**Event Subscription Pattern:**

```typescript
const events = await client.event.subscribe();
for await (const event of events.stream) {
  switch (event.type) {
    case "session.created":
      // Increment session counter, record start time
      break;
    case "session.error":
      // Log error, increment error counter, alert if threshold exceeded
      await client.app.log({
        body: {
          service: "rs-observability",
          level: "error",
          message: `Session error: ${event.properties.errorMessage}`,
          extra: { sessionId: event.properties.sessionId },
        },
      });
      break;
    case "session.compacted":
      // Record compaction metrics for cost analysis
      trackCompaction(event.properties);
      break;
  }
}
```

### 3.3 Session Compaction Events for Context Pressure Monitoring

The `session.compacted` event is particularly useful for monitoring context pressure. The RuneSmith plugin should track:

| Metric | How to Measure | Significance |
|---|---|---|
| Compaction frequency | Count of `session.compacted` events per session per hour | High frequency = context window filling fast = token cost concern |
| Tokens reclaimed | `preTokens - postTokens` from event properties | Large reclamation = verbose session; small = session already compact |
| Compaction trigger | Whether triggered by context limit or explicit API call | Frequent limit-triggered compaction suggests need for larger context budget |
| Compaction duration | Time between compaction start and completion | Slow compaction indicates model or infrastructure bottleneck |

### 3.4 Local Telemetry Directory Design

Following the telemetry pattern established in [rollout-strategy.md](./rollout-strategy.md) §Automated Telemetry, the RuneSmith plugin writes telemetry to a local directory: `.runesmith/telemetry/`.

**Directory Structure:**

```
.runesmith/
├── telemetry/
│   ├── sessions/
│   │   ├── 2026-06-09.jsonl       # Session events, append-only
│   │   └── 2026-06-10.jsonl
│   ├── costs/
│   │   ├── 2026-06-09.jsonl       # Per-invocation token counts
│   │   └── 2026-06-10.jsonl
│   ├── errors/
│   │   ├── 2026-06-09.jsonl       # Structured error records
│   │   └── 2026-06-10.jsonl
│   ├── metrics/
│   │   ├── 2026-06-09.jsonl       # Aggregated metrics (hourly rollups)
│   │   └── 2026-06-10.jsonl
│   └── meta.json                  # Telemetry config and rotation state
├── .gitignore                     # Ignores entire .runesmith/ directory
```

**Telemetry File Format (JSONL — one JSON object per line):**

```json
{"timestamp":"2026-06-09T10:30:00Z","type":"agent_invocation","data":{"agent":"rs-developer","sessionId":"abc123","tokens":{"input":12000,"output":8000,"thinking":0},"duration":45000,"success":true}}
{"timestamp":"2026-06-09T10:31:00Z","type":"gate_evaluation","data":{"agent":"rs-architect","gate":"implementation","result":"pass","retries":0,"duration":3200}}
{"timestamp":"2026-06-09T10:32:00Z","type":"session_event","data":{"sessionId":"abc123","event":"session.compacted","preTokens":85000,"postTokens":12000}}
```

**Telemetry Configuration (`meta.json`):**

```json
{
  "version": 1,
  "rotation": {
    "maxFileSize": 10485760,
    "maxDays": 90,
    "compression": "gzip"
  },
  "enabled": true
}
```

**Design Principles:**

- **Append-only JSONL:** New events are appended to the daily file. No random-access writes. This is safe for concurrent plugin sessions on the same machine.
- **Daily rotation:** A new file per day per category. Old files are compressed after `maxDays`.
- **No external transmission:** Telemetry stays local in all phases. Phase 3 may add opt-in central reporting (see [rollout-strategy.md](./rollout-strategy.md) §Automated Telemetry).
- **Git-ignored:** The `.runesmith/` directory is added to `.gitignore` in every repo that uses the plugin (handled by the init hook).

---

## 4. Monitoring and Alerting

### 4.1 Plugin Health Indicators

The RuneSmith plugin exposes health indicators that can be monitored by developers and, in Phase 3, by a central dashboard. These are collected from the init hook, session events, and SDK API calls.

| Indicator | Source | Healthy State | Unhealthy State |
|---|---|---|---|
| Init hook success/failure | Init hook return value | Returns `true` | Returns `false` or throws |
| Version stamp match | Version comparison | Local stamp matches plugin version | Stamp mismatch (stale install) |
| Agent file existence | File system check | All 7 agent `.md` files present | One or more missing |
| Task permission enforcement | Permission check | Leaf agents have `task: deny` | Leaf agents can invoke `task()` |
| Session creation | `session.created` event | Sessions created on demand | Session creation fails |
| Agent invocation error rate | `session.error` events | < 5% of invocations error | >= 5% error rate |
| Compaction success | `session.compacted` event | Compaction completes normally | Compaction fails or times out |

### 4.2 Key Metrics to Track

#### Invocation Metrics

| Metric | Source | Granularity | Purpose |
|---|---|---|---|
| Invocation count per agent | SDK `app.agents()` + session events | Per session, per day | Track adoption, detect usage patterns |
| Invocation count per developer | Session metadata | Per week | Measure engagement per rollout phase |
| Delegation chain depth | Architect `task()` calls | Per pipeline | Detect runaway delegation |
| Session count per repo | Project metadata | Per day | Track repo-level adoption |

#### Error Metrics

| Metric | Source | Granularity | Purpose |
|---|---|---|---|
| Error rate (all agents) | `session.error` events | Per hour | Overall system health |
| Error rate per agent | Error event metadata | Per hour | Identify problematic agents |
| Gate failure rate | Architect gate logs | Per pipeline stage | Detect patterns in gate failures |
| Retry frequency | Agent invocation logs | Per session | Measure error recovery effectiveness |
| Escalation rate | Architect escalation logs | Per week | Track unresolved failures |

#### Performance Metrics

| Metric | Source | Granularity | Purpose |
|---|---|---|---|
| Session latency (p50, p95, p99) | Session timestamps | Per session | User experience monitoring |
| Agent response time | SDK prompt completion | Per invocation | Detect slow models or network issues |
| Init hook execution time | Init hook instrumentation | Per startup | Track plugin loading performance |
| Compaction duration | `session.compacted` event | Per compaction | Monitor context management overhead |

#### Token Metrics

| Metric | Source | Granularity | Purpose |
|---|---|---|---|
| Token consumption per session | Session event metadata | Per session | Cost tracking |
| Token consumption per agent | Agent invocation logs | Per invocation | Per-agent cost breakdown |
| Thinking tokens used (architect) | Architect invocation logs | Per invocation | Track thinking budget utilisation |
| Compaction token reclamation | `session.compacted` event | Per compaction | Measure compaction efficiency |
| Cost per session (computed) | Token counts × pricing | Per session | Dollar cost per session |

### 4.3 Alert Thresholds and Escalation Paths

Alert thresholds are defined per rollout phase. Phase 1 uses conservative thresholds with manual review; Phase 3 uses tighter thresholds with automated notification.

| Alert | Threshold (Phase 1) | Threshold (Phase 2) | Threshold (Phase 3) | Escalation |
|---|---|---|---|---|
| Error rate spike | > 10% in 1 hour | > 5% in 1 hour | > 3% in 30 min | Developer → Team lead → Plugin maintainer |
| Session latency p95 | > 60 seconds | > 30 seconds | > 20 seconds | Developer investigation → Architect prompt optimisation |
| Init hook failure | Any failure | > 1 failure per day | > 0 failures | Immediate fix |
| Token overrun (per session) | > 200K tokens | > 150K tokens | > 100K tokens | Architect context management review |
| Cost spike (daily) | > $1/day | > $3/day | > $5/day | Budget review |
| Compaction failure | Any failure | > 1 per week | > 0 failures | Compaction hook fix |
| Agent file missing | Any missing file | > 0 missing files | > 0 missing files | Re-init or reinstall plugin |

### 4.4 Dashboard Design for Org-Wide Monitoring (Phase 3)

In Phase 3, the cooperative may deploy a central monitoring dashboard for RuneSmith health and cost across all repos. This dashboard is **not** mandatory in Phase 1 or Phase 2.

**Proposed Dashboard Sections:**

#### Section 1: Org Health Overview

- Total active developers using plugin (gauge)
- Total repos with active sessions (gauge)
- Overall error rate (sparkline, 7-day window)
- Current phase adoption rate (bar chart: Phase 1 / Phase 2 / Phase 3 repos)

#### Section 2: Cost Dashboard

- Daily cost (area chart, 30-day)
- Monthly projected cost (gauge with budget line)
- Cost per developer (histogram, top 10 developers)
- Cost by agent type (stacked bar)
- Cost by workflow type (pie chart: simple / moderate / complex / failed)

#### Section 3: Performance

- Session latency by agent (box plot, p50/p95/p99)
- Init hook timing per repo (scatter plot)
- Compaction rate per session (heat map)
- Token consumption per session (time series)

#### Section 4: Error Analysis

- Error count by agent (bar chart)
- Gate failure rate by phase (funnel chart)
- Retry distribution (histogram)
- Escalation log (table with message, agent, timestamp, repo)

#### Section 5: Adoption

- Session count per repo (bar chart)
- Active users per week (line chart, rolling 12 weeks)
- Feature adoption (% of sessions using full pipeline vs bypass)
- Agent usage ranking (sorted bar: most invoked agent → least)

**Implementation Note:** The dashboard requires centralised telemetry collection, which is a cooperative governance decision deferred to Phase 3 (see [rollout-strategy.md](./rollout-strategy.md) §Automated Telemetry). The technical foundation — local JSONL telemetry files — is established in Phase 1 and can be adapted for central ingestion in Phase 3.

---

## 5. Debugging Pipeline Failures

### 5.1 Common Failure Modes

#### Failure Mode 1: Init Hook Errors

| Symptom | Likely Cause | Detection |
|---|---|---|
| Plugin doesn't load after install | npm auth missing; `GITHUB_TOKEN` not set | Init hook returns false; error log |
| Agent files not copied | Version stamp exists but files missing | Agent file existence check fails |
| Permission errors on init hook run | Shell access not granted by user | Error in plugin init lifecycle |
| Stale agent files after update | Version stamp not matching | Version comparison log warning |

**Debugging approach:**
1. Check `~/.cache/opencode/node_modules/@runicengines/opencode-runesmith/` exists.
2. Verify npm auth: `npm whoami --registry=https://npm.pkg.github.com`.
3. Check `.opencode/.runesmith-version` content matches plugin version.
4. Run the verification checklist from [verification.md](./verification.md).

#### Failure Mode 2: Agent Delegation Failures

| Symptom | Likely Cause | Detection |
|---|---|---|
| `task()` returns error/undefined | Agent name misspelled or not in allowlist | Architect error log |
| Subagent doesn't complete | Timeout; context too large; model error | Session error event; task() timeout |
| Wrong output from subagent | Incorrect prompt context; agent confusion | Gate validation failure |
| Permission denied on task() | Agent not in architect's task allowlist | Permission error in logs |

**Debugging approach:**
1. Verify the agent name in the `task()` call matches `agents/rs-*.md` filename.
2. Check the architect's agent file `task` allowlist includes the target agent.
3. Inspect the prompt sent to the subagent — was context adequate?
4. Reduce context size and retry; check if compaction is needed.

#### Failure Mode 3: Skill Chain Breaks

| Symptom | Likely Cause | Detection |
|---|---|---|
| Skill not found | Skill directory not copied; name mismatch | Skill invocation error |
| Skill returns wrong output | Incorrect arguments; schema mismatch | Downstream gate failure |
| Chained skill fails mid-chain | Dependency skill not available | Partial skill result |
| Permission denied on skill | Skill's required tool not in agent's permissions | Permission error in logs |

**Debugging approach:**
1. Verify skill directory exists: `.opencode/skills/rs-*/SKILL.md`.
2. Check the skill name matches the `name` field in SKILL.md.
3. Check the calling agent's `permission.skill` allowlist.
4. Test the skill in isolation with known inputs.

#### Failure Mode 4: Gate Validation Failure

| Symptom | Likely Cause | Detection |
|---|---|---|
| Plan gate fails repeatedly | Spec missing sections; criteria vague | Architect spec validation log |
| Implementation gate fails | Code doesn't compile; lint errors | Architect gate check output |
| Review gate fails | Reviewer finds S1/S2 issues | Review report severity count |
| Test gate fails | Tests don't pass; coverage gaps | Test output and coverage report |

**Debugging approach:**
1. Read the architect's gate evaluation log entry — it contains the exact pass/fail condition check.
2. Inspect the subagent's output file (spec, diff, review report, test output).
3. Determine if the failure is a genuine quality issue or a gate threshold that is too strict.
4. If the threshold is too strict, consider adjusting the gate pass condition (requires a proposal change).

#### Failure Mode 5: Compaction Failures

| Symptom | Likely Cause | Detection |
|---|---|---|
| Context window overflow | Compaction not triggered; threshold too high | Session error; token count > context limit |
| Lost context after compaction | Compaction prompt doesn't preserve pipeline state | Architect confused about phase |
| Slow compaction | Large prompt; model timeout | Compaction duration > 10 seconds |

**Debugging approach:**
1. Check the `session.compacted` event properties for pre/post token counts.
2. Inspect the compaction hook's `output.prompt` or `output.context` for completeness.
3. Verify the compaction hook is registered and fires on the expected triggers.
4. If the compaction prompt truncates pipeline state, revise the hook implementation.

### 5.2 Log Analysis Patterns

The RuneSmith plugin writes structured logs via `client.app.log()` and events via `client.event.subscribe()`. These can be analysed with standard log analysis tools (grep, jq, or a dedicated observability platform).

**Pattern 1: Find all pipeline failures in a time range:**

```bash
grep '"level":"error"' .runesmith/telemetry/sessions/2026-06-09.jsonl | jq '.data'
```

**Pattern 2: Identify the most error-prone agent:**

```bash
jq -r 'select(.type == "agent_invocation" and .data.success == false) | .data.agent' .runesmith/telemetry/sessions/*.jsonl | sort | uniq -c | sort -rn
```

**Pattern 3: Track compaction efficiency over time:**

```bash
jq -r 'select(.type == "session_event" and .data.event == "session.compacted") | "\(.data.preTokens) \(.data.postTokens) \(.data.preTokens - .data.postTokens)"' .runesmith/telemetry/sessions/*.jsonl
```

**Pattern 4: Detect runaway delegation chains:**

```bash
# Count delegation depth per session
jq -r 'select(.data.agent == "rs-architect" and .data.action == "task") | .data.sessionId' .runesmith/telemetry/sessions/*.jsonl | sort | uniq -c | sort -rn | head
```

**Pattern 5: Compute daily cost estimate:**

```bash
# Rough cost from token counts (replace rates with actual provider pricing)
jq -r 'select(.type == "agent_invocation") | .data.tokens | .input * 0.002 + .output * 0.008 + (.thinking // 0) * 0.008' .runesmith/telemetry/costs/2026-06-09.jsonl | awk '{s+=$1} END {print s, "USD"}'
```

### 5.3 Troubleshooting Documentation Recommendations

The following troubleshooting guides should be created alongside the plugin (deferred to [rollout-strategy.md](./rollout-strategy.md) Phase 2 entry criteria):

| Guide | Audience | Content |
|---|---|---|
| **Installation Troubleshooting** | All developers | npm auth issues, permission errors, init hook failures, stale cache |
| **Agent Invocation Guide** | All developers | How to invoke agents, `@mention` vs `task()`, common errors |
| **Permission Error Reference** | Developers, maintainers | Each permission error type, why it happened, how to resolve |
| **Pipeline Failure Walkthrough** | Plugin maintainers | Step-by-step debugging for each failure mode (see §5.1) |
| **Cost Optimisation Guide** | Team leads | How to reduce token consumption, when to bypass pipeline, thinking budget tuning |
| **Telemetry FAQ** | All developers | What is collected, where it's stored, how to opt out, privacy implications |

---

## 6. Open Questions

1. **Thinking token configurability:** Should the architect's `max_thinking_tokens` be dynamically adjustable per-session based on task complexity? A simple bug-fix delegation does not need 16K thinking tokens. Note: `max_thinking_tokens` is an OpenCode pass-through field forwarded to the provider; its support in DeepSeek is unverified — if unsupported, alternative mechanisms (e.g. `reasoning_effort`, model selection) should be explored.

2. **Central telemetry ingestion:** Phase 3 proposes opt-in central telemetry for org-wide dashboards. Is the JSONL local-first format suitable for ingestion? Should we use a structured log shipper (e.g., Vector, Fluentd) or write a custom uploader?

3. **Budget enforcement:** Should the plugin enforce per-developer or per-repo token budgets? A `runesmith.json` config key like `"monthlyBudget": 50` (in USD) could trigger warnings when approaching the limit.

4. **Failure cost attribution:** When a pipeline fails and costs $0.87, who bears the cost? Should failed pipeline costs be tracked separately from successful ones for budget planning?

5. **Alerting infrastructure:** Phase 3 dashboard assumes an aggregator service. Should we use a self-hosted Grafana stack, a lightweight solution (e.g., Netdata), or outsource to a commercial observability platform (e.g., Datadog)?

6. **Compaction hook stability:** The `experimental.session.compacting` event is currently marked experimental in the OpenCode SDK. What is the migration path if the API changes in a stable release?

---

## 7. Cost-Saving Recommendations

Based on the cost analysis in §1, the following actions have the highest cost-saving potential per unit of effort:

| Priority | Action | Est. Saving (org-wide) | Effort | Risk |
|---|---|---|---|---|
| P0 | Implement dynamic thinking tokens for architect | ~$30/month | Low | Low — but `max_thinking_tokens` is an OpenCode pass-through field; its effect on DeepSeek is unverified. Test during Phase 1. If unsupported, fall back to `reasoning_effort` or model-tier switching. |
| P0 | Ensure pipeline bypass for < 20-line changes | Already implemented | None | None |
| P1 | Implement per-phase compaction in plugin | ~$8/month | Medium | Low — non-breaking addition |
| P1 | Document cache hit strategies for teams | ~$12/month | Low | None |
| P2 | Reduce retry budget from 3 to 2 for non-critical gates | ~$5/month | Low | Low — may increase escalation rate |
| P2 | Monthly cost review cadence | Informational | Low | None |
| P3 | Batch small changes into single pipeline runs | Variable | Medium | Medium — changes developer workflow |

At DeepSeek's current pricing, the absolute dollar amounts are very low. The primary cost concern is not absolute dollar spend but **cost predictability** — a single runaway session or infinite retry loop could spike costs despite low per-invocation rates. Monitoring and alerting (see §4) are the most important defences.

---

## See Also

- Agent cost basis: [architect.md](../agents/architect.md) (token config), [architect-orchestration.md](../agents/architect-orchestration.md) (pipeline cost)
- Rollout context: [rollout-strategy.md](./rollout-strategy.md) (telemetry design, phased adoption)
- Verification: [verification.md](./verification.md) (smoke test checklist)
- Update propagation: [update-propagation.md](./update-propagation.md) (version stamping)
- SDK logging: [knowledge/tooling/opencode/sdk/api-misc.md](../../../knowledge/tooling/opencode/sdk/api-misc.md)
- Plugin events: [knowledge/tooling/opencode/plugins/event-session.md](../../../knowledge/tooling/opencode/plugins/event-session.md)
- Compaction hooks: [knowledge/tooling/opencode/plugins/event-compaction.md](../../../knowledge/tooling/opencode/plugins/event-compaction.md)
