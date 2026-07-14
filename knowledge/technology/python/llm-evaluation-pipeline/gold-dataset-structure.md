---
title: "Gold Dataset Structure"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - gold-dataset
  - pydantic
  - schema
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI"
last_audit_date: 2026-06-09
---

# Gold Dataset Structure

Schema for a single evaluation gold dataset entry.

## Pydantic Model

```python
from pydantic import BaseModel, Field
from typing import Any
from enum import Enum


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class GoldEntry(BaseModel):
    """One labeled example in a gold dataset."""
    id: str = Field(..., description="Unique identifier")
    category: str = Field(..., description="Task category")
    input: str = Field(..., description="Prompt or input")
    expected: str | None = Field(None, description="Expected output")
    difficulty: Difficulty = Difficulty.medium
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(..., description="ISO date string")
    version: int = Field(1, description="Dataset iteration version")
```

## Usage

```python
entry = GoldEntry(
    id="code-gen-001",
    category="code_generation",
    input="Write a Python function to reverse a linked list.",
    expected="class ListNode: ...",
    difficulty="hard",
    tags=["linked-list", "python"],
    created_at="2026-06-09",
    version=2
)
```

See [gold-dataset-formats.md](gold-dataset-formats.md) for serialization and [gold-dataset-versioning.md](gold-dataset-versioning.md) for iteration tracking.
