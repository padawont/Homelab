---
title: "Plugin File Events"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - files
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin File Events

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## File Events

File events are SSE events. They come through the wildcard `event` handler as `{ event: { type: string, properties: {...} } }` and are not individual named hooks with typed input/output parameters.

### `file.edited`

Fires after a file is written or modified through the OpenCode editor tool.

**When it fires:** After the file content has been written to disk by OpenCode's write tool.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `file` | string | Absolute path to the modified file |

**Output:** None. Observation-only event.

**Use case:** Track file modification history. Trigger linting, formatting, or indexing after edits.

### `file.watcher.updated`

Fires when the file watcher detects changes to files outside OpenCode's own write operations.

**When it fires:** When a file system event (create, modify, delete) is detected in a watched directory.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `file` | string | Path of the file that changed |
| `event` | string | Type of change: `"add"`, `"change"`, or `"unlink"` |

**Output:** None. Observation-only event.

**Use case:** Auto-reload plugin configuration when the config file changes on disk. Surface external edits to the user.

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin System Events](event-system.md) — Other SSE observation-only events
