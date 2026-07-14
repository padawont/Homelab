---
title: "Pydantic Validation — OpenAI Responses"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - pydantic
  - validation
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# Pydantic Validation — OpenAI Responses

## Install Pydantic

```bash
# openai depends on pydantic; install explicitly if needed:
uv add pydantic
```

## Validate Chat Response

```python
from pydantic import BaseModel, Field
from openai import OpenAI


class ChatResponse(BaseModel):
    content: str
    finish_reason: str
    model: str
    prompt_tokens: int
    completion_tokens: int


def parse_response(response) -> ChatResponse:
    choice = response.choices[0]
    return ChatResponse(
        content=choice.message.content or "",
        finish_reason=choice.finish_reason or "",
        model=response.model,
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
    )


client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
parsed = parse_response(response)
print(parsed.model_dump())
```

## Validate Structured Output

```python
from pydantic import BaseModel


class Person(BaseModel):
    name: str
    age: int


# OpenAI returns JSON string in content
import json
raw = response.choices[0].message.content
person = Person.model_validate_json(raw)
```

See [openai-structured-outputs-basemodel.md](./openai-structured-outputs-basemodel.md) for schema-driven structured outputs and [pydantic-streaming-validation.md](./pydantic-streaming-validation.md) for streaming chunks.
