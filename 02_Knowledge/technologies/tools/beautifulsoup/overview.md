---
title: "BeautifulSoup — parsing HTML"
status: draft
author: "padawont"
date: 2026-10-12
tags: [beautifulsoup, html-parsing, python, scraping, bs4]
sources:
  - url: "https://www.crummy.com/software/BeautifulSoup/bs4/doc/"
    title: "Beautiful Soup Documentation"
  - url: "https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all"
    title: "Beautiful Soup — Searching the tree (find_all)"
  - url: "https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors-through-the-css-property"
    title: "Beautiful Soup — CSS selectors via select()"
  - url: "https://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class"
    title: "Beautiful Soup — Searching by CSS class"
last_audit_date: 2026-10-12
related_docs:
  - "./05_Implementations/node-main/cv-sender/overview.md"
  - "./02_Knowledge/technologies/tools/playwright/overview.md"
---

# BeautifulSoup — parsing HTML

## Overview

BeautifulSoup (the `bs4` package, imported as `from bs4 import BeautifulSoup`) is a Python library for **parsing** and navigating HTML/XML documents. It turns a markup string into a traversable tree of Python objects, so you can pull text and attributes out by tag name, attribute, or CSS selector.

Its scope is deliberately narrow: it parses a string you already have — it **does not fetch** URLs (that's `requests`, `httpx`, or a browser) and it **does not render** or execute JavaScript. That makes it the natural *second* half of a scraping pipeline in a homelab: a headless browser (Playwright) fetches and renders the page, then BeautifulSoup parses the resulting DOM HTML.

## Details

### Step 1 — Parse

Pass the markup string and a parser name to the constructor. `"html.parser"` is the built-in, dependency-free parser and is the safe default when you don't want to install extra C libraries.

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
```

The result is a `BeautifulSoup` object that behaves like the root of a tree. From here every search and navigation method is available.

### Tree navigation

Tags are reached as attributes of their parent and are iterable. `.text` (or `.get_text()`) returns the human-readable text with tags stripped.

```python
soup.title          # <title>...</title>
soup.body.div       # first <div> inside <body>
soup.find_all("a")  # all <a> tags, in document order
```

### `find` / `find_all`

`find` returns the first match, `find_all` returns a list of all matches. Both accept a tag name, a dict of attributes, or keyword arguments. Because `class` is a Python keyword, BeautifulSoup uses the special keyword `class_` (or the attrs dict) for CSS classes.

| Call | Returns |
|---|---|
| `soup.find("div")` | first `<div>` |
| `soup.find_all("a")` | every `<a>` |
| `soup.find("div", class_="card")` | first `<div class="card">` |
| `soup.find_all("a", attrs={"data-role": "next"})` | `<a>` matching the attribute |
| `soup.find_all(["h1", "h2"])` | any `h1` or `h2` |

Example — abstract:

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")

# every link with a non-empty href
links = [a["href"] for a in soup.find_all("a", href=True)]

# first element carrying a CSS class
card = soup.find("div", class_="card")
if card is not None:
    print(card.get_text(strip=True))
```

### CSS selectors with `select()`

`.select()` and `.select_one()` accept CSS selector strings, which is convenient when you already think in selector syntax. Results are always in document order.

```python
soup.select("div.card")            # class selector
soup.select("#main a[href]")       # id + descendant + attribute
soup.select_one("ul.nav > li")     # direct child
```

Rule of thumb: use `find`/`find_all` for simple, readable lookups and `select()` when the selector is naturally expressed in CSS (ids, descendant/child combinators, attribute prefixes).

### Homelab framing

Typical use is DOM extracted from a headless browser rather than a raw HTTP response, because SPAs and JS-rendered pages otherwise yield an empty shell. The split of responsibilities is:

1. **Playwright** launches Chromium, waits for the page (or a selector) to be ready, and returns `page.content()`.
2. **BeautifulSoup** parses that HTML and extracts the fields you need.

See `./05_Implementations/node-main/cv-sender/overview.md` for the pipeline this supports, and `./02_Knowledge/technologies/tools/playwright/overview.md` for the fetch/render side.

This note is version-agnostic and does not pin a `bs4` release; the API described here has been stable across recent major versions.

## Sources / Further Reading

- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) — overview and quick start
- [`find_all`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all) — searching the tree
- [Searching by CSS class](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class) — the `class_` argument
- [CSS selectors through the `.css` property](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors-through-the-css-property) — `select()` / `select_one()`
