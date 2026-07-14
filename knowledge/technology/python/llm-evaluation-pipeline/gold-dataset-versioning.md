---
title: "Gold Dataset Versioning"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - gold-dataset
  - versioning
sources: []
last_audit_date: 2026-06-09
---

# Gold Dataset Versioning

Track dataset iterations via version field and file naming.

## Version Strategy

Each gold entry carries a `version` integer. Bump it when:

- A new entry is added to the dataset.
- An existing entry's `expected` output is corrected.
- An entry's `input` or `metadata` is updated.

## File Naming Convention

```
evals/datasets/
├── code-gen-v1.jsonl      # initial version
├── code-gen-v2.jsonl      # after additions/fixes
└── code-gen-v3.jsonl      # after rubric changes
```

## Changelog

Maintain a version log in the dataset directory:

```yaml
# evals/datasets/code-gen-changelog.yaml
versions:
  - version: 1
    date: 2026-01-15
    changes: "Initial creation — 50 entries"
  - version: 2
    date: 2026-03-01
    changes: "Added 20 entries, fixed 3 expected outputs"
  - version: 3
    date: 2026-06-09
    changes: "Updated rubric dimensions, re-split"
```

## Cross-referencing

When re-recording VCR cassettes after a dataset change, see [ci-cassette-regeneration.md](ci-cassette-regeneration.md).
