---
title: "Anthropic Streaming"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - streaming
sources:
  - url: "https://docs.anthropic.com/en/docs/build-with-claude/streaming"
    title: "Anthropic Streaming Guide"
last_audit_date: 2026-06-09
---

# Anthropic Streaming

## Sync Streaming

```python
from anthropic import Anthropic

client = Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Count to 5"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="")
```

## Using Stream Events

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            print(event.delta.text, end="")
```

## Async Streaming

```python
import asyncio
from anthropic import AsyncAnthropic

async def main():
    client = AsyncAnthropic()
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}],
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="")

asyncio.run(main())
```

## Final Message

After streaming completes, get the full message:

```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="")
    message = stream.get_final_message()
    print(f"Tokens: {message.usage.input_tokens + message.usage.output_tokens}")
```

See [anthropic-tool-use-streaming.md](./anthropic-tool-use-streaming.md) for streaming with tool use.
