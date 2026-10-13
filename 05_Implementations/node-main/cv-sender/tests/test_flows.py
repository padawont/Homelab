"""E2E flow tests for cv sender (issue #631): present email, enrichment,
no-result enrichment, end-of-day digest. SMTP is mocked and mail redirected to
TEST_RECIPIENT; T1/T2/T4 skip without credentials/CV; T3 is offline."""
import os
import sys
import tempfile
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

TEST_RECIPIENT = "RyanHarrisZubair@gmail.com"
PASSWORD_ENV = "GMAIL_APP_PASSWORD"

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

import main
from config import load_config
import enrich
from monitor import send_digest
from sender import send_email, _body
from state import State
import validate
from validate import classify

CONTAINER_CONFIG_PATH = Path("/app/config/config.yaml")
HOST_CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "config.yaml"
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


class CvSenderFlowTests(unittest.TestCase):
    def test_send_with_present_email(self):
        """T1: a valid, in-scope row is sent with the CV attached, redirected."""
        config = _load_config_or_skip(self)
        config["dry_run"] = False  # these tests assert a real send
        _require_send_prereqs(self, config)
        cv_path = config["email"]["attachment"]
        row = {"name": "Testvirksomhed A/S", "postdistrikt": "Aarhus C", "branche": "computer", "address": "Testvej 1", "email": "accounts@example.com", "phone": "1", "employees": "1"}
        send_row = dict(row)
        send_row["email"] = TEST_RECIPIENT  # redirect: never mail the real address
        smtp_cls, sent = _fake_smtp()
        with mock.patch("smtplib.SMTP", smtp_cls):
            message_id = send_email(config, send_row, cv_path)
        self.assertIsNotNone(message_id)
        message = sent[0]
        self.assertEqual(message["To"], TEST_RECIPIENT)
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
        send_row = dict(row)
        send_row["email"] = TEST_RECIPIENT  # enriched address asserted, never mailed
        smtp_cls, sent = _fake_smtp()
        with mock.patch("smtplib.SMTP", smtp_cls):
            message_id = send_email(config, send_row, config["email"]["attachment"])
        self.assertIsNotNone(message_id)
        self.assertEqual(sent[0]["To"], TEST_RECIPIENT)
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
