---
title: "Mounting FastMCP on FastAPI"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - fastapi
  - mounting
  - asgi
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://gofastmcp.com/integrations/fastapi.md"
    title: "FastAPI Integration — official docs"
last_audit_date: 2026-06-09
---

# Mounting FastMCP on FastAPI

FastMCP can be mounted as a sub-application on a FastAPI app. This lets you share routes, middleware, and infrastructure.

## Basic mounting

```python
from fastapi import FastAPI
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def hello(name: str) -> str:
    return f"Hello, {name}!"

mcp_app = mcp.http_app(path="/mcp")
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)
```

## With prefix

```python
# All MCP endpoints available under /api/mcp/
app.mount("/api/mcp", mcp.http_app())
```

## Separate lifespan

The FastAPI app and FastMCP server have independent lifespans. Coordinate startup/shutdown via lifecycle hooks:

```python
@mcp.startup()
async def init_mcp():
    ...

@mcp.shutdown()
async def cleanup_mcp():
    ...
```

## Why mount?

- Share a single HTTP server (port, TLS)
- Add FastAPI routes alongside MCP endpoints
- Apply FastAPI middleware (CORS, auth) to MCP
- Use FastAPI dependency injection

## Next steps

- [FastAPI Shared Middleware](./fastapi-shared-middleware.md)
- [FastAPI Dependency Injection](./fastapi-dependency-injection.md)
- [Transport: SSE](./transport-sse.md)
