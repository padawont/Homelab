---
title: "LLM-as-Judge Multi-LLM"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - llm-as-judge
  - multi-model
sources:
  - url: "https://platform.openai.com/docs/guides/evals"
    title: "OpenAI Evaluation Guide"
last_audit_date: 2026-06-09
---

# LLM-as-Judge Multi-LLM

Use multiple judge models and aggregate their scores for robustness.

## Motivation

Single-judge bias is a known issue. Using 3+ judges and averaging reduces model-specific skew.

## Implementation

```python
from openai import OpenAI
from llm_as_judge_structured_output import JudgeScore
from llm_as_judge_prompt_template import build_judge_prompt
from llm_as_judge_rubric import Rubric


JUDGE_MODELS = ["gpt-4o-mini", "gpt-4o", "claude-3-haiku-20240307"]


def multi_judge(
    input_text: str,
    response: str,
    rubric: Rubric,
    expected: str | None = None,
) -> dict[str, JudgeScore]:
    prompt = build_judge_prompt(input_text, response, rubric, expected)
    scores = {}
    for model in JUDGE_MODELS:
        client = OpenAI()  # or appropriate client
        score = judge_response(client, prompt, model=model)
        scores[model] = score
    return scores


def aggregate_multi(scores: dict[str, JudgeScore]) -> dict[str, float]:
    """Average scores across all judges."""
    dims = [d for d in scores.values()][0].model_fields
    agg = {}
    for dim in dims:
        if dim == "reasoning":
            continue
        vals = [getattr(s, dim) for s in scores.values()]
        agg[dim] = sum(vals) / len(vals)
    return agg
```

## Judge Selection

| Judge Model | Strength | Cost |
|---|---|---|
| `gpt-4o-mini` | Fast, cheap, decent alignment | Low |
| `gpt-4o` | Best alignment, slower | High |
| `claude-3-haiku` | Good for creative tasks | Low |

See [results-aggregation.md](results-aggregation.md) for full aggregation patterns.
