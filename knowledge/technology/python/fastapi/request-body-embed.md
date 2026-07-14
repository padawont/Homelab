---
title: "Request Body — Embed Parameter"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - request-body
  - pydantic
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/body-multiple-params/#embed-a-single-body-parameter"
    title: "FastAPI Docs — Embed Single Body"
last_audit_date: 2026-06-09
---

# Request Body — Embed Parameter

By default, a single Pydantic body parameter expects a flat JSON body:

```python
@app.post("/items")
async def create_item(item: Item):
    return item
```

→ Client sends `{"name": "Foo", "price": 42}`

## Using `embed=True`

Wrap the body in a key matching the parameter name:

```python
from fastapi import Body

@app.post("/items")
async def create_item(item: Item = Body(embed=True)):
    return item
```

→ Client sends `{"item": {"name": "Foo", "price": 42}}`

## When to use

- When you need to distinguish between multiple single-model bodies
- When the API contract expects a wrapping key
- When backward compatibility requires a specific JSON shape

## Without vs With `embed`

| Without `embed` | With `embed=True` |
|---|---|
| `{"name": "Foo"}` | `{"item": {"name": "Foo"}}` |

See [request-body-single.md](./request-body-single.md) and [request-body-multiple.md](./request-body-multiple.md) for related patterns.
