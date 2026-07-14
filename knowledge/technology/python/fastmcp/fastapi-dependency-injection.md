---
title: "FastAPI Dependency Injection"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - fastapi
  - dependency-injection
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---
# FastAPI Dependency Injection

When FastMCP is mounted on FastAPI, your tools can access FastAPI's dependency injection via the app's `request.state`.

## Accessing request state

```python
from fastapi import FastAPI, Request
from fastmcp import FastMCP

mcp = FastMCP("my-server")
app = FastAPI()

# Inject db_session via middleware
@app.middleware("http")
async def add_db_session(request: Request, call_next):
    request.state.db = await create_session()
    return await call_next(request)

app.mount("/mcp", mcp.sse_app())
```

## Using state in tools

The `Context` object can surface request state:

```python
@mcp.tool()
async def query_users(ctx: Context) -> list[dict]:
    """List all users from the database."""
    db = ctx.request.state.db
    return await db.fetch_all("SELECT * FROM users")
```

## Alternative: passing through app state

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.startup()
async def init():
    mcp.state.db = await create_session()

@mcp.tool()
async def get_user(user_id: int, ctx: Context) -> dict:
    db = mcp.state.db
    return await db.fetch_one(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    )
```

## Next steps

- [Mounting FastMCP on FastAPI](./mounting-fastapi.md)
- [FastAPI Shared Middleware](./fastapi-shared-middleware.md)
- [Lifecycle Hooks](./lifecycle-hooks.md)
