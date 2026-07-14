---
title: "VCR Cassette Cache Invalidation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - vcr
  - invalidation
  - cassettes
sources:
  - url: "https://vcrpy.readthedocs.io/"
    title: "VCR.py documentation"
last_audit_date: 2026-06-09
---

# VCR Cassette Cache Invalidation

Knowing when to invalidate the VCR cassette cache is critical to avoid false positives from stale recordings.

## When to Bust the Cache

| Trigger | Action | Cache Key Change |
|---|---|---|
| API contract changes | Re-record all cassettes | Bump version prefix |
| New tests added | Record new cassettes | Auto (new files in hash) |
| Test logic changes | Re-record affected cassettes | Content hash changes |
| Data freshness needed | Scheduled re-recording | Add date to key |

## Strategies

### Manual Version Bump

```yaml
key: vcr-v2-${{ hashFiles('tests/cassettes/**') }}
```

Increment `v2` to `v3` when the external API changes significantly.

### Date-based Rotation

```yaml
- name: Get date
  id: date
  run: echo "date=$(date +'%Y-%m-%d')" >> "$GITHUB_OUTPUT"

# Then in the cache step:
key: vcr-${{ steps.date.outputs.date }}-${{ hashFiles('tests/cassettes/**') }}
```

The `steps.date.outputs.date` expression resolves to the current date (e.g. `2026-06-10`), forcing a daily fresh recording. Useful for APIs with frequently changing data.

### Selective Re-recording

Delete individual cassette files and re-run tests. Only the deleted cassettes are re-recorded.

```bash
rm tests/cassettes/test_get_users.yaml
uv run pytest tests/test_api.py::test_get_users --record-mode=new_episodes
```

## Automatic Detection

Use a CI scheduled workflow to re-record cassettes periodically:

```yaml
on:
  schedule:
    - cron: "0 6 * * 1"  # Every Monday
```

## Stale Cassette Detection

Add a step that fails if cassettes are older than a threshold:

```bash
if find tests/cassettes -name '*.yaml' -mtime +30 -print -quit | grep -q .; then
  echo "Stale cassettes found"
  exit 1
fi
```

See [vcr-cache-selective-recording](./vcr-cache-selective-recording.md) for granular re-recording patterns.
