---
title: "URI Pattern Resources"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - resources
  - uri
  - patterns
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# URI Pattern Resources

Resources with URI parameters return different data based on the requested path. Use `{placeholders}` in the URI.

## Parameterized URI

```python
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> dict:
    """Get a user's profile by ID."""
    user = db.find_user(int(user_id))
    if user is None:
        raise ValueError(f"User {user_id} not found")
    return user.to_dict()
```

## Multiple URI parameters

```python
@mcp.resource("repos://{owner}/{repo}/readme")
def get_repo_readme(owner: str, repo: str) -> str:
    """Get the README for a GitHub repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    resp = httpx.get(url)
    return base64.b64decode(resp.json()["content"]).decode()
```

## Type coercion

URI parameters are strings by default. Cast to the needed type inside the function.

## Next steps

- [Static vs Dynamic Resources](./resources-static-resources.md)
- [Resource Templates](./resource-templates.md)
