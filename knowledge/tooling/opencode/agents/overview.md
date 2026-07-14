---
title: "OpenCode Agents"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - agents
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
  - url: "https://opencode.ai/docs/tools"
    title: "OpenCode Tools Documentation"
last_audit_date: 2026-06-07
---

# OpenCode Agents

Reference documentation for the OpenCode agent system: agent types, configuration, permissions, discovery, lifecycle, interactions, role-based profiles, and context loading.

## Files

- [concepts](concepts.md) — What agents are, primary vs subagent comparison, and the built-in agents table.
- [interactions](interactions.md) — How agents interact with the `skill` tool and the `task` tool.
- [lifecycle](lifecycle.md) — Primary agent access, subagent invocation, custom agent creation, hidden system agents, and session navigation shortcuts.
- [configuration](configuration.md) — Agent definition formats (JSON and Markdown), all configuration options with defaults.
- [discovery](discovery.md) — Agent definition locations, auto-discovery mechanism, explicit registration, naming conventions, and precedence.
- [permissions](permissions.md) — Permission model, keys reference, shorthand vs object form, bash/task/skill granularity, and global vs per-agent defaults.
- [context-loading](context-loading.md) — How `AGENTS.md` and instruction files are consumed via `instructions`, `prompt`, and lazy loading patterns.
- [roles](roles.md) — Pre-assembled subagent role profiles for domain-specific tasks: Architect, Tech-Lead, Developer, Test-Specialist, and more.
- [composition-patterns](composition-patterns.md) — Common workflow patterns pairing primaries with specialist subagents, review pipelines, and best practices.
- [orchestration-patterns](orchestration-patterns.md) — Multi-agent coordination patterns: hub-and-spoke, gated pipeline, chain-of-responsibility, and skill-routing.
