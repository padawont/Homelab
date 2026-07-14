---
title: "Plugin Session Events"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - session
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Session Events

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## Session Events

Session events are SSE events. They come through the wildcard `event` handler as `{ event: { type: string, properties: {...} } }` and are not individual named hooks.

### `session.created`

Fires when a new OpenCode session begins.

**When it fires:** At session initialization, after the project is loaded and the plugin system is ready.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `info` | Session | The full Session object |

**Output:** None. Observation-only event.

**Use case:** Initialize session-scoped resources. Start session timers.

### `session.compacted`

Fires after a session compaction completes, when the conversation history has been summarized and older messages pruned.

**When it fires:** After the LLM has generated a continuation summary and the conversation state has been updated.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | Unique session identifier |

> **Note:** There is no `summary` field in this event's properties.

**Output:** None. Observation-only event.

**Use case:** Log compaction summaries for long-running session analysis. Notify the user that compaction occurred.

### `session.deleted`

Fires when a session is ended and its state is cleaned up.

**When it fires:** On session teardown, after any cleanup routines have run.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `info` | Session | The full Session object |

**Output:** None. Observation-only event.

**Use case:** Release session-scoped resources. Save final session metrics.

### `session.diff`

Fires when a session diff is generated, representing the changes made during the session.

**When it fires:** Periodically or on demand, when OpenCode computes a diff of workspace changes.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | Unique session identifier |
| `diff` | Array<FileDiff> | Array of file diff objects representing the changes |

**Output:** None. Observation-only event.

**Use case:** Generate session change summaries. Store diffs for later review or rollback.

### `session.error`

Fires when a session encounters an error.

**When it fires:** On any unhandled error within the session lifecycle, such as LLM API failures or internal errors.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | _Optional._ Unique session identifier |
| `error` | ProviderAuthError \| UnknownError \| ... | The error object (union type), not a plain string |

**Output:** None. Observation-only event.

**Use case:** Implement error reporting and telemetry. Trigger fallback or recovery logic.

### `session.idle`

Fires when a session becomes idle after a period of inactivity.

**When it fires:** After a configurable idle timeout with no user or AI activity.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | Unique session identifier |

> **Note:** There is no `idleDuration` field in this event's properties.

**Output:** None. Observation-only event.

**Use case:** Auto-save work, send idle notifications, or trigger cleanup tasks after inactivity.

### `session.status`

Fires when the session status changes.

**When it fires:** On transitions between session states (e.g., active, idle, error, compacting).

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | Unique session identifier |
| `status` | SessionStatus | The session status object (union type), not a plain string |

> **Note:** There is no `previousStatus` field in this event's properties.

**Output:** None. Observation-only event.

**Use case:** Drive UI indicators that reflect session state. Trigger behaviors on specific status transitions.

### `session.updated`

Fires when session metadata or configuration is updated.

**When it fires:** When session properties change, such as mode switching or configuration updates.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `info` | Session | The full updated Session object |

**Output:** None. Observation-only event.

**Use case:** Persist session configuration changes. Synchronize session state across multiple clients.

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin Examples](examples.md) — Notification example using session events
- [Plugin Compaction Hooks](event-compaction.md) — Session compaction hooks
