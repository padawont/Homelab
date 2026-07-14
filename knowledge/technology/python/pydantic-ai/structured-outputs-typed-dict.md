---
title: "Structured Outputs — TypedDict"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic-ai
  - structured-outputs
  - typed-dict
sources:
  - url: "https://ai.pydantic.dev/"
    title: "Pydantic AI Documentation"
last_audit_date: 2026-06-09
---

# Structured Outputs — TypedDict

## TypedDict as Output Type

```python
from typing import TypedDict
from pydantic_ai import Agent

class MovieReview(TypedDict):
    title: str
    rating: float
    summary: str

agent = Agent(
    "openai:gpt-4o",
    output_type=MovieReview
)

result = agent.run_sync("Review Inception")
# result.output == {"title": "Inception", "rating": 9.0, ...}
```

## Key Differences from BaseModel

| Aspect | TypedDict | BaseModel |
|---|---|---|
| Validation | Runtime (via TypeAdapter) | Full Pydantic validation |
| Performance | Minimal overhead | Slightly more overhead |
| Type safety | Static only | Static + runtime |
| Methods/validators | Not supported | Full support |

## Use Case

TypedDict is best for simple data extraction where you only need static type hints and maximum throughput. For validated outputs, see [structured outputs basemodel](./structured-outputs-basemodel.md). For class-based syntax, see [structured outputs dataclass](./structured-outputs-dataclass.md).
