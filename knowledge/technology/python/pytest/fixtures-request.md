---
title: "The Request Fixture Object"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - fixtures
  - request
sources:
  - url: "https://docs.pytest.org/en/stable/reference/reference.html#request"
    title: "pytest Request Object Reference"
last_audit_date: 2026-06-09
---

# The Request Fixture Object

The built-in `request` fixture provides introspection into the requesting test and access to fixture parameters.

## Accessing Parametrized Fixture Values

```python
@pytest.fixture(params=["a", "b"])
def param_fixture(request):
    return request.param
```

## Inspecting the Test Context

```python
@pytest.fixture
def log_test_name(request):
    print(f"\nRunning: {request.node.name}")
    yield
    print(f"\nFinished: {request.node.name}")
```

## Common Attributes

| Attribute | Description |
|---|---|
| `request.param` | Current parameter value (for parametrized fixtures) |
| `request.node` | The test node (for the requesting test) |
| `request.node.name` | Test function name |
| `request.function` | The test function object |
| `request.cls` | Test class (if test is in a class) |
| `request.module` | Test module |
| `request.scope` | Current fixture scope |
| `request.config` | The pytest configuration object |
| `request.getfixturevalue("name")` | Dynamically request another fixture |

## Dynamic Fixture Resolution

```python
@pytest.fixture
def dynamic_fixture(request):
    fixture_name = request.node.get_closest_marker("fixture_name")
    if fixture_name:
        return request.getfixturevalue(fixture_name.args[0])
```

Use `request.getfixturevalue` sparingly — it bypasses the fixture dependency graph.
