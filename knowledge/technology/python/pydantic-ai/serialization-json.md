---
title: "Serialization — model_dump_json()"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - serialization
  - json
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/serialization/#model_dump_json"
    title: "Pydantic model_dump_json"
last_audit_date: 2026-06-09
---

# Serialization — model_dump_json()

## Basic Usage

```python
from pydantic import BaseModel
from datetime import datetime

class Event(BaseModel):
    name: str
    ts: datetime

e = Event(name="deploy", ts=datetime.now())
json_str = e.model_dump_json()
# '{"name":"deploy","ts":"2026-06-09T12:00:00"}'
```

## Custom Encoder

```python
from pydantic import BaseModel, field_serializer
from datetime import datetime, timezone

class Event(BaseModel):
    name: str
    ts: datetime

    @field_serializer("ts")
    def serialize_ts(self, v: datetime) -> str:
        return v.astimezone(timezone.utc).isoformat()
```

## Indentation and Exclusions

```python
e.model_dump_json(indent=2, exclude={"internal_id"})
```

All `model_dump()` keyword options (`exclude`, `include`, `by_alias`, `exclude_unset`, `exclude_defaults`) also work with `model_dump_json()`. See [serialization model dump](./serialization-model-dump.md) for the full list.
