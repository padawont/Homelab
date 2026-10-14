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

Readiness: TARGIT hydrates its client-side data model long after the initial DOM
appears, and an export clicked before that hydration completes downloads a
0-byte workbook. The scraper therefore waits for the grid to actually render its
data (header row + row-total KPI) before the first click, and keeps a bounded
retry backstop for the remaining -- unobservable -- hydration, since a slow
TARGIT hydration can still take longer than any single readiness signal.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

logger = logging.getLogger(__name__)

# Stable selectors -- never hardcode session-scoped TARGIT GUIDs.
_EXCEL_EXPORT_SELECTOR = '.ActionButton[actionid="excel"]'
_CROSSTAB_SELECTOR = "div.lsCrosstab"

#: JS that un-hides the TARGIT toolbar. The toolbar (``.Toolbar``) is
#: ``display: none`` by default, so the Excel action never becomes "visible" to
#: Playwright and a visibility-gated wait/click would time out forever.
#: ``.ActionButtons`` and its ``.ActionButton`` children are already
#: ``inline-block`` and auto-size once their parent is shown, so only
#: ``.Toolbar`` needs un-hiding. The check keeps the snippet idempotent so it can
#: be re-run safely on every attempt (a Blazor re-render can re-hide the bar).
_REVEAL_EXPORT_JS = """\
(() => {
    const toolbar = document.querySelector('.Toolbar');
    if (toolbar && getComputedStyle(toolbar).display === 'none') {
        toolbar.style.display = 'block';
    }
})()
"""

#: JS readiness probe: the cross-tab renders a placeholder ("Du kan også finde
#: ...") until its data models land; the header row ("Hovedkategori ...") and the
#: row-total KPI (e.g. "37,319") appear once the grid is populated.
_READY_JS = """() => {
    const crosstab = document.querySelector('div.lsCrosstab');
    const headerReady = !!crosstab && /Hovedkategori/.test(crosstab.innerText || '');
    let total = 0;
    for (const node of document.querySelectorAll('.lsKpiChart svg text')) {
        const digits = (node.textContent || '').replace(/[^0-9]/g, '');
        if (digits) total = Math.max(total, parseInt(digits, 10));
    }
    return { headerReady, total };
}"""

_NAV_TIMEOUT_MS = 60_000
_CROSSTAB_TIMEOUT_MS = 60_000
_ACTION_TIMEOUT_MS = 30_000
_DOWNLOAD_TIMEOUT_MS = 180_000
_READY_TIMEOUT_MS = 60_000
_READY_POLL_MS = 1_000
#: The view's displayed total must be at least this many rows before the first
#: export click; it rules out the placeholder phase but not the full hydration.
_MIN_ROW_TOTAL = 1_000
_SETTLE_TIMEOUT_MS = 1_000
#: Retry backstop: TARGIT hydration can outlive every readiness signal, so the
#: export is retried until a non-empty workbook is saved (or the budget runs out).
_EXPORT_MAX_ATTEMPTS = 6
_EXPORT_RETRY_DELAY_MS = 10_000


def export_companies(config: dict, out_dir: str) -> str:
    """Download the full company list as ``.xlsx``.

    Navigates to ``config['source']['url']``, waits for the cross-tab grid to
    render its data, reveals the toolbar and triggers the Excel export (retrying
    until the download is non-empty), then saves the workbook under ``out_dir``.
    The export is unfiltered: Branche selection happens in Python after the
    workbook is read.

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
            _wait_until_ready(page)
            download_path = _export_to_excel(page, target_dir)
        finally:
            browser.close()

    logger.info("Saved company list export to %s", download_path)
    return download_path


def _wait_until_ready(page: Page) -> None:
    """Wait until the view has rendered its data, rather than a fixed sleep.

    The cross-tab renders a placeholder until its data models land; the header
    row and the row-total KPI appear once the grid is populated. Both are polled
    so the first export click never lands during the placeholder phase. The
    remaining TARGIT hydration is client-side and not observable in the DOM or
    the network, so this wait is a floor, not a guarantee -- the retry backstop
    in :func:`_export_to_excel` covers the rest.
    """

    deadline = time.monotonic() + _READY_TIMEOUT_MS / 1000
    while time.monotonic() < deadline:
        state = page.evaluate(_READY_JS)
        if state["headerReady"] and state["total"] >= _MIN_ROW_TOTAL:
            logger.info(
                "view ready: cross-tab rendered, %d rows total", state["total"]
            )
            return
        page.wait_for_timeout(_READY_POLL_MS)

    logger.warning(
        "view readiness wait timed out after %.0fs; proceeding (retry backstop applies)",
        _READY_TIMEOUT_MS / 1000,
    )


def _export_to_excel(page: Page, target_dir: Path) -> str:
    """Trigger the Excel export and persist the download in ``target_dir``.

    The toolbar is ``display: none`` by default, so a visibility-gated wait never
    resolves; it is re-revealed at the top of every attempt because a Blazor
    re-render can re-hide it. TARGIT generates the workbook from its in-memory
    document state and returns a 0-byte file when clicked before the model has
    hydrated, so every attempt is checked and retried until a non-empty workbook
    is saved (or the budget is exhausted). A download that never fires (a
    Playwright timeout) is folded into the same retry budget, and any
    empty/partial workbook is removed so a later ``read_rows`` never sees a
    0-byte file.
    """

    action = page.locator(_EXCEL_EXPORT_SELECTOR).first
    for attempt in range(1, _EXPORT_MAX_ATTEMPTS + 1):
        _reveal_export_button(page)
        target: Path | None = None
        try:
            with page.expect_download(timeout=_DOWNLOAD_TIMEOUT_MS) as download_info:
                action.click()
            download = download_info.value
            target = target_dir / _xlsx_filename(download.suggested_filename)
            # ``_xlsx_filename`` strips directory components, but re-assert
            # containment as a defense-in-depth boundary (FIX-4).
            if not _is_within(target.resolve(), target_dir.resolve()):
                raise ValueError(
                    f"refusing to save download outside {target_dir}: {target.name}"
                )
            _discard_partial(target)  # remove any stale file from a prior attempt
            download.save_as(str(target))
            if target.stat().st_size > 0:
                logger.info(
                    "Excel export succeeded on attempt %d/%d (%d bytes)",
                    attempt,
                    _EXPORT_MAX_ATTEMPTS,
                    target.stat().st_size,
                )
                return str(target)
        except PlaywrightTimeoutError:
            logger.warning(
                "Excel export attempt %d/%d: no download arrived within timeout",
                attempt,
                _EXPORT_MAX_ATTEMPTS,
            )
        except OSError as exc:
            logger.warning(
                "Excel export attempt %d/%d could not be saved: %s",
                attempt,
                _EXPORT_MAX_ATTEMPTS,
                exc,
            )
        else:
            logger.warning(
                "Excel export attempt %d/%d was empty; waiting %.0fs before retrying",
                attempt,
                _EXPORT_MAX_ATTEMPTS,
                _EXPORT_RETRY_DELAY_MS / 1000,
            )
        _discard_partial(target)
        if attempt < _EXPORT_MAX_ATTEMPTS:
            page.wait_for_timeout(_EXPORT_RETRY_DELAY_MS)

    raise RuntimeError(
        f"Excel export was empty or never completed after "
        f"{_EXPORT_MAX_ATTEMPTS} attempts"
    )


def _reveal_export_button(page: Page) -> None:
    """Un-hide the toolbar so the export buttons are clickable (idempotent)."""

    page.evaluate(_REVEAL_EXPORT_JS)
    page.wait_for_timeout(_SETTLE_TIMEOUT_MS)


def _xlsx_filename(suggested: str | None) -> str:
    """Return a safe ``.xlsx`` filename for a downloaded export.

    ``download.suggested_filename`` comes from the server's
    ``Content-Disposition`` header and is untrusted: it may carry directory
    components (``..``) or an absolute path that could escape ``target_dir``.
    Everything but the final path component is stripped, and the ``.xlsx``
    suffix is enforced.
    """

    candidate = Path(suggested or "").name.strip() or "erhvervspraktik.xlsx"
    if not candidate.lower().endswith(".xlsx"):
        candidate += ".xlsx"
    return candidate


def _discard_partial(target: Path | None) -> None:
    """Remove an empty/partial workbook so a later ``read_rows`` never sees it.

    A 0-byte ``.xlsx`` would raise ``BadZipFile`` downstream, so failed export
    attempts must not leave one behind. Best-effort: removal failures are logged
    rather than masking the original error.
    """

    if target is None:
        return
    try:
        if target.exists():
            target.unlink()
            logger.debug("removed partial export %s", target)
    except OSError:
        logger.warning("could not remove partial export %s", target, exc_info=True)


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
