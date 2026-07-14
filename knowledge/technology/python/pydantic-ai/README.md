# Pydantic AI

Data validation framework for gold datasets and structured LLM outputs.

## Installation & Setup

- [installation.md](./installation.md) — `uv add`, Python version requirements, dependencies

## Core Models

- [defining-models.md](./defining-models.md) — `BaseModel` class syntax, basic field declarations
- [field-types.md](./field-types.md) — `str`, `int`, `float`, `bool`, `Enum`, `Literal`, `Optional`, `List`, `Dict`
- [field-defaults.md](./field-defaults.md) — `default`, `default_factory` patterns
- [field-aliases.md](./field-aliases.md) — `Field(alias=...)`, `populate_by_name` config
- [nested-models.md](./nested-models.md) — Model with `List[OtherModel]`, nested schema patterns
- [union-types.md](./union-types.md) — `Union[A, B]`, annotated validators
- [discriminated-unions.md](./discriminated-unions.md) — Tagged union with `Discriminator`
- [generic-models.md](./generic-models.md) — `Generic[T]`, `TypeVar` usage

## Validation

- [field-validation.md](./field-validation.md) — `@field_validator` syntax and usage
- [model-validation.md](./model-validation.md) — `@model_validator` syntax and usage
- [validation-context.md](./validation-context.md) — `ValidationInfo`, context parameter
- [validation-before-after-wrap.md](./validation-before-after-wrap.md) — `before`/`after`/`wrap` validator modes
- [model-config.md](./model-config.md) — `model_config` options reference

## Serialization & Deserialization

- [serialization-model-dump.md](./serialization-model-dump.md) — `model_dump()` with `exclude`, `include`, `by_alias`
- [serialization-json.md](./serialization-json.md) — `model_dump_json()` with custom encoder
- [deserialization-model-validate.md](./deserialization-model-validate.md) — `model_validate()` from dict
- [deserialization-from-json.md](./deserialization-from-json.md) — `model_validate_json()` from string

## Error Handling

- [error-handling.md](./error-handling.md) — `ValidationError` structure, accessing errors

## Structured LLM Outputs

- [structured-outputs-intro.md](./structured-outputs-intro.md) — When to use `with_structured_output`
- [structured-outputs-basemodel.md](./structured-outputs-basemodel.md) — Returning `BaseModel` from LLM calls
- [structured-outputs-typed-dict.md](./structured-outputs-typed-dict.md) — `TypedDict` as output type
- [structured-outputs-dataclass.md](./structured-outputs-dataclass.md) — `dataclass` as output type
- [structured-outputs-streaming.md](./structured-outputs-streaming.md) — Streaming structured output chunks

## Evaluation & Datasets

- [gold-dataset-schemas.md](./gold-dataset-schemas.md) — Schema patterns for evaluation datasets
- [gold-dataset-versioning.md](./gold-dataset-versioning.md) — Dataset iteration and tracking
- [llm-judge-scoring.md](./llm-judge-scoring.md) — LLM-as-judge evaluation setup
- [llm-judge-rubrics.md](./llm-judge-rubrics.md) — Scoring rubrics with Pydantic models

## Integration & Performance

- [integration-vcrpy.md](./integration-vcrpy.md) — Validating VCR.py cassette responses against Pydantic models
- [performance-optimization.md](./performance-optimization.md) — Fast validation tips, avoiding slow patterns
- [troubleshooting.md](./troubleshooting.md) — Common errors and solutions
