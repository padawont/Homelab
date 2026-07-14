---
title: "Type System"
status: draft
author: "Khalid Zubair (refactorartist)"
date: 2026-06-28
tags: [python, type-checker, astral, ty]
sources:
  - url: "https://docs.astral.sh/ty/features/type-system/"
    title: "ty Type System Documentation"
  - url: "https://github.com/astral-sh/ty"
    title: "ty GitHub Repository"
last_audit_date: 2026-06-28
---

# Type System

ty implements a modern Python type system with several advanced features beyond what mypy and Pyright support. You can generally expect ty to support all typing features described in the Python typing documentation.

## Redeclarations

ty allows reusing the same symbol with a different type within the same scope:

```python
def split_paths(paths: str) -> list[Path]:
    paths: list[str] = paths.split(":")
    return [Path(p) for p in paths]
```

The `paths` parameter is redeclared as `list[str]` inside the function body. ty tracks the new type flow-sensitively — after the redeclaration, `paths` is treated as `list[str]`.

## Intersection Types

ty has first-class support for intersection types using the `&` operator. An intersection type represents a value that satisfies all of the intersected types simultaneously:

```python
class Serializable:
    def serialize_json(self) -> str: ...

class Versioned:
    version: str

def output_as_json(obj: Serializable) -> str:
    if isinstance(obj, Versioned):
        # obj is narrowed to Serializable & Versioned
        reveal_type(obj)  # Serializable & Versioned
        return str({
            "data": obj.serialize_json(),
            "version": obj.version
        })
    else:
        return obj.serialize_json()
```

Intersections are used internally by ty's type narrowing — when you narrow with `isinstance`, ty creates intersection types rather than unions.

Direct use of intersection types in annotations is possible using `Intersection` from the `ty_extensions` module (available at type-checking time only):

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ty_extensions import Intersection
    type SerializableVersioned = Intersection[Serializable, Versioned]

def output_as_json(obj: SerializableVersioned) -> str: ...
```

## Top and Bottom Materializations

Gradual types have two special materializations:

- **Top materialization**: Represents the largest type a gradual type can materialize to. For `Any`, it is `object`. For `Any & int`, it is `int`. Used when `isinstance` checks involve generic classes:

```python
@final
class Item: ...

def process(items: Item | list[Item]):
    if isinstance(items, list):
        # reveals: list[Item]
        reveal_type(items)
```

## Reachability Based on Types

ty's reachability analysis is based on type inference, allowing it to detect unreachable branches in more situations than pattern-matching approaches:

```python
import pydantic
from pydantic import BaseModel

PYDANTIC_V2 = pydantic.__version__.startswith("2.")

class Person(BaseModel):
    name: str

def to_json(person: Person):
    if PYDANTIC_V2:
        return person.model_dump_json()  # no error when checking with 1.x
    else:
        return person.json()
```

With pydantic 2.x installed, ty evaluates the `startswith("2.")` check and considers only the first branch reachable. With pydantic 1.x, only the second branch is reachable.

## Type Narrowing

ty performs control-flow-based type narrowing, refining the type of a variable based on conditional checks:

```python
def process(x: str | int) -> None:
    if isinstance(x, str):
        # x is narrowed to str here
        print(x.upper())
    else:
        # x is narrowed to int here
        print(x + 1)
```

ty supports narrowing via:

- `isinstance()` and `issubclass()`
- `type(x) is T` and `type(x) == T`
- `x is None` / `x is not None`
- `x == value` and `x != value`
- Truthiness checks (`if x:`)
- `assert isinstance(x, T)`
- Type guards (`TypeIs` and `TypeGuard`)
- `match`/`case` pattern matching
- `hasattr()` checks (creates intersection with synthetic protocol)

## Gradual Typing

ty supports gradual typing, allowing mixed typed and untyped code:

```python
from typing import Any

# Fully typed
def add(a: int, b: int) -> int:
    return a + b

# Partially typed
def process(value: Any) -> str:
    return str(value)

# Untyped — no annotations
def legacy(x, y):
    return x + y
```

Key behaviors:

- **Optional types**: `str | None` is preferred over `Optional[str]`
- **`Any`**: Propagates through operations — `Any` + `int` = `Any`
- **Implicit `Any`**: In non-strict mode, unannotated parameters default to the gradual type
- **Strict mode**: The `--strict` CLI flag enables additional checks

## Generics

ty supports generic type parameters with variance:

```python
from typing import TypeVar, Generic

T = TypeVar("T")
U = TypeVar("U", covariant=True)

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value
```

Supported generics features:

- `TypeVar` with bounds and constraints
- `Generic[T]` base classes
- Variance annotations (`covariant`, `contravariant`)
- User-defined generic functions
- Generic protocols
- Type parameter defaults

## Protocol Structural Subtyping

ty supports structural subtyping via `Protocol`, enabling static duck typing:

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

def render(obj: Drawable) -> None:
    obj.draw()

render(Circle())  # OK — structural subtype
```

Key details:

- Protocols are checked structurally at type-check time
- `@runtime_checkable` enables `isinstance()` checks with protocols at runtime
- Protocol members can be methods, properties, or attributes
- Protocols support inheritance and composition
- ty supports both `typing.Protocol` and `typing_extensions.Protocol`
