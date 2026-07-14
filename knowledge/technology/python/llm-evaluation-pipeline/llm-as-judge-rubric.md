---
title: "LLM-as-Judge Rubric Design"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - llm-as-judge
  - rubric
sources: []
last_audit_date: 2026-06-09
---

# LLM-as-Judge Rubric Design

Scoring rubric configuration for LLM judge evaluation.

## Rubric Format (YAML)

```yaml
# rubrics/helpfulness.yaml
name: helpfulness
scale: 1-5
dimensions:
  - name: correctness
    weight: 0.4
    description: "Is the answer factually correct?"
  - name: clarity
    weight: 0.3
    description: "Is the answer clear and well-structured?"
  - name: completeness
    weight: 0.3
    description: "Does the answer fully address the question?"
```

## Rubric Model

```python
from pydantic import BaseModel, Field


class Dimension(BaseModel):
    name: str
    weight: float = Field(ge=0.0, le=1.0)
    description: str


class Rubric(BaseModel):
    name: str
    scale: str = "1-5"
    dimensions: list[Dimension]


def load_rubric(path: str) -> Rubric:
    import yaml
    with open(path) as f:
        return Rubric(**yaml.safe_load(f))
```

## Design Principles

- **3-5 dimensions** keeps judges focused.
- **Weights sum to 1.0** for a single composite score.
- **Descriptions** should be concrete (e.g., "Does the code compile?" not "Is it good?").
- **Scale** should be consistent across dimensions (1–5 or 1–10).

See [llm-as-judge-prompt-template.md](llm-as-judge-prompt-template.md) for how rubrics are injected into prompts.
