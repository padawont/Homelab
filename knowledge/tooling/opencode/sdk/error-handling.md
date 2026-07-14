---
title: "SDK Error Handling"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - sdk
  - javascript
  - typescript
  - errors
sources:
  - url: "https://opencode.ai/docs/sdk"
    title: "OpenCode SDK Documentation"
  - url: "https://opencode.ai/docs/server"
    title: "OpenCode Server Documentation"
last_audit_date: 2026-06-07
---

# SDK Error Handling

By default (`throwOnError: false`), HTTP-level errors are returned on the response data rather than thrown. The SDK can still throw for certain invalid operations, such as accessing a non-existent session:

```ts
try {
  const session = await client.session.get({ path: { id: "invalid-id" } });
} catch (error) {
  console.error("Failed to get session:", (error as Error).message);
}
```

## throwOnError

When `throwOnError: true` is passed to `createOpencodeClient`, all HTTP error status codes are thrown instead of returned.

## Structured Output Validation Failures

Structured output validation failures are never thrown. They are returned on the response data under `info.error`:

```ts
if (result.data.info.error?.name === "StructuredOutputError") {
  console.error(
    "Failed to produce structured output:",
    result.data.info.error.message,
  );
}
```
