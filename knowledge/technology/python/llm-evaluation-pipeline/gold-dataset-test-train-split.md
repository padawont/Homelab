---
title: "Gold Dataset Test-Train Split"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - gold-dataset
  - split
sources: []
last_audit_date: 2026-06-09
---

# Gold Dataset Test-Train Split

Splitting gold datasets into evaluation vs. development subsets.

## Strategy

Use stratified splits to preserve category balance.

```python
from gold_dataset_structure import GoldEntry
import random


def split_dataset(
    entries: list[GoldEntry],
    test_ratio: float = 0.2,
    seed: int = 42,
) -> tuple[list[GoldEntry], list[GoldEntry]]:
    """Stratified split by category."""
    rng = random.Random(seed)
    by_cat: dict[str, list[GoldEntry]] = {}
    for e in entries:
        by_cat.setdefault(e.category, []).append(e)

    test, train = [], []
    for cat, group in by_cat.items():
        rng.shuffle(group)
        split_idx = max(1, int(len(group) * test_ratio))
        test.extend(group[:split_idx])
        train.extend(group[split_idx:])

    rng.shuffle(test)
    rng.shuffle(train)
    return test, train
```

## Persistent Split Files

Save splits into separate files:

```
evals/datasets/
├── code-gen-v2.train.jsonl
├── code-gen-v2.test.jsonl
└── code-gen-v2.full.jsonl
```

The test split is used in [ci-deterministic-replay.md](ci-deterministic-replay.md) for CI runs; the full set is used in [evaluation-batch-processing.md](evaluation-batch-processing.md).
