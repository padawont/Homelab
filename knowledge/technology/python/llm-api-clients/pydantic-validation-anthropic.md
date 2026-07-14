---
title: "Pydantic Validation — Anthropic Responses"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - pydantic
  - validation
sources:
  - url: "https://docs.anthropic.com/en/docs"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# Pydantic Validation — Anthropic Responses

## Validate Messages Response

```python
from pydantic import BaseModel
from anthropic import Anthropic


class ClaudeResponse(BaseModel):
    text: str
    stop_reason: str | None
    model: str
    input_tokens: int
    output_tokens: int


def parse_response(response) -> ClaudeResponse:
    return ClaudeResponse(
        text=response.content[0].text,
        stop_reason=response.stop_reason,
        model=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
parsed = parse_response(response)
print(parsed.model_dump())
```

## Validate Tool Use

```python
class ToolUseBlock(BaseModel):
    name: str
    input_data: dict


def extract_tool_calls(response) -> list[ToolUseBlock]:
    return [
        ToolUseBlock(name=block.name, input_data=block.input)
        for block in response.content
        if block.type == "tool_use"
    ]
```

See [pydantic-validation-openai.md](./pydantic-validation-openai.md) for OpenAI validation patterns and [pydantic-streaming-validation.md](./pydantic-streaming-validation.md) for streaming validation.
