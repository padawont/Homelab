---
title: "Issue-to-Plan Workflow Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - workflows
  - planning
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Issue-to-Plan Workflow Skill

## Purpose

Decompose a GitHub issue into a structured implementation plan. The skill reads the issue body and comments, analyzes requirements, breaks work into steps, suggests an approach, and estimates effort.

## When to Invoke

An agent should load this skill when the task mentions "plan this issue", "break down", "create implementation plan", or when the user pastes a GitHub issue URL without a pre-existing plan.

## Trigger Conditions

| Condition | Type |
|---|---|
| Issue URL or number provided in conversation | Manual (user prompt) |
| `@mentioned` in a GitHub issue comment with `/plan` | Automatic |
| New issue assigned to a project board column | Automatic (webhook) |

## Required Permissions

| Permission | Purpose |
|---|---|
| `gh` | Read issue details, list comments, check labels and milestones |
| `grep` | Search existing knowledge notes for related context |
| `read` | Load existing plans, templates, and project documentation |
| `bash` | Run `gh` CLI commands, optionally create local plan files |

## Agent Tool Requirements

The agent must have access to the `gh` skill (to invoke GitHub CLI correctly) and the `write` tool for creating plan documents. The agent should have the `plan` or `general` persona with `permission.skill: { "gh": "allow" }`.

## Example SKILL.md Frontmatter

```yaml
---
name: issue-to-plan
description: Decompose a GitHub issue into a structured implementation plan with steps, approach, and effort estimates
license: MIT
compatibility: opencode
metadata:
  workflow: planning
  audience: developers
  trigger: manual+automatic
---
```

## Expected Skill Body Sections

- Requirements extraction from issue body and comments
- Existing context search (knowledge base, related issues, ADRs)
- Breakdown into implementation steps
- Effort estimation guidelines
- Plan output format (template reference)

## See Also

- [PR Packager](pr-packager.md) — Next step after planning, prepare PR from implementation
- [Workflow Patterns](workflow-patterns.md) — Cross-cutting conventions for all workflow skills
