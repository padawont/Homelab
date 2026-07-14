---
title: "Server Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - server
  - configuration
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Server Configuration

FastMCP servers can be configured via constructor arguments and a `Settings` object.

## Name and version

```python
from fastmcp import FastMCP

mcp = FastMCP(
    "data-service",
    version="2.1.0"
)
```

The `name` is sent to the client during the `initialize` handshake. The `version` is optional but recommended for protocol compatibility tracking.

## Settings fields

```python
settings = FastMCP.Settings(
    log_level="DEBUG",              # one of DEBUG, INFO, WARNING, ERROR
    rate_limit=100,                 # max requests per minute (0 = unlimited)
    max_payload_size=5_000_000,     # max incoming message bytes
    read_timeout=30,                # seconds before read timeout
    write_timeout=30,               # seconds before write timeout
)
```

## Environment-based configuration

```python
import os
from fastmcp import FastMCP

settings = FastMCP.Settings(
    log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
    rate_limit=int(os.getenv("MCP_RATE_LIMIT", "100")),
)
mcp = FastMCP("my-server", settings=settings)
```

## Next steps

- [Server Initialization](./server-initialization.md)
- [Lifecycle Hooks](./lifecycle-hooks.md)
