---
title: "Anthropic Rate Limits"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - rate-limits
  - errors
sources:
  - url: "https://docs.anthropic.com/en/docs"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# Anthropic Rate Limits

## Detecting Rate Limits

```python
from anthropic import RateLimitError

try:
    response = client.messages.create(...)
except RateLimitError as e:
    retry_after = e.response.headers.get("retry-after", "5")
    print(f"Rate limited. Retry after {retry_after}s")
```

## Response Headers

```python
response = client.messages.create(...)

headers = response.headers
print(headers.get("x-ratelimit-limit-requests"))
print(headers.get("x-ratelimit-remaining-requests"))
print(headers.get("x-ratelimit-reset-requests"))
print(headers.get("x-ratelimit-limit-tokens"))
print(headers.get("x-ratelimit-remaining-tokens"))
print(headers.get("x-ratelimit-reset-tokens"))
```

## Simple Backoff

```python
import time

def call_with_backoff(client, **kwargs):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except RateLimitError as e:
            wait = int(e.response.headers.get("retry-after", 2 ** attempt))
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

## Tenacity Integration

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from anthropic import RateLimitError, OverloadedError

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=lambda e: isinstance(e, (RateLimitError, OverloadedError)),
)
def call_claude(client, **kwargs):
    return client.messages.create(**kwargs)
```

See [anthropic-error-handling.md](./anthropic-error-handling.md) for error types and [openai-retry-strategy.md](./openai-retry-strategy.md) for general retry patterns.
