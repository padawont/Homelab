---
title: "Anthropic Messages API"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - messages
  - api
sources:
  - url: "https://docs.anthropic.com/en/api/messages"
    title: "Anthropic Messages API Reference"
last_audit_date: 2026-06-09
---

# Anthropic Messages API

## Basic Call

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ],
)
print(response.content[0].text)
```

## Key Parameters

| Parameter | Type | Description |
|---|---|---|
| `model` | str | Model ID (e.g., `claude-sonnet-4-20250514`) |
| `messages` | list | Array of message objects |
| `max_tokens` | int | Maximum output tokens (required) |
| `system` | str/list | System prompt(s) |
| `temperature` | float | Sampling temperature (0–1) |
| `top_p` | float | Nucleus sampling |
| `stop_sequences` | list | Custom stop sequences |
| `metadata` | dict | User ID, etc. |

## Response Object

```python
response.id              # "msg_..."
response.model           # "claude-sonnet-4-20250514"
response.content         # list of ContentBlock objects
response.content[0].text # str
response.usage.input_tokens   # int
response.usage.output_tokens  # int
response.stop_reason     # "end_turn" | "max_tokens" | "tool_use"
```

See [anthropic-messages-format.md](./anthropic-messages-format.md) for message structure details.
