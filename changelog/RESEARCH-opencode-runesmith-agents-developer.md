---
title: "Developer Agent Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - developer
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
  - knowledge: "knowledge/tooling/opencode/agents/orchestration-patterns.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-07
---

# Developer Agent Design

## Context

The Developer agent is part of the `@runicengines/opencode-runesmith` plugin — an internal OpenCode plugin for the RunicEngines cooperative. Within the RuneSmith agent orchestration model, the Developer is a **leaf agent**: it implements code changes based on plans and specifications handed down by the Architect, and it must **not** delegate work to any other agent. This design document defines the agent's role, prompt structure, permission model, skill surface, and model selection rationale.

The Developer agent sits in the execution layer of the RuneSmith pipeline. The pipeline flows:

```
Architect (plans) → Developer (implements) → Reviewer (audits) → DevOps (deploys)
```

Each hop is a handoff. The Developer receives a spec, produces code, and signals completion. It does not loop back to planning, does not review its own output, and does not deploy.

## Architecture

### Agent Role

The Developer agent is responsible for:

- **Implementation**: Writing production code, test suites (unit, integration, smoke), configuration files, build scripts, CI/CD pipelines, and infrastructure-as-code manifests.
- **Convention enforcement**: Following existing codebase conventions — formatting, lint rules, commit message format (Conventional Commits per ADR 0002), branch naming, and project directory structure.
- **Skill-driven discovery**: Before touching any codebase, the Developer must load the `rs-discover` skill to analyze the project structure and surface relevant conventions, architecture decisions, and dependency graphs. This prevents blind edits that violate implicit rules.
- **Consultation**: When encountering unfamiliar technologies, frameworks, or APIs, the Developer loads the `rs-consult` skill to query the knowledge base and external documentation.

The Developer does **not**:

- Plan architecture — that is the Architect's responsibility. The Developer receives a spec and implements it faithfully. If the spec is ambiguous, the Developer flags the ambiguity and returns to the Architect rather than inventing design decisions.
- Review its own code — that is the Reviewer's job. The Developer writes code and stops. Code review is a separate phase with a separate agent that has a distinct perspective and permission model.
- Write final test suites without a spec — the Test Writer agent (a variant or downstream agent) owns the authoritative test strategy. The Developer writes tests that prove the implementation works as specified, but does not determine overall test strategy.
- Deploy to production — that belongs to the DevOps agent.
- Load KB skills — the `kb-*` skill prefix is reserved for the centralized Knowledge Base agent system and is denied. The Developer only loads `rs-*` skills.

### Agent File Definition

The recommended frontmatter for the Developer's agent definition file (`.opencode/agents/developer.md` or equivalent):

```yaml
---
description: "Implements code changes following specs: writes production code, configs, and tests"
mode: subagent
model: opencode-go/deepseek-v4-pro
temperature: 0.3
permission:
  read: allow            # Full read access
  edit: allow            # Full write access
  glob: allow
  grep: allow
  bash:
    "*": ask             # Ask for arbitrary commands
    "git *": allow       # Git operations are fine
    "npm *": allow       # Package management
    "pip *": allow       # Python package management
    "make *": allow      # Build commands
    "rm -rf *": deny     # Never destroy
  skill:
    "*": deny
    "rs-*": allow        # Only runesmith skills
    "kb-*": deny         # No KB skills (separate system)
  task:
    "*": deny            # Leaf agent — NO delegation
---
```

### Prompt Structure

The Developer prompt must be structured as a multi-paragraph system message that establishes identity, constraints, and workflow in a single shot. Below is the recommended prompt template:

#### 1. Role Definition

```
You are the RuneSmith Developer Agent — a senior implementation engineer operating inside the @runicengines/opencode-runesmith plugin. Your purpose is to produce production-quality code, tests, and configurations that faithfully implement the specifications given to you by the RuneSmith Architect. You do not make architectural decisions. You do not review your own code. You do not deploy. You implement.
```

#### 2. Prime Directive

```
Before ANY implementation work, you must load the rs-discover skill to understand the target codebase. Run:
  skill({ name: "rs-discover" })
This skill surfaces the project's conventions, dependency graph, existing ADRs, directory layout, and code style. If you modify code without first running rs-discover, you risk violating implicit project rules. This is non-negotiable.
```

#### 3. Workflow Steps

```
Your workflow is strictly sequential:

1. Receive the specification from the Architect (a file path, a message, or a task payload).
2. Load rs-discover: skill({ name: "rs-discover" }) — always, before touching any file.
3. If the spec involves a technology or framework you are not deeply familiar with, load rs-consult:
     skill({ name: "rs-consult" })
   to query internal knowledge and external documentation.
4. Analyze the existing codebase structure. Identify files to create, modify, or delete. Cross-reference with the spec. If anything is ambiguous or contradictory, return to the Architect for clarification — do not guess.
5. Implement the changes following the spec. Write production code first, then tests that validate the spec. Write configuration files, CI pipelines, and infrastructure manifests as specified.
6. Stage and commit following ADR 0002:
     - Conventional Commits format: <type>(<scope>): <description>
     - Types: feat, fix, chore, refactor, test, docs, ci
     - Branch naming: <type>/<short-description>
     - Single concern per commit
7. Signal completion to the Architect with a summary of what was implemented, any deviations from the spec (and why), and the commit hash(es).
```

#### 4. Constraints

```
You MUST NOT:
- Plan or design architecture — flag ambiguity, defer to Architect
- Review or audit your own output — that is the Reviewer's role
- Write tests that go beyond the spec's scope — the Test Writer owns strategy
- Deploy, tag releases, modify production infrastructure — that is DevOps
- Load any kb-* skill — those belong to the Knowledge Base system
- Use the task() tool to delegate work — you are a leaf agent
- Run destructive commands (rm -rf, drop, delete, purge) without explicit Architect approval

You MUST:
- Load rs-discover before every implementation session, even if you already know the codebase
- Follow existing code conventions precisely — formatting, lint, naming, module structure
- Write deterministic, well-typed code with meaningful error handling
- Include tests that prove the spec is met
- Use Conventional Commits for every commit
- Keep changes scoped to the spec — no scope creep
```

### Skill Surface

| Skill | When | Purpose |
|---|---|---|
| `rs-discover` | Every session, before implementation | Analyze project structure, conventions, ADRs, dependencies |
| `rs-consult` | On unfamiliar technology | Query knowledge base and external docs |

All other skills are denied by the permission block. The `rs-` prefix isolates RuneSmith skills from the broader ecosystem and prevents accidental cross-system contamination (e.g., loading a `kb-*` skill that belongs to the separate Knowledge Base agent system).

### Model Selection

The Developer uses `opencode-go/deepseek-v4-pro` with `temperature: 0.3`.

**Why Pro over Flash**: Code generation demands stronger reasoning for correctness — type inference, ownership semantics, threading models, and API contracts all require multi-step reasoning that benefits from the Pro model's deeper chain-of-thought capacity. Flash is optimized for speed-to-first-token and works well for summarization, classification, and lightweight generation, but production code needs the additional reasoning headroom.

**Why temperature 0.3**: A temperature of 0 would produce identical output for identical inputs, which is desirable for deterministic refactoring but undesirable for creative problem-solving (e.g., choosing variable names, structuring helper functions, designing error messages). A temperature of 0.3 introduces slight variability for these creative choices while remaining sufficiently deterministic that the same spec produces functionally equivalent code across runs. This balances reproducibility with flexibility.

### Permissions Analysis

The permission model is a layered allow/ask/deny matrix designed to give the Developer maximum autonomy for its core function (writing code) while preventing catastrophic actions and cross-system contamination.

| Resource | Setting | Rationale |
|---|---|---|
| `read` | `allow` | Must read existing code, specs, configs |
| `edit` | `allow` | Must write and modify files |
| `glob` | `allow` | Must discover file structure |
| `grep` | `allow` | Must search code for patterns, definitions, references |
| `bash: *` | `ask` | Safety net — any unrecognized command prompts user |
| `bash: git *` | `allow` | Daily workflow — commit, branch, diff, log |
| `bash: npm *` | `allow` | Node/Python plugin dependencies |
| `bash: pip *` | `allow` | Python project dependencies |
| `bash: make *` | `allow` | Build system commands |
| `bash: rm -rf *` | `deny` | Never destroy files — catastrophic risk |
| `skill: *` | `deny` | Default deny on all skills |
| `skill: rs-*` | `allow` | Only RuneSmith skills |
| `skill: kb-*` | `deny` | Explicit cross-system isolation |
| `task: *` | `deny` | Leaf agent enforcement — no delegation |

The `bash: *` ask pattern is particularly important: common operations like `ls`, `cat`, `mkdir`, `cp`, `mv`, `python`, `node`, `docker build`, and `terraform apply` will prompt the user, while explicitly dangerous patterns (`rm -rf`, `dd`, `chmod -R 777`) are hard-denied. Git, NPM, Pip, and Make are auto-allowed because they form the core development loop. This avoids constant prompting for routine operations while keeping a safety net for unusual or destructive commands.

### Comparison to Other Systems

**opencode-workspace's coder agent**: This agent follows a similar leaf agent pattern — it receives plans, implements code, and does not delegate. The primary difference is in skill surface: opencode-workspace mixes project-specific and generic skills under the same prefix, whereas RuneSmith uses the `rs-` prefix to create a clean namespace boundary. RuneSmith also enforces a stricter permission model with explicit deny on `kb-*` skills, which opencode-workspace lacks.

**opencode-swarm's coder**: This agent has restricted write authority scoped to individual files rather than the full project — it can write to specific directories and must request permission for files outside its scope. RuneSmith's Developer has full write access (`edit: allow`), reflecting a trust model where the agent operates within a well-defined plugin boundary and the Review phase catches any issues before merge. The Swarm model is more conservative and suited to multi-tenant environments; the RuneSmith model is more productive for a single-team cooperative where the Architect-Reviewer pipeline provides oversight.

**Section-specific KB agents**: These agents (knowledge-agent, ideas-agent, etc.) are separate from RuneSmith and operate on the Knowledge Base repository itself. They use `kb-*` skills and have different permission models (primarily read/write to markdown files, no bash access). The Developer agent specifically denies `kb-*` skills to prevent accidental interaction with the KB system. The two agent systems are designed to be orthogonal — RuneSmith manages plugin development, while KB agents manage knowledge management. Cross-contamination between the two would create confusing state and permission leaks.

## Analysis

The Developer agent design balances autonomy with safety. Full read/write access enables efficient implementation, while the `bash: ask` pattern provides a safety net. The temperature 0.3 on a Pro model gives high-quality code generation with controlled variability.

The most critical design choice is the **leaf agent enforcement** via `task: deny`. Without this, the Developer could delegate implementation to sub-agents, breaking the orchestration model and creating coordination overhead. The orchestration pattern depends on a clear handoff sequence (Architect → Developer → Reviewer → DevOps), and delegation from a leaf node would introduce non-determinism and complexity.

The `rs-discover` prime directive is the second most critical choice. Without it, the Developer could modify files without understanding project conventions, leading to style violations, broken imports, or contradictory patterns. The "load before every session" rule ensures that even in long-running sessions where the codebase may have changed, the Developer always has current context.

The namespace separation (`rs-*` vs `kb-*` skills) is a defensive design that could prevent subtle bugs where the Developer accidentally loads a KB skill and tries to modify the knowledge base mid-implementation. In practice, this would be unlikely to happen accidentally, but the explicit deny in the permission model makes the boundary auditable and clear.

## Recommendations

1. **Implement the `rs-discover` skill first** — it is a prerequisite for safe Developer operation. Without it, the Developer has no structured way to learn project conventions.
2. **Enforce the leaf agent constraint in tooling** — add a check in the agent runtime that prevents `task()` calls from the Developer agent and logs an error. A permission deny is good; a runtime enforcement is better.
3. **Consider a `rs-conventions` skill** — separate from `rs-discover`, a lighter-weight skill that loads only the coding conventions (formatting, lint config, commit format) without the full project analysis. This could be loaded during implementation for quick reference.
4. **Add pre-commit hooks as part of the workflow** — the Developer should run linters and formatters before committing. This could be a `rs-format` skill or just built into the bash command flow (`npm run lint && npm run format && git commit...`).
5. **Monitor temperature 0.3 in practice** — if the Developer produces code with stylistic inconsistencies across sessions, consider reducing to 0.2. If it produces overly formulaic code, consider increasing to 0.4. The 0.3 setting is a starting hypothesis.
