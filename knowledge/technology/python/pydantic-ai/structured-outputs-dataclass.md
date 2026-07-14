---
title: "Structured Outputs — dataclass"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic-ai
  - structured-outputs
  - dataclass
sources:
  - url: "https://ai.pydantic.dev/"
    title: "Pydantic AI Documentation"
last_audit_date: 2026-06-09
---

# Structured Outputs — dataclass

## dataclass as Output Type

```python
from dataclasses import dataclass
from pydantic_ai import Agent

@dataclass
class StockInfo:
    symbol: str
    price: float
    change_pct: float

agent = Agent(
    "openai:gpt-4o",
    output_type=StockInfo
)

result = agent.run_sync("Get AAPL stock price")
# result.output == StockInfo(symbol="AAPL", price=245.0, change_pct=1.2)
```

## When to Use

- You prefer the standard library `@dataclass` decorator
- You don't need Pydantic's custom validators
- You want minimal boilerplate for simple output shapes

## Comparison

| Type | Validation | Boilerplate | Use Case |
|---|---|---|---|
| BaseModel | Full | Medium | Complex validated data |
| TypedDict | Runtime (via TypeAdapter) | Low | Simple, high throughput |
| dataclass | Minimal | Low | Lightweight objects |

See [structured outputs basemodel](./structured-outputs-basemodel.md) for full validation, and [structured outputs typed dict](./structured-outputs-typed-dict.md) for static-only typing.
