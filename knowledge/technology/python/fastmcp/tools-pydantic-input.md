---
title: "Pydantic Tool Input Models"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - tools
  - pydantic
  - input-models
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Pydantic Tool Input Models

For complex parameters, use a Pydantic model as the tool argument. FastMCP automatically generates JSON Schema and validates input.

## Model as parameter

```python
from pydantic import BaseModel
from fastmcp import FastMCP

mcp = FastMCP("demo")

class SearchParams(BaseModel):
    query: str
    limit: int = 10
    offset: int = 0
    filters: dict[str, str] | None = None

@mcp.tool()
def search(params: SearchParams) -> list[dict]:
    """Search the database."""
    return db.search(
        params.query,
        limit=params.limit,
        offset=params.offset,
    )
```

## Multiple models

```python
class User(BaseModel):
    id: int
    name: str

class CreateUserInput(BaseModel):
    name: str
    email: str

@mcp.tool()
def create_user(input: CreateUserInput) -> User:
    """Create a new user."""
    return create_user_in_db(input.name, input.email)
```

## Nested models

Pydantic models can be nested for complex input structures. FastMCP derives the full JSON Schema recursively.

```python
from pydantic import BaseModel
from fastmcp import FastMCP

mcp = FastMCP("demo")

class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class User(BaseModel):
    name: str
    email: str
    address: Address

@mcp.tool()
def register_user(user: User) -> dict:
    """Register a new user with address."""
    return {
        "name": user.name,
        "email": user.email,
        "city": user.address.city,
        "country": user.address.country,
    }
```

## Next steps

- [Defining Tools](./tools-defining.md)
- [Async Tools](./tools-async-tools.md)
- [Tool Error Handling](./tools-error-handling.md)
