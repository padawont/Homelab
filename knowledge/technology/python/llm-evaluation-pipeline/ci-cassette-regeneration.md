---
title: "CI Cassette Regeneration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - ci
  - vcr
  - regeneration
sources:
  - url: "https://vcrpy.readthedocs.io/en/latest/"
    title: "VCR.py Documentation"
last_audit_date: 2026-06-09
---

# CI Cassette Regeneration

Auto re-record VCR cassettes when schemas or datasets change.

## Trigger Scenarios

- Gold dataset version bumped (see [gold-dataset-versioning.md](gold-dataset-versioning.md))
- Judge rubric changed (see [llm-as-judge-rubric.md](llm-as-judge-rubric.md))
- Model provider schema changes (API response format)

## Regeneration Workflow

```yaml
# .github/workflows/regenerate-cassettes.yml
name: Regenerate Cassettes
on:
  workflow_dispatch:
    inputs:
      run_id:
        description: "Run ID for cassette"
        required: true

jobs:
  record:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Sync and record
        run: uv run python run_eval.py evals/configs/record.yaml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Create PR
        uses: peter-evans/create-pull-request@v6
        with:
          commit-message: "chore(eval): regenerate cassettes for ${{ github.event.inputs.run_id }}"
          branch: eval/regenerate-cassettes
          delete-branch: true
          title: "Regenerate VCR cassettes for ${{ github.event.inputs.run_id }}"
```

## Recording Config

```yaml
# evals/configs/record.yaml
vcr:
  enabled: true
  record_mode: once        # writes new cassette
```

Always review cassette diffs before merging. See [ci-deterministic-replay.md](ci-deterministic-replay.md) for replay mode.
