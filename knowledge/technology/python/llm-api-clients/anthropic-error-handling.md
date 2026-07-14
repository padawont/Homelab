---
title: "Anthropic Error Handling"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - errors
  - exceptions
sources:
  - url: "https://docs.anthropic.com/en/cli-sdks-libraries/sdks/python"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# Anthropic Error Handling

## Exception Hierarchy

All exceptions inherit from `anthropic.AnthropicError`:

| Exception | HTTP Status | When |
|---|---|---|
| `APIConnectionError` | — | Network failure |
| `RateLimitError` | 429 | Rate limit exceeded |
| `APIStatusError` | 4xx/5xx | Base for HTTP errors |
| `BadRequestError` | 400 | Invalid request |
| `AuthenticationError` | 401 | Invalid API key |
| `PermissionDeniedError` | 403 | Insufficient access |
| `NotFoundError` | 404 | Resource not found |
| `InternalServerError` | 500 | Server error |
| `OverloadedError` | 529 | API overloaded |

## Basic Error Handling

```python
from anthropic import (
    Anthropic,
    RateLimitError,
    APIConnectionError,
    OverloadedError,
)

client = Anthropic()

try:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}],
    )
except RateLimitError:
    print("Rate limited — back off")
except OverloadedError:
    print("API overloaded — retry later")
except APIConnectionError:
    print("Network issue")
except Exception as e:
    print(f"Error: {e}")
```

## OverloadedError Handling

Anthropic returns HTTP 529 when overloaded. Check `retry-after` header:

```python
except OverloadedError as e:
    retry_after = e.response.headers.get("retry-after", "5")
    print(f"Retry after {retry_after}s")
```

See [anthropic-rate-limits.md](./anthropic-rate-limits.md) for rate limit handling.
