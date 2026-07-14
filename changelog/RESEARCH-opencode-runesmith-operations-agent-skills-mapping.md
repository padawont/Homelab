---
title: "Agent-Skills Mapping"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - skills
  - mapping
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Agent-Skills Mapping

- **Plugin:** `@runicengines/opencode-runesmith`
- **Skill prefix:** `rs-`
- **Status:** Draft analysis

## Overview

The `@runicengines/opencode-runesmith` plugin ships a set of specialised skills that agents load on-demand via `skill({ name: "rs-<name>" })`. Each agent requires a different combination of skills depending on its role. This document maps every agent to the skills it loads, the order in which it loads them, and the purpose each skill serves.

Skills are loaded explicitly inside agent prompt files — there is no dynamic routing engine. The mapping is static: an architect always loads `rs-issue-to-plan`, `rs-discover`, and `rs-consult` in that order for every task. This design is intentional and is discussed in more detail under **Why Routing Was Not Chosen (Yet)** below.

## Agent → Skill Mapping Matrix

| Agent | Skills Loaded | When | Purpose |
|---|---|---|---|---|---|
| **All agents** | `rs-scratchpad` | Session start | Scratchpad lifecycle (init, clear, status) |
| **Architect** | `rs-issue-to-plan`, `rs-discover`, `rs-consult`, `rs-doc-architect` | On task | Plan understanding, codebase context, domain expertise, documentation audit |
| **Spec-Writer** | `rs-issue-to-plan`, `rs-discover`, `rs-pr-writer` | On task | Issue decomposition, codebase understanding, PR body from spec |
| **Developer** | `rs-discover` | Always first | Codebase understanding before implementation |
| **Developer** | `rs-consult` | When needed | Domain expertise for unfamiliar tech |
| **Developer** | `rs-commit-writer` | After staging | Generate Conventional Commit messages from staged diff |
| **Developer** | `rs-pr-writer` | Before coding | Generate draft PR body from issue/spec |
| **Developer** | `rs-env-validator` | Project setup | Validate .env configuration |
| **Reviewer** | `rs-review-methodology`, `rs-review-severity`, `rs-review-security`, `rs-doc-auditor` | On review | Structured review process, severity classification, security patterns, documentation compliance |
| **Test-Writer** | `rs-test-helper-run`, `rs-test-helper-diagnose` | After writing tests | Run tests, diagnose failures |
| **Tech-Writer** | `rs-changelog-manager`, `rs-consult`, `rs-doc-architect`, `rs-doc-llm-txt`, `rs-doc-auditor` | On task | Changelog generation, research, documentation architecture, llms.txt generation, compliance self-check |
| **DevOps** | `rs-dependency-checker`, `rs-discover`, `rs-doc-llm-txt`, `rs-env-validator` | On task | Vulnerability scanning, infrastructure context, llms.txt generation, environment validation |
| **Debugger** | `rs-discover`, `rs-consult` | On task | Codebase context, domain expertise for bug investigation |

### Notes on the Matrix

- **All agents** call `rs-scratchpad init` at session start before any role-specific skills. The scratchpad skill is loaded by the first agent in a session to initialize the session-scoped working directory.
- **Developer** appears twice because it loads skills conditionally: `rs-discover` is always loaded first (the agent cannot implement without context), while `rs-consult` is only loaded when the task involves technology the agent is unfamiliar with.
- **Reviewer** loads three skills in strict sequence — methodology first, then severity classification, then security patterns. This order enforces a top-down review structure: know *how* to review before classifying severity, and know severity before checking for security issues.
- **Test-Writer** loads skills *after* writing tests, not before. The skills are diagnostic, not generative — they run the test suite and interpret failures.
- **Tech-Writer** pairs a Runesmith-specific skill (`rs-changelog-manager`) with the general research skill (`rs-consult`) to pull domain context for changelog entries. It also loads documentation skills (`rs-doc-architect`, `rs-doc-llm-txt`, `rs-doc-auditor`) when working on documentation structure, LLM discoverability, or compliance self-checks.
- **Developer** loads multiple skills conditionally: `rs-discover` always first, `rs-consult` for unfamiliar tech, `rs-commit-writer` after staging changes, `rs-pr-writer` to open draft PRs before coding, and `rs-env-validator` during project setup.
- **Debugger** is the newest agent (see [rs-debugger.md](../agents/rs-debugger.md)). It loads `rs-discover` for codebase context and `rs-consult` for domain expertise on unfamiliar error patterns. It is a leaf agent (no delegation) and read-only on source files.

## Skill Loading Order

Each agent loads skills in a specific sequence. The order matters because later skills often depend on context or output from earlier ones.

### Reviewer Loading Sequence

The reviewer demonstrates the clearest example of ordered skill loading:

```
1. rs-review-methodology  → "How to review"
   Establishes the structured review framework: what to check, in what order,
   what evidence to gather. Sets the mental model for the entire review.

2. rs-review-severity     → "How to classify findings"
   Provides the severity rubric (critical, major, minor, cosmetic) and
   criteria for each level. Builds on the methodology by adding a
   classification layer to each finding.

3. rs-review-security     → "What security patterns to check"
   Supplies the security-specific checklist (OWASP Top 10, injection
   prevention, auth patterns). Loaded last because security is a
   specialised pass within the broader review — the reviewer must first
   understand the general methodology and severity scale before applying
   security-specific scrutiny.
```

### Developer Loading Sequence

```
1. rs-discover            → "Explore the codebase"
   Loaded unconditionally. Runs file-tree analysis, pattern recognition,
   and dependency tracing to understand the project structure before
   any code generation begins.

2. rs-consult (optional)  → "Domain expertise for unfamiliar tech"
   Loaded conditionally. The agent prompt checks whether the task
   mentions technology outside the agent's core competency and loads
   this skill only when needed. Keeps prompt size small for common tasks.
```

### Architect Loading Sequence

```
1. rs-issue-to-plan       → "Parse the issue into a structured plan"
   Extracts requirements, constraints, and acceptance criteria from the
   task description. Produces a structured plan that the architect uses as
   its working context.

2. rs-discover            → "Explore the codebase"
   Uses the plan to guide discovery — the architect knows what it is
   looking for and can focus `rs-discover` on relevant areas.

3. rs-consult             → "Consult domain expertise"
   Loaded last to fill gaps in the architect's understanding before the
   final design is produced.
```

## Skill-Routing YAML (Future Option)

If the agent prompts grow too complex — for example, if an agent needs to dynamically select skills based on task content — a `skill-routing.yaml` file could be added to the plugin root. This file would map skills to trigger keywords, allowing a lightweight routing engine to load skills without modifying every agent prompt.

### Proposed Schema

```yaml
version: 1
routing:
  rs-developer:
    - path: .opencode/skills/rs-discover/SKILL.md
      keywords: ["implement", "code", "build", "refactor"]
    - path: .opencode/skills/rs-consult/SKILL.md
      keywords: ["design", "architecture", "pattern", "unfamiliar"]
  rs-reviewer:
    - path: .opencode/skills/rs-review-methodology/SKILL.md
      keywords: ["review", "pr", "approve", "audit"]
    - path: .opencode/skills/rs-review-severity/SKILL.md
      keywords: ["severity", "classify", "priority"]
    - path: .opencode/skills/rs-review-security/SKILL.md
      keywords: ["security", "vulnerability", "owasp", "cve"]
  rs-test-writer:
    - path: .opencode/skills/rs-test-helper-run/SKILL.md
      keywords: ["test", "spec", "coverage", "assert"]
    - path: .opencode/skills/rs-test-helper-diagnose/SKILL.md
      keywords: ["fail", "error", "timeout", "flaky"]
```

### How Routing Would Work

A generic `skill-router` agent or middleware component would:

1. Parse the incoming task text and extract keywords.
2. Match keywords against the routing table for the current agent.
3. Load matched skills (deduplicated, ordered by match score).
4. Inject skill content into the agent's system prompt.

The routing engine itself is straightforward — roughly 50 lines of JavaScript — but it introduces a new component that must be maintained, tested, and documented.

### Why Routing Was Not Chosen (Yet)

The `@runicengines/opencode-runesmith` plugin deliberately hardcodes skill loading in agent prompts rather than implementing a routing YAML. The reasons are:

| Concern | Hardcoded Loading | Routing YAML |
|---|---|---|
| **Complexity** | Skills loaded explicitly in agent `.md` files — zero infrastructure | Requires a routing engine to parse YAML, match keywords, and inject skill content |
| **Debugging** | Open the agent file, see exactly which skills load and in what order | Must trace through agent → router → YAML → skill file to understand the loading chain |
| **Maintainability** | Adding a skill means editing one agent file | Adding a skill means editing the YAML *and* potentially the routing engine |
| **Flexibility** | Static — every task for an agent gets the same skills | Dynamic — skills adapt to task content, but behaviour is less predictable |
| **Cognitive load** | A Python or JavaScript developer can read and modify an agent `.md` file immediately | Requires understanding the routing abstraction on top of the skill system |

The mapping is static: each agent always needs the same skills for the same role. An architect always needs planning, discovery, and consultation regardless of whether the task says "implement" or "review". A reviewer always needs methodology, severity, and security regardless of whether the PR is frontend or backend.

Dynamic routing adds indirection without benefit when the mapping is static. If a future agent prompt grows to reference ten or more skills, or if a single agent needs radically different skill sets depending on sub-commands, the YAML approach can be revisited. For the current set of nine agents, hardcoded loading is simpler, more transparent, and easier to maintain.

## Skill Lifecycle within an Agent Session

Skills are loaded once per task invocation and held in context for the duration of the conversation turn. OpenCode does not cache skill content between turns — each new user message triggers a fresh skill load if the agent's prompt references the `skill()` call.

This has two implications:

1. **Order independence for stateless skills.** Skills like `rs-discover` and `rs-consult` are stateless — they provide reference material and methodology. Loading order does not affect their content, only the structure of the agent's reasoning.

2. **Order dependence for stateful skills.** The reviewer's three skills are consumed sequentially: methodology feeds into severity classification, which feeds into security checking. If the order were reversed, the reviewer would lack the framework to classify findings or apply security checks meaningfully.

## Agent Prompt Integration

Skills are loaded inside agent prompt files using OpenCode's `skill()` helper. A typical integration looks like this:

```markdown
# Developer Agent

You are a senior software engineer implementing features.

## Skills

<skill({ name: "rs-discover" })>

This skill provides codebase exploration capabilities. Use it when you
need to understand project structure, find relevant files, or trace
dependencies before writing code.

<skill({ name: "rs-consult" })>

This skill provides domain expertise. Load it *only* when the task
mentions technology you are unfamiliar with.
```

The `<skill({ name: "rs-..." })>` call is an OpenCode template directive. At agent initialisation time, OpenCode resolves the directive by locating `SKILL.md` in the plugin's `.opencode/skills/rs-*/` directory and inlines its content into the prompt. This is the same mechanism used for built-in skills like `gh` and `kb-scaffold-topic`.

## Summary

The agent-skills mapping for `@runicengines/opencode-runesmith` is a static, explicit mapping defined in agent prompt files. Each agent loads a role-specific set of skills in a carefully chosen order. The design prioritises simplicity and debuggability over dynamic flexibility, rejecting a YAML-based routing layer until the mapping grows complex enough to warrant it. The current matrix of nine agents and seventeen skills fits comfortably within the hardcoded approach.
