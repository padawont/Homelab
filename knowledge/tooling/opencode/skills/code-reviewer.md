---
title: "Code Reviewer Workflow Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - workflows
  - review
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Code Reviewer Workflow Skill

## Purpose

Review pull requests against team conventions. The skill analyzes diffs for style violations, security issues, performance concerns, and structural problems, then generates structured review comments.

## When to Invoke

When a PR review is requested via GitHub, the user says "review this PR", "check my changes", or a CI workflow triggers review on new commits.

## Trigger Conditions

| Condition | Type |
|---|---|
| PR review requested via GitHub | Automatic (webhook) |
| User asks for review in chat | Manual |
| PR opened or new commits pushed | Automatic (configurable) |

## Required Permissions

| Permission | Purpose |
|---|---|
| `gh` | Fetch PR diff, post review comments |
| `bash` | Run linters, formatters, security scanners |
| `read` | Read project conventions, style guides |
| `grep` | Search for patterns in diff |
| `glob` | Locate config files and convention docs |

## Agent Tool Requirements

The agent needs the `gh` skill for PR operations and `bash` for running local analysis tools — see [`gh-case-study.md`](./gh-case-study.md) for detailed usage patterns. The agent should have the `kb-editor` persona if reviewing within a knowledge base context.

## Example SKILL.md Frontmatter

```yaml
---
name: code-reviewer
description: Review pull requests against team conventions, analyze diffs for style, security, performance issues, generate structured comments
license: MIT
compatibility: opencode
metadata:
  workflow: github
  audience: developers
  trigger: manual+automatic
---
```

## Expected Skill Body Sections

- PR diff acquisition (`gh pr diff` or `git fetch + diff`)
- Style guide conformance checks
- Security scan patterns (hardcoded secrets, injection vectors, unsafe deserialization)
- Performance anti-patterns (N+1 queries, large payloads, sync I/O in hot paths)
- Structural review (architecture fit, layering violations)
- Comment generation format (file:line annotations, severity levels)
- Inline vs summary comment strategy

## See Also

- [Test Helper](test-helper.md) — Complementary testing workflow
- [gh-case-study.md](gh-case-study.md) — Detailed `gh` skill walkthrough
- [Issue-to-Plan](issue-to-plan.md) — Review implementation plans against code
- [Workflow Patterns](workflow-patterns.md) — Cross-cutting conventions for all workflow skills
