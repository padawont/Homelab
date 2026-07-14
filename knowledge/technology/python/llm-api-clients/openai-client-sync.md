---
title: "OpenAI Sync Client Usage"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - sync
  - client
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# OpenAI Sync Client Usage

## Basic Chat Completion

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
```

## Context Manager

The client supports `with` for automatic cleanup:

```python
with OpenAI() as client:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hi"}]
    )
    print(response.choices[0].message.content)
```

The sync client uses `httpx` under the hood and is thread-safe.

See [openai-client-async.md](./openai-client-async.md) for the async counterpart and [openai-chat-completions.md](./openai-chat-completions.md) for full API details.
