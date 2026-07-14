---
title: "OpenAI Chat Completions API"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - chat
  - completions
sources:
  - url: "https://platform.openai.com/docs/api-reference/chat"
    title: "OpenAI Chat Completions API Reference"
last_audit_date: 2026-06-09
---

# OpenAI Chat Completions API

## Basic Call

```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
```

## Key Parameters

| Parameter | Type | Description |
|---|---|---|
| `model` | str | Model ID (e.g., `gpt-4o`, `gpt-4o-mini`) |
| `messages` | list | Array of message objects |
| `temperature` | float | Sampling temperature (0–2) |
| `max_tokens` | int | Maximum output tokens (deprecated in favor of `max_completion_tokens`; incompatible with o-series models) |
| `top_p` | float | Nucleus sampling parameter |
| `frequency_penalty` | float | –2 to 2 penalty for token frequency |
| `presence_penalty` | float | –2 to 2 penalty for new topics |
| `stop` | str/list | Stop sequences |

## Response Object

```python
response.id                   # "chatcmpl-..."
response.model                # "gpt-4o"
response.usage.prompt_tokens  # int
response.usage.completion_tokens  # int
response.choices[0].message.content   # str
response.choices[0].finish_reason      # "stop" | "length" | "tool_calls" | "content_filter" | "function_call" (deprecated)
```

See [openai-messages-format.md](./openai-messages-format.md) for message structure, [openai-streaming-basic.md](./openai-streaming-basic.md) for streaming, and [openai-structured-outputs.md](./openai-structured-outputs.md) for JSON mode.
