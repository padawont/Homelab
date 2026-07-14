---
title: "Quality Model — Functional vs Deep Quality"
status: draft
tags: [diataxis, quality, functional-quality, deep-quality]
author: "RunicEngines Knowledge Base"
date: 2026-06-14
sources:
  - url: https://diataxis.fr/quality/
    title: "Diátaxis — Towards a Theory of Quality in Documentation"
  - url: https://diataxis.fr/
    title: "Diátaxis — Home"
last_audit_date: 2026-06-14
---

# Quality Model — Functional vs Deep Quality

Diátaxis is fundamentally an approach to *quality* in documentation. It posits a distinction between two kinds of quality: **functional quality** and **deep quality**.

## Functional Quality

Functional quality refers to objectively measurable standards that documentation must meet:

| Property | Description |
|---|---|
| Accuracy | Documentation conforms to the world it describes |
| Completeness | All necessary information is present |
| Consistency | No internal contradictions or contradictory patterns |
| Usefulness | Documentation serves a practical purpose |
| Precision | Information is exact and unambiguous |

These properties are **independent** of each other — documentation can be accurate without being complete, or complete without being consistent.

Functional quality is **objective** — it belongs to the world and can be measured against it.

## Deep Quality

Deep quality refers to characteristics that go beyond functional correctness:

| Characteristic | Description |
|---|---|
| Feeling good to use | The documentation is pleasant to work with |
| Having flow | Movement through the documentation feels natural |
| Fitting to human needs | The documentation aligns with how people actually work |
| Being beautiful | The documentation is aesthetically well-crafted |
| Anticipating the user | The documentation seems to know what the user needs next |

These characteristics are **interdependent** — having flow and anticipating the user are aspects of each other. They cannot be measured numerically; they require *judgement*.

Deep quality is **subjective** — it can be assessed only in the light of human needs and experience.

## Key Differences

| Functional Quality | Deep Quality |
|---|---|
| Independent characteristics | Interdependent characteristics |
| Objective | Subjective |
| Measured against the world | Assessed against the human |
| A condition of deep quality | Conditional upon functional quality |
| Aspects of constraint | Aspects of liberation |

### Conditional Relationship

Deep quality is **conditional** upon functional quality. Documentation can be accurate and complete without being truly excellent — but it will never have deep quality without being accurate, complete, and consistent. The moment a user encounters a functional lapse, the experience of documentation is tarnished.

### Burden vs Liberation

Functional quality characteristics appear as **burdens and constraints** — each one represents a test that must be passed, and the work must be rechecked with every release.

Deep quality characteristics represent **liberation** — the work of creativity and taste. To attain functional quality, we must *conform*; to attain deep quality, we must *invent*.

## Diátaxis and Quality

### Cannot Fix Functional Quality

Diátaxis cannot address functional quality in documentation. It is concerned only with certain aspects of deep quality. Conscientious observance of the craft of documentation — solid technical skill and domain knowledge — is required for functional quality.

### Exposes Lapses in Functional Quality

Although Diátaxis cannot *give* us functional quality, it works effectively to **expose lapses** in it. Applying Diátaxis to existing documentation often makes problems suddenly apparent that were obscured before:

- Recommending that reference architecture mirrors code architecture makes gaps visible.
- Moving explanatory digressions out of a tutorial highlights where the reader has been left to work something out for themselves.

### Creates Conditions for Deep Quality

Diátaxis helps attain deep quality by:

- **Fitting user needs** — describing documentation modes based on user needs
- **Preserving flow** — preventing disruption when a digression into explanation interrupts a how-to guide
- **Structuring material** — organising content, form, and language to fit user needs

### Understanding the Limits

Diátaxis is not a formula or a short-cut. It does not by itself *make documentation beautiful*. It lays down some conditions for the *possibility* of deep quality, but the characteristics of deep quality are forever being renegotiated, reinterpreted, and reinvented.
