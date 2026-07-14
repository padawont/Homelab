---
title: "Structured Outputs — BaseModel"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic-ai
  - structured-outputs
  - basemodel
sources:
  - url: "https://ai.pydantic.dev/"
    title: "Pydantic AI Documentation"
last_audit_date: 2026-06-09
---

# Structured Outputs — BaseModel

## Returning BaseModel from LLM Calls

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class Person(BaseModel):
    name: str
    age: int
    email: str

agent = Agent(
    "openai:gpt-4o",
    output_type=Person,
    system_prompt="Extract person info from text"
)

result = agent.run_sync(
    "John Doe, 30 years old, john@example.com"
)
print(result.output)
# Person(name="John Doe", age=30, email="john@example.com")
```

## Nested Structures

BaseModel outputs support any Pydantic feature — nested models, unions, discriminated unions, validators, and custom serializers:

```python
class Address(BaseModel):
    city: str
    country: str

class Person(BaseModel):
    name: str
    address: Address
```

See [nested models](./nested-models.md) for nesting patterns, and [structured outputs typed dict](./structured-outputs-typed-dict.md) for the lighter TypedDict alternative.
