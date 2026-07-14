---
title: "MCP Specification (2025-11-25)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - mcp
  - protocol
  - json-rpc
sources:
  - url: "https://modelcontextprotocol.io/specification/2025-11-25/"
    title: "MCP Specification (2025-11-25)"
last_audit_date: 2026-06-09
---

# MCP Protocol Basics

The Model Context Protocol (MCP) is a JSON-RPC 2.0-based protocol that lets LLM clients discover and invoke capabilities on a server.

## JSON-RPC foundation

MCP defines three JSON-RPC message types:

- **Requests** — `jsonrpc`, `id` (string or integer, never null), `method`, `params?` (optional)
- **Responses** — `jsonrpc`, `id` (matching the request), plus either `result` (success) or `error` (with `code`, `message`, and optional `data`)
- **Notifications** — `jsonrpc`, `method`, `params?` (optional), and **no `id`** (one-way messages that expect no response)

FastMCP handles serialization and deserialization automatically.

## Core capabilities

| Capability | Purpose | Decorator |
|---|---|---|
| Tools | Callable functions | `@mcp.tool()` |
| Resources | URI-addressable data | `@mcp.resource()` |
| Prompts | Template prompts | `@mcp.prompt()` |

## Protocol lifecycle

1. **Initialize** — Client sends `initialize` with protocol version + capabilities; server responds with its capabilities
2. **Initialized** — Client sends `notifications/initialized` to signal it is ready for normal operations
3. **List** — Client calls `tools/list`, `resources/list`, or `prompts/list` to discover available handlers
4. **Call/Read** — Client invokes a tool (`tools/call`), reads a resource (`resources/read`), or gets a prompt (`prompts/get`)
5. **Shutdown** — Client or server closes the transport

## Capability negotiation

During initialization the server advertises what it supports:

```python
mcp = FastMCP("my-server")
# FastMCP automatically advertises tools, resources, and prompts
```

## Transport layer

MCP supports two transport modes:
- **Streamable HTTP** — see [transport-sse.md](./transport-sse.md)
- **stdio** over stdin/stdout — see [transport-stdio.md](./transport-stdio.md)

## Next steps

- [Server Initialization](./server-initialization.md)
