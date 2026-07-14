---
title: "Server Initialization"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - server
  - initialization
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Server Initialization

The `FastMCP` constructor creates an MCP server instance.

## Basic usage

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")
```

## Constructor parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | required | Server name, sent during initialization |
| `version` | `str` | `"1.0.0"` | Server version |
| `settings` | `FastMCP.Settings` | default | Configuration object |

## Settings object

```python
from fastmcp import FastMCP

settings = FastMCP.Settings(
    log_level="INFO",
    rate_limit=100,        # requests per minute
    max_payload_size=1_000_000,
)
mcp = FastMCP("my-server", settings=settings)
```

## The app pattern

`FastMCP` follows an app-like pattern. You define handlers after construction:

```python
mcp = FastMCP("my-server")

@mcp.tool()
def my_tool(x: int) -> int:
    return x * 2
```

## Next steps

- [Server Configuration](./server-configuration.md)
- [Transport: SSE](./transport-sse.md)
- [Transport: stdio](./transport-stdio.md)
