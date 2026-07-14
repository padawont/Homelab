---
title: "llms.txt Format Specification"
status: draft
author: "Khalid Zubair"
date: 2026-06-14
tags:
  - llms-txt
  - specification
  - markdown
  - documentation
sources:
  - url: "https://llmstxt.org"
    title: "The /llms.txt file"
  - url: "https://github.com/AnswerDotAI/llms-txt"
    title: "AnswerDotAI/llms-txt — GitHub Repository"
last_audit_date: 2026-06-14
---

# llms.txt Format Specification

The `llms.txt` file lives at the root path `/llms.txt` of a website (or optionally in a subpath). It uses plain Markdown with a strict section ordering to remain both human-readable and machine-parseable via regex or classical parsing techniques.

## Required Sections (in order)

The file must follow this exact section order:

1. **Optional BOM** — A byte-order mark may be present.
2. **H1 with project/site name** — `# Title`. This is the **only required** section. Everything else is optional.
3. **Blockquote summary** — `> Brief description`. A short summary containing key information needed to understand the rest of the file.
4. **Info sections (zero or more)** — Any Markdown content except headings (paragraphs, lists, code blocks, etc.). Provides detailed background about the project and how to interpret linked files.
5. **H2-delimited file lists (zero or more)** — Sections starting with `## SectionName`, each containing a Markdown list of hyperlinks.

### File List Entry Format

Each entry in an H2 section is a Markdown list item:

```markdown
- [Link Title](https://url): Optional notes about the file
```

- The hyperlink `[name](url)` is **required**.
- The `: notes` suffix is **optional**.
- URLs should point to clean Markdown versions of pages (typically the original URL with `.md` appended).

## Special Section: "Optional"

An H2 section titled exactly **`Optional`** has special meaning: URLs listed under it can be **skipped** when a shorter context is needed. Use it for secondary or supplementary information.

```markdown
## Optional

- [Extended reference](https://example.com/docs/extended.md): Deep-dive material, safe to omit
```

## Design Rationale

The spec uses Markdown rather than a structured format like XML because these files are primarily read by LLMs and agents at inference time. Markdown is the most widely understood format for language models. Despite this, the precise ordering and fixed patterns make the file equally parsable by classical programming techniques.

## Mock Example

```markdown
# My Project

> A short summary describing the project.

Some additional context about the project that helps
interpret the linked resources below.

## Documentation

- [Getting Started](https://example.com/docs/start.md): Quick setup guide
- [API Reference](https://example.com/docs/api.md): Full API documentation

## Tutorials

- [Beginner Tutorial](https://example.com/tutorials/intro.md)

## Optional

- [Historical Background](https://example.com/background.md)
```

## Markdown Pages Convention

Websites that serve HTML pages should also provide a clean Markdown version at the same URL with `.md` appended. For URLs without a file name (directory-style URLs), append `index.html.md` instead. This gives LLMs a plain-text alternative to navigation-heavy, JavaScript-laden HTML.
