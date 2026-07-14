---
title: "OpenAI Timeout Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - timeout
  - configuration
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# OpenAI Timeout Configuration

## Per-Request Timeout

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    timeout=30.0,  # seconds
)
```

## Client-Level Timeout

```python
client = OpenAI(timeout=60.0)
```

Applies to all requests made with this client.

## Granular Timeouts

Pass an `httpx.Timeout` object for fine-grained control:

```python
from openai import OpenAI
import httpx

client = OpenAI(
    http_client=httpx.Client(
        timeout=httpx.Timeout(
            connect=5.0,    # connection timeout
            read=60.0,      # read timeout
            write=10.0,     # write timeout
            pool=30.0,      # connection pool timeout
        )
    ),
)
```

## Async Timeout

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(timeout=120.0)
```

Longer timeouts are recommended for streaming or complex tool calls. See [openai-retry-strategy.md](./openai-retry-strategy.md) for combining timeouts with retries.
