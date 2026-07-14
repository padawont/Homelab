---
title: "Integration — FastMCP Events"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - fastmcp
  - integration
sources:
  - url: "https://fastapi.tiangolo.com/"
    title: "FastAPI Documentation"
last_audit_date: 2026-06-09
---

# Integration — FastMCP Events

Mount a FastMCP server as a sub-application under FastAPI:

```python
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("My MCP Server")


@mcp.tool()
async def get_weather(city: str) -> str:
    return f"Weather data for {city}"


@mcp.resource("config://app")
async def get_config() -> str:
    return "App configuration data"


# Mount FastMCP under FastAPI
app.mount("/mcp", mcp.sse_app())
```

## How it works

- `FastMCP` provides an `.sse_app()` that returns an ASGI app
- `app.mount("/mcp", mcp.sse_app())` mounts it at the `/mcp` prefix
- Clients connect via SSE to `/mcp/sse`

## Multiple MCP servers

```python
mcp_v1 = FastMCP("v1")
mcp_v2 = FastMCP("v2")

app.mount("/mcp/v1", mcp_v1.sse_app())
app.mount("/mcp/v2", mcp_v2.sse_app())
```

## CORS and shared middleware

See [integration-fastmcp-middleware.md](./integration-fastmcp-middleware.md) for shared middleware patterns between FastAPI and FastMCP.

See also [mounting-sub-apps.md](./mounting-sub-apps.md) for general sub-application mounting.
