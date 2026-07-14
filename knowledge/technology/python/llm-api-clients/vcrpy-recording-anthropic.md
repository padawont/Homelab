---
title: "VCR.py — Recording Anthropic Calls"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - vcrpy
  - testing
  - cassettes
sources:
  - url: "https://docs.anthropic.com/en/docs"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# VCR.py — Recording Anthropic Calls

## Sync Recording

```python
import vcr
from anthropic import Anthropic

with vcr.use_cassette("cassettes/anthropic_messages.yaml"):
    client = Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}],
    )
    print(response.content[0].text)
```

## Async Recording

```python
import asyncio
import vcr
from anthropic import AsyncAnthropic

async def test_anthropic_async():
    with vcr.use_cassette("cassettes/anthropic_async.yaml"):
        client = AsyncAnthropic()
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": "Hello"}],
        )
        print(response.content[0].text)

asyncio.run(test_anthropic_async())
```

## Streaming Recording

```python
with vcr.use_cassette("cassettes/anthropic_streaming.yaml"):
    client = Anthropic()
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hi"}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="")
```

See [vcrpy-filtering-anthropic.md](./vcrpy-filtering-anthropic.md) for filtering API keys in Anthropic cassettes.
