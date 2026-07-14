---
title: "Anthropic Tool Use Streaming"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - tools
  - streaming
sources:
  - url: "https://docs.anthropic.com/en/docs/build-with-claude/streaming"
    title: "Anthropic Streaming Documentation"
last_audit_date: 2026-06-09
---

# Anthropic Tool Use Streaming

## Streaming with Tools

```python
from anthropic import Anthropic

client = Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=[
        {
            "name": "get_weather",
            "description": "Get weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                },
                "required": ["location"],
            },
        }
    ],
    messages=[{"role": "user", "content": "Weather in London?"}],
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "tool_use":
                print(f"Tool: {event.content_block.name}")
        elif event.type == "content_block_delta":
            if event.delta.type == "input_json_delta":
                print(event.delta.partial_json, end="")
```

## Checking for Tool Use After Stream

```python
message = stream.get_final_message()
for block in message.content:
    if block.type == "tool_use":
        print(f"Tool: {block.name}, Args: {block.input}")
```

Text deltas and tool input JSON deltas arrive in the same stream. Use `event.type` to distinguish them.

See [anthropic-tool-use.md](./anthropic-tool-use.md) for non-streaming tool use and [anthropic-streaming.md](./anthropic-streaming.md) for basic streaming.
