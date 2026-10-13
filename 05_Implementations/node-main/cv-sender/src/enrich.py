"""Best-effort email enrichment for cv sender rows.

Both enrichment sources sit behind bot challenges (``selskabsinfo.dk`` returns
HTTP 429 to plain HTTP clients), so enrichment uses a headless Playwright
browser. The function is a deliberate no-op when the row already carries an
email, and every lookup is memoised in the caller-supplied ``cache`` dict.
"""

from __future__ import annotations

import logging
import re
from urllib.parse import quote_plus

from playwright.sync_api import Page, sync_playwright

logger = logging.getLogger(__name__)

#: Default selskabsinfo.dk search URL; overridable via
#: ``config['enrichment']['selskabsinfo_search_url']``.
DEFAULT_SEARCH_URL = "https://selskabsinfo.dk/search?q={query}"

_DIRECTORY_DOMAINS = ("selskabsinfo.dk", "aarhus.dk", "aarhuskommune.dk")
_BLOCKED_LOCALS = frozenset(
    {"noreply", "no-reply", "donotreply", "postmaster", "webmaster", "privacy", "abuse"}
)

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_ADDRESS_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

_NAV_TIMEOUT_MS = 45_000
_RENDER_WAIT_MS = 1_500


def enrich(row: dict, config: dict, cache: dict) -> str | None:
    """Return an enrichment email for ``row`` or ``None`` when none is found.

    The function is a no-op (returns ``None``) when ``row`` already has an
    email. Results -- including negative ones -- are memoised in ``cache`` keyed
    by company name and postdistrikt, so repeated calls never re-query the
    network.

    Sources are tried in order: ``selskabsinfo.dk`` first, then
    ``config['enrichment']['aarhus_url']``.
    """

    if _clean(row.get("email")):
        logger.debug("Enrichment skipped for %s: email already present", row.get("name"))
        return None

    name = _clean(row.get("name"))
    if not name:
        return None

    key = _cache_key(row)
    if key in cache:
        return cache[key]

    email = _lookup(name, config)
    if email:
        logger.info("Enriched %s with %s", name, email)
    else:
        logger.info("No enrichment email found for %s", name)
    cache[key] = email
    return email


def _lookup(name: str, config: dict) -> str | None:
    """Try each enrichment source in order and return the first email found."""

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_context().new_page()
                for url in _search_urls(name, config):
                    email = _scrape_email(page, url)
                    if email:
                        return email
                return None
            finally:
                browser.close()
    except Exception:  # pragma: no cover - browser/driver failures are non-fatal
        logger.warning("Enrichment browser failed for %s", name, exc_info=True)
        return None


def _scrape_email(page: Page, url: str) -> str | None:
    """Load ``url`` in ``page`` and return the first contactable email."""

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=_NAV_TIMEOUT_MS)
        page.wait_for_timeout(_RENDER_WAIT_MS)
        content = page.content()
    except Exception:
        logger.warning("Failed to load enrichment page %s", url, exc_info=True)
        return None

    from_mailto = _first_mailto(page)
    if from_mailto:
        return from_mailto
    return _first_contactable(content)


def _first_mailto(page: Page) -> str | None:
    """Return the first contactable ``mailto:`` address on the page."""

    try:
        anchors = page.locator('a[href^="mailto:"]')
        count = anchors.count()
    except Exception:
        return None

    for index in range(count):
        href = anchors.nth(index).get_attribute("href") or ""
        if not href.lower().startswith("mailto:"):
            continue
        candidate = _clean(href[len("mailto:"):].split("?")[0])
        if candidate and _is_contactable(candidate):
            return candidate.lower()
    return None


def _first_contactable(content: str) -> str | None:
    """Return the first contactable email address found in raw page content."""

    for match in _EMAIL_RE.findall(content or ""):
        if _is_contactable(match):
            return match.lower()
    return None


def _is_contactable(email: str) -> bool:
    """Reject malformed addresses and directory/role mailboxes."""

    candidate = _clean(email).lower()
    if not _ADDRESS_RE.match(candidate):
        return False
    local, _, domain = candidate.partition("@")
    if not local or not domain:
        return False
    if any(
        domain == blocked or domain.endswith("." + blocked) for blocked in _DIRECTORY_DOMAINS
    ):
        return False
    if local in _BLOCKED_LOCALS:
        return False
    return True


def _search_urls(name: str, config: dict) -> list[str]:
    """Build the ordered enrichment URLs for ``name``."""

    enrichment = (config or {}).get("enrichment", {}) or {}
    template = enrichment.get("selskabsinfo_search_url") or DEFAULT_SEARCH_URL
    urls = [str(template).replace("{query}", quote_plus(name))]

    aarhus_url = enrichment.get("aarhus_url")
    if aarhus_url:
        urls.append(str(aarhus_url))
    return urls


def _cache_key(row: dict) -> str:
    """Return a stable cache key for ``row``."""

    return f"{_clean(row.get('name')).lower()}::{_clean(row.get('postdistrikt')).lower()}"


def _clean(value: object) -> str:
    """Return ``value`` as a trimmed string, treating ``None`` as empty."""

    return "" if value is None else str(value).strip()
