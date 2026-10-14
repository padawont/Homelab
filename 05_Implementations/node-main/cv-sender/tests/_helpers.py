"""Shared test helpers and host-environment shims for the cv sender tests.

Importing this module puts ``src`` on ``sys.path`` and installs the Playwright
stub (when Playwright is absent), so every test module sees the same
environment. It must be imported before any cv-sender module (``main``,
``enrich``, ``scraper``, ...); it deliberately imports none of them at module
level. The leading underscore keeps it out of ``unittest`` discovery.
"""
import os
import re
import sys
import time
import types
from pathlib import Path
from unittest import mock

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

PASSWORD_ENV = "GMAIL_APP_PASSWORD"
TEST_RECIPIENT_ENV = "CV_SENDER_TEST_RECIPIENT"
LIVE_SEND_ENV = "CV_SENDER_LIVE_SEND"
LIVE_RECIPIENT_ENV = "CV_SENDER_LIVE_RECIPIENT"
VERIFY_TIMEOUT_ENV = "CV_SENDER_VERIFY_TIMEOUT"

# Host has no Playwright; stub it so enrich.py imports (its `_lookup` wraps
# everything in try/except, so `sync_playwright=None` degrades to a None result).
try:
    import playwright.sync_api  # noqa: F401
except ImportError:
    _s = types.ModuleType("playwright.sync_api")
    _s.sync_playwright = None
    _s.Page = object
    _s.TimeoutError = Exception  # scraper.py imports this; unused on the host
    _p = types.ModuleType("playwright")
    _p.sync_api = _s
    sys.modules.update(playwright=_p, **{"playwright.sync_api": _s})

CONTAINER_CONFIG_PATH = Path("/app/config/config.yaml")
HOST_CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "config.yaml"
HOST_CONFIGMAP_PATH = Path(__file__).resolve().parents[1] / "configs" / "configmap.yaml"
SUBJECT_PATH = SRC_DIR / "templates" / "subject.txt"


def _resolve_config_path():
    """Return the first config path that exists across both run environments."""
    env = os.environ.get("CV_SENDER_CONFIG")
    if env and Path(env).is_file():
        return env
    if CONTAINER_CONFIG_PATH.is_file():
        return str(CONTAINER_CONFIG_PATH)
    if HOST_CONFIG_PATH.is_file():
        return str(HOST_CONFIG_PATH)
    return None


def _load_config_or_skip(testcase):
    """Load the cv-sender config, skipping cleanly when none can be located."""
    from config import load_config

    path = _resolve_config_path()
    if not path:
        testcase.skipTest(
            "no cv-sender config found (set CV_SENDER_CONFIG, mount "
            "/app/config/config.yaml, or keep configs/config.yaml)"
        )
    return load_config(path)


def _fake_smtp():
    sent = []
    cls = mock.MagicMock()
    cls.return_value.__enter__.return_value = cls.return_value
    cls.return_value.__exit__.return_value = False
    cls.return_value.send_message.side_effect = sent.append
    return cls, sent


def _require_send_prereqs(testcase, config):
    if not os.environ.get(PASSWORD_ENV):
        testcase.skipTest(f"{PASSWORD_ENV} is not set; cannot build a real message")
    cv = config.get("email", {}).get("attachment")
    if not cv or not Path(cv).is_file():
        testcase.skipTest(f"CV attachment not found: {cv!r}")


def _test_recipient(config):
    """Resolve the mocked-send recipient: explicit override, else the sender.

    T1/T2 redirect SMTP traffic to the sending account itself so no test can
    ever reach an applicant's real mailbox. ``CV_SENDER_TEST_RECIPIENT``
    overrides that default when an operator wants a specific test mailbox.
    """
    override = (os.environ.get(TEST_RECIPIENT_ENV) or "").strip()
    if override:
        return override
    return config.get("account", {}).get("email", "")


def _quote_mailbox(name):
    """Wrap a mailbox name in double quotes for ``imap.select``, idempotently.

    ``imaplib`` only auto-quotes mailbox names on newer Pythons; on 3.10 the raw
    bytes are sent as-is, so a name containing spaces or brackets (e.g.
    ``[Gmail]/Sent Mail``) is rejected with ``BAD Could not parse command``.
    Always quote explicitly, but never double-quote a name that is already
    quoted. An embedded ``\\`` or ``"`` is backslash-escaped (mirroring
    ``imaplib``'s own quoting) so the quoted string stays a single valid token.
    """
    if not name:
        return name
    if name.startswith(b'"') and name.endswith(b'"'):
        return name
    escaped = name.replace(b"\\", b"\\\\").replace(b'"', b'\\"')
    return b'"' + escaped + b'"'


def _discover_sent_folder(imap):
    """Return the Gmail ``Sent Mail`` folder name from the IMAP LIST response.

    Gmail advertises the RFC 6154 ``\\Sent`` special-use flag on its Sent folder,
    so the name is discovered rather than hardcoded (it may be ``[Gmail]/Sent
    Mail``, ``[Google Mail]/Sent Mail``, or a modified-UTF-7 localised name).
    The returned name is already double-quoted for use with ``imap.select`` so a
    caller cannot forget: explicit quoting works on both Python 3.10 and 3.14,
    whereas relying on imaplib's auto-quoting fails on 3.10 for names with spaces
    or brackets.
    """
    typ, data = imap.list()
    if typ != "OK":
        raise RuntimeError(f"IMAP LIST failed: {typ!r}")
    entries = [e for e in (data or []) if isinstance(e, (bytes, bytearray))]
    for entry in entries:
        if b"\\Sent" in entry:
            match = re.search(rb'"([^"]*)"\s*$', entry)
            if match:
                return _quote_mailbox(match.group(1))
    # Fallback for servers that omit the special-use flag: any folder named
    # "sent..." (English Gmail always advertises \Sent, so this is belt/braces).
    for entry in entries:
        if b"sent" in entry.lower():
            match = re.search(rb'"([^"]*)"\s*$', entry)
            if match:
                return _quote_mailbox(match.group(1))
    raise RuntimeError("no Sent folder found in IMAP LIST response")


_FALLBACK_SCAN_LIMIT = 50


def _fetch_rfc822(imap, num):
    typ, payload = imap.fetch(num, "(RFC822)")
    if typ == "OK" and payload and isinstance(payload[0], tuple):
        return payload[0][1]
    return None


def _poll_for_message_id(imap, message_id, timeout=None, interval=5.0):
    """Poll the selected folder for ``message_id``; return the RFC822 payload.

    ``timeout=None`` resolves from ``CV_SENDER_VERIFY_TIMEOUT`` (seconds), then
    60. Some servers treat ``SEARCH HEADER Message-ID`` as a no-op and return no
    UIDs even for a delivered message; when the header search is empty, fall
    back to ``SEARCH ALL`` and scan the most recent UIDs client-side.
    """
    if timeout is None:
        try:
            timeout = float(os.environ.get(VERIFY_TIMEOUT_ENV, "") or 60)
        except ValueError:
            timeout = 60.0
    search_key = message_id.strip("<>")
    needle = search_key.encode()
    deadline = time.monotonic() + timeout
    while True:
        typ, data = imap.search(None, "HEADER", "Message-ID", search_key)
        nums = data[0].split() if typ == "OK" and data and data[0] else []
        if nums:
            raw = _fetch_rfc822(imap, nums[-1])
            if raw is not None:
                return raw
        else:
            typ_all, data_all = imap.search(None, "ALL")
            if typ_all == "OK" and data_all and data_all[0]:
                for num in reversed(data_all[0].split()[-_FALLBACK_SCAN_LIMIT:]):
                    raw = _fetch_rfc822(imap, num)
                    if raw is not None and needle in raw:
                        return raw
        if time.monotonic() >= deadline:
            return None
        time.sleep(interval)


def _dict_diff(file_cfg, cm_cfg):
    """Return human-readable lines describing how two config mappings differ.

    Walks the two mappings recursively so a drift report names the exact dotted
    key path and both values, instead of dumping two whole (deeply nested)
    dicts that a bare ``assertEqual`` would render impenetrably.
    """
    diffs = []

    def walk(prefix, left, right):
        for key in sorted(set(left) | set(right), key=str):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in left:
                diffs.append(f"  + {path}: {right[key]!r} (only in configmap.yaml)")
            elif key not in right:
                diffs.append(f"  - {path}: {left[key]!r} (only in config.yaml)")
            else:
                lv, rv = left[key], right[key]
                if isinstance(lv, dict) and isinstance(rv, dict):
                    walk(path, lv, rv)
                elif lv != rv:
                    diffs.append(f"  ~ {path}: config.yaml={lv!r} vs configmap.yaml={rv!r}")

    walk("", file_cfg, cm_cfg)
    return diffs
