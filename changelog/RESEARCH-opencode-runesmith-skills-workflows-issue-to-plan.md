---
title: "Issue-to-Plan Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - issue-to-plan
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/concepts.md"
  - knowledge: "knowledge/tooling/opencode/skills/configuration.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://conventionalcommits.org/en/v1.0.0/"
    title: "Conventional Commits"
  - url: "https://docs.github.com/en/issues/tracking-your-work-with-issues"
    title: "GitHub Issues Documentation"
last_audit_date: 2026-06-07
---

# Issue-to-Plan Skill Design

## Purpose

The `rs-issue-to-plan` skill converts a GitHub issue into a structured implementation plan. It is the core workflow skill for the `@runicengines/opencode-runesmith` plugin — the instruction bundle that a spec-writer agent loads on-demand to decompose ambiguous issue descriptions into phased, actionable specs.

This document is a **research analysis** of the skill's design. It is not the skill itself. The actual skill file will live at `.opencode/skills/rs-issue-to-plan/SKILL.md` inside the plugin's repository. This analysis informs that file's construction and documents the design decisions behind it.

## Background

Skills in OpenCode are lightweight instruction bundles — markdown files with YAML frontmatter — that agents load on-demand via `skill({ name: "..." })`. They are discovered through the `<available_skills>` XML block injected into the agent's tool description. Each skill has a `name` (matching its parent directory) and a `description` the agent uses to decide whether loading it is relevant.

The Knowledge Base already has a workflow skill at `knowledge/tooling/opencode/skills/issue-to-plan.md`. That skill covers a similar scenario — issue decomposition — but targets **KB content creation** (ideas, knowledge notes, research). The RuneSmith version targets **code implementation planning**. The two are complementary but distinct, and this document highlights where they diverge.

## Skill Identity

The RuneSmith plugin uses the `rs-` prefix for all its skills. The name `rs-issue-to-plan` satisfies the OpenCode name validation regex (`^[a-z0-9]+(-[a-z0-9]+)*$`) and is 17 characters — well within the 64-character limit. The directory it will live in is `.opencode/skills/rs-issue-to-plan/` within the plugin's repository root, containing a single `SKILL.md` file.

### Recommended Frontmatter

```yaml
---
name: rs-issue-to-plan
description: >
  Convert a GitHub issue into a structured implementation plan with
  phases, acceptance criteria, and test strategy. Follows ADR 0002
  conventions for branch naming, commits, and PR workflow.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: manual+chained
---
```

**Design notes on the frontmatter:**

- **`description`** starts with an action verb ("Convert") and includes domain keywords ("GitHub issue", "implementation plan", "phases", "acceptance criteria", "ADR 0002") so agents can match it against user prompts like "plan this issue" or "break down #42".
- **`metadata.plugin`** is a RuneSmith-specific marker. Since skills are discovered globally (OpenCode walks up from CWD to worktree root and loads from `.opencode/skills/`, `.claude/skills/`, and `.agents/skills/`), a plugin marker helps disambiguate skills when multiple plugins are installed. The plugin registry can filter by this field.
- **`metadata.trigger`** is `manual+chained` because the skill is primarily loaded by a spec-writer agent (manual via the agent's prompt), but may also be chained from `rs-discover` when context scanning reveals additional issues to decompose.

## Skill Instructions — Full Body

The skill body should contain the following sections. These are the instructions injected into the agent's context when `skill({ name: "rs-issue-to-plan" })` is called.

```markdown
## What This Skill Does

Takes a GitHub issue (by URL, issue number, or raw description) and produces a
phased implementation plan. The output is a `spec.md` document with:
- A summary of the work
- 3–5 implementation phases, each independently reviewable and mergeable
- Acceptance criteria per phase (testable, measurable conditions)
- A test strategy covering unit, integration, and e2e
- ADR 0002 conventions for branch naming and commits

## Input

Accept any of the following formats:

| Format | Example | How to resolve |
|--------|---------|----------------|
| Full URL | `https://github.com/owner/repo/issues/42` | Fetch via `gh issue view 42 -R owner/repo` or `webfetch` |
| Issue number | `#42` or `42` | Resolve via `gh issue view 42` (repo inferred from CWD) |
| Raw text | A multi-line description | Treat as the issue body directly — no fetch needed |

When given a URL or number, always fetch the live issue from GitHub first.
The issue may have updated comments, labels, or linked PRs since it was created.

## Step-by-Step Workflow

### 1. Fetch and parse the issue

Use `gh issue view <number> --json title,body,labels,comments,state,milestone,assignees`
to extract the full issue context. If `gh` is unavailable, fall back to `webfetch`
on the issue URL and parse the markdown body manually.

Extract the following from the issue:
- **Title** — used as the spec title
- **Description** — the canonical requirements source
- **Labels** — used to determine issue type (bug, feature, refactor, chore per ADR 0002)
- **Comments** — may contain additional requirements, constraints, or decisions
- **Linked PRs/issues** — cross-reference any related work

### 2. Classify the issue type

Map the issue to a Conventional Commit type based on its labels and content:

| Label | Type | Meaning |
|-------|------|---------|
| `bug` | `fix` | Defect correction |
| `enhancement` | `feat` | New feature |
| `chore` | `chore` | Maintenance, tooling, deps |
| `documentation` | `docs` | Docs-only changes |
| `refactor` | `refactor` | Restructuring without behaviour change |

This type feeds into the ADR 0002 branch naming convention:
`{type}/{issue-number}-{kebab-description}`.

### 3. Scan the codebase for context

Invoke `skill({ name: "rs-discover" })` to identify:
- Entry points — where the change starts
- Relevant modules — files that will likely need modification
- Existing tests — test directories, test runners, coverage thresholds
- Configuration files — dependency manifests, CI configs, linter rules

If `rs-discover` is unavailable or the issue is self-contained (e.g., a
dependency bump), skip this step.

### 4. Decompose into implementation phases

Break the work into 3–5 phases. Each phase must be:
- **Independently reviewable** — a reviewer can evaluate it without context
  from later phases
- **Mergeable** — the codebase compiles and tests pass after each phase
- **Scoped** — one phase = one logical unit of change

Phase naming convention: "Phase N: Short Imperative Description"

Typical phase structure for a feature:

| Phase | Content |
|-------|---------|
| 1 | Models and data layer |
| 2 | Validation and serialization |
| 3 | Endpoint / handler wiring |
| 4 | Tests (unit + integration) |

For bugs, a typical structure is:

| Phase | Content |
|-------|---------|
| 1 | Reproduction — write a failing test |
| 2 | Fix the root cause |
| 3 | Regression tests |

### 5. For each phase, document

```markdown
### Phase N: {Description}

**Requirements:**
- What must be true for this phase to be done
- Written as conditions, not tasks

**Files to Change:**
- Exact file paths relative to repo root
- Use glob patterns where multiple files are affected

**Risks:**
- What could go wrong in this phase
- Dependencies on other phases or external changes

**Acceptance Criteria:**
- [ ] Testable, measurable conditions
- [ ] Each criterion verifiable by automation or manual check
- [ ] Prefer "all existing tests pass" over "works correctly"
```

### 6. Define the test strategy

Cover three levels of testing:

| Level | Purpose | Example |
|-------|---------|---------|
| Unit | Isolated module correctness | Test a validator function |
| Integration | Component interaction | Test database write + read |
| End-to-end | Full workflow | Test API endpoint with real DB |

Include the exact command to run tests:

```bash
pytest tests/ -x -v --cov=app
```

### 7. Output the spec document

Write to `.runesmith/{date}-{branch}/specs/{issue-number}-{kebab-title}.md` using this template:

```markdown
---
spec_of: {issue-url}
author: {agent-name}
created: {iso-date}
issue_type: {fix|feat|chore|docs|refactor}
phases: {count}
---

# Spec: {Issue Title}

**Issue**: #{number} — {url}
**Author**: {who created this spec}
**Created**: {date}

## Summary

{2–3 sentences describing the implementation approach}

## Implementation Phases

...

## Test Strategy

{description of what gets tested at what level}

**Command**: `pytest tests/ -x -v --cov=app`
```

## ADR 0002 Compliance

When the spec is consumed by a developer or implementation agent:

- **Branch**: `{type}/{issue-number}-{kebab-description}` — e.g., `feat/42-user-registration`
- **Commit messages**: Conventional Commits format with issue reference — e.g.,
  `feat(api): add user registration endpoint (#42)`
- **PR body**: Include `Closes #{issue-number}` as the final line
- **Labels**: Carry over the issue's type labels to the PR

## Tool Requirements

The calling agent must have these tools available:

| Tool | Required | Purpose |
|------|----------|---------|
| `bash` | Yes | Run `gh issue view` to fetch issue data |
| `gh` | Yes | GitHub CLI for structured issue queries |
| `read` | Yes | Read existing codebase files for context |
| `glob` | Yes | Discover relevant files by pattern |
| `grep` | Yes | Search for imports, references, patterns |
| `edit` | Yes | Write the spec file to `.runesmith/{date}-{branch}/specs/` |
| `webfetch` | No | Fallback for issue fetch when `gh` is unavailable |

## Chained Skills

This skill may direct the agent to load the following skills during execution:

| Skill | When to Chain | Purpose |
|-------|---------------|---------|
| `rs-discover` | Step 3 — codebase scanning | Identify modules, tests, entry points |
| `rs-consult` | When domain expertise is needed | Answer questions about technology choices |
```

## Permission Requirements

The spec-writer agent (the primary consumer of this skill) needs the following permission configuration to execute the skill's instructions:

```yaml
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": deny
    "gh *": allow
  webfetch: allow
  skill:
    "*": allow
    "rs-*": allow
```

The critical design choice is **`bash: { "*": "deny", "gh *": "allow" }`**. The skill needs `gh` to fetch issues, but nothing else from the shell. Locking down bash to a single allowed pattern prevents the agent from running arbitrary commands — the spec-writer is a read-first, write-limited agent and should not execute build commands, run tests, or modify source files. If a future version of the skill needs broader shell access (e.g., to run a test command and capture output), the permission model should be tightened further with an explicit command allow-list rather than a blanket `bash: allow`.

## Comparison with KB's Issue-to-Plan

The Knowledge Base already has a skill analysis at `knowledge/tooling/opencode/skills/issue-to-plan.md`. The two skills share a name and a high-level goal — decompose issues into plans — but diverge in every dimension of execution.

| Dimension | KB `issue-to-plan` | RuneSmith `rs-issue-to-plan` |
|---|---|---|
| **Target output** | Knowledge Base content (ideas, knowledge notes, research) | Code implementation spec (`spec.md`) |
| **Consumer** | KB contributor or research agent | Spec-writer agent (and by extension, developer-agent) |
| **Primary tool** | `gh` + `grep` for KB content discovery | `gh` + `rs-discover` for codebase context |
| **Output location** | KB section folders | `.runesmith/{date}-{branch}/specs/` |
| **Output format** | KB markdown with frontmatter | Spec markdown with YAML frontmatter and phase breakdown |
| **ADR 0002 scope** | Branch naming for content branches (e.g., `research/13-topic`) | Branch naming for code branches (e.g., `feat/42-endpoint`) |
| **Chained skills** | None declared | `rs-discover`, `rs-consult` |
| **Permissions** | `gh`, `grep`, `read`, `bash` | `bash` restricted to `gh *` only |
| **Trigger** | Manual + automatic (webhook) | Manual + chained (from agent prompt) |
| **Phase decomposition** | Steps, approach, effort estimates | Phased with per-phase requirements, files, risks, acceptance criteria |
| **Test strategy** | Not included | Required section (unit/integration/e2e) |
| **Metadata marker** | None | `plugin: "@runicengines/opencode-runesmith"` |

The KB skill is a **content workflow skill** — it plans what to write. The RuneSmith skill is a **code workflow skill** — it plans what to build. The KB skill concludes with a proposal or outline; the RuneSmith skill concludes with a testable, phased implementation blueprint.

## Integration Points

### With the Spec-Writer Agent

The spec-writer agent (designed in `research/opencode-runesmith/agents/spec-writer.md`) loads `rs-issue-to-plan` as its first action. The agent's prompt says:

> Load `skill({ name: "rs-issue-to-plan" })` to begin decomposition.

The skill provides the step-by-step workflow. The agent's prompt provides the role definition, permission model, and output template. The skill is the reusable logic; the agent is the configuration that binds it to a specific context (model, temperature, permissions). This separation means the same skill can be reused by a different agent — for example, an architect agent that loads the skill to validate whether a proposed implementation plan is complete.

### With the Architect Agent

The architect agent may load `rs-issue-to-plan` as a **validation pass** — given a pre-written spec, the architect loads the skill to check that all phases are properly decomposed, acceptance criteria are testable, and the test strategy covers all levels. The architect's perspective adds a review layer without requiring a separate specification-review skill.

### With ADR 0002

The skill hard-codes ADR 0002 conventions because the spec-writer agent is designed to follow them by default. Every spec produced by this skill includes the branch naming pattern, commit message format, and PR body convention. This ensures consistency across all specs without each agent needing to re-learn the conventions.

## Open Questions

### 1. Should the skill include effort estimation guidelines?

The KB's issue-to-plan includes effort estimation. The RuneSmith skill currently does not — effort is left to the developer or implementation agent. Adding effort estimation would require a baseline understanding of the team's velocity and a consistent unit (hours, story points, t-shirt sizes). This may be worth adding in a later iteration once historical data exists.

### 2. Should the skill auto-create a branch for the spec?

Current design says no — the spec is written to `.runesmith/{date}-{branch}/specs/` without a branch. The developer branches when they begin implementation. If spec review is desired (someone other than the author reviews the plan before coding starts), branching could be introduced.

### 3. Should phase numbering be zero-indexed or one-indexed?

The spec-writer agent design uses one-indexed phases (Phase 1, Phase 2, ...). Zero-indexing (Phase 0 for setup/scaffolding) was considered for consistency with conventions in other tools, but the spec-writer design explicitly chose one-indexed because "Phase 0" causes confusion in code review and task tracking. The skill should use one-indexed phases.

## Recommendations

1. **Implement `rs-issue-to-plan` first**, before the spec-writer agent. The agent's prompt depends on this skill existing. (This mirrors the recommendation from the spec-writer analysis.)
2. **Keep the skill body direct and terse** — follow the `gh` skill case study's pattern: short sections, gotcha-first warnings, LLM-scannable prose. The skill is loaded into an agent's context window; every word competes with other context.
3. **Use the full recommended frontmatter** including `metadata.plugin` — it costs nothing and future-proofs the skill for multi-plugin environments.
4. **Do not duplicate ADR 0002 content** — reference it by path (`adr/0002-github-etiquettes/overview.md`) rather than restating its rules. The skill body should say "follow ADR 0002" with a quick-reference table; the full rules live in the ADR itself.
5. **Design for the spec-writer agent**, but keep the skill generic enough that the architect agent can load it for validation passes. Avoid spec-writer-specific language in the skill body (e.g., "you are a spec-writer" — let the agent's prompt handle identity).
