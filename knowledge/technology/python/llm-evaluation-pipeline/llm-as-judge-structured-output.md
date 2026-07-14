---
title: "LLM-as-Judge Structured Output"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - llm-as-judge
  - pydantic
  - structured-output
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI"
last_audit_date: 2026-06-09
---

# LLM-as-Judge Structured Output

Parse judge LLM responses into typed Pydantic models.

## Judge Score Model

```python
from pydantic import BaseModel, Field
from typing import Any


class JudgeScore(BaseModel):
    """Structured score from an LLM judge."""
    correctness: float = Field(ge=1, le=5)
    clarity: float = Field(ge=1, le=5)
    completeness: float = Field(ge=1, le=5)
    reasoning: str
```

## Extraction via OpenAI Structured Outputs

```python
from openai import OpenAI


def judge_response(
    client: OpenAI,
    prompt: list[dict],
    model: str = "gpt-4o-mini",
) -> JudgeScore:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=prompt,
        response_format=JudgeScore,
    )
    return completion.choices[0].message.parsed
```

## Dynamic Rubric Dimensions

```python
from pydantic import BaseModel, create_model
from llm_as_judge_rubric import Rubric, Dimension


def create_judge_model(rubric: Rubric) -> type[BaseModel]:
    fields = {}
    for d in rubric.dimensions:
        fields[d.name] = (float, Field(ge=1, le=5))
    fields["reasoning"] = (str, ...)
    return create_model("DynamicJudgeScore", **fields)
```

This uses `pydantic.create_model` to generate a model from any rubric. See [llm-as-judge-rubric.md](llm-as-judge-rubric.md) for rubric definition.
