---
title: "LLM Judge Rubrics"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - llm-judge
  - rubrics
  - evaluation
sources:
  - url: "https://ai.pydantic.dev/"
    title: "Pydantic AI Documentation"
last_audit_date: 2026-06-10
---

# LLM Judge Rubrics

## Scoring Rubrics with Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import List

class RubricCriterion(BaseModel):
    name: str
    weight: float = Field(ge=0.0, le=1.0)
    score: float = Field(ge=0.0, le=1.0)
    feedback: str

class RubricScore(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    criteria: List[RubricCriterion]
    summary: str

rubric_agent = Agent(
    "openai:gpt-4o",
    output_type=RubricScore,
    system_prompt="""Score the response on these criteria:
1. accuracy (weight 0.5) — factual correctness
2. clarity (weight 0.3) — clear and concise
3. completeness (weight 0.2) — covers all aspects"""
)
```

## Weighted Scoring

```python
result = rubric_agent.run_sync("...")
rubric = result.output
# overall_score = weighted average of criteria scores
```

See [llm judge scoring](./llm-judge-scoring.md) for the basic single-score setup, and [gold dataset schemas](./gold-dataset-schemas.md) for defining the examples being scored.
