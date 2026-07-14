---
title: "Pipeline Architecture"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - pipeline
  - architecture
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI"
  - url: "https://docs.pytest.org/"
    title: "pytest Documentation"
last_audit_date: 2026-06-09
---

# Pipeline Architecture

End-to-end data flow for LLM evaluation.

## Stages

```
Gold Dataset ──► Item Sampler ──► Execution (Live/Recorded)
                                   │
                                   ├──► LLM API Call
                                   ├──► LLM-as-Judge
                                   └──► Result Collector
                                         │
                                         ▼
                                   Aggregation ──► Reports ──► Charts
```

## Directory Layout

```
evals/
├── datasets/          # Gold datasets (JSONL, Parquet)
├── cassettes/         # VCR cassettes
├── configs/           # YAML run configs
├── results/           # Raw per-item results
├── reports/           # Aggregated reports (JSON/MD)
└── charts/            # Generated chart images
```

## Execution Modes

- **Recorded** (`VCR=True`): Replay cassettes for fast, deterministic runs.
- **Live** (`VCR=False`): Hit real APIs for ground-truth updates.

See [evaluation-live-mode.md](evaluation-live-mode.md) and [evaluation-recorded-mode.md](evaluation-recorded-mode.md).
