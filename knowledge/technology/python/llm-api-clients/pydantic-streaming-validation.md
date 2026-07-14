---
title: "Pydantic Streaming Validation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - python
  - pydantic
  - streaming
  - validation
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# Pydantic Streaming Validation

## Validate Accumulated Content

```python
from pydantic import BaseModel
from openai import OpenAI


class FinalResponse(BaseModel):
    content: str
    model: str


client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)

full_content = ""
model = ""
for chunk in stream:
    if chunk.choices[0].delta.content:
        full_content += chunk.choices[0].delta.content
    if chunk.model:
        model = chunk.model

validated = FinalResponse(content=full_content, model=model)
print(validated)
```

## Validate Partial Chunks (Type Coercion)

For partial streaming data, use `model_validate` with `strict=False`:

```python
class StreamingChunk(BaseModel):
    content: str | None = None
    finish_reason: str | None = None

    model_config = {"extra": "ignore"}


for chunk in stream:
    delta = chunk.choices[0].delta
    validated = StreamingChunk.model_validate(
        {"content": delta.content, "finish_reason": chunk.choices[0].finish_reason},
        strict=False,
    )
    if validated.content:
        print(validated.content, end="")
```

## Validate Anthropic Stream

```python
from anthropic import Anthropic

client = Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
) as stream:
    for text in stream.text_stream:
        # Validate each text chunk
        chunk = ChunkModel(content=text)
```

See [pydantic-validation-openai.md](./pydantic-validation-openai.md) and [pydantic-validation-anthropic.md](./pydantic-validation-anthropic.md) for full response validation.
