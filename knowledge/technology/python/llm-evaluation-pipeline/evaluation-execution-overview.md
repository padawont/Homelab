---
title: "Evaluation Execution Overview"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - execution
  - vcr
  - live
sources:
  - url: "https://vcrpy.readthedocs.io/en/latest/"
    title: "VCR.py Documentation"
last_audit_date: 2026-06-09
---

# Evaluation Execution Overview

Two execution modes: recorded (VCR) and live.

## Mode Selection

```python
from pipeline_configuration import RunConfig


def get_executor(config: RunConfig):
    if config.vcr.enabled:
        from evaluation_recorded_mode import RecordedExecutor
        return RecordedExecutor(config)
    else:
        from evaluation_live_mode import LiveExecutor
        return LiveExecutor(config)
```

## Common Interface

```python
from abc import ABC, abstractmethod
from pipeline_data_contracts import EvalItem, EvalResult


class EvalExecutor(ABC):
    @abstractmethod
    def execute(self, item: EvalItem) -> EvalResult:
        ...
```

## Workflow

1. Load gold dataset entries.
2. For each entry, call executor.
3. Collect `EvalResult` into a list.
4. Pass to LLM-as-judge for scoring.
5. Aggregate and report.

See [evaluation-recorded-mode.md](evaluation-recorded-mode.md) and [evaluation-live-mode.md](evaluation-live-mode.md) for mode-specific details.
