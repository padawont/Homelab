---
title: "Playwright — capturing downloads and exports"
status: draft
author: "padawont"
date: 2026-10-12
tags: [playwright, downloads, exports, file-handling, python]
sources:
  - url: "https://playwright.dev/python/docs/downloads"
    title: "Playwright — Downloads"
  - url: "https://playwright.dev/python/docs/api/class-download"
    title: "Playwright — Download API reference"
  - url: "https://playwright.dev/python/docs/input"
    title: "Playwright — Actions"
last_audit_date: 2026-10-12
related_docs:
  - "./02_Knowledge/technologies/tools/playwright/overview.md"
  - "./02_Knowledge/technologies/tools/playwright/selectors-and-waiting.md"
---

# Playwright — capturing downloads and exports

## Overview

How to capture a file that a page produces in response to a click — for example an
"Export to Excel" (or CSV/PDF) button — using Python Playwright. The key idea is
that a download is an *event*, and the click that triggers it must be wrapped in an
expectation so the browser context can hand you the resulting file.

When a click causes the browser to start a download, Playwright emits it on the
page as a `Download` object rather than navigating. Tooling must therefore:

1. Tell the context downloads are allowed (`accept_downloads`).
2. Arm an expectation *before* the triggering click.
3. Persist the download to disk with `save_as`.

This matters in a headless container where there is no visible download shelf: the
file only exists if the script saves it explicitly.

## Details

### The core pattern

Wrap the click in `expect_download`, then save the resulting download. The context
manager returns a `Download` object (`dl_info.value`) once the download starts.

```python
# Example — abstract
with page.expect_download() as dl_info:
    page.get_by_role("button", name="Export to Excel").click()

download = dl_info.value          # a Download object
download.save_as("/data/export.xlsx")
```

- The click **must** happen inside the `with` block; arming the expectation after
  the click can miss the event.
- `dl_info.value` is the `Download`; `save_as(path)` writes it to disk.
- In a headless container, pick an absolute path that is mounted/persisted
  (e.g. `/data/...`), otherwise the file lands in the ephemeral container FS.

### Naming the file

`suggested_filename` is typically computed by the browser from the
`Content-Disposition` header or the `download` attribute. Use it to preserve the
export's own naming, or to derive a save path.

```python
# Example — abstract
download = dl_info.value
print(download.suggested_filename)     # e.g. "report-2026-10-12.xlsx"
download.save_as(f"/data/{download.suggested_filename}")
```

`suggested_filename` is generally the most faithful name to keep, since the browser
derives it from the `Content-Disposition` header or the `download` attribute. Always
resolve the final path yourself — never trust a suggested name to be filesystem-safe.

### Context and browser configuration

For programmatic flows (headless, no user), allow downloads on the browser
context and, optionally, choose where downloads land when the browser is
launched. `downloads_path` is a `browser_type.launch()` option; `new_context()`
accepts `accept_downloads` only.

```python
# Example — abstract
browser = playwright.chromium.launch(
    headless=True,
    downloads_path="/data/downloads",   # where downloads are stored by default
)
context = browser.new_context(
    accept_downloads=True,
)
page = context.new_page()
```

- `accept_downloads` is a **context** option; `accept_downloads=False` makes
  downloads fail rather than silently disappear.
- `downloads_path` is a **launch** option of `browser_type.launch()` and sets a
  base directory for downloads. `save_as` is still preferred, since it gives you
  an explicit, deterministic target path.
- Set context options at creation time; they are not reliably changeable later.

### Waiting and cleanup

`expect_download` waits for the event and fails on timeout. The `Download` object
also exposes `path()` (server-side temp path) and `delete()`. After `save_as`,
call `download.delete()` if you want to reclaim the temp file in long-running jobs.

### Homelab use case

In a headless container, an "Export to Excel" button in an internal tool produces a
file that must be written to a mounted volume. The pattern above is exactly what an
automation script needs: arm the download, click, save to `/data`, and the file
appears on the host. Works the same for CSV, XLSX, PDF, or ZIP exports, and is
independent of the Playwright version in use.

## Sources / Further Reading

- Playwright — Downloads: https://playwright.dev/python/docs/downloads
- Playwright — Download API reference: https://playwright.dev/python/docs/api/class-download
- Playwright — Actions: https://playwright.dev/python/docs/input
