---
title: "Defining Prompts"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - prompts
  - decorators
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Defining Prompts

Prompts are reusable templates that produce structured messages for the LLM. Decorate a function with `@mcp.prompt()`.

## Basic prompt

```python
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.prompt()
def system_prompt() -> str:
    """System-level instructions."""
    return "You are a helpful assistant that speaks concisely."
```

## Prompt with messages

Return a list of message objects for multi-turn prompts:

```python
@mcp.prompt()
def chat_starter() -> list[dict]:
    return [
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user", "content": "Help me debug this Python code."},
    ]
```

## How prompts appear to the client

When the client calls `prompts/list`, FastMCP returns the prompt name and description. The client can then call `prompts/get` to retrieve the rendered content.

## Next steps

- [Prompt Arguments](./prompt-arguments.md)
- [Prompt Templates](./prompt-templates.md)
