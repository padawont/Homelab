---
title: "OpenAI Async Client Usage"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - async
  - client
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# OpenAI Async Client Usage

## Basic Async Chat Completion

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Hello!"}
        ]
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

## Context Manager

```python
async with AsyncOpenAI() as client:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hi"}]
    )
    print(response.choices[0].message.content)
```

## Concurrent Requests

```python
async def main():
    async with AsyncOpenAI() as client:
        tasks = [
            client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            for prompt in ["Tell me a joke", "Say hello"]
        ]
        responses = await asyncio.gather(*tasks)
        for r in responses:
            print(r.choices[0].message.content)
```

Use `asyncio.gather` or `asyncio.TaskGroup` for concurrency. Avoid creating a new client per request — reuse the instance.
