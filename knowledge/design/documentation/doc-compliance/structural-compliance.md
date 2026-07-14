---
title: "Structural Compliance"
status: draft
author: "Khalid Zubair"
date: 2026-06-14
tags:
  - documentation
  - structural-compliance
  - diataxis
  - frontmatter
  - cross-links
sources:
  - url: "https://diataxis.fr/"
    title: "Diataxis — The four types of documentation"
last_audit_date: 2026-06-14
---

# Structural Compliance

Structural compliance checks that a documentation site has all required components in place. These checks are the easiest to automate and should run as part of CI.

## Diataxis Section Coverage

Every documentation set following the Diataxis framework must have content in all four quadrants:

| Quadrant | Purpose | Required |
|---|---|---|
| **Tutorials** | Learning-oriented, step-by-step lessons | Yes |
| **How-to Guides** | Goal-oriented, recipes for specific problems | Yes |
| **Reference** | Information-oriented, authoritative descriptions | Yes |
| **Explanation** | Understanding-oriented, background and discussion | Yes |

A structural compliance check verifies that at least one page exists under each quadrant.

## Required Repository Files

Most documentation repositories are expected to include these standard files:

| File | Purpose |
|---|---|
| `README.md` | Project overview, quick start |
| `CHANGELOG.md` | Version history and release notes |
| `CONTRIBUTING.md` | Guide for contributors |
| `LICENSE` | Licensing information |

## Frontmatter Validation

All documentation pages should have valid frontmatter (YAML) that meets the project's schema requirements:

- Required fields are present and non-empty
- Field types match expectations (e.g., `date` is `YYYY-MM-DD`)
- Status values come from the allowed lifecycle
- Tags are kebab-case
- Template comments have been removed

## Cross-Link Resolution

Every cross-reference within the documentation must resolve to an existing target file or URL:

- Relative `[links](path/to/file.md)` resolve on disk
- Absolute paths point to valid locations in the repository
- URL references are reachable (checked periodically or with a head-request)
- No dangling internal anchors (`[text](#missing-anchor)`)

## Compliance Automation

Structural checks are well-suited for CI pipelines:

```
# Example: structural compliance check in CI
- Run markdownlint on all .md files
- Run frontmatter schema validation
- Run lychee for broken links
- Assert required files exist
- Assert Diataxis quadrant directories exist
```
