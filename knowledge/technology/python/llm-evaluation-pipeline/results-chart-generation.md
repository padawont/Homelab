---
title: "Results Chart Generation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - results
  - charts
  - visualization
sources: []
last_audit_date: 2026-06-09
---

# Results Chart Generation

Visualize evaluation results with matplotlib charts.

## Setup

```
uv add matplotlib numpy
```

## Chart Functions

```python
import matplotlib.pyplot as plt
import numpy as np
from results_aggregation import RunSummary


def plot_dimension_scores(summary: RunSummary, path: str) -> None:
    dims = list(summary.dimension_scores.keys())
    scores = list(summary.dimension_scores.values())

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(dims, scores, color="steelblue")
    ax.set_ylim(0, 5)
    ax.set_ylabel("Score")
    ax.set_title(f"Dimension Scores — {summary.run_id}")

    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{score:.2f}", ha="center", va="bottom")

    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_comparison(
    baseline: RunSummary,
    experiment: RunSummary,
    path: str,
) -> None:
    dims = list(baseline.dimension_scores.keys())
    x = np.arange(len(dims))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width/2, [baseline.dimension_scores[d] for d in dims],
           width, label=baseline.run_id, color="lightgray")
    ax.bar(x + width/2, [experiment.dimension_scores[d] for d in dims],
           width, label=experiment.run_id, color="steelblue")

    ax.set_ylabel("Score")
    ax.set_xticks(x)
    ax.set_xticklabels(dims)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
```

Charts are saved to `evals/charts/` as configured in [pipeline-configuration.md](pipeline-configuration.md).
