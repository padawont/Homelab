---
title: "VCR Cassette Cache Key Design"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - vcr
  - cache-key
  - cassettes
sources:
  - url: "https://vcrpy.readthedocs.io/"
    title: "VCR.py documentation"
last_audit_date: 2026-06-09
---

# VCR Cassette Cache Key Design

Designing the right cache key for VCR cassettes balances cache hit rate against correctness.

## Key Strategies

### Content-based (Recommended)

Hash the cassette files themselves. Only invalidates when cassettes change:

```yaml
key: vcr-${{ hashFiles('tests/cassettes/**') }}
```

Pro: Maximum reuse. Con: Does not detect when cassettes are stale relative to source code.

### Source-aware

Include test file hashes to bust cache when test logic changes:

```yaml
key: vcr-${{ hashFiles('tests/cassettes/**', 'tests/test_api.py') }}
```

Pro: Automatically re-records when tests change. Con: More cache misses.

### Version-tagged

Include a manual version to force a full re-recording:

```yaml
key: vcr-v1-${{ hashFiles('tests/cassettes/**') }}
```

Bump `v1` to `v2` when the external API contract changes.

## Restoration Strategy

```yaml
restore-keys: |
  vcr-
```

This gives a fallback to any previous cassette cache if the content hash does not match.

## Best Practice

Start with content-based keys. Add source-awareness only if you regularly encounter stale cassette issues.

See [vcr-cache-invalidation](./vcr-cache-invalidation.md) for when to invalidate.
