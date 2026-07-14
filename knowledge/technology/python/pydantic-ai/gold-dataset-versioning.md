---
title: "Gold Dataset Versioning"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - gold-datasets
  - versioning
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/models/"
    title: "Pydantic Models Documentation"
last_audit_date: 2026-06-09
---

# Gold Dataset Versioning

## Dataset Iteration and Tracking

Use Pydantic models to version your evaluation datasets:

```python
from pydantic import BaseModel
from typing import List
from datetime import datetime

class DatasetVersion(BaseModel):
    version: str                  # semver: "1.0.0"
    description: str              # what changed
    example_count: int
    created_at: datetime

class VersionedDataset(BaseModel):
    name: str
    current_version: str
    versions: List[DatasetVersion]
    examples: List[dict]          # reference to gold examples
```

## Semver Convention

- **Major**: Schema-breaking changes (new required fields)
- **Minor**: New optional fields, new examples
- **Patch**: Bug fixes, corrected expected outputs

## Tracking

```python
dataset = VersionedDataset(
    name="qa-benchmark",
    current_version="1.2.0",
    versions=[
        DatasetVersion(
            version="1.0.0",
            description="Initial release",
            example_count=100,
            created_at=datetime(2026, 1, 1)
        ),
        DatasetVersion(
            version="1.2.0",
            description="Added 50 hard examples",
            example_count=150,
            created_at=datetime(2026, 6, 1)
        )
    ],
    examples=[...]
)
```

See [gold dataset schemas](./gold-dataset-schemas.md) for defining example shapes.
