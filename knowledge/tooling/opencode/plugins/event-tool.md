---
title: "Plugin Tool Events"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - tools
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Tool Events

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## Tool Events

### `tool.execute.before`

Fires before a tool is invoked, allowing plugins to inspect, modify, or block the execution.

**When it fires:** After the tool has been selected and arguments parsed, but before the `execute` function runs.

**Input:**

| Field | Type | Description |
|---|---|---|
| `tool` | string | The name of the tool about to be executed |
| `sessionID` | string | The session identifier |
| `callID` | string | The call identifier |

**Output:**

| Field | Type | Description |
|---|---|---|
| `args` | object | Tool arguments. The `args` field is output-only — it is **not** available on the input object. Set properties on this object to modify what the tool receives. |

Throwing an error from this handler blocks the tool from executing entirely.

> **Note:** The input does **not** contain the tool's arguments. Arguments are only available via the output `args` field. If you need to inspect the arguments, use `tool.execute.after` instead, which receives them on input.

**Use case:** Implement access control for specific tools. Add required flags or parameters to tool calls. Block dangerous operations (e.g., prevent reading `.env` files) by throwing an error.

### `tool.execute.after`

Fires after a tool finishes execution, giving plugins access to the result.

**When it fires:** After the tool's `execute` function completes, whether successful or not.

**Input:**

| Field | Type | Description |
|---|---|---|
| `tool` | string | The name of the tool that was executed |
| `sessionID` | string | The session identifier |
| `callID` | string | The call identifier |
| `args` | object | The arguments that were passed to the tool (available here, unlike `tool.execute.before`) |

**Output:**

| Field | Type | Description |
|---|---|---|
| `title` | string | Modified title for the tool result display |
| `output` | string | Modified output content |
| `metadata` | object | Modified metadata object |

> **Note:** There is no single `result` field on input or output. The output is structured into `title`, `output`, and `metadata` independently.

**Use case:** Transform tool outputs for post-processing. Log tool execution results. Filter sensitive data from tool responses before they reach the conversation.

### `tool.definition`

Allows plugins to define tool metadata or modify tool definitions.

**When it fires:** During plugin initialization, when tools are being registered.

**Input:**

| Field | Type | Description |
|---|---|---|
| `toolID` | string | The tool identifier |

**Output:**

| Field | Type | Description |
|---|---|---|
| `description` | string | The tool description |
| `parameters` | any | The tool's input schema (JSON Schema) |

**Use case:** Register custom tool schemas, modify tool descriptions, or annotate tools with metadata for the AI to use during tool selection.

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin Examples](examples.md) — .env protection and custom tools examples
- [Plugin Permission Events](event-permission.md) — Related access control events
