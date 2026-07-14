---
title: "Test Helper Workflow Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - workflows
  - testing
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Test Helper Workflow Skill

## Purpose

Run tests, parse failures, and suggest corrections. The skill identifies the test framework in use, executes the test suite (or a subset), interprets failure output, and proposes targeted fixes.

## When to Invoke

When the user asks "run tests", "fix this test", "why is this test failing", or when a CI check fails and the agent is asked to diagnose.

## Trigger Conditions

| Condition | Type |
|---|---|
| User provides a test command or file path | Manual |
| CI failure report posted to PR | Automatic (webhook) |
| File change detected in test files | Automatic (watch mode) |

## Required Permissions

| Permission | Purpose |
|---|---|
| `bash` | Run test commands, install dependencies |
| `read` | Read test files, config files, CI output |
| `grep` | Search for test patterns, error signatures |
| `glob` | Locate test files and configuration |

## Agent Tool Requirements

The agent needs `bash` for execution and `read`/`grep`/`glob` for analysis. No special agent persona is required, but the agent must have `permission.bash` configured to allow arbitrary command execution.

## Example SKILL.md Frontmatter

```yaml
---
name: test-helper
description: Run tests, parse failures, identify test framework, suggest targeted fixes
license: MIT
compatibility: opencode
metadata:
  workflow: testing
  audience: developers
  trigger: manual+automatic
---
```

## Expected Skill Body Sections

- Framework detection (pytest, vitest, cargo test, go test, etc.)
- Targeted test execution (single file, single test, entire suite)
- Failure output parsing (stack traces, assertion diffs)
- Common failure pattern catalog
- Suggested fix format (present diffs, not apply them automatically)
- Retry confirmation loop

## See Also

- [Code Reviewer](code-reviewer.md) — Complementary review of code quality after tests pass
- [Workflow Patterns](workflow-patterns.md) — Cross-cutting conventions for all workflow skills
