---
title: "Plugin Chat Events"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - chat
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Chat Events

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## Chat Events

Chat events are named hooks with typed input/output parameters.

### `chat.message`

Fires on chat messages, allowing plugins to observe or react to chat traffic.

**When it fires:** When a chat message is sent or received.

**Input:**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | The session identifier |
| `agent` | string | _Optional._ The agent identifier |
| `model` | object | _Optional._ `{ providerID: string, modelID: string }` |
| `messageID` | string | _Optional._ The message identifier |
| `variant` | string | _Optional._ The message variant |

**Output:**

| Field | Type | Description |
|---|---|---|
| `message` | UserMessage | The chat message object |
| `parts` | Part[] | Array of message parts |

**Use case:** Log chat interactions for analytics. Implement custom chat filtering or augmentation.

### `chat.params`

Modify chat parameters before they are sent to the AI provider.

**When it fires:** Before a chat completion request is dispatched to the LLM.

**Input:**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | The session identifier |
| `agent` | string | The agent identifier |
| `model` | Model | The model configuration object |
| `provider` | ProviderContext | The provider context object |
| `message` | UserMessage | The chat message object |

**Output:**

| Field | Type | Description |
|---|---|---|
| `temperature` | number | Sampling temperature |
| `topP` | number | Top-p nucleus sampling |
| `topK` | number | Top-k sampling |
| `maxOutputTokens` | number | Maximum output token count |
| `options` | object | Additional provider-specific options |

> **Note:** Output fields are flat — there is no `{ params }` wrapper. Each parameter is set directly on the output object.

**Use case:** Inject system messages, adjust model parameters per request, or route to different model endpoints.

### `chat.headers`

Modify HTTP headers sent with chat completion requests.

**When it fires:** Before the HTTP request to the AI provider's API is made.

**Input:**

| Field | Type | Description |
|---|---|---|
| `sessionID` | string | The session identifier |
| `agent` | string | The agent identifier |
| `model` | Model | The model configuration object |
| `provider` | ProviderContext | The provider context object |
| `message` | UserMessage | The chat message object |

**Output:**

| Field | Type | Description |
|---|---|---|
| `headers` | object | Modified headers. Add or override headers here. |

**Use case:** Inject custom authentication headers, API version headers, or tracing metadata.

## See Also

- [Plugin Event Handler Patterns](event-patterns.md) — Named vs wildcard handlers
- [Plugin Examples](examples.md) — Complete code examples using events
