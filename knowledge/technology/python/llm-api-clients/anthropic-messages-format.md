---
title: "Anthropic Message Format"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - messages
  - roles
  - content-blocks
sources:
  - url: "https://docs.anthropic.com/en/docs"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# Anthropic Message Format

## Roles

Only two roles:

```python
{"role": "user", "content": "Hello"}
{"role": "assistant", "content": "Hi!"}
```

## Content Blocks

Content can be a string or a list of content blocks:

```python
{"role": "user", "content": "Hello"}
```

Multi-part content:

```python
{
    "role": "user",
    "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image", "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "..."
        }},
    ]
}
```

## Assistant with Tool Use

```python
{
    "role": "assistant",
    "content": [
        {"type": "text", "text": "I'll look up the weather."},
        {"type": "tool_use", "id": "toolu_...", "name": "get_weather", "input": {"location": "Paris"}},
    ]
}
```

## Tool Result

```python
{
    "role": "user",
    "content": [
        {"type": "tool_result", "tool_use_id": "toolu_...", "content": "Sunny, 22°C"},
    ]
}
```

See [anthropic-messages-api.md](./anthropic-messages-api.md) for the base API and [anthropic-system-prompts.md](./anthropic-system-prompts.md) for system prompts.
