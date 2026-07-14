---
title: "Anthropic System Prompts"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - system-prompt
sources:
  - url: "https://docs.anthropic.com/en/docs"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# Anthropic System Prompts

## Simple System Prompt

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are a helpful assistant that speaks like a pirate.",
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
)
print(response.content[0].text)
```

## Multiple System Messages

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {"type": "text", "text": "You are a helpful assistant."},
        {"type": "text", "text": "Always respond in JSON format."},
        {"type": "text", "text": "Keep responses under 100 tokens."},
    ],
    messages=[{"role": "user", "content": "Hello"}],
)
```

## System Prompt Overrides

Later system texts can override earlier ones when the same instruction is provided. Combine with `temperature=0` for more deterministic behavior.

See [anthropic-messages-api.md](./anthropic-messages-api.md) for the Messages API reference.
