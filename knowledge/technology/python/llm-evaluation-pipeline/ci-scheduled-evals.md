---
title: "CI Scheduled Evals"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - ci
  - scheduled
  - cron
sources: []
last_audit_date: 2026-06-09
---

# CI Scheduled Evals

Periodic evaluation runs triggered by cron — track model drift over time.

## Workflow

```yaml
# .github/workflows/scheduled-eval.yml
name: Scheduled Evaluation
on:
  schedule:
    - cron: "0 6 * * 1"   # every Monday 06:00 UTC
  workflow_dispatch:        # manual trigger too

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Sync
        run: uv sync
      - name: Run live evaluation
        run: uv run python run_eval.py evals/configs/scheduled.yaml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Archive results with date
        run: |
          DATE=$(date +%Y-%m-%d)
          cp -r evals/results "evals/results-$DATE"

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: weekly-eval-${{ github.run_id }}
          path: evals/results-*/
```

## Scheduled Config

```yaml
# evals/configs/scheduled.yaml
run_id: "weekly-$(date +%Y-%m-%d)"
model:
  provider: openai
  name: gpt-4o
  temperature: 0.0
dataset:
  path: evals/datasets/code-gen-v3.full.jsonl
  sample: 30
vcr:
  enabled: false             # live — capture current model behavior
```

## Trend Tracking

Compare weekly runs in [results-comparison.md](results-comparison.md) and chart trends via [results-chart-generation.md](results-chart-generation.md).
