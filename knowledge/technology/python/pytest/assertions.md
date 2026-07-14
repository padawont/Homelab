---
title: "Assertions in pytest"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - assertions
  - testing
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/assert.html"
    title: "pytest How-to — Assertions"
last_audit_date: 2026-06-09
---

# Assertions in pytest

pytest uses Python's built-in `assert` with rich diff output on failure.

## Basic Assertions

```python
def test_math():
    assert 2 + 2 == 4
    assert "hello".upper() == "HELLO"
    assert [1, 2, 3].count(2) == 1
```

## Asserting Exceptions with `pytest.raises`

```python
import pytest

def test_raises():
    with pytest.raises(ValueError, match="invalid value"):
        int("not-a-number")
```

Access the exception object:

```python
def test_raises_details():
    with pytest.raises(ValueError) as exc_info:
        int("x")
    assert "invalid literal" in str(exc_info.value)
```

## Approximate Comparisons with `pytest.approx`

```python
def test_approx():
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert (2.0 / 3.0) == pytest.approx(0.6667, rel=1e-3)
    assert {"a": 0.333} == pytest.approx({"a": 1/3})
```

## Assertion Introspection

pytest rewrites assert statements to show intermediate values. No special assertion methods required.
