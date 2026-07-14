---
title: "OpenAI Tool Calling"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - tools
  - function-calling
sources:
  - url: "https://platform.openai.com/docs/guides/function-calling"
    title: "OpenAI Function Calling Guide"
last_audit_date: 2026-06-09
---

# OpenAI Tool Calling

## Define a Tool

```python
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["c", "f"]},
                },
                "required": ["location"],
            },
        },
    }
]
```

## Make a Call

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto",
)
```

## Handle Tool Call

```python
message = response.choices[0].message
if message.tool_calls:
    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        args = tool_call.function.arguments
        # Execute function and return result
```

## tool_choice Options

| Value | Behavior |
|---|---|
| `"auto"` | Model decides whether to call a tool |
| `"required"` | Must call one or more tools |
| `"none"` | Never call tools |
| `{"type": "function", "function": {"name": "get_weather"}}` | Force specific tool |

See [openai-tool-calling-parallel.md](./openai-tool-calling-parallel.md) for parallel tool calls.
