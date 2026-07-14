---
title: "Selective VCR Cassette Recording"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - vcr
  - recording
  - cassettes
sources:
  - url: "https://vcrpy.readthedocs.io/"
    title: "VCR.py documentation"
last_audit_date: 2026-06-09
---

# Selective VCR Cassette Recording

Only re-record cassettes for endpoints that have actually changed, preserving cache hits for the rest.

## Per-endpoint Cassettes

Each test function should use its own cassette file:

```python
@my_vcr.use_cassette("tests/cassettes/test_get_users.yaml")
def test_get_users():
    ...

@my_vcr.use_cassette("tests/cassettes/test_create_user.yaml")
def test_create_user():
    ...
```

This allows selective invalidation at the cassette level.

## Re-recording a Specific Cassette

```bash
# Delete the specific cassette
rm tests/cassettes/test_get_users.yaml

# Run the specific test with new_episodes mode
# Requires the pytest-recording plugin to recognise --record-mode
uv run pytest tests/test_api.py::test_get_users --record-mode=new_episodes
```

## Environment-based Recording

Use an environment variable to control recording mode:

```python
import os
import vcr

record_mode = os.environ.get("VCR_RECORD_MODE", "once")
my_vcr = vcr.VCR(record_mode=record_mode)
```

Then in CI:

```yaml
- name: Run tests (selective re-record)
  env:
    VCR_RECORD_MODE: new_episodes
  run: uv run pytest tests/test_api.py::test_get_users
```

## CI Workflow for Selective Recording

```yaml
- name: Delete stale cassettes
  run: |
    if [ "${{ github.event_name }}" == "schedule" ]; then
      rm -rf tests/cassettes/
    fi

- name: Run tests
  env:
    VCR_RECORD_MODE: ${{ github.event_name == 'schedule' && 'new_episodes' || 'once' }}
  run: uv run pytest
```

## CI Cache Result

- Unchanged cassettes: cache hit, no recording needed.
- Missing cassettes: recorded fresh, cached for next run.
- Changed APIs: re-record only affected files.

See [vcr-cache-invalidation](./vcr-cache-invalidation.md) for when to trigger re-recording.
