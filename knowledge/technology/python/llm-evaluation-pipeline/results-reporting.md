---
title: "Results Reporting"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - results
  - reporting
sources: []
last_audit_date: 2026-06-09
---

# Results Reporting

Generate human-readable reports from aggregated evaluation results.

## JSON Report

```python
from results_aggregation import RunSummary
import json


def save_report(summary: RunSummary, path: str) -> None:
    report = {
        "run_id": summary.run_id,
        "overall": {
            "mean": round(summary.mean_score, 2),
            "median": round(summary.median_score, 2),
            "std_dev": round(summary.std_dev, 2),
        },
        "by_dimension": {
            k: round(v, 2)
            for k, v in summary.dimension_scores.items()
        },
        "items_evaluated": summary.total_items,
        "judge_model": summary.judge_model,
    }
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
```

## Markdown Report

```python
def save_markdown_report(summary: RunSummary, path: str) -> None:
    lines = [
        f"# Evaluation Report: {summary.run_id}",
        "",
        f"**Judge Model:** {summary.judge_model}",
        f"**Items Evaluated:** {summary.total_items}",
        "",
        "## Overall Scores",
        f"| Metric | Score |",
        f"|--------|-------|",
        f"| Mean   | {summary.mean_score:.2f} |",
        f"| Median | {summary.median_score:.2f} |",
        f"| Std Dev| {summary.std_dev:.2f} |",
        "",
        "## Dimension Scores",
    ]
    for dim, score in summary.dimension_scores.items():
        lines.append(f"- **{dim}**: {score:.2f}")
    lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))
```

See [results-comparison.md](results-comparison.md) for diff reports and [results-chart-generation.md](results-chart-generation.md) for visualizations.
