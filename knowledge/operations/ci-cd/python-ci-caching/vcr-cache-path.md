---
title: "VCR Cassette Cache Path"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - vcr
  - cache-path
  - cassettes
sources:
  - url: "https://vcrpy.readthedocs.io/"
    title: "VCR.py documentation"
last_audit_date: 2026-06-09
---

# VCR Cassette Cache Path

VCR cassettes are YAML files stored on disk. CI caching preserves these files between workflow runs.

## Default Cassette Location

By convention, cassettes are stored in a `cassettes/` directory under the test folder:

```
tests/
├── cassettes/
│   ├── test_endpoint_1.yaml
│   ├── test_endpoint_2.yaml
│   └── ...
└── test_api.py
```

## Configuration

Set the cassette directory in your VCR configuration:

```python
import vcr

my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/",
    record_mode="once",
)
```

Or per test:

```python
@my_vcr.use_cassette("tests/cassettes/test_get_users.yaml")
def test_get_users():
    ...
```

## CI Cache Step

```yaml
- uses: actions/cache@v4
  id: vcr-cache
  with:
    path: tests/cassettes
    key: vcr-${{ hashFiles('tests/cassettes/**') }}
    restore-keys: |
      vcr-
```

## Size Considerations

- Each cassette file is typically 1–50 KB.
- A full test suite may generate 1–50 MB of cassettes.
- Git-committing cassettes is possible but bloats the repository — caching in CI avoids this.

## Alternative: Single Cassette File

For small projects, a single cassette file works:

```python
@my_vcr.use_cassette("tests/cassettes/all_interactions.yaml")
```

But per-endpoint cassettes (one per test) are recommended for selective re-recording.

See [vcr-cache-selective-recording](./vcr-cache-selective-recording.md) for cassette management patterns.
