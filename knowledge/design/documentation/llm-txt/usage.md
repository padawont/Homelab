---
title: "llms.txt Companion Files and CLI Tools"
status: draft
author: "Khalid Zubair"
date: 2026-06-14
tags:
  - llms-txt
  - cli
  - context-generation
  - llms_txt2ctx
sources:
  - url: "https://llmstxt.org"
    title: "The /llms.txt file"
  - url: "https://llmstxt.org/intro.html"
    title: "Python module & CLI — llms-txt"
  - url: "https://github.com/AnswerDotAI/llms-txt"
    title: "AnswerDotAI/llms-txt — GitHub Repository"
last_audit_date: 2026-06-14
---

# Companion Files and CLI Tools

The llms.txt proposal includes companion files that expand the curated link list into full LLM context documents, and a CLI tool to generate them.

## Companion Files

### llms-ctx.txt

An expanded version of the `llms.txt` that includes the **contents** of all linked Markdown files (excluding those under the `Optional` section). The output uses an XML-based structure suitable for LLMs such as Claude. This provides a single document with the essential project information within a manageable context size.

### llms-ctx-full.txt

Same as `llms-ctx.txt` but **includes** the content from `Optional` section URLs. Use this when the context window is large enough to accommodate supplementary material.

### Naming Convention

Both files sit alongside `llms.txt` on the web server (e.g. `https://example.com/llms-ctx.txt`, `https://example.com/llms-ctx-full.txt`).

## llms_txt2ctx CLI

The official Python CLI for generating context files from `llms.txt` input.

### Installation

```bash
pip install llms-txt
```

### Usage

Convert an `llms.txt` file to XML context and output to `llms.md`:

```bash
llms_txt2ctx llms.txt > llms.md
```

Include the Optional section:

```bash
llms_txt2ctx --optional True llms.txt > llms-ctx-full.txt
```

Get help:

```bash
llms_txt2ctx -h
```

## Python API

The `llms-txt` package also exposes a Python API for programmatic use:

```python
from llms_txt import *

# Parse an llms.txt file into a structured data object
parsed = parse_llms_file("path/to/llms.txt")
# parsed.title, parsed.summary, parsed.sections

# Generate XML context for LLMs
ctx = create_ctx("path/to/llms.txt")
```

The `parse_llms_file` function returns an object with `title`, `summary`, `info`, and `sections` attributes. The `create_ctx` function produces the XML context output that the CLI writes to stdout.

## Reference Parser

The reference implementation includes a complete parser in under 20 lines of Python with no dependencies:

```python
from pathlib import Path
import re, itertools

def chunked(it, chunk_sz):
    it = iter(it)
    return iter(lambda: list(itertools.islice(it, chunk_sz)), [])

def parse_llms_txt(txt):
    "Parse llms.txt file contents in `txt` to a `dict`"
    def _p(links):
        link_pat = r'-\s*\[(?P<title>[^\]]+)\]\((?P<url>[^\)]+)\)(?::\s*(?P<desc>.*))?'
        return [re.search(link_pat, l).groupdict()
                for l in re.split(r'\n+', links.strip()) if l.strip()]

    start, *rest = re.split(r'^##\s*(.*?$)', txt, flags=re.MULTILINE)
    sects = {k: _p(v) for k, v in dict(chunked(rest, 2)).items()}
    pat = r'^#\s*(?P<title>.+?$)\n+(?:^>\s*(?P<summary>.+?$)$)?\n+(?P<info>.*)'
    d = re.search(pat, start.strip(), (re.MULTILINE | re.DOTALL)).groupdict()
    d['sections'] = sects
    return d
```

A test suite is available at `tests/test-parse.py` in the repository.
