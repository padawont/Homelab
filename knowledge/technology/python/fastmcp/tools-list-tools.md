---
title: "How Tools Are Listed"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - tools
  - listing
  - protocol
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://spec.modelcontextprotocol.io/"
    title: "MCP Specification"
last_audit_date: 2026-06-09
---

# How Tools Are Listed

When an MCP client connects, it calls `tools/list` to discover available tools. FastMCP handles this automatically.

## Automatic discovery

Every `@mcp.tool()` decorated function is registered and included in the `tools/list` response. No extra wiring needed.

## What the client receives

The response is a list of tool definitions with JSON Schema for parameters:

```json
{
  "tools": [
    {
      "name": "add",
      "description": "Add two numbers together.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "a": {"type": "integer"},
          "b": {"type": "integer"}
        },
        "required": ["a", "b"]
      }
    }
  ]
}
```

## Manual registration (if needed)

```python
async def my_tool(x: int) -> int:
    return x * 2

mcp.add_tool(my_tool, name="double")
```

## Next steps

- [Defining Tools](./tools-defining.md)
- [List Resources](./resources-list-resources.md)
- [List Prompts](./prompts-defining.md)
