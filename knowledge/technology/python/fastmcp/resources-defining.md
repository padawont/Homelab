---
title: "Defining Resources"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - resources
  - decorators
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Defining Resources

Resources expose data that an LLM can read — files, API responses, computed values. Decorate a function with `@mcp.resource()`.

## Basic resource

```python
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.resource("config://app/settings")
def get_settings() -> str:
    """Application configuration as JSON."""
    return '{"theme": "dark", "locale": "en-US"}'
```

## Resource URI scheme

Resources use a URI scheme (like `config://` or `data://`) to organize content. Choose a scheme that reflects the data domain:

```python
@mcp.resource("docs://api/overview")
def get_api_docs() -> str:
    return open("README.md").read()

@mcp.resource("db://schema/users")
def get_users_schema() -> str:
    return json.dumps(users_table_schema())
```

## Returning structured data

Resources must return `str`, `bytes`, or `ResourceResult`. For structured data, serialise with `json.dumps()`:

```python
import json

@mcp.resource("users://current")
def get_current_user() -> str:
    return json.dumps({"id": 1, "name": "Alice"})
```

## Next steps

- [Static vs Dynamic Resources](./resources-static-resources.md)
- [URI Pattern Resources](./resources-uri-pattern.md)
- [Resource Templates](./resource-templates.md)
