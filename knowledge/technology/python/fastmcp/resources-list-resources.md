---
title: "FastMCP Resources and Resource Listing"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - resources
  - listing
  - protocol
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://modelcontextprotocol.io/specification/latest/server/resources.md"
    title: "MCP Resources Specification"
last_audit_date: 2026-06-09
---

# FastMCP Resources and Resource Listing

The MCP client calls `resources/list` to discover what data the server exposes.

## Automatic registration

Every `@mcp.resource()` decorated function is registered automatically. Static resources appear directly in the listing.

## What the client receives

```json
{
  "resources": [
    {
      "uri": "config://app/settings",
      "name": "get_settings",
      "description": "Application configuration as JSON",
      "mimeType": "text/plain"
    }
  ]
}
```

## Resources with URI templates

Parameterized resources expose a template rather than listing every possible URI. See [Resource Templates](./resource-templates.md).

## Manual resource registration

```python
from fastmcp.resources import TextResource

my_resource = TextResource(
    uri="docs://manual/example",
    name="my_resource",
    description="Example manual resource",
    text="Hello from a manually registered resource!"
)
mcp.add_resource(my_resource)
```

## Next steps

- [Resource Templates](./resource-templates.md)
- [URI Pattern Resources](./resources-uri-pattern.md)
