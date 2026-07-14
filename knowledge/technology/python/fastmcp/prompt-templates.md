---
title: "Prompt Templates"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - prompts
  - templates
  - rendering
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Prompt Templates

Prompt templates let you build structured outputs using string formatting or message lists.

## f-string template

```python
@mcp.prompt()
def greet(name: str, language: str = "en") -> str:
    """Generate a greeting."""
    greetings = {"en": "Hello", "es": "Hola", "fr": "Bonjour"}
    greeting = greetings.get(language, "Hello")
    return f"{greeting}, {name}!"
```

## Message list template

```python
@mcp.prompt()
def tutorial(topic: str, difficulty: str) -> list[dict]:
    """Create a tutorial prompt with examples."""
    return [
        {
            "role": "system",
            "content": f"You are a {difficulty}-level tutor.",
        },
        {
            "role": "user",
            "content": f"Teach me about {topic}. Include examples.",
        },
    ]
```

## Conditional content in templates

```python
@mcp.prompt()
def debug_help(code: str, error: str | None = None) -> list[dict]:
    """Help debug code with optional error context."""
    messages = [
        {"role": "system", "content": "You are a Python debugging assistant."},
        {"role": "user", "content": f"Debug this code:\n\n{code}"},
    ]
    if error:
        messages.append({
            "role": "user",
            "content": f"The error I'm seeing is: {error}",
        })
    return messages
```

## Next steps

- [Prompt Arguments](./prompt-arguments.md)
- [Defining Prompts](./prompts-defining.md)
