"""Email syntax / MX validation and row classification for cv sender.

Classification uses a fixed status vocabulary so that ``state.py`` and
``monitor.py`` can persist and query statuses without translation.
"""

from __future__ import annotations

import logging
import re

import dns.exception
import dns.resolver

logger = logging.getLogger(__name__)

# Fixed status vocabulary shared with the rest of the worker.
STATUS_VALID = "valid"
STATUS_NO_MX = "no_mx"
STATUS_SKIPPED_NO_EMAIL = "skipped_no_email"
STATUS_SKIPPED_NO_DISTRICT = "skipped_no_district"
STATUS_SKIPPED_OUT_OF_AREA = "skipped_out_of_area"

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

_RESOLVER_TIMEOUT = 5.0
_RESOLVER_LIFETIME = 10.0


def has_valid_syntax(email: str) -> bool:
    """Return ``True`` when ``email`` looks like a syntactically valid address."""

    candidate = (email or "").strip()
    if not candidate or "@" not in candidate:
        return False
    return bool(_EMAIL_RE.match(candidate))


def has_valid_mx(email: str) -> bool:
    """Return ``True`` when the email domain publishes an MX record.

    Fail-safe: a syntax problem, a missing record, or any DNS error yields
    ``False`` so that a transient resolver failure never mails an unreachable
    domain.
    """

    if not has_valid_syntax(email):
        return False

    domain = email.strip().rsplit("@", 1)[1].lower().rstrip(".")
    if not domain:
        return False

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = _RESOLVER_TIMEOUT
        resolver.lifetime = _RESOLVER_LIFETIME
        answers = resolver.resolve(domain, "MX")
    except dns.exception.DNSException as exc:
        logger.debug("MX lookup failed for %s: %s", domain, exc)
        return False
    except Exception:  # pragma: no cover - defensive, never fail open
        logger.debug("Unexpected MX lookup error for %s", domain, exc_info=True)
        return False

    return len(answers) > 0


def classify(row: dict, config: dict) -> tuple[str, str]:
    """Classify ``row`` against the configured filters.

    Returns a ``(status, reason)`` pair drawn from the fixed vocabulary. The
    service-area filter is applied before the email checks, mirroring the
    pipeline order in ADR-612 (filter, then validate, then enrich).
    """

    postdistrikt = _clean(row.get("postdistrikt"))
    email = _clean(row.get("email"))
    allowed = _allowed_districts(config)

    if not postdistrikt:
        return STATUS_SKIPPED_NO_DISTRICT, "row has no postdistrikt"
    if postdistrikt.lower() not in allowed:
        return STATUS_SKIPPED_OUT_OF_AREA, f"postdistrikt {postdistrikt!r} is out of area"
    if not email:
        return STATUS_SKIPPED_NO_EMAIL, "row has no email address"
    if not has_valid_syntax(email):
        return STATUS_NO_MX, f"email {email!r} has invalid syntax"
    if not has_valid_mx(email):
        return STATUS_NO_MX, f"domain of {email!r} has no MX record"
    return STATUS_VALID, "email passes syntax and MX checks"


def _allowed_districts(config: dict) -> set[str]:
    """Return the lower-cased set of accepted postdistrikter."""

    districts = (config or {}).get("filters", {}).get("postdistrikter", []) or []
    return {str(item).strip().lower() for item in districts if str(item).strip()}


def _clean(value: object) -> str:
    """Return ``value`` as a trimmed string, treating ``None`` as empty."""

    return "" if value is None else str(value).strip()
