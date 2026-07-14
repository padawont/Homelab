---
title: "Anthropic Extended Thinking"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - thinking
  - extended
sources:
  - url: "https://docs.anthropic.com/en/docs"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# Anthropic Extended Thinking

## Enabling Thinking

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    thinking={"type": "enabled", "budget_tokens": 2048},
    messages=[{"role": "user", "content": "Solve a complex math problem"}],
)
```

## Accessing Thinking Content

```python
for block in response.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Response: {block.text}")
```

## Requirements

- `max_tokens` must be at least `budget_tokens + 1024`
- Not all models support thinking mode
- When thinking is enabled, `temperature` cannot be set (it forces 1.0)

## Streaming with Thinking

```python
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    thinking={"type": "enabled", "budget_tokens": 2048},
    messages=[{"role": "user", "content": "Complex problem"}],
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(f"Thinking: {event.delta.thinking}", end="")
            elif event.delta.type == "text_delta":
                print(f"Text: {event.delta.text}", end="")
```

See [anthropic-streaming.md](./anthropic-streaming.md) for streaming patterns.
