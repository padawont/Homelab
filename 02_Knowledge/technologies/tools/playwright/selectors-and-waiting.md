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
  - url: "https://playwright.dev/python/docs/network"
    title: "Playwright — Network"
last_audit_date: 2026-10-22
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
| `page.get_by_text("Sign in")` | text content |
| `page.get_by_label("Username")` | form control by its `<label>` |
| `page.get_by_placeholder(...)` | placeholder attribute |
| `page.get_by_alt_text(...)` | image alt text |
| `page.get_by_title(...)` | title attribute |
| `page.get_by_test_id(...)` | `data-testid` |

Prefer these over raw CSS/XPath: they read like intent, survive markup refactors better, and produce clearer errors. Any locator used in an action or assertion also fails loudly — it times out rather than silently matching nothing — when the element is absent or not yet rendered, which is exactly the case for a client-rendered element that has not hydrated. Note what each `get_by_*` locator matches: `get_by_role` matches by ARIA role, ARIA attributes, and accessible name; `get_by_label` matches by the text of the associated `<label>` or `aria-labelledby` element, or by the `aria-label` attribute; `get_by_alt_text` matches by alt text; `get_by_title` matches by the title attribute; and the remaining locators match by text content, placeholder, or `data-testid` (https://playwright.dev/python/docs/api/class-locator).

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
expect(value).to_have_text("1,234")   # retries until it passes or times out
```

Use `expect(locator).to_have_text(...)` here, not `value.inner_text() == "1,234"`: `inner_text()` is a single, non-retrying read and fails immediately if the client-rendered value has not populated yet, whereas the `expect` form polls (https://playwright.dev/python/docs/actionability).

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
- Never hardcode a session/dashboard GUID in the selector. Instead of pre-building a URL — GUIDs expire and change per session — arm the expectation *before* the navigation that triggers the response, so the event is never missed:

  Example — abstract:

  ```python
  with page.expect_response("**/api/fetch_data") as r:
      page.goto(url)   # armed before the trigger: the response cannot be missed
  ```

  Arming `expect_response` after the navigation/click can miss the response entirely (https://playwright.dev/python/docs/network).

Because role and label locators describe the accessibility tree and text locators describe text rather than DOM internals, this guidance holds across the supported API surface — with version floors: the `get_by_*` locators require Playwright Python >= 1.27 and `locator.and_()` requires >= 1.34 (https://playwright.dev/python/docs/api/class-locator).

## Sources / Further Reading

- [Playwright — Locators](https://playwright.dev/python/docs/locators)
- [Playwright — Auto-waiting](https://playwright.dev/python/docs/actionability)
- [Playwright — Locator API reference](https://playwright.dev/python/docs/api/class-locator)
- [Playwright — Network](https://playwright.dev/python/docs/network)
