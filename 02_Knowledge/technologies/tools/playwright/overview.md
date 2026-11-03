---
title: "Playwright — headless browser automation"
status: draft
author: "padawont"
date: 2026-10-12
tags: [playwright, browser-automation, headless, python, docker]
sources:
  - url: "https://playwright.dev/python/docs/intro"
    title: "Playwright for Python — Installation"
  - url: "https://playwright.dev/python/docs/test-runners"
    title: "Playwright Pytest Plugin Reference"
  - url: "https://playwright.dev/python/docs/docker"
    title: "Playwright — Docker"
last_audit_date: 2026-10-22
related_docs:
  - "./05_Implementations/node-main/cv-sender/overview.md"
  - "./02_Knowledge/technologies/tools/playwright/selectors-and-waiting.md"
  - "./02_Knowledge/technologies/tools/playwright/downloads-exports.md"
---

# Playwright — headless browser automation

## Overview

Playwright is a browser automation library that drives real browsers (Chromium,
Firefox, WebKit) programmatically. It can run them **headless** — no display, no
window — which makes it usable on a headless homelab node or inside a container.

It matters here because a lot of modern pages are **client-rendered**: the HTML that
a plain HTTP fetch (`curl`, `wget`, static scrapers) receives is an empty shell, and
the content only exists after JavaScript runs. Playwright launches the browser, runs
that JavaScript, and then lets the script read the resulting DOM, fill forms, click,
screenshot, or export files.

## Details

### When to reach for it

| Situation | Static fetch enough? | Playwright needed? |
|---|---|---|
| Plain server-rendered HTML / APIs | yes | no |
| SPA / JS-rendered content | no | yes |
| Login flows, form filling behind JS | no | yes |
| Screenshots / PDF of a page | no | yes |

### Install (Python)

- `pip install pytest-playwright` installs the library plus the pytest integration
  ([Installation](https://playwright.dev/python/docs/intro)).
- `playwright install` downloads the browser binaries; check the documented OS and
  Python system requirements before deploying to a node.

### Pytest plugin

The pytest plugin wraps the library with fixtures and markers so tests (or jobs) are
declared per-function and browser setup/teardown is handled automatically
([Pytest Plugin Reference](https://playwright.dev/python/docs/test-runners)). This is
the usual entry point when a scheduled task is really "a browser test that produces a
side effect".

### Example — abstract

```python
# simplified, vendor-neutral
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()            # headless by default
    page = browser.new_page()
    page.goto("https://example.com")
    page.get_by_role("searchbox", name="Search").fill("homelab")
    page.get_by_role("button", name="Search").click()
    results = page.get_by_role("list", name="Results")   # lazy, auto-waits
    print(results.inner_text())
    browser.close()
```

Locators (`get_by_*`) and auto-waiting — why no explicit `wait_for_selector` is
needed here — are covered in
`./02_Knowledge/technologies/tools/playwright/selectors-and-waiting.md`.

### Running in Docker

Docker is the cleanest way to run a headless browser on a homelab node: the image
ships the browser plus every system library it needs, so the host stays untouched.
Playwright publishes official images with language-specific tags — for Python, the
`mcr.microsoft.com/playwright/python` repository
([Docker](https://playwright.dev/python/docs/docker)).

The image ships the browsers and their system dependencies, but **not** the Playwright
Python package itself — it must be installed separately. Running a script directly on
the base image fails with `ModuleNotFoundError`. Either install the package in a derived
image, or install it at run time:

#### Example — abstract: derived image

```dockerfile
# derived image — package version must match the image tag
FROM mcr.microsoft.com/playwright/python:<tag>
RUN pip install playwright==<version matching the tag>
```

#### Example — abstract: docker run

```bash
# docker run — base image plus a run-time install (scraping/crawling case)
docker run --rm --init --ipc=host \
  --user pwuser --security-opt seccomp=seccomp_profile.json \
  -v "$PWD":/work -w /work \
  mcr.microsoft.com/playwright/python:<tag> \
  sh -c "pip install playwright==<version matching the tag> && python scrape.py"
```

Keep the installed package version aligned with the image tag: per the Docker page, a
mismatch leaves Playwright unable to locate the browser executables.

Be aware that the image runs as **root by default**, which disables the Chromium sandbox,
so the example drops to the shipped `pwuser` and applies Playwright's seccomp profile. The
published image ships that user, but `seccomp_profile.json` is **not** in a homelab
checkout — take it from
[microsoft/playwright — seccomp_profile.json](https://github.com/microsoft/playwright/blob/main/utils/docker/seccomp_profile.json).
The Docker page also warns the image is intended for testing and development only and is
**not recommended for visiting untrusted websites**
([Docker](https://playwright.dev/python/docs/docker)).

The two flags are recommended for a well-behaved browser container:

- `--init` — runs a tiny init process as PID 1 so orphaned browser child processes are
  reaped and signals (Ctrl-C, stop) are forwarded correctly.
- `--ipc=host` — shares the host IPC namespace. Chromium relies on shared memory; the
  container default `/dev/shm` is small, and without shared IPC the browser can crash.

Both flags, and the published image tags, are documented in the Docker page above.

## Sources / Further Reading

- [Playwright for Python — Installation](https://playwright.dev/python/docs/intro)
- [Playwright Pytest Plugin Reference](https://playwright.dev/python/docs/test-runners)
- [Playwright — Docker](https://playwright.dev/python/docs/docker)
