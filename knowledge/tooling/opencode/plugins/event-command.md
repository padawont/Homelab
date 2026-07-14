---
title: "Plugin Command Events"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - commands
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Command Events

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## Command Events

### `command.execute.before`

Fires before a command is executed, allowing plugins to inspect or modify the command before it runs.

**When it fires:** Before the shell spawns a command process.

**Input:**

| Field | Type | Description |
|---|---|---|
| `command` | string | The command string about to be executed |
| `sessionID` | string | The session identifier |
| `arguments` | string | Additional arguments passed to the command |

**Output:**

| Field | Type | Description |
|---|---|---|
| `parts` | array | Array of command parts (splitting the raw command into segments). Modifying this array changes the command that executes. |

**Use case:** Intercept commands to add safety guards, log command execution, or rewrite commands before they reach the shell.

> **Note:** `command.executed` exists as an SSE event (received via the wildcard `event` handler) but is **not** available as a named hook. The only named command hook is `command.execute.before`.

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin Examples](examples.md) — Complete code examples using events
