---
title: "Benchmark: uv Install Timing"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - benchmarks
  - uv
  - timing
sources: []
last_audit_date: 2026-06-09
---

# Benchmark: uv Install Timing

Reference timing data for uv dependency installation in CI. These numbers are representative of a medium-sized Python project (~100 dependencies) on a standard GitHub-hosted runner.

## Cold Cache (No Cache)

| Operation | Time (approx) |
|---|---|
| `uv sync --frozen` | 5–20s |
| Dependency resolution | <1s |
| Download + build | 3–15s |
| Virtual environment creation | 1–2s |

## Warm Cache (Cache Hit)

| Operation | Time (approx) |
|---|---|
| `uv sync --frozen` | 1–3s |
| Cache restore from GitHub | 1–3s |
| Validation pass | <1s |

## Cache Miss (With Fallback)

| Operation | Time (approx) |
|---|---|
| Partial restore from cache key | 1–3s |
| Incremental download | 3–8s |

## Cache Size

| Metric | Value |
|---|---|
| `~/.cache/uv` size | 100–500 MB |
| `.venv` size | 50–300 MB |
| Cache save time | 3–8s |
| Cache restore time | 1–3s |

## Key Observations

- uv resolves dependencies in under 1 second — pip takes 5–30s for the same project.
- Download parallelism makes uv 3–5× faster on cache miss.
- uv's hardlink deduplication keeps cache size smaller over time.

## Comparison with Pip

| Metric | pip | uv | Speedup |
|---|---|---|---|
| Cold install | 45–120s | 5–20s | 6–9× |
| Warm install | 5–15s | 1–3s | 5× |
| Cache size | 200–600 MB | 100–500 MB | ~20% less |

See [benchmark-pip-timing](./benchmark-pip-timing.md) for pip baseline data.
