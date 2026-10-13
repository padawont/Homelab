"""Extract the Aarhus Kommune erhvervspraktik company list via TARGIT Excel export.

The TARGIT Anywhere view renders its grid client-side and caps the rendered DOM
grid at roughly 18 rows, so the full filtered set is obtained through the
*Export to Excel* action rather than by DOM scraping. Element handles are
resolved by stable placeholder text and class/attribute selectors, never by
session-scoped TARGIT GUIDs (``slicer-<GUID>`` / ``crosstab-<GUID>``), which
change between sessions.
"""

from __future__ import annotations

import logging
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

logger = logging.getLogger(__name__)

# Stable selectors -- never hardcode session-scoped TARGIT GUIDs.
_BRANCHE_SEARCH_SELECTOR = 'input[placeholder="Search Branche"]'
_SELECT_ALL_SELECTOR = ".slicerSelectAll"
_EXCEL_EXPORT_SELECTOR = '.ActionButton[actionid="excel"]'
_CROSSTAB_SELECTOR = "div.lsCrosstab"

_NAV_TIMEOUT_MS = 60_000
_CROSSTAB_TIMEOUT_MS = 60_000
_ACTION_TIMEOUT_MS = 30_000
_DOWNLOAD_TIMEOUT_MS = 180_000
_SETTLE_TIMEOUT_MS = 1_000


def export_companies(config: dict, out_dir: str) -> str:
    """Download the full filtered company list as ``.xlsx``.

    Navigates to ``config['source']['url']``, waits for the cross-tab grid,
    applies the Branche filter, selects every matching slicer value, triggers the
    Excel export and saves the download under ``out_dir``.

    Parameters
    ----------
    config:
        Validated cv sender configuration.
    out_dir:
        Destination directory for the export. Must live inside
        ``config['paths']['data_dir']`` when that key is set.

    Returns
    -------
    str
        Path to the downloaded ``.xlsx`` file.

    Raises
    ------
    ValueError
        If ``out_dir`` would write scraped data outside the configured data dir.
    """

    source_url = config["source"]["url"]
    branche_query = config.get("filters", {}).get("branche_query", "")
    target_dir = _resolve_out_dir(config, out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Exporting company list from %s", source_url)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            page.set_default_timeout(_ACTION_TIMEOUT_MS)
            page.set_default_navigation_timeout(_NAV_TIMEOUT_MS)

            page.goto(source_url, wait_until="domcontentloaded")
            page.wait_for_selector(
                _CROSSTAB_SELECTOR, state="visible", timeout=_CROSSTAB_TIMEOUT_MS
            )
            _apply_branche_filter(page, branche_query)
            download_path = _export_to_excel(page, target_dir)
        finally:
            browser.close()

    logger.info("Saved company list export to %s", download_path)
    return download_path


def _apply_branche_filter(page: Page, branche_query: str) -> None:
    """Type ``branche_query`` into the Branche slicer and select every match."""

    search = page.locator(_BRANCHE_SEARCH_SELECTOR).first
    search.wait_for(state="visible", timeout=_CROSSTAB_TIMEOUT_MS)
    search.click()
    search.fill(branche_query or "")
    page.wait_for_timeout(_SETTLE_TIMEOUT_MS)

    select_all = page.locator(_SELECT_ALL_SELECTOR).first
    select_all.wait_for(state="visible", timeout=_ACTION_TIMEOUT_MS)
    select_all.click()
    page.wait_for_timeout(_SETTLE_TIMEOUT_MS)


def _export_to_excel(page: Page, target_dir: Path) -> str:
    """Trigger the Excel export and persist the download in ``target_dir``."""

    action = page.locator(_EXCEL_EXPORT_SELECTOR).first
    action.wait_for(state="visible", timeout=_ACTION_TIMEOUT_MS)
    with page.expect_download(timeout=_DOWNLOAD_TIMEOUT_MS) as download_info:
        action.click()

    download = download_info.value
    target = target_dir / _xlsx_filename(download.suggested_filename)
    download.save_as(str(target))
    return str(target)


def _xlsx_filename(suggested: str | None) -> str:
    """Return a safe ``.xlsx`` filename for a downloaded export."""

    candidate = (suggested or "").strip() or "erhvervspraktik.xlsx"
    if not candidate.lower().endswith(".xlsx"):
        candidate += ".xlsx"
    return candidate


def _resolve_out_dir(config: dict, out_dir: str) -> Path:
    """Resolve ``out_dir`` and enforce the configured data-dir boundary."""

    target = Path(out_dir).expanduser().resolve()
    data_dir = _data_dir(config)
    if data_dir is not None and not _is_within(target, data_dir):
        raise ValueError(
            f"refusing to write scraped data to {target}: outside data_dir {data_dir}"
        )
    return target


def _data_dir(config: dict) -> Path | None:
    """Return the configured data directory, or ``None`` when unset."""

    value = config.get("paths", {}).get("data_dir")
    if not value:
        return None
    return Path(str(value)).expanduser().resolve()


def _is_within(path: Path, parent: Path) -> bool:
    """Return ``True`` when ``path`` is ``parent`` or lives beneath it."""

    return path == parent or parent in path.parents
