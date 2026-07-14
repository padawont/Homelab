---
title: "OpenAI Rate Limits"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - rate-limits
  - errors
sources:
  - url: "https://platform.openai.com/docs/guides/rate-limits"
    title: "OpenAI Rate Limits Guide"
last_audit_date: 2026-06-09
---

# OpenAI Rate Limits

## Detecting Rate Limits

```python
from openai import RateLimitError

try:
    response = client.chat.completions.create(...)
except RateLimitError as e:
    print(f"Retry after: {e.response.headers.get('retry-after-ms')}")
    print(f"Retry after (seconds): {e.response.headers.get('retry-after')}")
```

## Headers to Monitor

```python
response = client.chat.completions.create(...)

headers = response.headers
print(headers.get("x-ratelimit-limit-requests"))      # Max requests per time window
print(headers.get("x-ratelimit-limit-tokens"))         # Max tokens per minute
print(headers.get("x-ratelimit-remaining-requests"))   # Remaining requests
print(headers.get("x-ratelimit-remaining-tokens"))     # Remaining tokens
print(headers.get("x-ratelimit-reset-requests"))       # Reset time for requests
```

## Handling with Backoff

```python
import time

def rate_limited_call(client, messages):
    while True:
        try:
            return client.chat.completions.create(...)
        except RateLimitError as e:
            wait = int(e.response.headers.get("retry-after-ms", 5000)) / 1000
            time.sleep(wait)
```

See [openai-retry-strategy.md](./openai-retry-strategy.md) for automated retry with tenacity, and [openai-cost-tracking.md](./openai-cost-tracking.md) for monitoring token usage.
