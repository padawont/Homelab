---
title: "VCR.py — Filtering OpenAI API Keys"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - vcrpy
  - filtering
  - security
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# VCR.py — Filtering OpenAI API Keys

## Filter Request Headers

```python
import vcr

my_vcr = vcr.VCR(
    filter_headers=["authorization"],
)

with my_vcr.use_cassette("cassettes/openai_chat.yaml"):
    client = OpenAI()
    response = client.chat.completions.create(...)
```

## Filter Query Parameters

```python
my_vcr = vcr.VCR(
    filter_query_parameters=["api_key"],
)
```

## Filter POST Body (Sensitive Fields)

```python
my_vcr = vcr.VCR(
    filter_post_data_parameters=["api_key"],
)
```

## Replace with Placeholder

```python
my_vcr = vcr.VCR(
    filter_headers=[("authorization", "Bearer sk-...REDACTED...")],
)
```

## Decorate Test Functions

```python
import pytest

@pytest.mark.vcr(
    filter_headers=["authorization"],
)
def test_openai_chat():
    client = OpenAI()
    response = client.chat.completions.create(...)
```

## Global VCR Config (conftest.py)

```python
import pytest
import vcr

@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
    }
```

See [vcrpy-recording-openai-sync.md](./vcrpy-recording-openai-sync.md) for recording setup and [vcrpy-filtering-anthropic.md](./vcrpy-filtering-anthropic.md) for Anthropic filtering.
