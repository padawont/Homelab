---
title: "Diátaxis Quality as Compliance Criteria"
status: draft
author: "Khalid Zubair"
date: 2026-06-14
tags:
  - diataxis
  - documentation-quality
  - compliance
  - quality-model
sources:
  - url: "https://diataxis.fr/quality/"
    title: "Diátaxis — Quality"
last_audit_date: 2026-06-14
---

# Diátaxis Quality as Compliance Criteria

> See [Quality Model](../diataxis/quality-model.md) for the canonical definition of the
> Diátaxis two-tier quality model. This note applies that model specifically to
> documentation compliance checking.

The Diátaxis framework defines two tiers of documentation quality that compliance checking should measure wherever possible.

## Functional Quality

Functional quality is objective and rule-based — the kind of thing an automated tool can detect:

| Criterion | Description | How to check |
|---|---|---|
| **Accuracy** | Content is factually correct, code samples compile, API docs match the implementation | Integration tests, schema validation, [link checks](./tooling.md) |
| **Completeness** | All necessary content is present — no missing sections, endpoints, or options | [Coverage analysis](./coverage-analysis.md), [structural audits](./structural-compliance.md) |
| **Consistency** | Terminology, tone, formatting, and conventions are uniform across the documentation | [Style guide enforcement](./tooling.md), [linters](./tooling.md) |
| **Usefulness** | Content serves its stated purpose — tutorials teach, references describe | User testing, task-completion metrics |
| **Precision** | Content is specific, concrete, and unambiguous | [Prose linters](./tooling.md), readability scores |

## Deep Quality

Deep quality is subjective and harder to automate — it requires human judgment or advanced heuristics:

| Criterion | Description |
|---|---|
| **Feeling good to use** | The documentation is pleasant and satisfying to interact with; users enjoy working with it |
| **Having flow** | The documentation guides the reader naturally from one concept to the next; there are no abrupt jumps or missing prerequisites |
| **Fitting to human needs** | Content is structured around user tasks and contexts, not the system's internal architecture |
| **Being beautiful** | Visual presentation, typography, diagrams, and layout make the documentation pleasant to use |
| **Anticipating the user** | The docs answer questions the reader has before they have to ask; error messages include solutions |

## Compliance Implications

A comprehensive compliance system should:

1. **Automate functional checks** — run [linters, coverage tools, and link checkers](./tooling.md) in CI
2. **Flag deep-quality gaps** — use checklists or review templates during manual reviews rather than ignoring these dimensions entirely
3. **Track both types in a dashboard** — functional checks produce pass/fail numbers; deep quality uses periodic sampling or user surveys

## References

- [Diátaxis — Quality](https://diataxis.fr/quality/) — canonical definition of the two-tier quality model
