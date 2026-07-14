---
title: "Rate Limiting"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - rate-limiting
  - throttling
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Rate Limiting

FastMCP provides built-in rate limiting to control how many requests the server processes per minute.

## Configuration

```python
from fastmcp import FastMCP

settings = FastMCP.Settings(
    rate_limit=60  # max 60 requests per minute
)
mcp = FastMCP("demo", settings=settings)
```

## How it works

When `rate_limit` is set, FastMCP tracks incoming requests in a sliding window. If the limit is exceeded, the server returns a JSON-RPC error:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Rate limit exceeded"
  },
  "id": 1
}
```

## Disabling rate limiting

```python
settings = FastMCP.Settings(
    rate_limit=0  # unlimited
)
```

## Per-tool limits (custom)

For per-tool rate limiting, implement a wrapper:

```python
import time
from functools import wraps

def rate_limited(max_per_minute: int):
    interval = 60.0 / max_per_minute
    last_call = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < interval:
                raise ValueError("Rate limit exceeded for this tool")
            last_call[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@mcp.tool()
@rate_limited(10)
def expensive_tool(data: str) -> str:
    ...
```

## Next steps

- [Server Configuration](./server-configuration.md)
- [Error Handling](./error-handling.md)
