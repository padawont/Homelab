---
title: "Anthropic Structured Outputs"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - structured
  - json
sources:
  - url: "https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs"
    title: "Anthropic Structured Outputs Guide"
last_audit_date: 2026-06-09
---

# Anthropic Structured Outputs

Anthropic supports structured JSON output via native structured outputs (`output_config.format`), tool use, and system prompt instruction.

## Via Native Structured Outputs (Recommended)

Use `client.messages.parse()` with a Pydantic model to get validated, typed output. This is the primary and most reliable approach as of the GA release.

```python
from pydantic import BaseModel
from anthropic import Anthropic


class Person(BaseModel):
    name: str
    age: int


client = Anthropic()

response = client.messages.parse(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Parse: Alice is 30 years old"}],
    output_format=Person,
)

person = response.parsed_output
print(person.name)  # "Alice"
print(person.age)   # 30
```

The `output_format` parameter accepts a Pydantic `BaseModel` subclass. The SDK automatically derives a JSON Schema from the model and enforces constrained decoding. The parsed instance is available on `response.parsed_output`.

You can also pass a raw JSON schema via `output_config` for non-Pydantic workflows:

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Parse: Alice is 30 years old"}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
                "required": ["name", "age"],
                "additionalProperties": False,
            },
        }
    },
)

import json
data = json.loads(response.content[0].text)
print(data["name"])  # "Alice"
```

## Via Tool Use (Secondary)

If you need tool call shaped output (e.g. for multi-turn agentic workflows), use a tool with no side effects to constrain output:

```python
tools = [
    {
        "name": "print_person",
        "description": "Print extracted person info",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
    }
]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "tool", "name": "print_person"},
    messages=[{"role": "user", "content": "Alice is 30"}],
)

for block in response.content:
    if block.type == "tool_use":
        print(block.input)  # {"name": "Alice", "age": 30}
```

See [anthropic-tool-use.md](./anthropic-tool-use.md) for more on tool use.

## Via System Prompt

As a fallback, you can instruct Claude to respond in JSON via the `system` parameter:

```python
from anthropic import Anthropic
import json

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="Always respond in valid JSON. Use the schema: {\"name\": string, \"age\": int}",
    messages=[{"role": "user", "content": "Parse: Alice is 30 years old"}],
)

data = json.loads(response.content[0].text)
print(data["name"])  # "Alice"
```

See [openai-structured-outputs.md](./openai-structured-outputs.md) for comparison with OpenAI's native JSON mode.
