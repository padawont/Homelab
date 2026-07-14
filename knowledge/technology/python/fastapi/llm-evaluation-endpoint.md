---
title: "LLM — Evaluation Endpoint"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - llm
  - evaluation
sources:
  - url: "https://fastapi.tiangolo.com/"
    title: "FastAPI Documentation"
last_audit_date: 2026-06-09
---

# LLM — Evaluation Endpoint

Scoring endpoint for LLM evaluation:

```python
from pydantic import BaseModel, Field
from fastapi import FastAPI

app = FastAPI()


class EvalRequest(BaseModel):
    prompt: str
    response: str
    expected: str | None = None


class EvalResponse(BaseModel):
    overall_score: float = Field(ge=0, le=1)
    relevance: float = Field(ge=0, le=1)
    accuracy: float = Field(ge=0, le=1)
    fluency: float = Field(ge=0, le=1)
    feedback: str | None = None


@app.post("/evaluate", response_model=EvalResponse)
async def evaluate(request: EvalRequest):
    # Placeholder — integrate with evaluation framework
    score = min(1.0, len(request.response) / 100)
    return EvalResponse(
        overall_score=score,
        relevance=score * 0.9,
        accuracy=score * 0.85,
        fluency=score * 0.95,
        feedback=None,
    )
```

## Response schema

| Field | Type | Range | Description |
|---|---|---|---|
| `overall_score` | float | 0–1 | Composite evaluation score |
| `relevance` | float | 0–1 | Relevance to the prompt |
| `accuracy` | float | 0–1 | Factual accuracy |
| `fluency` | float | 0–1 | Language fluency |
| `feedback` | str | — | Free-text evaluation notes |

## Testing

See [testing-json-params.md](./testing-json-params.md) for testing JSON endpoints.

See also [llm-streaming-endpoint.md](./llm-streaming-endpoint.md) for streaming LLM responses.
