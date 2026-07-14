---
title: "Common Caching Issues — Troubleshooting"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - troubleshooting
  - uv
  - vcr
  - docker
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions Caching Documentation"
last_audit_date: 2026-06-09
---

# Common Caching Issues — Troubleshooting

## Cache Not Restoring

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Cache not found` | Key mismatch | Verify `hashFiles` glob pattern matches actual files |
| Cache not found for first run | No prior cache | Expected — run once to populate |
| Restore returns wrong files | restore-key matched stale cache | Tighten restore-keys or add version prefix |

## Cache Too Large

GitHub Actions cache limit is 10 GB per repository. If exceeded:

- Cache both `~/.cache/uv` and `.venv` as separate entries with different keys.
- Use `uv cache clean` to remove unused cache segments.
- Switch to `mode=min` for Docker layer caching.

## Cache Poisoning

| Symptom | Likely Cause | Fix |
|---|---|---|
| Tests fail on one OS but pass on another | Cross-platform cache reuse | Add `runner.os` to key |
| Wrong Python version's site-packages | Missing Python version in key | Add `matrix.python-version` to `.venv` key |
| uv lock mismatch | Stale `~/.cache/uv` from different lock | Use lockfile hash in key |

## VCR Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| Tests fail with "No cassette" | VCR record_mode is `none` | Set `record_mode=new_episodes` on cache miss |
| Stale test data | Cassette not re-recorded | Purge cassettes and re-run |
| Cassette file conflicts | Parallel test runners | Use `record_mode=once` with per-process cassettes |

## Docker Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| All layers rebuilding | Cache from/to not configured | Add `cache-from: type=gha` and `cache-to: type=gha` |
| DLC cache pruned frequently | Inactivity > 7 days | Reduce cache scope or use registry backend |
| Layer cache not shared between PRs | Branch-scoped cache | Use `scope` parameter or registry backend |

## Cache Save Failures

- **"Cache size exceeded"**: Compress or split caches.
- **"Cache upload failed"**: Temporary GitHub Actions issue — retry.
- **"Cache service unavailable"**: Transient — workflow still succeeds, next run will populate.
