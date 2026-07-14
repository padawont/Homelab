---
title: "Evaluation Recorded Mode"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - execution
  - vcr
  - recorded
sources:
  - url: "https://vcrpy.readthedocs.io/en/latest/"
    title: "VCR.py Documentation"
last_audit_date: 2026-06-09
---

# Evaluation Recorded Mode

Run evaluation by replaying VCR cassettes — fast, deterministic, no API cost.

## Setup

```
uv add vcrpy
```

## Usage

```python
import vcr
from pipeline_configuration import RunConfig
from pipeline_data_contracts import EvalItem, EvalResult


class RecordedExecutor:
    def __init__(self, config: RunConfig):
        self.config = config

    def execute(self, item: EvalItem) -> EvalResult:
        cassette_path = (
            f"{self.config.vcr.cassette_dir}/{self.config.run_id}.yaml"
        )
        with vcr.use_cassette(
            cassette_path,
            record_mode=self.config.vcr.record_mode,
        ):
            # Calls are replayed from cassette
            return self._call_llm(item)
```

## When to Use

- **CI runs**: See [ci-deterministic-replay.md](ci-deterministic-replay.md).
- **Local dev iteration**: Fast feedback without waiting for API.
- **Before/after comparisons**: Same recorded responses for identical inputs.

## Record Mode Values

| Mode | Behavior |
|---|---|
| `once` | Replay if cassette exists, record if not. **Caution:** raises `CannotOverwriteExistingCassetteException` for new or unmatched requests when a cassette already exists |
| `new_episodes` | Replay existing, record new |
| `all` | Always record, ignore any existing cassette |
| `none` | Replay only, fail if missing |

See [evaluation-live-mode.md](evaluation-live-mode.md) for the live counterpart.
