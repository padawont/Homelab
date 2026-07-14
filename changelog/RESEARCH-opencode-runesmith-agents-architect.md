---
title: "Architect Agent Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - architect
  - runesmith
  - orchestration
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
  - knowledge: "knowledge/tooling/opencode/agents/orchestration-patterns.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
  - url: "https://opencode.ai/docs/config"
    title: "OpenCode Config Documentation"
last_audit_date: 2026-06-07
---

# Architect Agent Design

> **Status:** Draft — initial analysis for the `@runicengines/opencode-runesmith` plugin architect agent.
> **Audience:** Python developers building the plugin.

## 1. Purpose

The architect agent is the central orchestrator of the RuneSmith multi-agent system. It does not write code, review diffs, or run tests. Its sole job is to **plan, delegate, validate, and report** — a hub that coordinates specialist spokes.

This document defines the architect's role, its agent file configuration, prompt structure, phase-gating workflow, model selection rationale, and the boundary rules that prevent delegation loops. It also compares the design against the `opencode-swarm` architect pattern to validate our choices.

## 2. Agent Role

The architect is the **hub** in a hub-and-spoke topology. It receives high-level requests from the user, decomposes them into phases, dispatches each phase to a specialist subagent, aggregates results, and reports back.

It must not:
- Implement code directly (delegates to the `developer` agent).
- Review code directly (delegates to the `reviewer` agent).
- Write tests directly (delegates to the `test-writer` agent).
- Persist its own state beyond the conversation context.

It must:
- Validate plans before implementation begins.
- Confirm gates pass before advancing to the next phase.
- Decide on error recovery when a specialist fails.
- Synthesise all specialist outputs into a coherent final response.

Because the architect holds full context across all phases, it requires strong reasoning capacity (Pro model) and careful permission scoping to prevent accidental escape into implementation work.

## 3. Recommended Agent File

This is the proposed `.opencode/agents/rs-architect.md` file for the plugin:

```yaml
---
description: "Orchestrates development work: plans, delegates to specialist agents, and validates results"
mode: subagent
model: opencode-go/deepseek-v4-pro
temperature: 0.1
max_thinking_tokens: 16000
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": deny
    "git *": allow
    "gh *": allow
  webfetch: allow
  task:
    "rs-spec-writer": allow
    "rs-developer": allow
    "rs-reviewer": allow
    "rs-test-writer": allow
    "rs-tech-writer": allow
    "rs-devops": allow
  skill:
    "*": allow
    "rs-*": allow
---
You are the RuneSmith Architect, the central orchestrator for the @runicengines/opencode-runesmith plugin.

## Your Role
You coordinate multi-agent development workflows. You do NOT write code, review code, or write tests.
You plan work, delegate to specialists, validate outputs, and report results.

## Core Responsibility
Understand high-level requests, create or validate plans, dispatch implementation to specialists,
gate each phase, and synthesise final results. You are the quality gate for the entire pipeline.

## Phase Gates
1. **Plan gate** — A spec must be approved before implementation starts.
2. **Implementation gate** — The developer must signal completion before review begins.
3. **Review gate** — The reviewer must approve the code before tests are written.
4. **Test gate** — All tests must pass before results are reported.
5. **Deploy Gate** — DevOps must confirm successful deployment with health checks passing.

Each phase must complete before the next begins. If a phase fails, decide whether to
retry with the same specialist, re-plan with the spec-writer, or escalate to the user.

## Delegation Rules
- Never implement code yourself — use the developer agent.
- Never review code yourself — use the reviewer agent.
- Never write tests yourself — use the test-writer agent.
- Never edit a file that a specialist has been dispatched to handle.
- Always verify outputs before approving a gate.

## Error Recovery
When a specialist fails:
1. **Retry** — Ask the same specialist to fix the issue with more context.
2. **Re-plan** — If the approach was wrong, go back to the spec-writer.
3. **Escalate** — If retries are exhausted, report the failure to the user with context.
```

### Key Configuration Decisions

| Field | Value | Rationale |
|---|---|---|
| `mode: subagent` | Prevents `@mention` access. The architect is invoked programmatically by the user's primary agent or via `task()`. This keeps the entry surface clean — users interact with a primary agent, which routes through the architect. |
| `model: opencode-go/deepseek-v4-pro` | Pro model needed for planning, validation, and recovery reasoning. Flash models are too fast-and-loose for gated orchestration. |
| `temperature: 0.1` | Low temperature ensures consistent delegation decisions. Creativity is not needed here — deterministic gate-keeping is. |
| `max_thinking_tokens: 16000` | Large thinking budget for multi-step reasoning: decomposing a request, planning phases, evaluating specialist outputs, and deciding on recovery paths. |
| `edit: allow` | The architect can write plans/specs but should not implement code. The `allow` here is for config and planning documents; the prompt instructs it to never edit implementation files directly. |
| `bash: "*": deny` with `"git *": allow` and `"gh *": allow` | Read-only git inspection (log, diff, status) and GitHub CLI access (issues, PRs). No arbitrary shell execution. |
| `task:` with explicit agent allowlist | The architect can only invoke the five specialist agents. No other agents are reachable. This is the **single delegation point** in the system. |

## 4. Prompt Structure

The architect's system prompt follows a five-part structure:

### 4.1 Role Definition

Opens with a crisp role statement: *"You are the RuneSmith Architect, the central orchestrator."* This sets the model's persona immediately, before any instructions. OpenCode agents read the system prompt top-to-bottom and the first line primes the entire response.

### 4.2 Core Responsibility

A single paragraph stating what the architect does and, crucially, what it does **not** do. Negative constraints are as important as positive ones — without explicit prohibition, a capable model will drift into implementation when given a code-related request.

### 4.3 Workflow Steps

The numbered workflow gives the model a fixed procedure to follow:

1. Receive task → understand requirements.
2. Delegate to spec-writer for a detailed plan (if no spec exists).
3. Review the plan → approve or send back.
4. Delegate to developer for implementation.
5. Delegate to reviewer for code review.
6. Delegate to test-writer for tests.
7. Delegate to rs-devops for deployment and monitoring (if applicable).
8. Aggregate all results → report to the user.

This sequence is deliberately linear. The phase gates (plan → implement → review → test) mirror a CI/CD pipeline's stage graph, making the flow predictable and auditable.

### 4.4 Phase Gates

Each gate has a hard pass condition:

| Gate | Pass Condition | Falls Back To |
|---|---|---|
| Plan | Spec is approved by the architect | Spec-writer revision |
| Implementation | Developer signals completion | Developer fix |
| Review | Reviewer approves the code | Developer rework |
| Test | All tests pass | Developer fix or re-plan |

If a gate fails, the circuit breaker logic (max 3 retries) kicks in before escalation. This prevents infinite loops on flaky gates — a known risk in gated pipelines (see [orchestration-patterns](../architecture/orchestration-patterns.md)).

### 4.5 Error Recovery

Three strategies, in order:

1. **Retry** — Re-invoke the same specialist with failure context appended. This covers transient errors (e.g., the developer missed an edge case).
2. **Re-plan** — Go back to the spec-writer with a "this approach failed" message. Covers fundamental misinterpretation of requirements.
3. **Escalate** — Report to the user with a summary of what was attempted, what failed, and why recovery was not possible. This should be rare — it means all retries and re-plans were exhausted.

## 5. Model Selection Rationale

The architect uses `opencode-go/deepseek-v4-pro` for three reasons:

**Reasoning depth.** The architect must evaluate specialist outputs against requirements, not just pass them through. Pro models produce more reliable chain-of-thought for comparative analysis. A Flash model might accept a superficial spec; the Pro model is more likely to spot gaps.

**Thinking budget.** At 16,000 `max_thinking_tokens`, the architect can reason through multi-step delegation sequences without losing coherence. Each delegation round consumes thinking tokens — plan validation, diff inspection, test output analysis. A smaller budget would truncate this reasoning.

**Temperature.** At `0.1`, the architect's decisions are near-deterministic. Delegation routing should not vary between invocations — the same spec should always pass the same gates. This is especially important for error recovery, where the model must consistently choose retry over re-plan when the approach is sound but execution was flawed.

## 6. Task Permission Uniqueness

The architect is the **only agent** in the RuneSmith system with `task` permission. All other agents — `spec-writer`, `developer`, `reviewer`, `test-writer`, `tech-writer`, `devops` — are leaf agents configured with `deny` for every task pattern.

This is a deliberate architectural constraint that prevents **delegation loops**:

```
❌ Unconstrained:  Developer → Reviewer → Developer → Reviewer → ...
✅ Constrained:   Architect → Developer
                  Architect → Reviewer
                  Architect → Developer (after review feedback)
```

If a leaf agent could invoke `task`, it could delegate part of its work to another agent, which could delegate further, creating a graph that is hard to trace and expensive in tokens. The flat hub-and-spoke topology means every delegation path starts and ends at the architect.

The `task` permission is configured with explicit agent names rather than wildcards:

```yaml
task:
  "rs-spec-writer": allow
  "rs-developer": allow
  "rs-reviewer": allow
  "rs-test-writer": allow
  "rs-tech-writer": allow
  "rs-devops": allow
```

This is a allowlist approach: only these six agents are invocable. Any agent not listed is effectively blocked. The wildcard `"*": deny` is implicit (OpenCode defaults to deny for unspecified targets). If a new specialist is added to the system, the architect's agent file must be updated — a deliberate coupling that forces explicit consent before delegation.

## 7. Skills the Architect Uses

Three RuneSmith skills are loaded into the architect's context:

| Skill | Purpose |
|---|---|
| `rs-issue-to-plan` | Converts a GitHub issue or user request into a structured plan with acceptance criteria. Used during the Plan phase. |
| `rs-discover` | Explores the codebase to answer questions about structure, existing patterns, and dependencies. Used before delegation to inform the spec-writer. |
| `rs-consult` | Loads domain-specific knowledge (e.g., architecture patterns, dependency docs) when the architect needs context it does not have in its prompt. Used during planning and review evaluation. |

These are invoked via `skill("rs-issue-to-plan")` etc. during the appropriate workflow phase. The `permission.skill` block is set to `"*": allow` and `"rs-*": allow` — effectively all skills are reachable, but the prompt restricts skill usage to these three.

## 8. Comparison with opencode-swarm's Architect

The `opencode-swarm` plugin implements a similar hub-and-spoke architecture. The comparison is useful because swarm is an existing, tested implementation — our design should differ only where our requirements differ.

| Dimension | opencode-swarm Architect | RuneSmith Architect | Rationale |
|---|---|---|---|
| **Mode** | `primary` | `subagent` | Swarm's architect is user-facing; RuneSmith's is invoked programmatically by a primary agent. |
| **Task permissions** | Broad allowlist (10+ agents) | Narrow allowlist (6 agents) | RuneSmith has fewer specialists and stricter encapsulation. |
| **Model** | `gpt-5.1-codex` | `opencode-go/deepseek-v4-pro` | Different model preference. Both are Pro-class for reasoning. |
| **Thinking tokens** | 8192 | 16000 | RuneSmith architect handles longer delegation chains (spec → code → review → test). |
| **Edit permission** | `deny` | `allow` | RuneSmith architect writes plans and specs. Swarm's architect delegates all writing. |
| **Phase gates** | Implicit (via prompt) | Explicit (4 named gates with circuit breakers) | RuneSmith formalises gates for auditability and error recovery. |
| **Skill prefix** | N/A | `rs-` | RuneSmith uses a dedicated skill prefix for plugin-scoped skills. |
| **KB agents** | Cross-delegation allowed | Separate (no cross-delegation) | RuneSmith KB agents are standalone; they do not participate in the orchestrated workflow. |
| **Error recovery** | Ad-hoc (model decides) | Structured (retry → re-plan → escalate) | RuneSmith codifies the recovery ladder for deterministic behaviour. |

### Key Divergence: Subagent Mode

The most important difference is `mode: subagent` vs `mode: primary`. In swarm, the architect is the user's entry point — you `@mention` the architect directly. In RuneSmith, the architect is a backplane agent invoked through a primary agent (e.g., a project-level "RuneSmith" agent). This means:

- The user never talks to the architect directly.
- The primary agent handles user interaction, request parsing, and initial triage.
- The architect focuses purely on orchestration without UI concerns.

This separation of concerns is more aligned with a microservices architecture — the primary agent is the API gateway, the architect is the orchestrator service.

### Key Divergence: Phase Gates

Swarm's architect relies on the model's innate ability to gate progression, which works well for straightforward flows but can skip steps under context pressure. RuneSmith's architect has **explicit phase gates** with named pass conditions, circuit breaker retry limits, and fallback routing. This is more code-intensive but produces deterministic, auditable pipelines — important for a cooperative where multiple developers may review the same workflow log.

## 9. Design Decisions Summary

| Decision | Choice | Why Not the Alternative |
|---|---|---|
| Hub-and-spoke over chain-of-responsibility | Centralised control, auditable logs | Chain-of-responsibility is harder to trace and debug. |
| Subagent over primary | Backplane invocation, cleaner separation | Primary mode would expose orchestration internals to the user. |
| Pro model over Flash | Reliable reasoning for gate validation | Flash would rush through gates. |
| 0.1 temperature over 0.7 | Deterministic delegation decisions | Higher temperature produces inconsistent routing. |
| Explicit agent allowlist over wildcards | Prevents accidental delegation to new agents | Wildcards could match a future agent that should not be in the pipeline. |
| 3-retry circuit breaker over unlimited retries | Prevents infinite token burn | Unlimited retries are the top gated-pipeline anti-pattern (see orchestration-patterns). |
| Prompt-based gate enforcement over structural gates | Simpler to implement, iterate, and understand | Structural gates (e.g., separate agent files per gate) add complexity without proportional benefit for a 6-agent system. |

## 10. Open Questions

1. Should the architect's thinking budget be configurable per-session? Some requests (e.g., a simple bugfix) do not need 16K thinking tokens.
2. Should the architect write plans to disk (e.g., `plans/<sha>.md`) for auditability, or keep them in-memory only?
3. Should the architect have a `max_steps` limit to prevent runaway delegation chains?

These will be resolved in the next phase (`exploring` → `proposed`) as the agent file is implemented in the plugin repository.

## See Also

- Orchestration design: `agents/architect-orchestration.md`
- Agent file reference: `knowledge/tooling/opencode/agents/agent-file-reference`
- Permissions model: `knowledge/tooling/opencode/agents/permissions`
- Orchestration patterns: `knowledge/tooling/opencode/agents/orchestration-patterns`
