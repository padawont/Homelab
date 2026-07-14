---
title: "Troubleshooting FastMCP"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - troubleshooting
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Troubleshooting FastMCP

Common issues and their solutions when working with FastMCP.

## "ModuleNotFoundError: No module named 'fastmcp'"

```bash
# Ensure fastmcp is installed
uv add fastmcp

# Verify installation
uv run python -c "import fastmcp"
```

## "Connection refused" with SSE

```bash
# Check if the port is already in use
lsof -i :8000

# Use a different port
mcp.run(transport="sse", port=9090)
```

## Tool not showing up in client

- Ensure the `@mcp.tool()` decorator is applied to the function
- Check that the module is imported before `mcp.run()`
- Verify the function has type annotations

## stdio mode hangs

```python
# Make sure your script has this guard
if __name__ == "__main__":
    mcp.run()  # transport defaults to stdio

# Without it, the client may hang waiting for the server
```

## Schema validation errors

```bash
# Test your Pydantic model directly
from pydantic import BaseModel

class MyInput(BaseModel):
    name: str
    count: int = 0

# Check schema
print(MyInput.model_json_schema())
```

## JSON-RPC parse errors

- Ensure all handler return types are JSON-serializable
- Avoid returning custom objects without `.model_dump()` or serialization
- Use `dict`, `list`, `str`, `int`, `float`, `bool`, or `None`

## Next steps

- [Debugging](./debugging.md)
- [Error Handling](./error-handling.md)
