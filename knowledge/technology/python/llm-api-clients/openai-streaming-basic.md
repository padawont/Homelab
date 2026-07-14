---
title: "OpenAI Basic Streaming"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - streaming
  - sync
sources:
  - url: "https://developers.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
  - url: "https://developers.openai.com/docs/guides/streaming-responses"
    title: "OpenAI Streaming Guide"
last_audit_date: 2026-06-09
---

# OpenAI Basic Streaming

## Sync Streaming

Set `stream=True` to receive chunks incrementally:

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Count to 10"}],
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

## Key Differences from Non-Streaming

- Each chunk has `delta` instead of `message`
- `finish_reason` is `None` on all chunks except the last
- The last chunk has `choices[0].finish_reason` set to `"stop"` or `"length"`
- Usage info arrives in the final chunk via `chunk.usage`

## Collecting Full Response

```python
full_content = ""
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        full_content += delta.content
```

See [openai-streaming-async.md](./openai-streaming-async.md) for async streaming.
