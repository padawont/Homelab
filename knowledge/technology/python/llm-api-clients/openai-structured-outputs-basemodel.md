---
title: "OpenAI Pydantic Model Response"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - pydantic
  - structured
  - basemodel
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# OpenAI Pydantic Model Response

Use Pydantic to define schemas for structured outputs.

## Define a Model

```python
from pydantic import BaseModel


class Person(BaseModel):
    name: str
    age: int
    email: str
```

## Generate JSON Schema

```python
schema = Person.model_json_schema()
```

Pass this to `response_format`:

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Parse: Alice, 30, alice@test.com"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "person",
            "strict": True,
            "schema": Person.model_json_schema(),
        },
    },
)

person = Person.model_validate_json(
    response.choices[0].message.content
)
print(person.name)  # "Alice"
```

## With Nested Models

```python
class Address(BaseModel):
    city: str
    country: str

class Employee(BaseModel):
    name: str
    address: Address
```

`model_json_schema()` handles nested models automatically. See [pydantic-validation-openai.md](./pydantic-validation-openai.md) for validating arbitrary responses.
