---
title: "Evaluation Batch Processing"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - batch
  - processing
sources: []
last_audit_date: 2026-06-09
---

# Evaluation Batch Processing

Process multiple gold-dataset items with progress tracking and error handling.

## Batch Runner

```python
from pipeline_configuration import RunConfig, load_config
from pipeline_data_contracts import EvalItem, EvalResult
from evaluation_execution_overview import get_executor
from gold_dataset_formats import load_jsonl
from gold_dataset_structure import GoldEntry


def run_batch(config_path: str) -> list[EvalResult]:
    config = load_config(config_path)
    executor = get_executor(config)

    entries: list[GoldEntry] = load_jsonl(config.dataset["path"])
    sample = config.dataset.get("sample")
    if sample:
        entries = entries[:sample]

    results: list[EvalResult] = []
    for i, entry in enumerate(entries):
        print(f"[{i+1}/{len(entries)}] {entry.id}")
        try:
            item = EvalItem(
                input=entry.input,
                expected=entry.expected,
                metadata=entry.metadata,
            )
            result = executor.execute(item)
            results.append(result)
        except Exception as e:
            print(f"  ERROR: {e}")

    return results
```

## CLI Entry Point

```python
# run_eval.py
import sys
from evaluation_batch_processing import run_batch

if __name__ == "__main__":
    results = run_batch(sys.argv[1])
    print(f"Completed {len(results)} items")
```

Run with: `uv run python run_eval.py evals/configs/my-run.yaml`
