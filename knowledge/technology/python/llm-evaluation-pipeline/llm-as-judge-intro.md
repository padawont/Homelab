---
title: "LLM-as-Judge Introduction"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - llm-as-judge
  - evaluation
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI"
  - url: "https://docs.pytest.org/"
    title: "pytest Documentation"
last_audit_date: 2026-06-10
---

# LLM-as-Judge Introduction

Using an LLM to evaluate LLM outputs — replacing human raters with automated scoring.

## Concept

Instead of comparing outputs against expected strings (brittle), an LLM judge scores responses based on a rubric:

```
Prompt + Response ──► Judge LLM ──► Score + Reasoning
```

## Judge Pipeline

```
EvalResult.response
        │
        ▼
Judge Prompt Constructor ──► Judge LLM Call ──► Structured Output (Pydantic)
                                                      │
                                                      ▼
                                              Score extraction → Aggregation
```

## Dependencies

```
uv add pydantic-evals openai
```

The [`pydantic-evals`](https://pydantic.ai/) package provides a built-in `LLMJudge` evaluator:

```python
from pydantic_evals.evaluators import LLMJudge
```

This evaluator handles prompt construction, structured output parsing, and scoring — covering the pipeline shown above out of the box.

## pytest Integration

Judge evaluations can be run as pytest test cases using the [`pytest`](https://docs.pytest.org/) framework. A typical pattern wraps LLM judge calls inside a test function and asserts on the returned score:

```python
import pytest
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge


def my_task(inputs: str) -> str:
    return "..."  # your LLM call here


def test_response_quality():
    dataset = Dataset(
        name='quality_check',
        cases=[Case(inputs='What is Python?')],
        evaluators=[
            LLMJudge(
                rubric='Response is accurate, concise, and helpful',
                include_input=True,
                score={'include_reason': True},
                assertion=False,
            ),
        ],
    )
    report = dataset.evaluate_sync(my_task)
    score = report.cases[0].scores['LLMJudge_score'].value
    assert score >= 0.7
```

This enables running judge evaluations as part of CI pipelines alongside existing test suites.

## Sub-topics

| Note | Focus |
|------|-------|
| [llm-as-judge-rubric.md](llm-as-judge-rubric.md) | Scoring rubric design |
| [llm-as-judge-prompt-template.md](llm-as-judge-prompt-template.md) | Prompt patterns |
| [llm-as-judge-structured-output.md](llm-as-judge-structured-output.md) | Pydantic output parsing |
| [llm-as-judge-multi-llm.md](llm-as-judge-multi-llm.md) | Multiple judge models |
| [llm-as-judge-calibration.md](llm-as-judge-calibration.md) | Calibration techniques |
