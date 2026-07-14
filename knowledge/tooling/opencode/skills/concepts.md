---
title: "Skill Concepts"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Skill Concepts

## What Are Skills?

OpenCode agent skills are reusable instruction bundles (markdown files) discovered from skill directories and loaded **on-demand** by agents via the `skill` tool. They are not injected into every conversation — only pulled in when the agent determines they are relevant.

## Skills vs Agents

| Aspect | Agent | Skill |
|---|---|---|
| Scope | Full assistant configuration | Lightweight instruction bundle |
| Configuration | System prompt, model, permissions, tools | Freeform markdown + frontmatter metadata |
| Invocation | Tab, @mention, or Task tool | On-demand via `skill()` tool call |
| Permissions | Full permission model | No permissions — controlled via agent's `permission.skill` |

## See Also

- [File Format](file-format.md) — SKILL.md structure and naming rules
- [Skill Tool Mechanism](tool-mechanism.md) — How the `skill` tool works
- [Configuration](configuration.md) — SKILL.md frontmatter specification and discovery paths
