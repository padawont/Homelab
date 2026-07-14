---
title: "OpenAI Structured Outputs"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - structured
  - json
  - response-format
sources:
  - url: "https://platform.openai.com/docs/guides/structured-outputs"
    title: "OpenAI Structured Outputs Guide"
last_audit_date: 2026-06-09
---

# OpenAI Structured Outputs

## response_format Parameter

Use `response_format` to get structured JSON output.

### JSON Object Mode

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Extract: Name is Alice, age 30"}],
    response_format={"type": "json_object"},
)
print(response.choices[0].message.content)
# {"name": "Alice", "age": 30}
```

Requires a system message instruction to output JSON.

### JSON Schema Mode

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Extract: Name is Alice, age 30"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "person",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
                "required": ["name", "age"],
                "additionalProperties": False,
            },
        },
    },
)
```

See [openai-structured-outputs-json-schema.md](./openai-structured-outputs-json-schema.md) for full JSON Schema details and [openai-structured-outputs-basemodel.md](./openai-structured-outputs-basemodel.md) for Pydantic integration.
