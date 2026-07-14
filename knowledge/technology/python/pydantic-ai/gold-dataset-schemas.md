---
title: "Gold Dataset Schemas"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - gold-datasets
  - schemas
  - evaluation
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/models/"
    title: "Pydantic Models Documentation"
last_audit_date: 2026-06-09
---

# Gold Dataset Schemas

## Schema Patterns for Evaluation Datasets

```python
from pydantic import BaseModel
from typing import List
from datetime import datetime

class GoldExample(BaseModel):
    input_text: str
    expected_output: str
    difficulty: str  # "easy", "medium", "hard"
    tags: List[str] = []

class GoldDataset(BaseModel):
    name: str
    version: str
    description: str
    examples: List[GoldExample]
    created_at: datetime
    metadata: dict = {}
```

## Usage

```python
dataset = GoldDataset(
    name="math-reasoning",
    version="1.0.0",
    description="Basic math word problems",
    examples=[
        GoldExample(
            input_text="What is 2+2?",
            expected_output="4",
            difficulty="easy"
        )
    ],
    created_at=datetime.now()
)

dataset.model_dump_json(indent=2)
```

See [gold dataset versioning](./gold-dataset-versioning.md) for iteration tracking, and [structured outputs basemodel](./structured-outputs-basemodel.md) for generating examples via LLM.
