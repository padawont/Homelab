---
title: "LLM-as-Judge Calibration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - llm-as-judge
  - calibration
sources: []
last_audit_date: 2026-06-09
---

# LLM-as-Judge Calibration

Calibrate judge scores to detect and correct bias.

## Bias Types

- **Leniency bias**: Judge consistently scores higher than human raters.
- **Severity bias**: Judge consistently scores lower.
- **Position bias**: Judge favors certain response positions in multi-turn.
- **Self-enhancement**: Judge prefers outputs from its own model family.

## Calibration Dataset

Maintain a small set of hand-scored gold items (10-20 entries):

```yaml
# calibrations/hand_scores.yaml
entries:
  - id: "code-gen-001"
    human_scores:
      correctness: 4
      clarity: 5
      completeness: 3
    judge_scores:
      correctness: 4.5
      clarity: 4.8
      completeness: 3.2
```

## Correction Factors

```python
def compute_correction(
    human_scores: list[float],
    judge_scores: list[float],
) -> tuple[float, float]:
    """Returns (slope, intercept) for linear correction."""
    import numpy as np
    slope, intercept = np.polyfit(judge_scores, human_scores, 1)
    return slope, intercept


def apply_correction(
    raw_score: float,
    slope: float,
    intercept: float,
) -> float:
    return max(1.0, min(5.0, slope * raw_score + intercept))
```

Apply corrections after scoring in [results-aggregation.md](results-aggregation.md).

## Regular Audits

Recompute correction factors monthly or after rubric changes. See [gold-dataset-versioning.md](gold-dataset-versioning.md).
