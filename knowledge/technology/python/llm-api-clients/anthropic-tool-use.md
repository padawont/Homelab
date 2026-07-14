---
title: "Anthropic Tool Use"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - tools
  - function-calling
sources:
  - url: "https://docs.anthropic.com/en/docs/tool-use"
    title: "Anthropic Tool Use Guide"
last_audit_date: 2026-06-09
---

# Anthropic Tool Use

## Define Tools

```python
from anthropic import Anthropic

client = Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get the weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
            },
            "required": ["location"],
        },
    }
]
```

## Call with Tools

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Weather in Paris?"}],
)
```

## Handle Tool Use

```python
for block in response.content:
    if block.type == "tool_use":
        print(f"Calling: {block.name}")
        print(f"Args: {block.input}")
        # Execute tool, then send tool_result
```

## tool_choice Options

| Value | Behavior |
|---|---|
| `"auto"` | Model decides whether to use tools |
| `"any"` | Model must use a tool |
| `"none"` | Model must not use any tool |
| `{"type": "tool", "name": "get_weather"}` | Force specific tool |

## Sending Tool Results

```python
# After executing the tool:
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": "Sunny, 22°C",
        }
    ],
})
```

See [anthropic-tool-use-streaming.md](./anthropic-tool-use-streaming.md) for streaming with tool use.
