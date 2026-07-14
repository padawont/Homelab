---
title: "Evaluation Caching Results"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - caching
  - results
sources: []
last_audit_date: 2026-06-09
---

# Evaluation Caching Results

Cache evaluation results so re-runs on unchanged datasets skip API calls.

## Result Cache

```python
import json
import hashlib
from pathlib import Path
from pipeline_data_contracts import EvalResult


class ResultCache:
    def __init__(self, cache_dir: str = ".eval_cache/"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, entry_id: str, model: str) -> str:
        raw = f"{entry_id}:{model}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, entry_id: str, model: str) -> EvalResult | None:
        path = self.cache_dir / f"{self._key(entry_id, model)}.json"
        if path.exists():
            data = json.loads(path.read_text())
            return EvalResult(**data)
        return None

    def set(self, entry_id: str, model: str, result: EvalResult) -> None:
        path = self.cache_dir / f"{self._key(entry_id, model)}.json"
        path.write_text(result.model_dump_json())
```

## Integration

```python
cache = ResultCache()

def execute_with_cache(entry_id, model, executor):
    cached = cache.get(entry_id, model)
    if cached:
        return cached
    result = executor.execute(...)
    cache.set(entry_id, model, result)
    return result
```

Clear the cache dir to force fresh runs: `rm -rf .eval_cache/`.
