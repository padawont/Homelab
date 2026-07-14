---
title: "OpenAI Message Format"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - messages
  - roles
sources:
  - url: "https://platform.openai.com/docs/api-reference/chat/create"
    title: "OpenAI Chat Completions API Reference"
last_audit_date: 2026-06-09
---

# OpenAI Messages Format

## Message Roles

### System

```python
{"role": "system", "content": "You are a helpful assistant."}
```

Sets behavior and persona. Optional but recommended.

### User

```python
{"role": "user", "content": "What is the capital of France?"}
```

Multi-part content with images:

```python
{
    "role": "user",
    "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "https://..."}}
    ]
}
```

### Assistant

```python
{"role": "assistant", "content": "The capital of France is Paris."}
```

For tool calls, include `tool_calls`:

```python
{"role": "assistant", "content": None, "tool_calls": [...]}
```

### Tool

```python
{"role": "tool", "tool_call_id": "call_abc123", "content": "Result"}
```

## Conversation Flow

Messages are ordered chronologically. The API uses the full message history for context.

See [openai-tool-calling.md](./openai-tool-calling.md) for tool message details and [openai-chat-completions.md](./openai-chat-completions.md) for the base API.
