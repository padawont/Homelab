---
title: "LLM-as-Judge Scoring"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - llm-judge
  - evaluation
  - scoring
sources:
  - url: "https://ai.pydantic.dev/"
    title: "Pydantic AI Documentation"
last_audit_date: 2026-06-10
---

# LLM-as-Judge Scoring

## Evaluation Setup

Use Pydantic AI's structured outputs to build an LLM judge that scores responses against criteria:

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class JudgeScore(BaseModel):
    score: float               # 0.0 to 1.0
    reasoning: str             # why this score
    issues: list[str] = []     # specific problems found

judge_agent = Agent(
    "openai:gpt-4o",
    output_type=JudgeScore,
    system_prompt=(
        "You are a strict evaluator. Score 0.0-1.0 based on "
        "accuracy, completeness, and clarity."
    )
)

result = judge_agent.run_sync(
    "Question: What is Python?\nAnswer: A programming language."
)
print(result.output)
# JudgeScore(score=0.9, reasoning="...", issues=[])
```

> **Note:** Pydantic AI also provides a dedicated [`LLMJudge`](https://pydantic.dev/docs/ai/evals/evaluators/llm-judge/index.md) class in `pydantic_evals.evaluators` for LLM-as-judge evaluation with built-in rubric support, score/assertion modes, and model selection. This is the recommended approach when using Pydantic AI's evaluation framework. The manual Agent approach shown here is still valid for educational purposes and custom judging logic that goes beyond what `LLMJudge` supports.

## Batch Evaluation

```python
for example in dataset.examples:
    result = judge_agent.run_sync(
        f"Question: {example.input_text}\nAnswer: {example.expected_output}"
    )
    scores.append(result.output.score)
```

See [llm judge rubrics](./llm-judge-rubrics.md) for structured scoring rubrics with multiple criteria.
