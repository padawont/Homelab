---
title: "Agent Concepts"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - agents
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-07
---

## What OpenCode Agents Are

Specialized AI assistants configured for specific tasks. Each agent has a custom system prompt, model override, permission set, temperature, and optional step cap. Agents are the unit of capability — they determine what tools are available and what context the model receives.

## Primary vs Subagent

| Aspect | Primary | Subagent |
|---|---|---|
| Who invokes | User via Tab | User via @mention or primary via `task` tool |
| Mode field value | `primary/all` | `subagent/all` |
| Default mode | `all` | `all` |
| Hidden agents | Hidden from @ autocomplete | Hidden from @ autocomplete but reachable via `task` tool |
| Session navigation | Owns a tab in the session bar | Creates child sessions under the invoking primary |
| Model | Uses global config | Inherits from invoker |

The `mode` field accepts `primary`, `subagent`, or `all` (default). It determines how the agent can be used — as a primary agent, a subagent, or either. Tool access is controlled by `permission`, not `mode`. Hidden agents (`"hidden": true`) are suppressed from the @mention autocomplete list but can still be invoked programmatically by a primary agent via the `task` tool.

## Built-in Agents

| Name | Mode | Hidden | Purpose |
|---|---|---|---|
| Build | primary | no | Default agent, all tools available |
| Plan | primary | no | Analysis-restricted toolset for design thinking |
| General | subagent | no | Multi-step subtasks delegated by primaries |
| Explore | subagent | no | Read-only code search and file reading |
| Scout | subagent | no | Read-only external research via WebFetch |
| Compaction | primary | yes | Automatic context window compression |
| Title | primary | yes | Automatic session title generation |
| Summary | primary | yes | Automatic session summary generation |

## See Also

- [configuration](configuration.md)
- [permissions](permissions.md)
- [discovery](discovery.md)
- [interactions](interactions.md)
- [lifecycle](lifecycle.md)
