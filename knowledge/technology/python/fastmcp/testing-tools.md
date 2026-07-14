---
title: "Testing Tool Functions"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - testing
  - tools
  - pytest
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Testing Tool Functions

Tool functions are plain Python functions — test them directly with standard pytest patterns.

## Unit testing tools

```python
# demo.py
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

```python
# test_demo.py
import pytest
from demo import add

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_add_edge_cases():
    assert add(0, 0) == 0
    assert add(1_000_000, 2_000_000) == 3_000_000
```

## Testing async tools

```python
@pytest.mark.asyncio
async def test_fetch_data():
    result = await fetch_data("https://example.com/data.json")
    assert "key" in result
```

## Testing tools with Pydantic input

```python
from demo import SearchParams, search

def test_search_with_model():
    params = SearchParams(query="python", limit=5)
    results = search(params)
    assert len(results) <= 5
```

## Next steps

- [Testing Resources](./testing-resources.md)
- [Testing Prompts](./testing-prompts.md)
- [Testing with MCP Client](./testing-with-mcp-client.md)
