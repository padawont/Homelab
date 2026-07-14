---
title: "Tool Error Handling"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - tools
  - error-handling
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Tool Error Handling

When a tool raises an exception, FastMCP converts it into a structured JSON-RPC error response.

## Custom error messages

```python
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

## Using FastMCPError

FastMCP provides `FastMCPError` for structured protocol errors:

```python
from fastmcp import FastMCP
from fastmcp.exceptions import FastMCPError

mcp = FastMCP("demo")

@mcp.tool()
def lookup_user(user_id: int) -> dict:
    """Look up a user by ID."""
    user = db.find_user(user_id)
    if user is None:
        raise FastMCPError(
            f"Tool error occurred (code -32000): User not found"
        )
    return user
```

## Standard error codes

| Code | Meaning |
|---|---|
| `-32700` | Parse error |
| `-32600` | Invalid request |
| `-32601` | Method not found |
| `-32602` | Invalid params |
| `-32603` | Internal error |
| `-32000` | Server error (custom) |

## Next steps

- [Error Handling Patterns](./error-handling.md)
- [Tool Context](./tools-context.md)
