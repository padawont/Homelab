---
title: "Pipeline Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - pipeline
  - configuration
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI"
last_audit_date: 2026-06-09
---

# Pipeline Configuration

YAML/JSON config files for evaluation runs.

## Example Config

```yaml
run_id: "eval-2026-06-09"
model:
  provider: openai
  name: gpt-4o
  temperature: 0.0

dataset:
  path: evals/datasets/code-gen-v2.jsonl
  sample: 50               # optional subset

judge:
  model: gpt-4o-mini
  rubric: rubrics/helpfulness.yaml

vcr:
  enabled: true
  cassette_dir: evals/cassettes/
  record_mode: once         # once | new_episodes | none

output:
  results_dir: evals/results/
  report_dir: evals/reports/
```

## Loading Config

```python
from pydantic import BaseModel, Field
import yaml


class VCRConfig(BaseModel):
    enabled: bool = True
    cassette_dir: str = "evals/cassettes/"
    record_mode: str = "once"


class RunConfig(BaseModel):
    run_id: str
    model: dict
    dataset: dict
    judge: dict | None = None
    vcr: VCRConfig = VCRConfig()
    output: dict = Field(default_factory=lambda: {
        "results_dir": "evals/results/",
        "report_dir": "evals/reports/"
    })


def load_config(path: str) -> RunConfig:
    with open(path) as f:
        return RunConfig.model_validate(yaml.safe_load(f))
```

See [evaluation-batch-processing.md](evaluation-batch-processing.md) for config-driven batch runs.
