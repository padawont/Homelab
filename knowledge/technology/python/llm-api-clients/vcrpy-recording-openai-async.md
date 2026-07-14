---
title: "VCR.py — Recording OpenAI Async Calls"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - vcrpy
  - async
  - testing
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# VCR.py — Recording OpenAI Async Calls

## Install with aiohttp Support

```bash
uv add vcrpy
```

No extra package needed — VCR.py supports `httpx` (the transport OpenAI uses) natively.

## Basic Async Recording

```python
import asyncio
import vcr
from openai import AsyncOpenAI

async def test_openai_async():
    with vcr.use_cassette("cassettes/openai_async_chat.yaml"):
        client = AsyncOpenAI()
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello async"}],
        )
        print(response.choices[0].message.content)

asyncio.run(test_openai_async())
```

## With aiohttp (if using)

```python
with vcr.use_cassette(
    "cassettes/openai_async.yaml",
    filter_headers=["authorization"],
):
    async with AsyncOpenAI() as client:
        response = await client.chat.completions.create(...)
```

## VCR.py and asyncio

VCR.py uses `aiohttp` or `httpx` interceptors automatically. For `httpx`-based clients (which OpenAI uses), no extra configuration is required.

See [vcrpy-recording-openai-sync.md](./vcrpy-recording-openai-sync.md) for sync recordings and [vcrpy-filtering-openai.md](./vcrpy-filtering-openai.md) for filtering sensitive data.
