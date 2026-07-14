---
title: "SDK Files API"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - sdk
  - javascript
  - typescript
  - api
  - files
sources:
  - url: "https://opencode.ai/docs/sdk"
    title: "OpenCode SDK Documentation"
  - url: "https://opencode.ai/docs/server"
    title: "OpenCode Server Documentation"
last_audit_date: 2026-06-07
---

# SDK Files API

## `client.find.text({ query })`

Search for text in workspace files using ripgrep-style patterns.

```ts
const matches = await client.find.text({
  query: {
    pattern: "TODO",
    include: "*.ts",
    directory: "src/",
  },
});
// [{ path: "src/index.ts", lines: ["// TODO: ..."], line_number: 10, absolute_offset: 240, submatches: [{ match: "TODO", start: 3, end: 7 }] }]
```

| Field | Type | Description |
|---|---|---|
| `query.pattern` | `string` | Search pattern |
| `query.include` | `string \| string[]` | File glob patterns to include (optional) |
| `query.exclude` | `string \| string[]` | File glob patterns to exclude (optional) |
| `query.directory` | `string` | Subdirectory to restrict search (optional) |
| `query.maxResults` | `number` | Maximum number of results (optional) |
| `query.contextLines` | `number` | Lines of context around each match (optional) |

## `client.find.files({ query })`

Find files or directories by name glob.

```ts
const files = await client.find.files({
  query: { query: "*.ts", type: "file", directory: "src/", limit: 10 },
});
// ["src/index.ts", "src/utils.ts"]
```

| Field | Type | Description |
|---|---|---|
| `query.query` | `string` | File name or glob pattern |
| `query.type` | `"file" \| "directory"` | Filter by filesystem type (optional) |
| `query.directory` | `string` | Subdirectory to restrict search (optional) |
| `query.limit` | `number` | Maximum number of results (1-200, optional) |

## `client.find.symbols({ query })`

Find workspace symbols (functions, classes, variables).

```ts
const symbols = await client.find.symbols({ query: { query: "createOpencode" } });
```

## `client.file.read({ query })`

Read a file from the workspace.

```ts
const content = await client.file.read({ query: { path: "src/index.ts" } });
// { type: "raw" | "patch", content: string }
```

## `client.file.status({ query })`

Get git status for tracked files in the workspace.

```ts
const status = await client.file.status({ query: { directory: "src/" } });
// [{ path: "src/index.ts", status: "modified" }]
```

| Field | Type | Description |
|---|---|---|
| `query.directory` | `string` | Subdirectory to restrict status (optional) |
