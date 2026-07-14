---
title: "Prompt Arguments"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - prompts
  - arguments
  - parameters
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Prompt Arguments

Prompts can accept parameters to customize their output based on the user's request.

## Parameterized prompt

```python
from fastmcp import FastMCP
from fastmcp.prompts import Message

mcp = FastMCP("demo")

@mcp.prompt
def explain_topic(topic: str, level: str = "beginner") -> str:
    """Explain a topic at a given expertise level."""
    return f"""
You are a tutor. Explain the topic '{topic}'
at a {level} level. Use examples and simple language.
"""
```

## Multiple arguments

```python
@mcp.prompt
def code_review(language: str, code_snippet: str) -> list[Message]:
    """Review a code snippet."""
    return [
        Message("You are a senior code reviewer."),
        Message(f"Review this {language} code:\n\n{code_snippet}", role="user"),
    ]
```

## Argument metadata

FastMCP uses Pydantic to derive JSON Schema for prompt arguments. Use type hints and defaults to control what the client sees:

```python
@mcp.prompt
def translate(text: str, target_lang: str = "es") -> str:
    """Translate text to a target language."""
    return f"Translate to {target_lang}: {text}"
```

## Next steps

- [Defining Prompts](./prompts-defining.md)
- [Prompt Templates](./prompt-templates.md)
