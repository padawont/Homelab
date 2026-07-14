---
title: "Performance Optimization"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - performance
  - optimization
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/performance/"
    title: "Pydantic Performance Guide"
last_audit_date: 2026-06-09
---

# Performance Optimization

## Fast Validation Tips

1. **Use `model_validate_json()`** instead of `json.loads()` + `model_validate()` — Rust-based JSON parsing is faster because `model_validate_json()` performs validation internally without an intermediate Python dict.

   > ⚠️ **Caveat**: `model_validate(json.loads(...))` may be faster when using `'before'` or `'wrap'` validators, since those validators intercept the raw input and the two-step approach avoids redundant internal parsing. See [this discussion](https://github.com/pydantic/pydantic/discussions/6388#discussioncomment-8193105) for details.

2. **Reuse `TypeAdapter` for repeated validation** — instantiate `TypeAdapter` once at module level rather than inside a function, so the validator and serializer are constructed only once.

3. **Use `Strict` types sparingly** — strict mode checks are more expensive than coercion.

   > *(Author's note: This recommendation is not from the cited Pydantic Performance Guide; it is inferred from general principles of strict-mode overhead.)*

## Patterns to Avoid

- **Avoid per-item `model_validate` loops** — instead, use `TypeAdapter(list[Item])` instantiated at module level (see Tip #2) for batched validation.

> *(Experience note: A container model pattern like `ItemList(BaseModel)` wrapping a list is an experience-based optimization, not from the cited Pydantic Performance Guide. Prefer `TypeAdapter` reuse as the source-backed alternative.)*

## Model Design

- **Use tagged (discriminated) unions** with `Field(discriminator=...)` instead of plain `Union` types — the discriminator lets Pydantic-core short-circuit type matching without attempting each branch
- **Avoid `'wrap'` validators if you really care about performance** — they materialize data in Python during validation, bypassing Rust-core speed
- **Use `TypedDict` over nested models** for pure data structures — `TypedDict` is approximately 2.5× faster in benchmarks (see [Pydantic Performance Guide](https://docs.pydantic.dev/latest/concepts/performance/))

See [field types](./field-types.md) for type choice guidance, and [deserialization from json](./deserialization-from-json.md) for the fast JSON parser.
