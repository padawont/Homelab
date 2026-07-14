---
title: "CI Pipeline Setup"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - ci
  - github-actions
sources: []
last_audit_date: 2026-06-09
---

# CI Pipeline Setup

GitHub Actions workflow for automated LLM evaluation.

## Basic Workflow

```yaml
# .github/workflows/eval.yml
name: LLM Evaluation
on:
  push:
    branches: [main]
  pull_request:
    paths:
      - "evals/**"
      - "knowledge/technology/python/llm-evaluation-pipeline/**"

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Sync dependencies
        run: uv sync

      - name: Run evaluation
        run: uv run python run_eval.py evals/configs/ci.yaml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Archive results
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: evals/results/
```

## CI-Specific Config

```yaml
# evals/configs/ci.yaml
run_id: "ci-${GITHUB_SHA::8}"
model:
  provider: openai
  name: gpt-4o-mini
  temperature: 0.0
dataset:
  path: evals/datasets/code-gen-v2.test.jsonl    # test split only
vcr:
  enabled: true                                    # recorded mode
  cassette_dir: evals/cassettes/
  record_mode: none                                # fail if cassette missing
```

See [ci-deterministic-replay.md](ci-deterministic-replay.md) for VCR details and [integration-github-actions.md](integration-github-actions.md) for cross-ref.
