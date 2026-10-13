---
title: "Playwright — locators and auto-waiting"
status: draft
author: "padawont"
date: 2026-10-12
tags: [playwright, locators, auto-waiting, selectors, python]
sources:
  - url: "https://playwright.dev/python/docs/locators"
    title: "Playwright — Locators"
  - url: "https://playwright.dev/python/docs/actionability"
    title: "Playwright — Auto-waiting"
  - url: "https://playwright.dev/python/docs/api/class-locator"
    title: "Playwright — Locator API reference"
last_audit_date: 2026-10-12
related_docs:
  - "./02_Knowledge/technologies/tools/playwright/overview.md"
  - "./02_Knowledge/technologies/tools/playwright/downloads-exports.md"
---

# Playwright — locators and auto-waiting

## Overview

A **locator** describes *how to find* element(s) on a page — it is not a resolved element handle. Locators are lazy: they resolve at action time, which is exactly what makes auto-waiting and auto-retrying assertions possible. Getting locators right (or wrong) is the main determinant of whether an automation script is stable or flaky.

## Details

### Built-in `get_by_*` locators

Playwright ships locators that map to how a user perceives the page:

| Locator | Matches |
|---|---|
| `page.get_by_role("button", name="Save")` | ARIA role + accessible name |
| `page.get_by_text("Sign in")` | visible text |
| `page.get_by_label("Username")` | form control by its `<label>` |
| `page.get_by_placeholder(...)` | placeholder attribute |
| `page.get_by_alt_text(...)` | image alt text |
| `page.get_by_title(...)` | title attribute |
| `page.get_by_test_id(...)` | `data-testid` |

Prefer these over raw CSS/XPath: they read like intent, survive markup refactors better, and produce clearer errors. They also fail loudly when an element is missing from the accessibility tree — often the same element a client-rendered app has not hydrated yet.

### Chaining and filtering

Locators narrow by chaining (search *within* the parent) and by filters:

- `page.get_by_role("row").filter(has_text="Total")` — rows containing text
- `locator.get_by_role("cell").nth(2)` — positional within a parent
- `filter(has=..., has_not=...)`, `locator.and_(...)`, `locator.or_(...)` — boolean composition

Chaining scopes the search, so `table.get_by_role("row")` returns only rows inside that table.

Example — abstract:

```python
# resolve a cell in a client-rendered table without depending on row order
table = page.get_by_role("table", name="Results")
total_row = table.get_by_role("row").filter(has_text="Total")
value = total_row.get_by_role("cell").nth(1)   # lazy: resolves on use
assert value.inner_text() == "1,234"
```

### Strict mode

Most locators must resolve to exactly one element. If several match, the action throws a strict-mode violation instead of silently taking the first. This is deliberate — it surfaces ambiguous selectors early. Disambiguate with `.filter()`, `.nth()`, `.first`, `.last`, or inspect `locator.count()`.

### Auto-waiting (actionability checks)

Playwright runs actionability checks before each action and retries within a timeout, so `locator.click()` auto-waits. Checks include:

- **Visible** — non-empty bounding box, not `visibility:hidden`
- **Stable** — not animating (same bounding box for two frames)
- **Receives events** — not obscured by another element
- **Enabled** — not disabled
- **Editable** — for `fill()`: enabled and not readonly

Auto-retrying assertions such as `expect(locator).to_have_text(...)` poll until they pass or time out. "Wait for the table to render" is therefore expressed as an assertion, not a sleep.

### When explicit waiting is still needed

Auto-waiting covers the action and the assertion. Explicit `wait_for_*` is only needed for:

- states not tied to an action, e.g. `locator.wait_for(state="hidden")` for a spinner
- the network call that populates a client-rendered table: `page.expect_response(...)`
- navigation or a popup that must happen before anything can be located

Never use `time.sleep()` or fixed timeouts: they are either too short (flaky) or too long (slow), and add nothing over the built-in retry.

### Homelab framing

The common homelab case is a BI dashboard (Grafana, Metabase, Superset, or a vendor portal) that renders its table client-side after an XHR. Two patterns:

- Locate the table by role/name and the target cell by row filter — not by CSS classes that embed build hashes.
- Never hardcode a session/dashboard GUID in the selector. Navigate normally, then wait on the response carrying the data (`expect_response`) instead of pre-building a URL — GUIDs expire and change per session.

Because locators describe the accessibility tree and text rather than DOM internals, this guidance is version-agnostic across Playwright Python releases.

## Sources / Further Reading

- [Playwright — Locators](https://playwright.dev/python/docs/locators)
- [Playwright — Auto-waiting](https://playwright.dev/python/docs/actionability)
- [Playwright — Locator API reference](https://playwright.dev/python/docs/api/class-locator)
