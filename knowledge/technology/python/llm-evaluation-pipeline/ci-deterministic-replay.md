---
title: "CI Deterministic Replay"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - ci
  - vcr
  - deterministic
sources:
  - url: "https://vcrpy.readthedocs.io/en/latest/"
    title: "VCR.py Documentation"
last_audit_date: 2026-06-09
---

# CI Deterministic Replay

Use VCR.py cassettes in CI for fast, repeatable evaluation runs.

## Why Deterministic

- No network calls → runs in seconds, not minutes.
- No API keys needed in CI → works on PRs from forks.
- Bit-identical re-runs → only code/dataset changes affect results.

## Cassette Directory

```
evals/cassettes/
├── ci-abc12345.yaml          # one per run_id
├── ci-def67890.yaml
└── ci-ghi11121.yaml
```

## CI Configuration

```yaml
vcr:
  enabled: true
  cassette_dir: evals/cassettes/
  record_mode: none           # strict — fails on unknown requests
```

## Recording Cassettes

Cassettes are recorded manually or automatically:

- **Manual**: run locally with `record_mode: once` once, commit cassette.
- **Automatic**: See [ci-cassette-regeneration.md](ci-cassette-regeneration.md).

## Cassette Validation

Pin cassettes in CI with a checksum check:

```yaml
- name: Verify cassette checksum
  run: sha256sum evals/cassettes/ci-*.yaml > cassettes.sha256
- name: Validate cassettes
  run: sha256sum -c cassettes.sha256
```

See [ci-pipeline-setup.md](ci-pipeline-setup.md) for the full workflow.
