---
title: "Results Comparison"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - results
  - comparison
sources: []
last_audit_date: 2026-06-09
---

# Results Comparison

Compare aggregated results across multiple experiment runs.

## Comparison Model

```python
from pydantic import BaseModel
from results_aggregation import RunSummary
import json


class RunComparison(BaseModel):
    baseline_id: str
    experiment_id: str
    score_delta: float
    dimension_deltas: dict[str, float]
    item_count_mismatch: bool


def compare_runs(baseline_path: str, experiment_path: str) -> RunComparison:
    with open(baseline_path) as f:
        baseline = json.load(f)
    with open(experiment_path) as f:
        experiment = json.load(f)

    return RunComparison(
        baseline_id=baseline["run_id"],
        experiment_id=experiment["run_id"],
        score_delta=round(
            experiment["overall"]["mean"] - baseline["overall"]["mean"], 3
        ),
        dimension_deltas={
            dim: round(
                experiment["by_dimension"][dim] - baseline["by_dimension"][dim], 3
            )
            for dim in baseline["by_dimension"]
        },
        item_count_mismatch=(
            baseline["items_evaluated"] != experiment["items_evaluated"]
        ),
    )
```

## CLI Usage

```
uv run python compare.py \
    evals/reports/baseline.json \
    evals/reports/experiment.json
```

## Output Example

```json
{
  "baseline_id": "eval-baseline",
  "experiment_id": "eval-gpt4o-v2",
  "score_delta": 0.35,
  "dimension_deltas": {
    "correctness": 0.4,
    "clarity": 0.3,
    "completeness": 0.35
  },
  "item_count_mismatch": false
}
```

See [results-chart-generation.md](results-chart-generation.md) for visual comparisons.
