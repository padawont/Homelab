---
title: "Pipeline Data Contracts"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - pipeline
  - data-contracts
  - pydantic
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI"
last_audit_date: 2026-06-09
---

# Pipeline Data Contracts

Interfaces between evaluation stages, defined with Pydantic.

```python
from pydantic import BaseModel
from typing import Any


class EvalItem(BaseModel):
    """Single item from a gold dataset."""
    input: str
    expected: str | None = None
    metadata: dict[str, Any] = {}


class EvalResult(BaseModel):
    """Output of one evaluation execution."""
    item: EvalItem
    response: str
    latency_ms: float
    token_count: int
    model_used: str


class JudgeScore(BaseModel):
    """Score from an LLM-as-judge."""
    score: float
    rubric_dimensions: dict[str, float]
    reasoning: str


class AggregatedResult(BaseModel):
    """Rolled-up scores across a run."""
    run_id: str
    mean_score: float
    dimension_scores: dict[str, float]
    item_count: int
```

These models are shared across [evaluation-execution-overview.md](evaluation-execution-overview.md) and [results-aggregation.md](results-aggregation.md).
