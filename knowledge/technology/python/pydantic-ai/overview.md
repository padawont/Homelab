---
title: "Pydantic AI"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - data-validation
  - llm
  - structured-outputs
sources:
  - url: "https://pydantic.ai/"
    title: "Pydantic AI — Official Site"
  - url: "https://docs.pydantic.dev/latest/"
    title: "Pydantic Documentation"
  - url: "https://ai.pydantic.dev/"
    title: "Pydantic AI Documentation"
last_audit_date: 2026-06-09
---

# Pydantic AI

Pydantic is the most widely used data validation library for Python, providing runtime type checking and serialization via `BaseModel`. Pydantic AI extends this with structured LLM output extraction.

## Atomic Notes

This topic contains 31 atomic notes covering:

| Area | Notes |
|---|---|
| **Core Models** | defining-models, field-types, field-defaults, field-aliases, nested-models, union-types, discriminated-unions, generic-models |
| **Validation** | field-validation, model-validation, validation-context, validation-before-after-wrap, model-config |
| **Serialization** | serialization-model-dump, serialization-json, deserialization-model-validate, deserialization-from-json |
| **Error Handling** | error-handling |
| **LLM Outputs** | structured-outputs-intro, structured-outputs-basemodel, structured-outputs-typed-dict, structured-outputs-dataclass, structured-outputs-streaming |
| **Evaluation** | gold-dataset-schemas, gold-dataset-versioning, llm-judge-scoring, llm-judge-rubrics |
| **Integration** | integration-vcrpy, performance-optimization, troubleshooting |

See [README.md](./README.md) for the full index.
