---
title: "Testing Prompt Templates"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - testing
  - prompts
  - pytest
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Testing Prompt Templates

Prompt functions are plain Python functions — test the rendered output directly.

## Testing string prompts

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.prompt()
def greet(name: str, language: str = "en") -> str:
    greetings = {"en": "Hello", "es": "Hola"}
    greeting = greetings.get(language, "Hello")
    return f"{greeting}, {name}!"
```

```python
# test_server.py
from server import greet

def test_greet_default():
    result = greet("Alice")
    assert "Hello, Alice!" in result

def test_greet_spanish():
    result = greet("Bob", language="es")
    assert "Hola, Bob!" in result
```

## Testing message list prompts

```python
# server.py
from fastmcp import FastMCP
from fastmcp.prompts import Message

mcp = FastMCP("demo")

@mcp.prompt()
def code_review(language: str, code: str) -> list:
    return [
        Message(f"Review the following {language} code:\n\n{code}"),
        Message("I'll review the code for bugs, style, and best practices.", role="assistant"),
    ]
```

```python
# test_server.py
from server import code_review

def test_code_review_prompt():
    result = code_review("python", "print('hello')")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].role == "user"
    assert result[1].role == "assistant"
    assert "python" in result[0].content.text
```

## Testing edge cases

```python
def test_greet_unknown_language():
    result = greet("Alice", language="de")
    assert "Hello, Alice!" in result  # fallback to "Hello"
```

## Next steps

- [Testing Tools](./testing-tools.md)
- [Testing Resources](./testing-resources.md)
- [Testing with MCP Client](./testing-with-mcp-client.md)
