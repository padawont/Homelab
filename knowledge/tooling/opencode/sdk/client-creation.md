---
title: "SDK Client Creation"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - sdk
  - javascript
  - typescript
  - client
sources:
  - url: "https://opencode.ai/docs/sdk"
    title: "OpenCode SDK Documentation"
  - url: "https://opencode.ai/docs/server"
    title: "OpenCode Server Documentation"
last_audit_date: 2026-06-07
---

# SDK Client Creation

Two factory functions are available depending on whether you need to start a server or connect to an existing one.

## `createOpencode()`

Starts an OpenCode server and returns a client connected to it. This is the simplest entry point for scripts that need a full session.

```ts
import { createOpencode } from "@opencode-ai/sdk";

const { client } = await createOpencode({
  hostname: "127.0.0.1",
  port: 4096,
  signal: AbortSignal.timeout(5000),
  timeout: 5000,
  config: {
    /* inline config overrides */
  },
});
```

| Option | Type | Default | Description |
|---|---|---|---|
| `hostname` | `string` | `"127.0.0.1"` | Server bind address |
| `port` | `number` | `4096` | Server port |
| `signal` | `AbortSignal` | `undefined` | Abort signal for cancellation |
| `timeout` | `number` | `5000` | Timeout in ms for server start |
| `config` | `Config` | `{}` | Inline configuration overrides |

The returned object also exposes a `server` property, which provides `server.url` and `server.close()` for lifecycle management.

```ts
const opencode = await createOpencode();
console.log(`Server running at ${opencode.server.url}`);
// ... use opencode.client for SDK calls
opencode.server.close();
```

## `createOpencodeClient()`

Connects to an already-running OpenCode server. Use this when the server lifecycle is managed externally (e.g., an existing editor instance).

```ts
import { createOpencodeClient } from "@opencode-ai/sdk";

const client = createOpencodeClient({
  baseUrl: "http://localhost:4096",
});
```

| Option | Type | Default | Description |
|---|---|---|---|
| `baseUrl` | `string` | `"http://localhost:4096"` | URL of the server |
| `fetch` | `typeof fetch` | `globalThis.fetch` | Custom fetch implementation |
| `parseAs` | `string` | `"auto"` | Response parsing method |
| `responseStyle` | `string` | `"fields"` | Return style: `data` or `fields` |
| `throwOnError` | `boolean` | `false` | Throw errors instead of returning on response data |
