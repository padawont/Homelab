---
title: "Benchmark: pip Install Timing"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - benchmarks
  - pip
  - timing
sources: []
last_audit_date: 2026-06-09
---

# Benchmark: pip Install Timing

Reference timing data for pip dependency installation in CI. These numbers are representative of a medium-sized Python project (~100 dependencies). Actual times vary by project complexity, network speed, and runner type.

## Cold Cache (No Cache)

| Operation | Time (approx) |
|---|---|
| `pip install -r requirements.txt` | 45–120s |
| Dependency resolution | 5–30s |
| Download wheels | 20–60s |
| Build from source | 10–60s |

## Warm Cache (Cache Hit)

| Operation | Time (approx) |
|---|---|
| `pip install -r requirements.txt` | 5–15s |
| Cache restore from GitHub | 2–5s |
| Verification pass | 3–10s |

## Cache Miss (With Fallback)

| Operation | Time (approx) |
|---|---|
| Partial restore from cache key | 2–5s |
| Download remaining packages | 15–40s |

## Cache Size

| Metric | Value |
|---|---|
| `~/.cache/pip` size | 200–600 MB |
| Cache save time | 5–15s |
| Cache restore time | 2–5s |

## Notes

- pip is single-threaded for downloads, making network latency a bottleneck.
- Resolution time grows non-linearly with dependency count.
- These numbers justify migration to uv. See [benchmark-uv-timing](./benchmark-uv-timing.md) for comparison.
