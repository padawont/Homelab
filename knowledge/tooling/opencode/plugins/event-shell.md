---
title: "Plugin Shell Events"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - shell
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Shell Events

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## Shell Events

### `shell.env`

Fires when the shell environment is being constructed for a command execution. Allows plugins to inject or override environment variables.

**When it fires:** Before each command execution, when OpenCode assembles the environment for the shell process.

**Input:**

| Field | Type | Description |
|---|---|---|
| `cwd` | string | The working directory for the command |
| `sessionID` | string | _Optional._ The session identifier |
| `callID` | string | _Optional._ The call identifier |

**Output:**

| Field | Type | Description |
|---|---|---|
| `env` | object | Environment variables to inject or override. The `env` field is output-only — it does not appear on input. Set properties on this object. |

> **Note:** The input does **not** contain an `env` field. The `env` field is exclusively an output mechanism. The previous input `cwd` and `env` was incorrect — `env` is output-only.

**Use case:** Inject API keys, proxy settings, or project-specific environment variables into all shell commands. Mask sensitive environment variables from the AI.

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin Examples](examples.md) — Inject environment variables example
- [Plugin Tool Events](event-tool.md) — Tool execution events
