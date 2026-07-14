---
title: "Lifecycle Hooks"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - lifecycle
  - hooks
  - startup
  - shutdown
sources:
      - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Lifecycle Hooks

FastMCP provides hooks that run on server startup and shutdown for initialization and cleanup.

## Startup hook

```python
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.startup()
async def init_db():
    """Initialize database connection on startup."""
    await db.connect()
    mcp.state.db = db
```

## Shutdown hook

```python
@mcp.shutdown()
async def close_db():
    """Close database connection on shutdown."""
    await mcp.state.db.close()
```

## Multiple hooks

You can define multiple startup/shutdown hooks. They run in registration order:

```python
@mcp.startup()
async def first():
    ...

@mcp.startup()
async def second():
    ...
```

## Sync hooks

```python
@mcp.startup()
def load_config():
    import json
    with open("config.json") as f:
        mcp.state.config = json.load(f)
```

## Typical use cases

| Hook | Use |
|---|---|
| `startup` | Connect DB, load config, init clients |
| `shutdown` | Close connections, flush logs, clean up |

## Next steps

- [Server Configuration](./server-configuration.md)
- [Server Middleware](./server-middleware.md)
