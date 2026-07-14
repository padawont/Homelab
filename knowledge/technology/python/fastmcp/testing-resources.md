---
title: "Testing Resource Handlers"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - testing
  - resources
  - pytest
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Testing Resource Handlers

Resource handler functions are plain Python or async functions — test them directly.

## Testing static resources

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.resource("config://app/version")
def get_version() -> str:
    return "2.1.0"
```

```python
# test_server.py
from server import get_version

def test_get_version():
    result = get_version()
    assert result == "2.1.0"
```

## Testing parameterized resources

```python
# server.py
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> dict:
    return {"id": int(user_id), "name": "Test User"}
```

```python
# test_server.py
from server import get_user_profile

def test_get_user_profile():
    result = get_user_profile("42")
    assert result["id"] == 42
    assert result["name"] == "Test User"
```

## Testing resources with errors

```python
def test_get_user_profile_not_found():
    with pytest.raises(ValueError, match="not found"):
        get_user_profile("999")
```

## Next steps

- [Testing Tools](./testing-tools.md)
- [Testing Prompts](./testing-prompts.md)
- [Testing with MCP Client](./testing-with-mcp-client.md)
