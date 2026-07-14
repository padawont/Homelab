---
title: "Workflow Skill Patterns"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - workflows
  - patterns
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Workflow Skill Patterns

## Overview

Workflow skills are reusable OpenCode skill templates that encode common development workflows. Unlike domain-specific skills (such as `gh` for GitHub CLI invocation), workflow skills coordinate multiple tools and agent capabilities to guide an agent through a multi-step process from start to finish.

Each pattern documented here follows the same structural conventions as standard skills described in [`configuration.md`](./configuration.md), but emphasizes **trigger conditions**, **tool requirements**, and **permission scoping** — dimensions essential for safe automated execution.

## Common Patterns Across All Workflow Skills

### SKILL.md Naming Convention

All workflow skills follow the standard naming rules from [`configuration.md`](./configuration.md):

- Regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- Directory name matches the `name` field exactly
- File is always named `SKILL.md` (uppercase, no variant)

### Cross-Reference: Skill Discovery

For details on how the agent discovers available skills and matches them to incoming task descriptions, see [`discovery-patterns.md`](./discovery-patterns.md). The discovery mechanism determines which `<available_skills>` entries the agent sees in step 2 of the Agent-Skill Interaction Flow below.

### Permission Design Guidelines

1. **Least privilege**: request only the permissions the skill actually uses. A dependency checker needs `bash` but not `gh`.
2. **Chain permissions via skills**: instead of giving `bash` + `gh` to every agent, load the `gh` skill when needed.
3. **Document required permissions in the skill body**: agents evaluate permissions before loading; explicit documentation avoids silent failures.

### Trigger Classification

| Trigger Class | Behavior | Examples |
|---|---|---|
| Manual | User explicitly invokes the skill via prompt | "review this PR", "check dependencies" |
| Automatic | System event triggers skill without user prompt | Webhook, cron, git hook |
| Chained | Another skill or workflow calls this skill as a sub-step | `pr-packager` calls `changelog-manager` |

### Agent-Skill Interaction Flow

1. Agent receives a task matching the skill's description
2. Agent inspects `<available_skills>` for matching entries
3. Agent calls `skill({ name: "<name>" })` to load the full SKILL.md
4. Skill instructions are injected into the agent's context
5. Agent checks permissions against configured `permission.skill` rules
6. Agent executes the skill's workflow using available tools
7. Agent reports results to the user

### Webhook Bridge

Automatic trigger conditions (see Trigger Classification above) require an external system to bridge the event source and the OpenCode agent. The bridge works as follows:

1. An external system — CI pipeline, webhook handler (e.g., GitHub App, GitLab webhook), cron scheduler, or git hook — detects an event (issue assigned, PR opened, tag pushed).
2. The external system invokes the OpenCode CLI with a carefully crafted prompt that triggers the relevant skill, for example:
   ```bash
   opencode run "Review PR #42 against team conventions"
   ```
3. The agent receives the prompt, inspects `<available_skills>`, and loads the matching skill (e.g., `code-reviewer`).
4. The skill instructions are injected into the agent's context, and execution proceeds from step 4 of Agent-Skill Interaction Flow above.

This design keeps the skill system pure — the agent does not listen for webhooks directly. All webhook routing and prompt generation is handled by the external bridge. The skill only needs to document its automatic trigger conditions so the bridge operator can configure the correct prompts.

### Chained Invocation

Chained invocation occurs when one skill programmatically triggers another as part of its workflow. Unlike webhook bridging, chaining is agent-internal and sequential:

1. The agent loads and executes Skill A (e.g., `pr-packager`) following the standard Agent-Skill Interaction Flow.
2. During execution, Skill A's instructions direct the agent to invoke Skill B (e.g., `changelog-manager`) as a next step.
3. The agent calls `skill({ name: "changelog-manager" })` a second time, loading Skill B's full instructions into context.
4. Skill B is executed independently — there is no return-value contract between skills. Each skill is loaded, executed, and its results are communicated via the agent's own context (variables, file writes, or conversation state).
5. The agent reports combined results to the user after all chained skills complete.

Common chaining scenarios documented in the patterns above:

| Parent Skill | Chained Skill | Trigger |
|---|---|---|
| `pr-packager` | `changelog-manager` | After PR body generation |
| `changelog-manager` | `dependency-checker` | Before a release cut |

Chaining is declared in the parent skill's SKILL.md body (under Expected Skill Body Sections or a dedicated "Chained Skills" section) rather than in its frontmatter, since the decision to chain depends on the workflow context.

## See Also

- [Issue-to-Plan](issue-to-plan.md) — Decompose issues into implementation plans
- [PR Packager](pr-packager.md) — Package PR descriptions from commits
- [Test Helper](test-helper.md) — Run tests and diagnose failures
- [Changelog Manager](changelog-manager.md) — Generate and maintain changelogs
- [Code Reviewer](code-reviewer.md) — Review PRs against conventions
- [Dependency Checker](dependency-checker.md) — Check for vulnerable dependencies
- [Configuration](configuration.md) — SKILL.md format and naming rules
- [Discovery Patterns](discovery-patterns.md) — Discovery skill catalogue
