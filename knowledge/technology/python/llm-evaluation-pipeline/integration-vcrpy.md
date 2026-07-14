---
title: "Integration: VCR.py"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - integration
  - vcrpy
sources:
  - url: "https://vcrpy.readthedocs.io/en/latest/"
    title: "VCR.py Documentation"
last_audit_date: 2026-06-09
---

# Integration: VCR.py

Cross-reference to VCR.py for HTTP recording/replay.

## Related Topic

See `knowledge/technology/python/vcrpy/` for VCR.py details.

## Usage in Pipeline

VCR is the backbone of deterministic CI evaluation:

| Component | VCR Mode |
|---|---|
| [evaluation-recorded-mode.md](evaluation-recorded-mode.md) | Primary usage — recorded execution |
| [ci-deterministic-replay.md](ci-deterministic-replay.md) | CI replay with `record_mode: none` |
| [ci-cassette-regeneration.md](ci-cassette-regeneration.md) | Re-recording cassettes |

## Installation

```
uv add vcrpy
```

## Basic Pattern

```python
import vcr

cassette = vcr.use_cassette("evals/cassettes/run.yaml", record_mode="once")
with cassette:
    response = client.chat.completions.create(...)  # recorded/replayed
```
