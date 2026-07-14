---
title: "Async Tools"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - tools
  - async
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Async Tools

FastMCP supports both sync and async tool definitions. Async tools are useful for I/O-bound operations like API calls or database queries.

## Async tool

```python
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.tool
async def fetch_data(url: str) -> dict:
    """Fetch data from a URL."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
```

## Mixing sync and async

You can freely mix sync and async tools on the same server:

```python
@mcp.tool
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool
async def fetch_users() -> list[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.example.com/users")
        return resp.json()
```

## Performance considerations

- Use `async` for HTTP calls, DB queries, file I/O
- Use `sync` for CPU-bound computation
- FastMCP runs sync tools in a thread pool to avoid blocking the event loop

## Next steps

- [Defining Tools](./tools-defining.md)
- [Pydantic Input Models](./tools-pydantic-input.md)
- [Tool Context](./tools-context.md)
