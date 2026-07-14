---
title: "VCR.py — Recording OpenAI Sync Calls"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - vcrpy
  - testing
  - cassettes
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# VCR.py — Recording OpenAI Sync Calls

## Install

```bash
uv add vcrpy
```

## Basic Recording

```python
import vcr
from openai import OpenAI

with vcr.use_cassette("cassettes/openai_chat.yaml"):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print(response.choices[0].message.content)
```

## Record Mode

```python
with vcr.use_cassette(
    "cassettes/openai_chat.yaml",
    record_mode="once",      # "once" | "new_episodes" | "all" | "none"
):
    ...
```

- `once` — record if cassette doesn't exist, replay otherwise
- `new_episodes` — record new requests, replay existing
- `all` — always re-record
- `none` — never record, only replay

## Match On

```python
with vcr.use_cassette(
    "cassettes/openai_chat.yaml",
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
):
    ...
```

See [vcrpy-recording-openai-async.md](./vcrpy-recording-openai-async.md) for async recordings and [vcrpy-filtering-openai.md](./vcrpy-filtering-openai.md) for filtering API keys.
