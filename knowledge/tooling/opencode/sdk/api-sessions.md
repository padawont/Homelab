---
title: "SDK Sessions API"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - sdk
  - javascript
  - typescript
  - api
  - sessions
sources:
  - url: "https://opencode.ai/docs/sdk"
    title: "OpenCode SDK Documentation"
  - url: "https://opencode.ai/docs/server"
    title: "OpenCode Server Documentation"
last_audit_date: 2026-06-07
---

# SDK Sessions API

Full CRUD plus specialized session operations. All session methods requiring a session ID pass it via `path.id`:

```ts
client.session.get({ path: { id: sessionId } });
```

## `client.session.list()`

List all sessions.

```ts
const sessions = await client.session.list();
```

## `client.session.get({ path })`

Get a single session by ID.

```ts
const session = await client.session.get({ path: { id: sessionId } });
```

## `client.session.children({ path })`

Get child sessions of a given session (created by subagent invocations).

```ts
const children = await client.session.children({ path: { id: sessionId } });
```

## `client.session.create({ body })`

Create a new session.

```ts
const session = await client.session.create({
  body: { title: "My Session" },
});
```

| Field | Type | Description |
|---|---|---|
| `body.title` | `string` | Session title (optional) |
| `body.parentID` | `string` | Parent session ID for child sessions (optional) |

## `client.session.delete({ path })`

Delete a session.

```ts
await client.session.delete({ path: { id: sessionId } });
```

## `client.session.update({ path, body })`

Update session metadata.

```ts
await client.session.update({
  path: { id: sessionId },
  body: { title: "Updated Title" },
});
```

| Field | Type | Description |
|---|---|---|
| `body.title` | `string` | Updated session title (optional) |

## `client.session.init({ path, body })`

Analyze the application and create or update `AGENTS.md`.

```ts
await client.session.init({
  path: { id: sessionId },
  body: { messageID: "...", providerID: "anthropic", modelID: "claude-sonnet-4-20250514" },
});
```

| Field | Type | Description |
|---|---|---|
| `body.messageID` | `string` | Message ID to start analysis from (required) |
| `body.providerID` | `string` | Provider ID (required) |
| `body.modelID` | `string` | Model ID (required) |

## `client.session.abort({ path })`

Abort a currently running session.

```ts
await client.session.abort({ path: { id: sessionId } });
```

## `client.session.share({ path })` / `client.session.unshare({ path })`

Share or unshare a session (makes it accessible to other users in multi-user setups).

```ts
await client.session.share({ path: { id: sessionId } });
await client.session.unshare({ path: { id: sessionId } });
```

## `client.session.summarize({ path, body })`

Request a summary of the session history.

```ts
await client.session.summarize({
  path: { id: sessionId },
  body: { providerID: "anthropic", modelID: "claude-sonnet-4-20250514" },
});
```

| Field | Type | Description |
|---|---|---|
| `body.providerID` | `string` | Provider ID for the summarization model |
| `body.modelID` | `string` | Model ID for the summarization model |

## `client.session.fork({ path, body })`

Fork an existing session at a specific message.

```ts
const forked = await client.session.fork({
  path: { id: sessionId },
  body: { messageID: messageId },
});
```

| Field | Type | Description |
|---|---|---|
| `body.messageID` | `string` | Message ID to fork at (optional) |

## `client.session.diff({ path, query })`

Get the file diff for a session.

```ts
const diff = await client.session.diff({
  path: { id: sessionId },
  query: { messageID: messageId },
});
// { file: string, before: string, after: string, additions: number, deletions: number }[]
```

| Field | Type | Description |
|---|---|---|
| `query.messageID` | `string` | Message ID to get diff for (optional) |

## `client.session.todo({ path })`

Get the todo list for a session.

```ts
const todos = await client.session.todo({ path: { id: sessionId } });
// [{ content: "...", status: "pending", priority: "high", id: "..." }]
```

## `client.session.permissions({ path, body })`

Respond to a permission request for a session.

```ts
await client.session.permissions({
  path: { id: sessionId, permissionID: permissionId },
  body: { response: "allow", remember: false },
});
```

| Field | Type | Description |
|---|---|---|
| `path.permissionID` | `string` | Permission request ID |
| `body.response` | `string` | Response: "allow" or "deny" |
| `body.remember` | `boolean` | Remember this decision (optional) |

## `client.session.messages({ path })`

Retrieve all messages in a session.

```ts
const messages = await client.session.messages({ path: { id: sessionId } });
// [{ info: Message, parts: Part[] }, ...]
```

## `client.session.message({ path })`

Retrieve a single message by ID.

```ts
const message = await client.session.message({
  path: { id: sessionId, messageID: messageId },
});
// { info: Message, parts: Part[] }
```

## `client.session.prompt({ path, body })`

Send a prompt to the session. This is the core interaction method.

```ts
const result = await client.session.prompt({
  path: { id: sessionId },
  body: {
    parts: [{ type: "text", text: "Refactor this function" }],
    noReply: false,
    format: { type: "json_schema", schema: { /* ... */ } },
  },
});
```

| Field | Type | Description |
|---|---|---|
| `body.parts` | `Part[]` | Message content parts (required) |
| `body.model` | `object` | Model override: `{ providerID, modelID }` (optional) |
| `body.agent` | `string` | Agent override (optional) |
| `body.noReply` | `boolean` | If true, injects context without expecting a response (optional) |
| `body.system` | `string` | System prompt override (optional) |
| `body.tools` | `ToolDef[]` | Tool definitions (optional) |
| `body.format` | `object` | Structured output format (optional) |

When `noReply: true`, the message is injected as context for subsequent prompts without consuming a model generation turn and returns a `UserMessage`. The default returns an `AssistantMessage`.

## `client.session.command({ path, body })`

Execute a slash command (e.g., `/help`, `/settings`).

```ts
const result = await client.session.command({
  path: { id: sessionId },
  body: { command: "/help" },
});
```

| Field | Type | Description |
|---|---|---|
| `body.messageID` | `string` | Message ID to associate command with (optional) |
| `body.agent` | `string` | Agent override (optional) |
| `body.model` | `object` | Model override: `{ providerID, modelID }` (optional) |
| `body.command` | `string` | Command name |
| `body.arguments` | `string` | Command arguments (optional) |

## `client.session.shell({ path, body })`

Run a shell command in the session's workspace context.

```ts
const result = await client.session.shell({
  path: { id: sessionId },
  body: { agent: "build", command: "npm test" },
});
```

| Field | Type | Description |
|---|---|---|
| `body.agent` | `string` | Agent name to execute the command (required) |
| `body.model` | `object` | Model override: `{ providerID, modelID }` (optional) |
| `body.command` | `string` | Shell command to execute (required) |

## `client.session.revert({ path, body })` / `client.session.unrevert({ path })`

Revert a message or undo a revert.

```ts
await client.session.revert({
  path: { id: sessionId },
  body: { messageID: messageId },
});

await client.session.unrevert({ path: { id: sessionId } });
```

| Field | Type | Description |
|---|---|---|
| `body.messageID` | `string` | Message ID to revert |
| `body.partID` | `string` | Specific part ID to revert (optional) |
