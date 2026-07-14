---
title: "OpenAI Error Handling"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - errors
  - exceptions
sources:
  - url: "https://github.com/openai/openai-python#handling-errors"
    title: "OpenAI Python SDK — Error Handling"
last_audit_date: 2026-06-09
---

# OpenAI Error Handling

## Exception Hierarchy

All exceptions inherit from `openai.APIError`:

| Exception | HTTP Status | When |
|---|---|---|
| `APIConnectionError` | — | Network failure |
| `RateLimitError` | 429 | Rate limit exceeded |
| `APIStatusError` | 4xx/5xx | Base for HTTP errors |
| `BadRequestError` | 400 | Invalid request |
| `AuthenticationError` | 401 | Invalid API key |
| `PermissionDeniedError` | 403 | Insufficient access |
| `NotFoundError` | 404 | Resource not found |
| `UnprocessableEntityError` | 422 | Semantic error |
| `InternalServerError` | >=500 | Server-side issue |

## Basic Try/Except

```python
from openai import OpenAI, RateLimitError, APIConnectionError

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}],
    )
except RateLimitError:
    print("Rate limited — back off and retry")
except APIConnectionError:
    print("Network issue — check connectivity")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Getting Error Details

```python
except APIStatusError as e:
    print(e.status_code)     # 400
    print(e.message)         # "..." 
    print(e.response.text)   # Raw response body
    print(e.body)            # Parsed JSON body
```

See [openai-retry-strategy.md](./openai-retry-strategy.md) for automatic retry patterns.
