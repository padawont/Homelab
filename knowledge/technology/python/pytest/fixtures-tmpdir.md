---
title: "Temporary Directories with tmp_path"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - fixtures
  - tmpdir
  - tempfile
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/tmp-path.html"
    title: "pytest tmp_path Fixture"
last_audit_date: 2026-06-09
---

# Temporary Directories with tmp_path

pytest provides built-in fixtures for temporary files and directories.

## tmp_path (Recommended)

`tmp_path` returns a `pathlib.Path` to a unique temporary directory per test.

```python
def test_write_file(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    f = d / "hello.txt"
    f.write_text("Hello, pytest!")
    assert f.read_text() == "Hello, pytest!"
```

## tmpdir (Legacy)

`tmpdir` returns a `py.path.local` object (deprecated in newer pytest versions):

```python
def test_old_style(tmpdir):
    f = tmpdir.join("output.txt")
    f.write("data")
    assert f.read() == "data"
```

## Scope Control

`tmp_path` is function-scoped by default. Use `tmp_path_factory` for session-scoped temporary directories:

```python
@pytest.fixture(scope="session")
def shared_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("shared_data")
```

## Cleanup

The temporary directory is automatically removed after each test completes.
