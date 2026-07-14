---
title: "Structured Outputs — Introduction"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic-ai
  - structured-outputs
  - llm
sources:
  - url: "https://ai.pydantic.dev/"
    title: "Pydantic AI Documentation"
last_audit_date: 2026-06-09
---

# Structured Outputs — Introduction

## Configuring Structured Outputs

Use `output_type=` in the Agent constructor when you need LLM responses as typed, validated data instead of free text:

- Extracting structured information from documents
- Validating LLM-generated JSON against a schema
- Building type-safe LLM pipelines
- Generating test fixtures or evaluation datasets

## Basic Flow

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class Extraction(BaseModel):
    name: str
    value: float

agent = Agent("openai:gpt-4o", output_type=Extraction)
result = agent.run_sync("Extract: price is 42.99")
print(result.output)  # Extraction(name="price", value=42.99)
```

## Output Types

Pydantic AI supports three output schema types:

- [BaseModel](./structured-outputs-basemodel.md) — Full validation, best for complex data
- [TypedDict](./structured-outputs-typed-dict.md) — Lightweight, no runtime validation
- [dataclass](./structured-outputs-dataclass.md) — Simple, familiar syntax

See [streaming structured outputs](./structured-outputs-streaming.md) for partial/streaming results.
