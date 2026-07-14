# LLM Evaluation Pipeline

End-to-end LLM evaluation pipeline combining gold datasets, API calls, VCR recording, Pydantic validation, and CI automation.

## Contents

- [overview.md](./overview.md) — Topic hub and index

### Pipeline Architecture
- [pipeline-architecture.md](./pipeline-architecture.md) — End-to-end data flow
- [pipeline-data-contracts.md](./pipeline-data-contracts.md) — Interfaces between stages
- [pipeline-configuration.md](./pipeline-configuration.md) — YAML/JSON run configuration

### Gold Dataset
- [gold-dataset-structure.md](./gold-dataset-structure.md) — Pydantic schema
- [gold-dataset-formats.md](./gold-dataset-formats.md) — JSONL & Parquet storage
- [gold-dataset-test-train-split.md](./gold-dataset-test-train-split.md) — Splitting strategy
- [gold-dataset-versioning.md](./gold-dataset-versioning.md) — Iteration tracking

### Evaluation Execution
- [evaluation-execution-overview.md](./evaluation-execution-overview.md) — Live vs recorded workflow
- [evaluation-recorded-mode.md](./evaluation-recorded-mode.md) — VCR cassette replay
- [evaluation-live-mode.md](./evaluation-live-mode.md) — Real API calls
- [evaluation-batch-processing.md](./evaluation-batch-processing.md) — Multi-item processing
- [evaluation-caching-results.md](./evaluation-caching-results.md) — Result caching

### LLM-as-Judge
- [llm-as-judge-intro.md](./llm-as-judge-intro.md) — Using LLM as evaluator
- [llm-as-judge-rubric.md](./llm-as-judge-rubric.md) — Scoring rubric design
- [llm-as-judge-prompt-template.md](./llm-as-judge-prompt-template.md) — Prompt patterns
- [llm-as-judge-structured-output.md](./llm-as-judge-structured-output.md) — Pydantic output
- [llm-as-judge-multi-llm.md](./llm-as-judge-multi-llm.md) — Multi-model judging
- [llm-as-judge-calibration.md](./llm-as-judge-calibration.md) — Score calibration

### Results
- [results-aggregation.md](./results-aggregation.md) — Score aggregation
- [results-reporting.md](./results-reporting.md) — Report generation
- [results-comparison.md](./results-comparison.md) — Run comparison
- [results-chart-generation.md](./results-chart-generation.md) — Chart visualization

### CI / GitHub Actions
- [ci-pipeline-setup.md](./ci-pipeline-setup.md) — GHA workflow
- [ci-deterministic-replay.md](./ci-deterministic-replay.md) — VCR for repeatable CI
- [ci-cassette-regeneration.md](./ci-cassette-regeneration.md) — Auto re-record cassettes
- [ci-scheduled-evals.md](./ci-scheduled-evals.md) — Periodic cron evals

### Integration Cross-References
- [integration-pydantic-ai.md](./integration-pydantic-ai.md) — Pydantic AI
- [integration-vcrpy.md](./integration-vcrpy.md) — VCR.py
- [integration-llm-clients.md](./integration-llm-clients.md) — LLM API clients
- [integration-github-actions.md](./integration-github-actions.md) — GitHub Actions

### Reference
- [troubleshooting.md](./troubleshooting.md) — Common issues & fixes
