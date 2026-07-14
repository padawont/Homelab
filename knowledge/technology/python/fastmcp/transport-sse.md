---
title: "SSE Transport"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - transport
  - sse
  - http
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://modelcontextprotocol.io/specification/draft/"
    title: "MCP Specification"
  - url: "https://modelcontextprotocol.io/specification/2024-11-05/basic/transports/"
    title: "MCP Specification (2024-11-05)"
last_audit_date: 2026-06-09
---

# SSE transport

> **Deprecated:** SSE transport is deprecated in favor of Streamable HTTP (`transport="http"`). Use HTTP transport for all new projects. SSE remains available only for compatibility with older clients. See [FastMCP deployment docs](https://gofastmcp.com/deployment/running-server.md).

Server-Sent Events (SSE) transport exposes the MCP server over HTTP, enabling remote clients to connect.

## Running with SSE

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

# Start SSE server on default port 8000
if __name__ == "__main__":
    mcp.run(transport="sse")
```

## Custom host and port

```python
mcp.run(transport="sse", host="0.0.0.0", port=9090)
```

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/sse` | GET | Client connects to receive events |
| `/messages/` | POST | Client sends JSON-RPC messages |

## How it works

1. Client opens an SSE connection to `/sse`
2. Server sends `endpoint` event with the `/messages/` URL
3. Client sends JSON-RPC messages via `POST /messages/`
4. Server pushes responses and events over the SSE stream

## Events

| Event | Purpose |
|---|---|
| `endpoint` | Tells client where to POST messages |
| `message` | JSON-RPC response or notification |

## Next steps

- [Transport: stdio](./transport-stdio.md)
- [Mounting FastMCP on FastAPI](./mounting-fastapi.md)
