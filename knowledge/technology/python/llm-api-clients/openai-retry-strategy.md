---
title: "OpenAI Retry Strategy"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - retry
  - tenacity
  - backoff
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# OpenAI Retry Strategy

## Install Tenacity

```bash
uv add tenacity
```

## Basic Retry

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import RateLimitError, APIConnectionError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=lambda e: isinstance(e, (RateLimitError, APIConnectionError)),
)
def call_openai(client, messages):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
```

## With Logging

```python
import logging
from tenacity import before_log, after_log

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=lambda e: isinstance(e, (RateLimitError, APIConnectionError)),
    before=before_log(logger, logging.WARNING),
    after=after_log(logger, logging.WARNING),
)
def call_openai(client, messages):
    ...
```

## Custom Backoff

```python
from tenacity import retry, wait_random_exponential

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def call_openai(client, messages):
    ...
```

See [openai-error-handling.md](./openai-error-handling.md) for error types to catch, and [openai-timeout-config.md](./openai-timeout-config.md) for timeout settings.
