---
title: "llms.txt Integrations and Ecosystem"
status: draft
author: "Khalid Zubair"
date: 2026-06-14
tags:
  - llms-txt
  - integrations
  - plugins
  - ecosystem
sources:
  - url: "https://llmstxt.org"
    title: "The /llms.txt file"
  - url: "https://llmstxt.org/intro.html"
    title: "Python module & CLI — llms-txt"
  - url: "https://github.com/AnswerDotAI/llms-txt"
    title: "AnswerDotAI/llms-txt — GitHub Repository"
last_audit_date: 2026-06-14
---

# Integrations and Ecosystem

The llms.txt specification has growing community adoption across programming languages, static site generators, content management systems, and editor tooling.

## Content Management Systems

| Integration | Type | Description |
|---|---|---|
| [Drupal LLM Support](https://www.drupal.org/project/llm_support) | Drupal Recipe | Provides full llms.txt support on any Drupal 10.3+ site |

## Static Site Generators

| Integration | Type | Description |
|---|---|---|
| [`vitepress-plugin-llms`](https://github.com/okineadev/vitepress-plugin-llms) | VitePress Plugin | Automatically generates llms.txt for VitePress documentation sites |
| [`docusaurus-plugin-llms`](https://github.com/rachfop/docusaurus-plugin-llms) | Docusaurus Plugin | Generates llms.txt following the llmstxt.org standard for Docusaurus sites |

## Programming Languages

| Integration | Language | Description |
|---|---|---|
| [`llms_txt2ctx`](https://llmstxt.org/intro.html#cli) | Python | Official CLI and Python module for parsing and context generation. Install via `pip install llms-txt` |
| [`llmstxt-js`](https://llmstxt.org/llmstxt-js.html) | JavaScript | Reference JavaScript implementation for parsing and generating llms.txt files |
| [`llms-txt-php`](https://github.com/raphaelstolt/llms-txt-php) | PHP | Library for writing and reading llms.txt Markdown files |

## Editors and IDEs

| Integration | Type | Description |
|---|---|---|
| [PagePilot](https://dmux.github.io/pagepilot) | VS Code Extension | Chat participant that automatically loads external context (docs, APIs, READMEs) from llms.txt files to provide enhanced responses |
| `ed` (standard text editor) | Editor | The llms.txt site includes an `ed` tutorial demonstrating that even the simplest editor can work with the format |

## Directories

Two community directories list known `llms.txt` files on the web:

- [llmstxt.site](https://llmstxt.site/) — community directory of sites with llms.txt files
- [directory.llmstxt.cloud](https://directory.llmstxt.cloud/) — alternative directory listing

## Core Library

The official [AnswerDotAI/llms-txt](https://github.com/AnswerDotAI/llms-txt) GitHub repository hosts the specification overview, the Python reference implementation, the JavaScript implementation, test suites, and tutorials covering llms.txt in different domains.

## nbdev Integration

All [nbdev](https://nbdev.fast.ai/) projects now generate `.md` versions of all pages by default. Answer.AI and fast.ai software projects using nbdev have had their documentation regenerated with this feature. This makes nbdev-based documentation automatically compatible with the llms.txt companion Markdown pages convention.
