---
title: "Plugin Compaction and Experimental Hooks"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - experimental
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://github.com/anomalyco/opencode"
    title: "OpenCode Source Code (plugin package)"
last_audit_date: 2026-06-07
---

# Plugin Compaction and Experimental Hooks

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## Experimental Hooks

### `experimental.session.compacting`

Fires before the LLM generates a continuation summary during session compaction. Allows plugins to influence what context is preserved when the conversation history is compressed.

**When it fires:** During session compaction, before the compaction prompt is sent to the LLM.

**Input:**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | Unique session identifier |

> **Note:** The input object does **not** contain `conversationLength` or `compactionThreshold`. Only `sessionID` is available on input.

**Output:**

| Field | Type | Description |
|---|---|---|
| `context` | array | Array of strings. Use `output.context.push(...)` to inject additional context sections into the compaction prompt. |
| `prompt` | string | _Optional._ Set this to completely replace the compaction prompt sent to the LLM. When set, `context` is ignored. |

**Use case:** Inject domain-specific context (task status, important decisions, active files) that the default compaction prompt would not capture. For advanced use cases, replace the entire compaction prompt.

**Example -- inject additional context:**

```javascript
"experimental.session.compacting": async (input, output) => {
  output.context.push(`## Custom Context

Include any state that should persist across compaction:
- Current task status
- Important decisions made
- Files being actively worked on`);
}
```

**Example -- replace the compaction prompt entirely:**

```javascript
"experimental.session.compacting": async (input, output) => {
  output.prompt = `You are generating a continuation prompt for a multi-agent swarm session.

Summarize:
1. The current task and its status
2. Which files are being modified and by whom
3. Any blockers or dependencies between agents
4. The next steps to complete the work

Format as a structured prompt that a new agent can use to resume work.`;
}
```

### `experimental.chat.messages.transform`

Allows plugins to transform the messages array before it is sent to the LLM.

**When it fires:** Before the chat completion request is dispatched, after messages are assembled.

**Input:** Empty object `{}`. No input fields.

**Output:**

| Field | Type | Description |
|---|---|---|
| `messages` | array | Array of transformed messages. Each element is `{ info: Message, parts: Part[] }`. |

**Use case:** Inject or remove messages from the conversation context before the LLM sees them. Redact sensitive information from messages.

### `experimental.chat.system.transform`

Allows plugins to modify the system prompt sent to the LLM.

**When it fires:** Before the chat completion request, when the system prompt is being assembled.

**Input:**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | _Optional._ The session identifier |
| `model` | Model | The model configuration object |

**Output:**

| Field | Type | Description |
|---|---|---|
| `system` | array | Array of system prompt strings to send to the LLM |

**Use case:** Inject project-specific context, coding conventions, or security instructions into the system prompt.

### `experimental.compaction.autocontinue`

Fires to control auto-continuation behavior after session compaction.

**When it fires:** After compaction completes, to determine whether to automatically continue the conversation.

**Input:**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | Unique session identifier |
| `agent` | string | The agent identifier |
| `model` | Model | The model configuration object |
| `provider` | ProviderContext | The provider context object |
| `message` | UserMessage | The chat message object |
| `overflow` | boolean | Whether the context window is overflowing |

**Output:**

| Field | Type | Description |
|---|---|---|
| `enabled` | boolean | Set to `true` to auto-continue, `false` to stop |

**Use case:** Prevent auto-continuation for sessions that have reached a natural stopping point. Force continuation for long-running background tasks.

### `experimental.text.complete`

Allows plugins to handle text completion requests.

**When it fires:** When a text completion (as opposed to chat completion) is requested.

**Input:**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | The session identifier |
| `messageID` | string | The message identifier |
| `partID` | string | The part identifier |

**Output:**

| Field | Type | Description |
|---|---|---|
| `text` | string | The completed text |

**Use case:** Implement custom completion providers or pre/post-process completion responses.

### `experimental.provider.small_model`

Fires to allow overriding the model for specific tasks.

**When it fires:** When OpenCode selects a model for a task, before the selection is finalized.

**Input:**

| Field | Type | Description |
|---|---|---|
| `provider` | ProviderV2 | The current provider context |

**Output:**

| Field | Type | Description |
|---|---|---|
| `model` | ModelV2 | _Optional._ The model to use as an override for this task |

**Use case:** Intercept and redirect specific operations to a smaller/faster model to reduce costs or latency.

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin Session Events](event-session.md) — Session lifecycle events
- [Plugin Examples](examples.md) — Compaction hook examples
