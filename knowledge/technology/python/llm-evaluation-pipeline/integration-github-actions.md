---
title: "Integration: GitHub Actions"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - integration
  - github-actions
sources: []
last_audit_date: 2026-06-09
---

# Integration: GitHub Actions

Cross-reference to GitHub Actions CI/CD configuration.

## Related Topic

See `knowledge/operations/ci-cd/github-actions/` for GHA fundamentals.

## Usage in Pipeline

| Component | Workflow |
|---|---|
| [ci-pipeline-setup.md](ci-pipeline-setup.md) | Main eval workflow |
| [ci-deterministic-replay.md](ci-deterministic-replay.md) | VCR replay in CI |
| [ci-cassette-regeneration.md](ci-cassette-regeneration.md) | Auto PR for cassettes |
| [ci-scheduled-evals.md](ci-scheduled-evals.md) | Cron-triggered evals |

## Key Patterns

- Use `uv` (not `pip`) in all `run:` steps.
- Store API keys in `secrets.OPENAI_API_KEY`.
- Use `actions/upload-artifact` for result persistence.
- Use `peter-evans/create-pull-request` for automated PRs.
