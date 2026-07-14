---
title: "VCR.py — Filtering Anthropic API Keys"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - vcrpy
  - filtering
  - security
sources:
  - url: "https://docs.anthropic.com/en/docs"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# VCR.py — Filtering Anthropic API Keys

## Filter x-api-key Header

Anthropic uses `x-api-key` (not `authorization`):

```python
import vcr

my_vcr = vcr.VCR(
    filter_headers=["x-api-key"],
)

with my_vcr.use_cassette("cassettes/anthropic_messages.yaml"):
    client = Anthropic()
    response = client.messages.create(...)
```

## Filter Both Headers

If using both providers in the same cassette:

```python
my_vcr = vcr.VCR(
    filter_headers=["authorization", "x-api-key"],
)
```

## With pytest-vcr

```python
@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": ["x-api-key"],
    }
```

## Verify Cassette Safety

After recording, inspect the cassette YAML to confirm keys are filtered:

```bash
grep -i "sk-ant" cassettes/anthropic_messages.yaml
# Should return nothing
```

See [vcrpy-filtering-openai.md](./vcrpy-filtering-openai.md) for OpenAI key filtering and [vcrpy-recording-anthropic.md](./vcrpy-recording-anthropic.md) for recording setup.
