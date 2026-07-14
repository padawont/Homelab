---
title: "Results Aggregation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - results
  - aggregation
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI"
last_audit_date: 2026-06-09
---

# Results Aggregation

Aggregate per-item scores into run-level summaries.

## Aggregation Model

```python
from pydantic import BaseModel
from pipeline_data_contracts import JudgeScore
import statistics


class RunSummary(BaseModel):
    run_id: str
    mean_score: float
    median_score: float
    std_dev: float
    dimension_scores: dict[str, float]
    total_items: int
    judge_model: str


def aggregate(scores: list[JudgeScore], run_id: str, judge_model: str) -> RunSummary:
    all_scores = [s.score for s in scores]
    dims = {}
    for s in scores:
        for dim, val in s.rubric_dimensions.items():
            dims.setdefault(dim, []).append(val)

    return RunSummary(
        run_id=run_id,
        mean_score=statistics.mean(all_scores),
        median_score=statistics.median(all_scores),
        std_dev=statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0,
        dimension_scores={k: statistics.mean(v) for k, v in dims.items()},
        total_items=len(scores),
        judge_model=judge_model,
    )
```

## Pipeline Integration

```python
def process_run(config_path: str) -> RunSummary:
    from evaluation_batch_processing import run_batch
    results = run_batch(config_path)
    # ... call judge on each result ...
    scores = [judge(r) for r in results]
    return aggregate(scores, config.run_id, config.judge["model"])
```

See [results-reporting.md](results-reporting.md) for output formats and [results-comparison.md](results-comparison.md) for delta analysis.
