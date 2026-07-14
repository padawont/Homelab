---
title: "Resource Templates"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - resources
  - templates
  - uri
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://spec.modelcontextprotocol.io/"
    title: "MCP Specification"
last_audit_date: 2026-06-09
---

# Resource Templates

Resource templates tell the client about parameterized resources without enumerating every possible URI.

## How templates work

When you define a resource with `{parameters}` in the URI, FastMCP generates a `ResourceTemplate`:

```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> dict:
    ...
```

This creates the template: `users://{user_id}/profile`

## Template in listing

```json
{
  "resourceTemplates": [
    {
      "uriTemplate": "users://{user_id}/profile",
      "name": "get_user_profile",
      "description": "Get a user's profile by ID"
    }
  ]
}
```

## Multiple templates

```python
@mcp.resource("docs://{lang}/{section}")
def get_docs(lang: str, section: str) -> str:
    ...

@mcp.resource("data://{year}/{month}/summary")
def get_monthly_summary(year: str, month: str) -> str:
    ...
```

## Client workflow

1. Client fetches `resources/list`, sees templates
2. Client substitutes concrete values into the URI
3. Client calls `resources/read` with the concrete URI
4. Server matches the URI to the handler and returns data

## Next steps

- [URI Pattern Resources](./resources-uri-pattern.md)
- [Resources Listing](./resources-list-resources.md)
