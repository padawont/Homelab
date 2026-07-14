---
title: "Gold Dataset Formats"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - gold-dataset
  - jsonl
  - parquet
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI"
last_audit_date: 2026-06-09
---

# Gold Dataset Formats

JSONL and Parquet storage for gold datasets.

## JSONL (default)

Line-delimited JSON — human-readable, git-friendly.

```python
from gold_dataset_structure import GoldEntry


def save_jsonl(entries: list[GoldEntry], path: str) -> None:
    with open(path, "w") as f:
        for e in entries:
            f.write(e.model_dump_json() + "\n")


def load_jsonl(path: str) -> list[GoldEntry]:
    entries = []
    with open(path) as f:
        for line in f:
            entries.append(GoldEntry.model_validate_json(line))
    return entries
```

## Parquet (large datasets)

Columnar storage for 10k+ entries. Install with:

```
uv add pyarrow pandas
```

```python
import pandas as pd


def save_parquet(entries: list[GoldEntry], path: str) -> None:
    df = pd.DataFrame([e.model_dump() for e in entries])
    df.to_parquet(path)


def load_parquet(path: str) -> list[GoldEntry]:
    df = pd.read_parquet(path)
    return [GoldEntry(**row) for _, row in df.iterrows()]
```

## Which to use

| Format | Use case |
|--------|----------|
| JSONL  | < 1k entries, code review diffs, manual inspection |
| Parquet| > 1k entries, CI speed, columnar filtering |

See [gold-dataset-structure.md](gold-dataset-structure.md) for the schema.
