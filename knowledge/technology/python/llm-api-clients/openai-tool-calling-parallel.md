---
title: "OpenAI Parallel Tool Calls"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - tools
  - parallel
sources:
  - url: "https://platform.openai.com/docs/guides/function-calling"
    title: "OpenAI Function Calling Guide"
last_audit_date: 2026-06-09
---

# OpenAI Parallel Tool Calls

OpenAI supports multiple tool calls in a single response. The model can invoke several functions at once.

## Response with Multiple Tool Calls

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Get weather in Paris and London"}],
    tools=[...],  # tool definitions
)
```

## Processing Parallel Calls

```python
message = response.choices[0].message

if message.tool_calls:
    results = []
    for tool_call in message.tool_calls:
        # Execute each call (consider concurrent execution)
        result = execute_function(
            tool_call.function.name,
            tool_call.function.arguments
        )
        results.append({
            "tool_call_id": tool_call.id,
            "result": result,
        })

    # Send all results back
    tool_messages = [
        {
            "role": "tool",
            "tool_call_id": r["tool_call_id"],
            "content": r["result"],
        }
        for r in results
    ]
```

## Concurrent Execution

For parallel calls, execute independent tools concurrently:

```python
import asyncio
import json

async def execute_tool(tool_call):
    args = json.loads(tool_call.function.arguments)
    if tool_call.function.name == "get_weather":
        return await fetch_weather(args["location"])

async def process_parallel(client, messages):
    response = await client.chat.completions.create(...)
    tasks = [execute_tool(tc) for tc in response.choices[0].message.tool_calls]
    return await asyncio.gather(*tasks)
```

See [openai-tool-calling.md](./openai-tool-calling.md) for basic tool calling setup.
