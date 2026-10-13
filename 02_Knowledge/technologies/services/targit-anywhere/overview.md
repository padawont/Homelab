---
title: "TARGIT Anywhere — client-rendered BI views"
status: draft
author: "padawont"
date: 2026-10-12
tags: [targit, business-intelligence, bi, blazor, scraping]
sources:
  - url: "https://community.targit.com/hc/en-us/articles/360017096337-TARGIT-Anywhere-overview"
    title: "TARGIT Anywhere — overview"
  - url: "https://ledelsesinformation.aarhuskommune.dk/Embed#vfs://global/AARHUS-I-TAL/UDDANNELSE_I_TAL-Erhvervspraktik-Virksomhedsliste.xview"
    title: "Aarhus Kommune — Erhvervspraktik virksomhedsliste (live view)"
last_audit_date: 2026-10-12
related_docs:
  - "./05_Implementations/node-main/cv-sender/overview.md"
  - "./02_Knowledge/technologies/tools/playwright/overview.md"
---

# TARGIT Anywhere — client-rendered BI views

## Overview

TARGIT Anywhere is the zero-footprint web client of the TARGIT BI platform. The
official overview describes it as a browser-based "Consumer" client: users open
dashboards and reports, apply filters, and export the result to Excel or PDF —
with nothing to install on the client machine. The documented client presents a
login screen, so access is normally authenticated.

This note documents the platform plus the DOM specifics of one live anonymous
view, so that a scraper can be reasoned about. **Important distinction:** the
platform capabilities below are publicly documented; everything in the
"observed at discovery" section is *not* — it was read off a running view and
may differ between TARGIT versions and customer configurations.

## Details

### The Consumer client (documented)

- Browser-based, zero-footprint — no local installation.
- View dashboards, reports, and crosstabs.
- Apply filters (including search slicers) to narrow the data set.
- Export the current view to **Excel** or **PDF**.

### What an unauthenticated client receives (observed at discovery)

- The Aarhus view was reachable **anonymously** (no login prompt) at discovery.
  Anonymity here is a property of that particular published view, **not**
  documented TARGIT platform behaviour.
- The HTTP response for the source URL is a **Blazor WebAssembly SPA shell** —
  a static bootstrap document. It returns HTTP 200 but contains no table data.
- The actual report markup is **rendered client-side after the WASM app boots**,
  so a plain HTTP fetch or `curl` yields nothing useful.
- A **real browser** (e.g. Playwright) is therefore required: navigate, wait for
  the crosstab to mount, then read or export.
- The private JSON/JWT data endpoints the app calls behind the scenes are
  deliberately **not reverse-engineered** here — see "Scope limits".

### Crosstab DOM (observed at discovery, client-rendered)

The rendered result table is a crosstab built from nested `div`/`span` elements
with library-specific CSS class names. The chain, observed at discovery:

```text
# Example — abstract
div.lsCrosstab                          # the crosstab container
  └─ div.CrosstabCell[cellx][celly]      # one data cell, addressed by coordinates
       └─ span.lsText                    # the visible cell text
```

- `div.CrosstabCell` carries `cellx` / `celly` attributes giving the cell's grid
  position — the stable handle for reading a value.
- Cell text is in the inner `span.lsText`.

### Slicers and row limits (observed at discovery)

- **Search slicer**: `input[placeholder="Search Branche"]` is the search box for
  the "Branche" (industry) filter; a sibling `.slicerSelectAll` control toggles
  "select all". Typing into the input filters the slicer's options.
- **Row limit**: the container gains the class `hasRowLimit` — `div.lsCrosstab.hasRowLimit`
  — and rendered only about **18 rows** in the observed view. The on-screen
  crosstab is therefore a truncated preview, not the full data set.

### Excel export (observed at discovery)

- The export control is `.ActionButton[actionid="excel"]`.
- Clicking it downloads an Excel file containing the **full filtered set**, not
  just the ~18 rows rendered in the DOM. This is the reliable way to obtain
  complete data from a limited-row view.
- Practical order: apply the slicer filter you want, then hit the export button.

### Scope limits

- TARGIT Anywhere is **version-agnostic** in this note — no version is pinned.
  Selectors above were observed on one live view and may change.
- The private JSON/JWT endpoints are intentionally out of scope: this note
  covers only what the public, anonymous client exposes.

### Homelab relevance

Relevant to the `cv-sender` tooling
(`./05_Implementations/node-main/cv-sender/overview.md`): an anonymous TARGIT
view can be driven with Playwright
(`./02_Knowledge/technologies/tools/playwright/overview.md`) to pull a list —
read the DOM for a quick preview, or click the Excel export for the full set.

## Sources / Further Reading

- TARGIT Anywhere overview: https://community.targit.com/hc/en-us/articles/360017096337-TARGIT-Anywhere-overview
- Aarhus Kommune live view (anonymous): https://ledelsesinformation.aarhuskommune.dk/Embed#vfs://global/AARHUS-I-TAL/UDDANNELSE_I_TAL-Erhvervspraktik-Virksomhedsliste.xview
- Playwright reference: `./02_Knowledge/technologies/tools/playwright/overview.md`
