---
title: "Plugin Permission Events"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - permissions
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Permission Events

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## Permission Events

### `permission.ask`

Fires when OpenCode requires user permission for a sensitive operation (e.g., file write, command execution, network access).

**When it fires:** Before the permission dialog is shown to the user. Plugins can inspect and respond to requests.

**Input:**

| Field | Type | Description |
|---|---|---|
| `permission` | string | The permission identifier (e.g., `"bash"`, `"write"`, `"network"`) |
| `metadata` | object | Context-specific details about the requested operation |

**Output:**

| Field | Type | Description |
|---|---|---|
| `status` | string | One of `"ask"` (show dialog), `"deny"` (auto-deny), or `"allow"` (auto-grant) |

> **Note:** `permission.replied` exists as an SSE event (received via the wildcard `event` handler) but is **not** available as a named hook. The only named permission hook is `permission.ask`, whose output `status` field controls the three possible outcomes.

**Use case:** Auto-approve permissions for trusted projects. Auto-deny risky operations (e.g., network access in a sensitive directory).

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin Tool Events](event-tool.md) — Tool execution events for access control complements
