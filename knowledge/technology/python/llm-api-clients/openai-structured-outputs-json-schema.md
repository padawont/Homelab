---
title: "OpenAI JSON Schema Mode"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - structured
  - json-schema
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# OpenAI JSON Schema Mode

## Strict JSON Schema

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Parse: John, 25, john@test.com"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "user_profile",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "email": {"type": "string", "format": "email"},
                },
                "required": ["name", "age", "email"],
                "additionalProperties": False,
            },
        },
    },
)

import json
data = json.loads(response.choices[0].message.content)
print(data["name"])  # "John"
```

## Nested Objects

```python
"properties": {
    "address": {
        "type": "object",
        "properties": {
            "street": {"type": "string"},
            "city": {"type": "string"},
        },
        "required": ["street", "city"],
        "additionalProperties": False,
    }
}
```

Strict mode (`"strict": True`) enforces `additionalProperties: False` and disallows undefined fields. Nesting and arrays are supported.

See [openai-structured-outputs.md](./openai-structured-outputs.md) for the overview and [openai-structured-outputs-basemodel.md](./openai-structured-outputs-basemodel.md) for Pydantic model-based usage.
