---
title: "LLM-as-Judge Prompt Template"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - llm-as-judge
  - prompt
sources: []
last_audit_date: 2026-06-09
---

# LLM-as-Judge Prompt Template

Prompt patterns for LLM judges with structured scoring.

## Base Template

```python
from llm_as_judge_rubric import Rubric, Dimension


def build_judge_prompt(
    input_text: str,
    response: str,
    rubric: Rubric,
    expected: str | None = None,
) -> list[dict]:
    dims = "\n".join(
        f"- {d.name} (weight {d.weight}): {d.description}"
        for d in rubric.dimensions
    )

    expected_section = ""
    if expected:
        expected_section = f"\n## Expected Output\n{expected}"

    system = (
        "You are an evaluator. Score the following response on a scale "
        f"of {rubric.scale} for each dimension. "
        "Output your scores as a JSON object."
    )

    user = f"""## Task Input
{input_text}

## Response to Evaluate
{response}{expected_section}

## Rubric Dimensions
{dims}

## Output Format
Return a JSON object with keys matching each dimension name,
plus a 'reasoning' field explaining your scores.
"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
```

## Variations

- **With expected**: Include `expected` for factual accuracy scoring.
- **Without expected**: For open-ended creativity evaluations.
- **Few-shot**: Add 2-3 example scores in the system message.

See [llm-as-judge-structured-output.md](llm-as-judge-structured-output.md) for parsing the response.
