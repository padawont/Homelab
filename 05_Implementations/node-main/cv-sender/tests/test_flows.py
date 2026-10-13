"""E2E flow tests for cv sender (issue #631): present email, enrichment,
no-result enrichment, end-of-day digest. SMTP is mocked and mail redirected to
the sending account (or ``CV_SENDER_TEST_RECIPIENT``); T1/T2/T4 skip without
credentials/CV; T3/T5/T6 are fully offline. T7 is an opt-in live send that
authenticates against real Gmail and verifies delivery over IMAP — it never runs
by default and is gated behind ``CV_SENDER_LIVE_SEND``. T8 guards against drift
between ``configs/config.yaml`` and the copy wrapped by ``configs/configmap.yaml``
and skips in the container, where ``configmap.yaml`` is not mounted."""
import imaplib
import os
import re
import sys
import tempfile
import time
import types
import unittest
from datetime import datetime, timezone
from email import message_from_bytes, policy
from email.utils import getaddresses
from pathlib import Path
from unittest import mock

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

PASSWORD_ENV = "GMAIL_APP_PASSWORD"
TEST_RECIPIENT_ENV = "CV_SENDER_TEST_RECIPIENT"
LIVE_SEND_ENV = "CV_SENDER_LIVE_SEND"
LIVE_RECIPIENT_ENV = "CV_SENDER_LIVE_RECIPIENT"

# Host has no Playwright; stub it so enrich.py imports (its `_lookup` wraps
# everything in try/except, so `sync_playwright=None` degrades to a None result).
try:
    import playwright.sync_api  # noqa: F401
except ImportError:
    _s = types.ModuleType("playwright.sync_api")
    _s.sync_playwright = None
    _s.Page = object
    _p = types.ModuleType("playwright")
    _p.sync_api = _s
    sys.modules.update(playwright=_p, **{"playwright.sync_api": _s})

import yaml

import main
from config import load_config
import enrich
from monitor import send_digest
from sender import send_email, _body
from state import State
import validate
from validate import classify

# openpyxl is present only in the worker image, not the host, so ``normalize``
# (which imports it at module load) is imported and its tests skipped on the host.
try:
    import normalize
    HAS_NORMALIZE = True
except ImportError:  # pragma: no cover - host has no openpyxl
    normalize = None
    HAS_NORMALIZE = False

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
    quoted.
    """
    if not name:
        return name
    if name.startswith(b'"') and name.endswith(b'"'):
        return name
    return b'"' + name + b'"'


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


def _poll_for_message_id(imap, message_id, timeout=60.0, interval=5.0):
    """Poll the selected folder for ``message_id``; return the RFC822 payload."""
    search_key = message_id.strip("<>")
    deadline = time.monotonic() + timeout
    while True:
        typ, data = imap.search(None, "HEADER", "Message-ID", search_key)
        if typ == "OK" and data and data[0]:
            nums = data[0].split()
            if nums:
                typ2, payload = imap.fetch(nums[-1], "(RFC822)")
                if typ2 == "OK" and payload and isinstance(payload[0], tuple):
                    return payload[0][1]
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


class CvSenderFlowTests(unittest.TestCase):
    def test_send_with_present_email(self):
        """T1: a valid, in-scope row is sent with the CV attached, redirected."""
        config = _load_config_or_skip(self)
        config["dry_run"] = False  # these tests assert a real send
        _require_send_prereqs(self, config)
        cv_path = config["email"]["attachment"]
        row = {"name": "Testvirksomhed A/S", "postdistrikt": "Aarhus C", "branche": "computer", "address": "Testvej 1", "email": "accounts@example.com", "phone": "1", "employees": "1"}
        recipient = _test_recipient(config)
        send_row = dict(row)
        send_row["email"] = recipient  # redirect: never mail the real address
        smtp_cls, sent = _fake_smtp()
        with mock.patch("smtplib.SMTP", smtp_cls):
            message_id = send_email(config, send_row, cv_path)
        self.assertIsNotNone(message_id)
        message = sent[0]
        self.assertEqual(message["To"], recipient)
        self.assertEqual(message["Message-ID"], message_id)
        self.assertEqual(message["Subject"], SUBJECT_PATH.read_text(encoding="utf-8").strip())
        self.assertEqual(
            message.get_body().get_content().rstrip("\n"),
            _body(config, row["name"]).rstrip("\n"),
        )
        [part] = list(message.iter_attachments())
        self.assertEqual(part.get_content_type(), "application/pdf")
        self.assertEqual(part.get_filename(), Path(cv_path).name)
        self.assertEqual(part.get_payload(decode=True), Path(cv_path).read_bytes())

    def test_enrich_missing_email_then_redirect(self):
        """T2: enrichment finds an address, asserted but never mailed."""
        config = _load_config_or_skip(self)
        config["dry_run"] = False  # these tests assert a real send
        _require_send_prereqs(self, config)
        enriched = "kontakt@example.dk"  # fixed contactable address; no network
        row = {"name": "Testvirksomhed ApS", "postdistrikt": "Aarhus C", "branche": "computer", "email": ""}
        with mock.patch.object(enrich, "_lookup", return_value=enriched):
            found = enrich.enrich(row, config, {})
        self.assertEqual(found, enriched)
        local, _, domain = enriched.partition("@")
        self.assertNotIn(local, enrich._BLOCKED_LOCALS)
        self.assertFalse(any(domain == d or domain.endswith("." + d) for d in enrich._DIRECTORY_DOMAINS))
        recipient = _test_recipient(config)
        send_row = dict(row)
        send_row["email"] = recipient  # enriched address asserted, never mailed
        smtp_cls, sent = _fake_smtp()
        with mock.patch("smtplib.SMTP", smtp_cls):
            message_id = send_email(config, send_row, config["email"]["attachment"])
        self.assertIsNotNone(message_id)
        self.assertEqual(sent[0]["To"], recipient)
        self.assertNotEqual(sent[0]["To"], enriched)

    def test_missing_email_no_enrichment_no_send(self):
        """T3: no enrichment → skipped_no_email and no SMTP (offline send path)."""
        db_dir = tempfile.mkdtemp(prefix="cv-sender-")
        config = {
            "dry_run": False,
            "email": {"attachment": "/app/config/cv/cv.pdf"},
            "rate": {"daily_cap": 400, "delay_seconds": 0},
            "filters": {"postdistrikter": ["Viby J", "Aarhus N", "Aarhus C", "Aarhus V"]},
            "state": {"db_path": os.path.join(db_dir, "state.db")},
        }
        row = {"name": "Definitely Not A Real Company", "postdistrikt": "Aarhus C", "branche": "computer", "email": ""}
        with mock.patch.object(main, "_load_rows", return_value=[row]), \
                mock.patch.object(enrich, "_lookup", return_value=None), \
                mock.patch("smtplib.SMTP") as smtp_cls:
            main._send_batch(config, limit=1)
        smtp_cls.assert_not_called()
        status, reason = classify(row, config)
        self.assertEqual(status, "skipped_no_email")
        self.assertTrue(reason)

    def test_end_of_day_digest(self):
        """T4: digest sums sent/replied/bounced counts, delivered to notify_email."""
        config = _load_config_or_skip(self)
        config["dry_run"] = False  # _send_notification short-circuits under dry_run
        _require_send_prereqs(self, config)
        state = State(os.path.join(tempfile.mkdtemp(prefix="cv-sender-"), "state.db"))
        state.init()
        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            seeds = [
                ("Alpha A/S", "Aarhus C", "alpha@example.com", f"{today} 09:00:00", False, False),
                ("Beta A/S", "Aarhus C", "beta@example.com", f"{today} 09:05:00", True, False),
                ("Gamma A/S", "Aarhus V", "gamma@example.com", f"{today} 09:10:00", False, True),
                ("Delta A/S", "Aarhus N", "delta@example.com", "2020-01-01 09:00:00", False, False),
                ("Epsilon A/S", "Viby J", "epsilon@example.com", f"{today} 09:20:00", True, True),
            ]
            for i, (name, district, email, sent_at, reply, bounce) in enumerate(seeds):
                state.record({"name": name, "postdistrikt": district, "email": email}, "valid", "ok")
                mid = f"<seed-{i}@test.local>"
                state.mark_sent(name, district, mid, sent_at)
                if reply:
                    state.mark_reply(mid, f"{today} 10:00:00")
                if bounce:
                    state.mark_bounce(email)
            smtp_cls, sent = _fake_smtp()
            with mock.patch("smtplib.SMTP", smtp_cls):
                send_digest(config, state)
            self.assertEqual(len(sent), 1)
            message = sent[0]
            self.assertEqual(message["To"], config["account"]["notify_email"])
            expected = ("cv sender — daglig digest\n\nSendt i alt: 5\n"
                        "Sendt i dag: 4\nSvar:        2\nBounces:     2\n")
            self.assertEqual(message.get_content(), expected)
        finally:
            state.close()

    def test_dry_run_sends_nothing(self):
        """T5: dry_run: true makes _send_batch send nothing (fail-closed, offline).

        A VALID, in-scope row (computer branch, Aarhus C, real-MX gmail.com) is
        fed to ``_send_batch`` with ``dry_run`` enabled. The guard returns ``0``
        immediately — before rows are even loaded — so ``smtplib.SMTP`` is never
        constructed and no ``sent`` row is recorded. ``has_valid_mx`` is stubbed
        (DNS is offline/non-deterministic) so the row would classify ``valid``,
        proving the assertion targets the dry-run interlock and not a validator
        rejection.
        """
        db_dir = tempfile.mkdtemp(prefix="cv-sender-")
        db_path = os.path.join(db_dir, "state.db")
        cv_path = os.path.join(db_dir, "cv.pdf")
        Path(cv_path).write_bytes(b"%PDF-1.4\nfake cv for offline test\n")

        config = {
            "dry_run": True,
            "email": {
                "attachment": cv_path,
                "signature_name": "Test User",
                "signature_phone": "+45 12 34 56 78",
            },
            "account": {
                "email": "sender@example.com",
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
            },
            "rate": {"daily_cap": 400, "delay_seconds": 0},
            "filters": {"postdistrikter": ["Viby J", "Aarhus N", "Aarhus C", "Aarhus V"]},
            "state": {"db_path": db_path},
        }
        row = {
            "name": "Testvirksomhed A/S",
            "postdistrikt": "Aarhus C",
            "branche": "computer",
            "address": "Testvej 1",
            "email": "accounts@gmail.com",
            "phone": "1",
            "employees": "1",
        }

        with mock.patch.object(main, "_load_rows", return_value=[row]) as load_rows, \
                mock.patch.object(validate, "has_valid_mx", return_value=True), \
                mock.patch("smtplib.SMTP") as smtp_cls:
            result = main._send_batch(config, limit=1)

        self.assertEqual(result, 0)
        smtp_cls.assert_not_called()  # no mail may ever leave the process
        load_rows.assert_not_called()  # guard returns before the scraper runs

        state = State(db_path)
        state.init()
        try:
            self.assertEqual(state.iter_sent(), [])
        finally:
            state.close()

    def test_dry_run_pilot_sends_nothing(self):
        """T6: _run_pilot with dry_run routes to the dry-run path and sends nothing."""
        db_dir = tempfile.mkdtemp(prefix="cv-sender-")
        preview_csv = os.path.join(db_dir, "preview.csv")
        config = {
            "dry_run": True,
            "filters": {"postdistrikter": ["Viby J", "Aarhus N", "Aarhus C", "Aarhus V"]},
            "state": {"db_path": os.path.join(db_dir, "state.db")},
            "paths": {"preview_csv": preview_csv},
        }
        row = {
            "name": "Testvirksomhed A/S",
            "postdistrikt": "Aarhus C",
            "branche": "computer",
            "email": "accounts@gmail.com",
        }
        with mock.patch.object(main, "_load_rows", return_value=[row]), \
                mock.patch.object(validate, "has_valid_mx", return_value=True), \
                mock.patch("smtplib.SMTP") as smtp_cls:
            result = main._run_pilot(config, 1)
        self.assertEqual(result, 0)
        smtp_cls.assert_not_called()
        self.assertTrue(Path(preview_csv).is_file())  # dry-run path actually ran

    @unittest.skipUnless(
        (os.environ.get(LIVE_SEND_ENV) or "").strip().lower()
        in ("1", "true", "yes", "on"),
        f"set {LIVE_SEND_ENV}=1 to send a real message via Gmail and verify it over IMAP",
    )
    def test_live_send_and_verify(self):
        """T7: opt-in live send through production send_email + IMAP verification.

        Sends exactly one enquiry over the real SMTP path (``smtp.gmail.com:587``
        + STARTTLS) and proves delivery by locating the returned ``Message-ID``
        in the sender's Gmail Sent Mail folder (discovered from ``imap.list()``,
        never hardcoded). The recipient is ``CV_SENDER_LIVE_RECIPIENT`` when set,
        otherwise the sender's own address — never a scraped company address.
        Skipped cleanly when the app password or the CV attachment is missing.
        """
        config = _load_config_or_skip(self)
        config["dry_run"] = False  # send_email refuses to send under dry_run
        _require_send_prereqs(self, config)

        account = config["account"]
        sender = account["email"]
        recipient = (os.environ.get(LIVE_RECIPIENT_ENV) or "").strip() or sender

        company_name = "Testvirksomhed Live A/S"
        row = {"name": company_name, "email": recipient}

        message_id = send_email(config, row, config["email"]["attachment"])
        self.assertIsNotNone(message_id)

        imap_host = account.get("imap_host") or "imap.gmail.com"
        imap = imaplib.IMAP4_SSL(imap_host, 993)
        payload = None
        try:
            imap.login(sender, os.environ[PASSWORD_ENV])
            folder = _discover_sent_folder(imap)
            typ, _data = imap.select(folder)
            if typ != "OK":
                self.fail(f"IMAP SELECT {folder!r} returned {typ!r}")
            payload = _poll_for_message_id(imap, message_id)
        finally:
            try:
                imap.logout()
            except Exception:  # noqa: BLE001 - best-effort teardown
                pass

        self.assertIsNotNone(
            payload, f"sent message {message_id!r} not found in Sent Mail within 60s"
        )
        message = message_from_bytes(payload, policy=policy.default)

        to_addrs = {addr.lower() for _, addr in getaddresses([message.get("To", "")])}
        self.assertIn(recipient.lower(), to_addrs)
        self.assertEqual(
            message.get("Subject", ""),
            SUBJECT_PATH.read_text(encoding="utf-8").strip(),
        )

        pdfs = [
            p for p in message.iter_attachments()
            if p.get_content_type() == "application/pdf"
        ]
        self.assertEqual(len(pdfs), 1, "expected exactly one application/pdf attachment")
        self.assertEqual(pdfs[0].get_filename(), "cv.pdf")
        self.assertEqual(
            pdfs[0].get_payload(decode=True),
            Path(config["email"]["attachment"]).read_bytes(),
        )

        body = message.get_body(preferencelist=("plain",)).get_content()
        self.assertIn(company_name, body)
        self.assertIn(config["email"]["signature_name"], body)
        self.assertIn(config["email"]["signature_phone"], body)

    def test_config_and_configmap_stay_in_sync(self):
        """T8: configs/config.yaml and configs/configmap.yaml must not drift.

        The ConfigMap wraps a copy of the source-of-truth config under
        ``data["config.yaml"]`` and the pod mounts only that copy, so a drift
        where the ConfigMap said ``dry_run: false`` while the file said ``true``
        would fail *open* at deploy. Parses both documents and asserts they are
        equal, plus the ConfigMap's own name/namespace and that the ``dry_run``
        safety flag survives into the copy. Skips cleanly in the container,
        where only ``/app/config/config.yaml`` is mounted (not ``configmap.yaml``).
        """
        missing = [
            str(p)
            for p in (HOST_CONFIG_PATH, HOST_CONFIGMAP_PATH)
            if not p.is_file()
        ]
        if missing:
            self.skipTest(
                "config/configmap drift guard skipped; missing files (expected in "
                "the container, which mounts only /app/config/config.yaml): "
                + ", ".join(missing)
            )

        file_config = yaml.safe_load(HOST_CONFIG_PATH.read_text(encoding="utf-8"))
        configmap = yaml.safe_load(HOST_CONFIGMAP_PATH.read_text(encoding="utf-8"))

        self.assertEqual(configmap["metadata"]["name"], "cv-sender-config")
        self.assertEqual(configmap["metadata"]["namespace"], "cv-sender")

        configmap_config = yaml.safe_load(configmap["data"]["config.yaml"])
        self.assertIn(
            "dry_run",
            configmap_config,
            "ConfigMap data['config.yaml'] is missing the dry_run safety flag",
        )

        self.assertEqual(
            file_config,
            configmap_config,
            msg="configs/config.yaml and configs/configmap.yaml have drifted:\n"
            + "\n".join(_dict_diff(file_config, configmap_config)),
        )


# -- normalize regression helpers (issue #638) ------------------------------

_HEADER = [
    "Hovedkategori", "Branche", "Virksomhed", "Postdistrikt",
    "Adresse", "Email", "Telefonnummer", "Antal medarbejdere",
]


def _write_xlsx(path, data_rows, targit_bug=False):
    """Write a TARGIT-shaped workbook: an empty first sheet + a ``Tabel`` sheet.

    ``targit_bug=True`` injects the ``defaultColWidthPt`` attribute that
    openpyxl 3.1.5 cannot parse, so ``read_rows`` must sanitise it in memory.
    """
    import openpyxl

    wb = openpyxl.Workbook()
    first = wb.active
    first.title = "Du kan også finde virksomhedern"
    first["A1"] = None
    tabel = wb.create_sheet("Tabel")
    tabel.append(_HEADER)
    for row in data_rows:
        tabel.append(row)
    wb.save(path)
    if targit_bug:
        _inject_default_col_width_pt(path)


def _inject_default_col_width_pt(path):
    """Add ``defaultColWidthPt`` to the worksheet XML of ``path`` in place."""
    import io
    import zipfile

    path = Path(path)
    raw = path.read_bytes()
    buffer = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as zin, \
            zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("xl/worksheets/") and item.filename.endswith(".xml"):
                if b"<sheetFormatPr" in data:
                    data = re.sub(
                        rb"<sheetFormatPr\b([^>]*?)(/?)>",
                        rb'<sheetFormatPr\1 defaultColWidthPt="7.5"\2>',
                        data,
                        count=1,
                    )
                else:
                    data = data.replace(
                        b"<sheetData>",
                        b'<sheetFormatPr defaultColWidthPt="7.5"/><sheetData>',
                        1,
                    )
            zout.writestr(item, data)
    path.write_bytes(buffer.getvalue())


@unittest.skipUnless(
    HAS_NORMALIZE,
    "openpyxl not installed (host); normalize tests run in the worker image",
)
class NormalizeTests(unittest.TestCase):
    """Normalization regressions for issue #638: the ``Tabel`` sheet, the
    openpyxl ``defaultColWidthPt`` sanitisation, and the Python-side Branche
    filter that replaced the in-browser slicer."""

    def _data_rows(self):
        return [
            ["IT", "Computerprogrammering", "Acme A/S", "Aarhus C",
             "Vej 1", "acme@example.com", "1", "10"],
            ["IT", "Computerkonsulentbistand og forvaltning af computerfaciliteter",
             "Beta ApS", "Viby J", "Vej 2", "beta@example.com", "2", "5"],
            ["Byg", "Byggeri", "Gamma A/S", "Aarhus N",
             "Vej 3", "gamma@example.com", "3", "20"],
        ]

    def test_read_rows_selects_tabel_not_active(self):
        """The data lives on ``Tabel``, not the empty ``workbook.active`` sheet."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "companies.xlsx"
            _write_xlsx(path, self._data_rows())
            rows = normalize.read_rows(str(path))
        self.assertEqual(
            [r["name"] for r in rows], ["Acme A/S", "Beta ApS", "Gamma A/S"]
        )

    def test_read_rows_strips_default_col_width_pt(self):
        """openpyxl 3.1.5 rejects ``defaultColWidthPt``; read_rows sanitises it."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "companies.xlsx"
            _write_xlsx(path, self._data_rows(), targit_bug=True)
            before = path.read_bytes()
            rows = normalize.read_rows(str(path))  # must not raise TypeError
            after = path.read_bytes()
        self.assertEqual(len(rows), 3)
        self.assertEqual(before, after)  # the file on disk is never mutated

    def test_filter_rows_case_insensitive_substring(self):
        rows = [
            {"branche": "Computerprogrammering", "name": "a"},
            {"branche": "computerkonsulentbistand", "name": "b"},
            {"branche": "Byggeri", "name": "c"},
        ]
        self.assertEqual(len(normalize.filter_rows(rows, "computer")), 2)
        self.assertEqual(len(normalize.filter_rows(rows, "COMPUTER")), 2)
        self.assertEqual(normalize.filter_rows(rows, ""), rows)  # no query -> unchanged
        self.assertEqual(normalize.filter_rows(rows, None), rows)
