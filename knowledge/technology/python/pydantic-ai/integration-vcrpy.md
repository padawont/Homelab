---
title: "Integration — VCR.py with Pydantic"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - vcrpy
  - testing
  - cassettes
sources:
  - url: "https://docs.pydantic.dev/latest/"
    title: "Pydantic Documentation"
last_audit_date: 2026-06-09
---

# Integration — VCR.py with Pydantic

## Validating VCR.py Cassette Responses

Use Pydantic models to validate HTTP responses recorded by VCR.py:

```python
from pydantic import BaseModel
from typing import Optional

class APIResponse(BaseModel):
    status_code: int
    headers: dict
    body: str
    encoding: Optional[str] = None
```

## Testing Pattern

```python
import pytest
import vcr
from pydantic import ValidationError

@vcr.use_cassette("fixtures/api_response.yaml")
def test_api_call():
    response = make_api_call()
    try:
        validated = APIResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.text
        )
    except ValidationError as e:
        pytest.fail(f"Response schema mismatch: {e}")
```

## Why This Matters

Cassettes freeze HTTP responses. Pydantic validation ensures the frozen responses still match your expected schema, catching API contract drift during test replay. See [error handling](./error-handling.md) for accessing `ValidationError` details.
