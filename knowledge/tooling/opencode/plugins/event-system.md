---
title: "Plugin System Events"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - messages
  - lsp
  - installation
  - server
  - todo
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin System Events

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## Installation Events

Installation events are SSE events. They come through the wildcard `event` handler as `{ event: { type: string, properties: {...} } }` and are not individual named hooks.

### `installation.updated`

Fires when the OpenCode installation state changes, typically after plugin installs or updates.

**When it fires:** After a plugin is installed, updated, or removed, and the plugin registry is refreshed.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `version` | string | The new version after the update |

**Output:** None. Observation-only event.

**Use case:** Log installation changes for audit trails. Re-initialize plugin state after an update.

## LSP Events

LSP events are SSE events. They come through the wildcard `event` handler as `{ event: { type: string, properties: {...} } }` and are not individual named hooks.

### `lsp.client.diagnostics`

Fires when the LSP client receives diagnostics (warnings, errors, hints) from a language server.

**When it fires:** After the language server publishes diagnostics for a file, typically on save or as the user types.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `serverID` | string | Identifier of the language server |
| `path` | string | The file path the diagnostics apply to |

**Output:** None. Observation-only event.

**Use case:** Collect diagnostic statistics across a project. Display diagnostic counts in a status bar widget.

### `lsp.updated`

Fires when the LSP server connection state changes.

**When it fires:** When the LSP server transitions between states (starting, running, stopping, stopped, error).

**Properties (`event.properties`):** Open-ended object `{[key: string]: unknown}`. The payload shape varies by server implementation.

**Output:** None. Observation-only event.

**Use case:** Show LSP server status in the UI. Automatically restart an LSP server after a crash.

## Message Events

Message events are SSE events. They come through the wildcard `event` handler as `{ event: { type: string, properties: {...} } }` and are not individual named hooks.

### `message.part.removed`

Fires when a part of a chat message (e.g., a code block, a text segment) is removed from the conversation.

**When it fires:** When a user or the system removes a specific part of a message, typically during editing.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | The session identifier |
| `messageID` | string | Identifier of the parent message |
| `partID` | string | Identifier of the removed part |

**Output:** None. Observation-only event.

**Use case:** Track conversation edits for audit logs. Maintain a local cache synchronized with conversation state.

### `message.part.updated`

Fires when a message part is modified, such as when streaming content updates mid-generation.

**When it fires:** As the LLM streams a response, each chunk update to a message part triggers this event.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `part` | Part | The updated Part object |
| `delta` | string | _Optional._ The incremental content delta, if applicable |

**Output:** None. Observation-only event.

**Use case:** Implement real-time conversation display or streaming transcription.

### `message.removed`

Fires when an entire message is deleted from the conversation.

**When it fires:** When a user deletes a message or the system prunes conversation history.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | The session identifier |
| `messageID` | string | Identifier of the removed message |

**Output:** None. Observation-only event.

**Use case:** Synchronize external conversation stores. Maintain undo history for message deletions.

### `message.updated`

Fires when a message's metadata or content is updated (excluding part-level granularity).

**When it fires:** When a message's content or metadata changes, typically after editing or after a stream completes.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `info` | Message | The full Message object after the update |

**Output:** None. Observation-only event.

**Use case:** Persist conversation state to external storage. Trigger post-processing on completed assistant messages.

## Server Events

Server events are SSE events. They come through the wildcard `event` handler as `{ event: { type: string, properties: {...} } }` and are not individual named hooks.

### `server.connected`

Fires when the OpenCode server establishes a connection.

**When it fires:** After a successful server connection is established at startup or after reconnection.

**Properties (`event.properties`):** Open-ended object `{[key: string]: unknown}`. The payload shape varies by server implementation.

**Output:** None. Observation-only event.

**Use case:** Display connection status in the UI. Initialize plugins that depend on server availability.

## Todo Events

Todo events are SSE events. They come through the wildcard `event` handler as `{ event: { type: string, properties: {...} } }` and are not individual named hooks.

### `todo.updated`

Fires when a todo item is created, completed, or modified.

**When it fires:** On any change to a todo item in the OpenCode todo system.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | The session identifier |
| `todos` | Array<Todo> | Array of Todo objects for the session |

**Output:** None. Observation-only event.

**Use case:** Integrate OpenCode todos with external task management systems. Track completion metrics.

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin Session Events](event-session.md) — Session lifecycle SSE events
- [Plugin File Events](event-file.md) — File-related SSE events
