---
title: "Plugin TUI Events"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - tui
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin TUI Events

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## TUI Events

TUI events are SSE events. They come through the wildcard `event` handler as `{ event: { type: string, properties: {...} } }` and are not individual named hooks.

### `tui.prompt.append`

Fires when content is appended to the user input prompt in the terminal UI.

**When it fires:** When text is programmatically added to the prompt area, such as context insertion.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `text` | string | The text being appended |

**Output:** None. Observation-only event.

**Use case:** Track prompt modifications for UX analytics. Implement custom prompt decoration.

### `tui.command.execute`

Fires when a command is executed through the TUI command palette.

**When it fires:** When the user runs a command from the command palette or via a keyboard shortcut.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `command` | string | The command identifier |

**Output:** None. Observation-only event.

**Use case:** Register custom TUI commands. Intercept existing commands to add behavior before the default handler runs.

### `tui.toast.show`

Fires when a toast notification is displayed in the TUI.

**When it fires:** When OpenCode shows a transient notification message to the user.

**Properties (`event.properties`):**

| Field | Type | Description |
|---|---|---|
| `message` | string | The toast message text |
| `variant` | string | The toast severity: `"info"`, `"success"`, `"warning"`, `"error"` |
| `title` | string | _Optional._ The toast title |

**Output:** None. Observation-only event.

**Use case:** Forward toast notifications to external notification systems (desktop notifications, webhooks).

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin Session Events](event-session.md) — Session lifecycle SSE events
- [Plugin System Events](event-system.md) — Other SSE observation-only events
