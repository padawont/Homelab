---
title: "MCP Logging Protocol"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - logging
  - protocol
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://spec.modelcontextprotocol.io/"
    title: "MCP Specification"
last_audit_date: 2026-06-09
---

# MCP Logging Protocol

MCP defines a logging protocol that lets servers send log messages to the client. FastMCP integrates with Python's standard logging.

## Basic logging

```python
import logging
from fastmcp import FastMCP

logger = logging.getLogger("my-server")
mcp = FastMCP("demo")

@mcp.tool()
def process(data: str) -> str:
    logger.info("Processing data: %s", data[:50])
    return data.upper()
```

## Log levels

MCP supports these levels, mapped from Python's logging:

| Python Level | MCP Level |
|---|---|
| `DEBUG` | `debug` |
| `INFO` | `info` |
| `WARNING` | `warning` |
| `ERROR` | `error` |
| `CRITICAL` | `critical` |

## Logging via context

The `Context` object provides logging methods that route through MCP:

```python
@mcp.tool()
def process(ctx: Context) -> str:
    ctx.info("Processing started")
    ctx.debug("Debug details here")
    return "done"
```

## Setting log level

```python
mcp = FastMCP("demo", settings=FastMCP.Settings(
    log_level="DEBUG"
))
```

## Next steps

- [Tool Context](./tools-context.md)
- [Debugging](./debugging.md)
