---
title: "Static vs Dynamic Resources"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - resources
  - static
  - dynamic
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Static vs Dynamic Resources

Resources in FastMCP can be static (fixed content) or dynamic (computed per request).

## Static resources

Static resources return the same content every time. They have a fixed URI:

```python
@mcp.resource("config://app/version")
def get_version() -> str:
    return "2.1.0"
```

## Dynamic resources

Dynamic resources use URI parameters to compute content per request:

```python
@mcp.resource("data://weather/{city}")
def get_weather(city: str) -> str:
    """Current weather for a city."""
    resp = httpx.get(f"https://api.weather.com/{city}")
    return resp.text
```

## When to use each

| Type | Use case | Example |
|---|---|---|
| Static | Config, constants, docs | `config://app/settings` |
| Dynamic | Per-item lookups | `users://{id}/profile` |

## Listing behavior

- Static resources are listed directly in `resources/list`
- Dynamic resources are typically listed via [ResourceTemplates](./resource-templates.md)

## Next steps

- [URI Pattern Resources](./resources-uri-pattern.md)
- [Resource Templates](./resource-templates.md)
