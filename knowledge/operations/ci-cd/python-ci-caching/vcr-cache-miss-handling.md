---
title: "VCR Cache Miss Handling"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - vcr
  - cache-miss
  - cassettes
sources:
  - url: "https://vcrpy.readthedocs.io/"
    title: "VCR.py documentation"
last_audit_date: 2026-06-09
---

# VCR Cache Miss Handling

On a VCR cassette cache miss, the CI pipeline must gracefully fall back to recording cassettes in `new_episodes` mode or using pre-seeded fixtures.

## Cache Miss Scenarios

| Scenario | Cause | Handling |
|---|---|---|
| First run | No cache yet | Run with `record_mode=new_episodes` |
| Cache evicted | 7 days since last access | Same as first run |
| Key changed | Cassette content modified | Selective re-recording |
| Partial miss | Some cassettes missing | Only missing ones re-recorded |

## CI Workflow for Resilient Cache Miss

```yaml
- uses: actions/cache@v4
  id: vcr-cache
  with:
    path: tests/cassettes
    key: vcr-${{ hashFiles('tests/cassettes/**') }}
    restore-keys: |
      vcr-

- name: Run tests
  env:
    VCR_RECORD_MODE: ${{ steps.vcr-cache.outputs.cache-hit == 'true' && 'once' || 'new_episodes' }}
  run: uv run pytest
```

On cache miss, tests run in `new_episodes` mode, recording any missing cassettes.

## Partial Restore Handling

Even with a fallback restore-key, individual cassette files may be outdated. VCR's default `record_mode: once` would fail if cassette content is stale — the serialized request in the cassette no longer matches the actual request (e.g. due to changed headers, query params, or request bodies), causing a `CannotOverwriteExistingCassetteException` or request mismatch error. Safer:

```yaml
env:
  VCR_RECORD_MODE: ${{ steps.vcr-cache.outputs.cache-hit == 'true' && 'once' || 'new_episodes' }}
```

## Without Cache Dependencies

If cassettes do not exist at all and network access is blocked in CI, tests will fail. Mitigations:

1. **Pre-seed cassettes** — commit a minimal cassette set to the repository.
2. **Mock fallback** — use unittest.mock as a fallback when cassettes are absent.
3. **Conditional VCR** — skip VCR-dependent tests when cassettes are missing:

```yaml
- name: Run tests (skip VCR on miss)
  env:
    SKIP_VCR_TESTS: ${{ steps.vcr-cache.outputs.cache-hit != 'true' }}
  run: uv run pytest -m "not vcr"
```

See [vcr-cassette-caching-intro](./vcr-cassette-caching-intro.md) for the overview.
