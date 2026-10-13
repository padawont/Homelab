"""Extract the Aarhus Kommune erhvervspraktik company list via TARGIT Excel export.

The TARGIT Anywhere view renders its grid client-side and caps the rendered DOM
grid at roughly 18 rows, so the full set is obtained through the *Export to
Excel* action rather than by DOM scraping. The export is triggered through the
toolbar's Excel action button, which is ``display: none`` by default and must be
un-hidden first. The download is *not* filtered in the browser: the full company
list is exported and the Branche selection happens downstream in Python
(``normalize``). Element handles are resolved by stable class/attribute
selectors, never by session-scoped TARGIT GUIDs (``slicer-<GUID>`` /
``crosstab-<GUID>``), which change between sessions.
"""

from __future__ import annotations

import logging
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

logger = logging.getLogger(__name__)

# Stable selectors -- never hardcode session-scoped TARGIT GUIDs.
_EXCEL_EXPORT_SELECTOR = '.ActionButton[actionid="excel"]'
_CROSSTAB_SELECTOR = "div.lsCrosstab"

#: JS that un-hides the TARGIT toolbar and gives the export buttons a size.
#: The toolbar (``.Toolbar`` / ``.ActionButtons``) is ``display: none`` by
#: default, so the Excel action never becomes "visible" to Playwright and a
#: visibility-gated wait/click would time out forever. Un-hiding the containers
#: and sizing the buttons makes the real ``.ActionButton[actionid="excel"]``
#: clickable.
_REVEAL_EXPORT_JS = """\
(() => {
    const un = el => { if (el && getComputedStyle(el).display === 'none') el.style.display = 'block'; };
    un(document.querySelector('.Toolbar'));
    un(document.querySelector('.ActionButtons'));
    const ab = document.querySelector('.ActionButtons');
    if (ab) ab.querySelectorAll('.ActionButton').forEach(b => {
        b.style.display = 'inline-block'; b.style.width = '24px'; b.style.height = '24px';
    });
})()
"""

_NAV_TIMEOUT_MS = 60_000
_CROSSTAB_TIMEOUT_MS = 60_000
_ACTION_TIMEOUT_MS = 30_000
_DOWNLOAD_TIMEOUT_MS = 180_000
_SETTLE_TIMEOUT_MS = 1_000
#: The view takes a while to finish loading its data models; an export clicked
#: too early downloads a 0-byte workbook. Retry with a delay until it is real.
_EXPORT_MAX_ATTEMPTS = 6
_EXPORT_RETRY_DELAY_MS = 10_000


def export_companies(config: dict, out_dir: str) -> str:
    """Download the full company list as ``.xlsx``.

    Navigates to ``config['source']['url']``, waits for the cross-tab grid,
    reveals the toolbar and triggers the Excel export (retrying until the
    download is non-empty), then saves the workbook under ``out_dir``. The
    export is unfiltered: Branche selection happens in Python after the workbook
    is read.

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
            download_path = _export_to_excel(page, target_dir)
        finally:
            browser.close()

    logger.info("Saved company list export to %s", download_path)
    return download_path


def _export_to_excel(page: Page, target_dir: Path) -> str:
    """Trigger the Excel export and persist the download in ``target_dir``.

    The toolbar and its action buttons are ``display: none`` by default, so a
    visibility-gated wait never resolves; we un-hide and size them first, then
    click the real button inside ``expect_download``. TARGIT generates the
    workbook from its document state and can return a 0-byte file when clicked
    before every data model has loaded, so the click is retried (with a delay)
    until the saved workbook is non-empty.
    """

    _reveal_export_button(page)
    action = page.locator(_EXCEL_EXPORT_SELECTOR).first
    target = None
    for attempt in range(1, _EXPORT_MAX_ATTEMPTS + 1):
        with page.expect_download(timeout=_DOWNLOAD_TIMEOUT_MS) as download_info:
            action.click()
        download = download_info.value
        target = target_dir / _xlsx_filename(download.suggested_filename)
        download.save_as(str(target))
        if target.stat().st_size > 0:
            return str(target)
        logger.warning(
            "Excel export attempt %d/%d was empty; waiting %.0fs before retrying",
            attempt,
            _EXPORT_MAX_ATTEMPTS,
            _EXPORT_RETRY_DELAY_MS / 1000,
        )
        page.wait_for_timeout(_EXPORT_RETRY_DELAY_MS)

    raise RuntimeError(
        f"Excel export stayed empty after {_EXPORT_MAX_ATTEMPTS} attempts "
        f"({target.name if target else 'unknown'}); the view never became ready"
    )


def _reveal_export_button(page: Page) -> None:
    """Un-hide the toolbar and size the export buttons so they are clickable."""

    page.evaluate(_REVEAL_EXPORT_JS)
    page.wait_for_timeout(_SETTLE_TIMEOUT_MS)


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
