---
title: "Benchmark: VCR Cassette Replay vs Live Speedup"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - benchmarks
  - vcr
  - cassettes
sources: []
last_audit_date: 2026-06-09
---

# Benchmark: VCR Cassette Replay vs Live Speedup

Caching VCR cassettes provides dramatic speedups for HTTP-dependent test suites in CI.

## Live HTTP vs Cassette Replay

| Operation | Live HTTP | Cassette Replay | Speedup |
|---|---|---|---|
| Single GET request | 200–800ms | 1–5ms | 40–400× |
| Single POST request | 300–1500ms | 2–8ms | 40–750× |
| Auth + token flow | 2–5s | 10–30ms | 100–200× |
| Full test suite (50 API calls) | 30–120s | 0.5–2s | 60× |
| Paginated endpoint (5 pages) | 3–10s | 10–50ms | 60–200× |

## Cache Size

| Metric | Value |
|---|---|
| Per cassette file | 1–50 KB |
| Full test suite cassettes | 1–50 MB |
| Cache save time | 1–3s |
| Cache restore time | 1–3s |

## CI Wall Clock Impact

| Scenario | Without Cassette Cache | With Cassette Cache | Saving |
|---|---|---|---|
| First run (record) | 3–5 min (live) | 3–5 min (live) | 0% |
| Subsequent runs | 3–5 min (live) | 30–90s (replay) | 70–85% |
| Cache miss + fallback | 3–5 min (live) | 90s–3min (partial) | 40–50% |

## Observations

- Cassette replay is essentially I/O-bound — limited by disk read speed.
- Live HTTP tests are network-bound and flaky (rate limits, DNS, TLS).
- The speedup factor increases with the number of API calls per test suite.

## Recommendation

Always cache cassettes in CI. The 1–3s cache overhead is negligible compared to the 60–120s saved per run.

See [vcr-cassette-caching-intro](./vcr-cassette-caching-intro.md) for implementation details.
