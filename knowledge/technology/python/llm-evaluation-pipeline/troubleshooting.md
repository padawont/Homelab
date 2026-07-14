---
title: "Troubleshooting"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - troubleshooting
sources: []
last_audit_date: 2026-06-09
---

# Troubleshooting

Common issues and solutions for the LLM evaluation pipeline.

## VCR Cassette Mismatch

**Symptom**: `CassetteNotFound: No matching cassette entry for request`
**Cause**: Request differs from recorded cassette (changed model, temperature, or prompt).
**Fix**: Re-record cassettes (see [ci-cassette-regeneration.md](ci-cassette-regeneration.md)).

## Structured Output Parsing Failure

**Symptom**: `pydantic.ValidationError` when parsing judge response
**Cause**: Judge model output doesn't match the expected schema.
**Fix**: Verify the prompt template matches the Pydantic model. Add `response_format` parameter.

## Rate Limit Errors

**Symptom**: `429 Too Many Requests` in live mode
**Cause**: Exceeding API rate limits during batch processing.
**Fix**: Add delays or use exponential backoff:

```python
import time
import random

def execute_with_retry(executor, item, max_retries=3):
    for attempt in range(max_retries):
        try:
            return executor.execute(item)
        except Exception as e:
            if "429" in str(e):
                time.sleep(2 ** attempt + random.random())
                continue
            raise
```

## CI Fails on PR from Fork

**Symptom**: `OPENAI_API_KEY not set`
**Cause**: Fork PRs don't have access to secrets.
**Fix**: Ensure VCR is enabled with `record_mode: none` so no API calls are made.

## Dataset Version Mismatch

**Symptom**: Results reference old `version` field
**Cause**: Dataset updated but config still points to old file.
**Fix**: Update `dataset.path` in config (see [pipeline-configuration.md](pipeline-configuration.md)).
