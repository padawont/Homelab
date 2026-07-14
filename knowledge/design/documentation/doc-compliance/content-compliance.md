---
title: "Content Compliance"
status: draft
author: "Khalid Zubair"
date: 2026-06-14
tags:
  - documentation
  - content-compliance
  - diataxis
  - stale-content
sources:
  - url: "https://diataxis.fr/"
    title: "Diataxis — The four types of documentation"
  - url: "https://www.writethedocs.org/guide/docs-as-code/"
    title: "Write the Docs — Docs as Code"
  - url: "https://diataxis.fr/tutorials/#the-language-of-tutorials"
    title: "Diataxis — The language of tutorials"
  - url: "https://diataxis.fr/how-to-guides/#the-language-of-how-to-guides"
    title: "Diataxis — The language of how-to guides"
last_audit_date: 2026-06-14
---

# Content Compliance

Content compliance checks that what is written is appropriate for where it appears. These checks require more sophistication than [structural checks](./structural-compliance.md) and often blend automation with human review. See also [Diátaxis Quality as Compliance Criteria](./diataxis-quality.md) for the quality model that underpins these checks.

## Diataxis Quadrant Classification

Each piece of documentation should belong to exactly one Diataxis quadrant. Common violations:

| Violation | Example | Fix |
|---|---|---|
| **Explanation in tutorials** | A step-by-step lesson that includes a 3-page history of the feature | Move historical context to an explanation page; link from the tutorial |
| **How-to in reference** | A reference page for an API endpoint that includes "how to authenticate" instructions | Keep reference purely descriptive; link to the how-to guide |
| **Tutorial in how-to** | A "how to deploy" page that expects the reader to follow from scratch | Split: keep the how-to concise; create a tutorial for beginners |
| **Reference in explanation** | An explanation page that becomes a dumping ground for configuration tables | Move structured data to reference; keep explanation narrative |

Automation approaches:
- **Keyword heuristics**: Count imperative verbs (tutorials/how-tos) vs declarative statements (reference/explanation)
- **Classifier models**: Train a lightweight text classifier on labelled pages
- **Frontmatter tagging**: Require explicit `diataxis_quadrant` field in frontmatter; flag mismatches with content analysis

## Language Pattern Compliance

Each quadrant has characteristic language patterns:

| Quadrant | Voice | Tense | Grammar |
|---|---|---|---|
| Tutorials | First-person plural ("We will") | Present/future | Short sentences, numbered steps |
| How-to Guides | Second person ("Do x to achieve y") | Present (imperative mood) | Action-oriented, problem-solution |
| Reference | Third person ("Returns a list") | Present | Definitions, signatures, tables |
| Explanation | Third person ("This occurs because") | Present/past | Paragraphs, analogies, background |

A [prose linter](./tooling.md) (e.g., Vale with a custom style) can flag mismatches — for instance, imperative mood in a reference page or second-person address in an explanation. See [Tooling Landscape](./tooling.md) for available tools.

## Stale Content Detection

Content that is outdated or no longer accurate must be identified and flagged:

| Technique | Description |
|---|---|
| **Age thresholds** | Flag pages not updated in N months (e.g., 12 months for stable docs, 3 months for beta features) |
| **Deprecation tags** | Require a `deprecated: true` frontmatter field for marked-as-deprecated features |
| **Version pinning** | Code samples that reference unmaintained versions (e.g., Python 2.7, Node 12) |
| **CI timestamps** | Each page records its `last_audit_date`; CI warns when this exceeds the threshold |
| **Dead link cascading** | A page with many [broken links](./tooling.md) is likely stale overall, not just structurally broken |

## Best Practices

- Run content compliance checks on every PR that touches documentation
- Combine automated flagging with a manual review checklist
- Use a docs health dashboard showing quadrant distribution, staleness, and classification confidence
