---
title: "llms.txt vs robots.txt vs sitemap.xml"
status: draft
author: "Khalid Zubair"
date: 2026-06-14
tags:
  - llms-txt
  - robots-txt
  - sitemap
  - comparison
  - web-standards
sources:
  - url: "https://llmstxt.org"
    title: "The /llms.txt file"
  - url: "https://github.com/AnswerDotAI/llms-txt"
    title: "AnswerDotAI/llms-txt — GitHub Repository"
last_audit_date: 2026-06-14
---

# llms.txt vs robots.txt vs sitemap.xml

The llms.txt proposal follows the established pattern of using a well-known path for a machine-readable file, joining `robots.txt` and `sitemap.xml`. Each serves a distinct purpose and targets a different lifecycle stage.

## Comparison Table

| Aspect | `robots.txt` | `sitemap.xml` | `llms.txt` |
|---|---|---|---|
| **Path** | `/robots.txt` | `/sitemap.xml` | `/llms.txt` |
| **Author** | Martijn Koster (1994) | Sitemaps Protocol (2005) | Jeremy Howard (2024) |
| **Primary Audience** | Crawlers (search bots) | Search engines | LLMs and AI agents |
| **Purpose** | Control crawler access permissions | List all indexable pages | Curated overview for LLM inference |
| **Lifecycle** | Training time (indexing) | Training time (indexing) | Inference time (on-demand use) |
| **Format** | Plain text (directives) | XML | Markdown |
| **Content Scope** | What to allow/deny | All public pages | Curated, expert-level subset |
| **Optional Filtering** | `Disallow` directives | Priority/frequency hints | `Optional` section headings |

## Detailed Comparison

### robots.txt

- **Controls crawler access** — tells automated tools what parts of a site are acceptable to crawl.
- **Training-time focus** — used during search indexing and, increasingly, during LLM training data collection.
- **Restrictive by nature** — specifies what should *not* be accessed.
- **Does not provide content** — it gives access rules, not the information itself.

### sitemap.xml

- **Lists all indexable pages** — provides a comprehensive XML listing of every public URL on a site.
- **Training-time focus** — helps search engines discover and prioritize content for indexing.
- **No LLM-friendly URLs** — typically lists HTML pages, not their Markdown equivalents.
- **Does not curate** — covers every page, resulting in far more URLs than an LLM context window can handle.
- **No external links** — only includes URLs within the same domain/site.

### llms.txt

- **Curated for LLMs** — hand-picked links with descriptions, optimized for understanding a project or site.
- **Inference-time focus** — used on-demand when a user requests information (e.g., coding assistant fetching library docs).
- **Provides context** — includes a summary and explanatory sections to help the LLM interpret linked resources.
- **Concise** — deliberately small enough to fit in an LLM context window.
- **External links allowed** — can reference URLs from other sites that are helpful for understanding.

## Coexistence

These three standards are complementary, not competitive:

```
robots.txt     → "You may crawl these paths"
sitemap.xml    → "Here are all my pages"
llms.txt       → "Here is the important stuff for understanding my site"
```

A well-configured site should have all three. For example:
- `robots.txt` allows a search bot to crawl the `/docs/` path
- `sitemap.xml` lists every HTML page in `/docs/`
- `llms.txt` points to the 10 most important Markdown pages in `/docs/` with descriptions, helping an LLM answer developer questions during inference

## Future Considerations

The standardization path follows the same approach as `robots.txt` and `sitemap.xml`: define a well-known URL path and a file format. While current usage focuses on inference time, widespread adoption could also benefit future LLM training runs that want to identify high-quality, curated content sources.
