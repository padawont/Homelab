---
title: "OpenAI Async Streaming"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - streaming
  - async
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# OpenAI Async Streaming

## Async Streaming with `async for`

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Count to 10"}],
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

asyncio.run(main())
```

## Streaming with Context Manager

```python
async with AsyncOpenAI() as client:
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}],
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
```

## Concurrent Streaming

Use `asyncio.TaskGroup` (Python 3.11+) for concurrent streaming from multiple prompts.

See [openai-streaming-basic.md](./openai-streaming-basic.md) for sync streaming patterns.
