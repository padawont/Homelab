---
title: "Tooling Landscape for Documentation Compliance"
status: draft
author: "Khalid Zubair"
date: 2026-06-14
tags:
  - documentation
  - tooling
  - vale
  - markdownlint
  - lychee
  - linters
sources:
  - url: "https://vale.sh"
    title: "Vale — Prose linter"
  - url: "https://lychee.cli.rs"
    title: "Lychee — Broken link checker"
  - url: "https://github.com/btford/write-good"
    title: "write-good — English prose checker"
  - url: "https://github.com/get-alex/alex"
    title: "alex — Insensitive language checker"
  - url: "https://typedoc.org"
    title: "TypeDoc — TypeScript API documentation generator"
  - url: "https://github.com/DavidAnson/markdownlint"
    title: "markdownlint — Markdown linter"
last_audit_date: 2026-06-14
---

# Tooling Landscape for Documentation Compliance

A variety of open-source tools exist to automate documentation compliance checks. This note catalogs the most relevant ones and their use cases.

## Prose Linting

### Vale

- **Purpose:** Style guide enforcement, prose linting
- **Website:** https://vale.sh
- **Strengths:** Supports custom style guides, works with any markup format, extensible rule system
- **Use case:** Enforce Diátaxis-appropriate language patterns, company-specific terminology, tone rules
- **CI integration:** Native GitHub Action, pre-commit hook, standalone CLI

### write-good

- **Purpose:** English prose checker focused on clarity
- **Repository:** https://github.com/btford/write-good
- **Strengths:** Catches weasel words, passive voice, lexical illusions, redundancies
- **Use case:** Quick clarity checks on explanation and how-to content
- **Limitation:** Node.js only, limited configuration

## Markdown Formatting

### markdownlint

- **Purpose:** Markdown formatting rule enforcement
- **Strengths:** 50+ built-in rules, configurable severity, auto-fix capability
- **Use case:** Enforce consistent heading structure, list formatting, code block style across all documentation
- **CI integration:** Available as CLI (`markdownlint-cli2`) or GitHub Action

## Link Checking

### lychee

- **Purpose:** Broken link checker
- **Website:** https://lychee.cli.rs
- **Strengths:** Fast (Rust), handles relative/absolute links, supports multiple file types, configurable retry/exclude
- **Use case:** Verify all cross-links and external URLs resolve correctly
- **CI integration:** GitHub Action, pre-commit hook

## Inclusive Language

### alex

- **Purpose:** Insensitive language checker
- **Repository:** https://github.com/get-alex/alex
- **Strengths:** Detects gendered, ableist, and otherwise insensitive phrasing; offers suggestions
- **Use case:** Ensure documentation is inclusive and avoids problematic terminology
- **Integration:** Standalone CLI or GitHub Actions, with editor integrations for VS Code and Vim

## Documentation Coverage

### TypeDoc

- **Purpose:** TypeScript API documentation generator with coverage reporting
- **Website:** https://typedoc.org
- **Strengths:** Generates reference documentation from TypeScript type annotations; reports undocumented exports and members
- **Use case:** Track TypeScript API documentation coverage percentage; identify undocumented public symbols

### documentationjs

- **Purpose:** JSDoc to markdown generator with coverage reporting
- **Strengths:** Generates reference documentation from JSDoc annotations; reports undocumented items
- **Use case:** Track API documentation coverage percentage over time

### MkDocs coverage plugins

- **Purpose:** Static site coverage analysis for MkDocs-based documentation
- **Strengths:** Can compare documented pages against a manifest of expected content
- **Use case:** MkDocs projects that need structural completeness checks

## Integration Patterns

Tools are most effective when composed in a pipeline:

```
Pre-commit hook:
  markdownlint → Vale (diff only)

CI per PR:
  markdownlint --fix → Vale --style=diataxis → lychee → alex

Nightly/scheduled:
  Coverage analysis → stale content report → broken external URL scan
```
