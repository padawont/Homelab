---
title: "Defining Tools"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - tools
  - decorators
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Defining Tools

Tools are callable functions that LLMs can invoke. Decorate a function with `@mcp.tool()` to expose it.

## Basic tool

```python
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

## Tool with a custom name

```python
@mcp.tool(name="calculate-sum")
def add(a: int, b: int) -> int:
    return a + b
```

## Docstring as description

The function's docstring becomes the tool description sent to the LLM. Write clear, actionable descriptions:

```python
@mcp.tool()
def fetch_weather(city: str) -> str:
    """Get the current weather for a given city.
    
    Args:
        city: The city name (e.g., "London", "Tokyo")
    """
    return get_weather(city)
```

## Type hints matter

FastMCP uses Pydantic to generate JSON Schema from type hints. Always annotate parameters and return types.

## Next steps

- [Pydantic Input Models](./tools-pydantic-input.md)
- [Async Tools](./tools-async-tools.md)
- [Tool Error Handling](./tools-error-handling.md)
- [Tool Context](./tools-context.md)
