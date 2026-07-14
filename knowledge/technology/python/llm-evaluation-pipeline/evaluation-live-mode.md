---
title: "Evaluation Live Mode"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - execution
  - live
  - api
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI"
last_audit_date: 2026-06-09
---

# Evaluation Live Mode

Run evaluation with real API calls — for ground-truth updates and final validations.

## Usage

```python
from openai import OpenAI
from pipeline_configuration import RunConfig
from pipeline_data_contracts import EvalItem, EvalResult


class LiveExecutor:
    def __init__(self, config: RunConfig):
        self.client = OpenAI()
        self.model = config.model["name"]
        self.temperature = config.model.get("temperature", 0.0)

    def execute(self, item: EvalItem) -> EvalResult:
        import time
        start = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": item.input}],
            temperature=self.temperature,
        )
        elapsed = (time.perf_counter() - start) * 1000

        return EvalResult(
            item=item,
            response=response.choices[0].message.content,
            latency_ms=elapsed,
            token_count=response.usage.total_tokens,
            model_used=self.model,
        )
```

## When to Use

- **Initial cassette recording**: Run live once to capture VCR cassettes.
- **Scheduled evals**: See [ci-scheduled-evals.md](ci-scheduled-evals.md).
- **Final validation**: Verify against latest model behavior.

## Cost Awareness

Always limit live runs:

```python
config.dataset["sample"] = 20   # limit to 20 items
```

See [evaluation-recorded-mode.md](evaluation-recorded-mode.md) for the recorded counterpart.
