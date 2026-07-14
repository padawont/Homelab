---
title: "VCR Cassette Caching — Introduction"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - vcr
  - testing
  - cassettes
sources:
  - url: "https://vcrpy.readthedocs.io/"
    title: "VCR.py documentation"
last_audit_date: 2026-06-09
---

# VCR Cassette Caching — Introduction

VCR.py records HTTP interactions as YAML "cassettes" and replays them during tests. Caching these cassettes in CI eliminates live HTTP calls, making tests faster, reliable, and deterministic.

## Why Cache Cassettes in CI

| Benefit | Explanation |
|---|---|
| **Speed** | Cassette replay is milliseconds; live HTTP is seconds to minutes. |
| **Reliability** | Eliminates network flakiness, rate limits, and API downtime. |
| **Determinism** | Tests run against recorded responses — no data drift. |
| **Cost** | Avoids API call costs on every CI run. |

## How It Works

1. First run (or re-recording): VCR makes real HTTP requests and saves cassettes.
2. Subsequent runs: cassettes are replayed from disk — no network calls.
3. CI caches the cassette directory between runs.

## Basic CI Caching

```yaml
- uses: actions/cache@v5
  id: vcr-cache
  with:
    path: tests/cassettes
    key: vcr-${{ runner.os }}-${{ hashFiles('tests/cassettes/**') }}
    restore-keys: |
      vcr-${{ runner.os }}-
```

> **Bootstrap note:** On the first CI run (or after cache eviction) the `tests/cassettes/`
> directory is empty, so `hashFiles` returns an empty string and the cache misses.
> This is expected — VCR records live HTTP and saves the cassettes post-job. On the
> next run, `restore-keys` matches the previously saved cache via the OS prefix,
> and subsequent runs hit the exact key once a hash is established.

## When to Re-record

- API contract changes (new fields, removed endpoints).
- Test logic changes that hit different endpoints.
- Intentional refresh of recorded data.

See [vcr-cache-invalidation](./vcr-cache-invalidation.md) for invalidation strategies.
