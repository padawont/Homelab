---
title: "Structured Outputs — Streaming"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic-ai
  - structured-outputs
  - streaming
sources:
  - url: "https://ai.pydantic.dev/"
    title: "Pydantic AI Documentation"
last_audit_date: 2026-06-09
---

# Structured Outputs — Streaming

## Streaming Structured Output Chunks

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class Extraction(BaseModel):
    name: str
    value: float

agent = Agent(
    "openai:gpt-4o",
    output_type=Extraction
)

async with agent.run_stream(
    "Extract: revenue is 1.5 million"
) as result:
    async for partial in result.stream_output():
        # partial is an Extraction instance
        # fields may be None until fully streamed
        print(partial)
```

## Partial Validation

During streaming, fields may be `None` or partially populated. The final chunk yields a complete, validated instance.

## Use Cases

- Real-time UI updates as structured data arrives
- Processing early-available fields before the full output
- Long extractions where latency matters

See [structured outputs intro](./structured-outputs-intro.md) for when to use structured outputs, and [structured outputs basemodel](./structured-outputs-basemodel.md) for the synchronous equivalent.
