"""Auth-invariant tests for the cv sender (post-#636 findings B-F8 / B-F9).

Why this file exists
--------------------
``config.account.email`` (e.g. ``sender@example.com``) is the SMTP/IMAP identity
the worker authenticates as; ``config.account.notify_email`` (e.g.
``applicant@example.com``) is the human the worker writes *to*. Those two are
easy to conflate. A future edit could reintroduce a hardcoded sender address, or
swap the two config keys, and — because the existing flow tests redirect all
traffic to the sending account itself and mock SMTP wholesale — nothing would
fail. These tests pin the invariant down on a config where the two addresses are
deliberately DISTINCT and assert *which* identity appears in ``login()``, in the
``From`` header, and in the ``To`` header.

All tests are offline: ``smtplib.SMTP`` / ``imaplib.IMAP4_SSL`` are patched and
State lives on a throwaway temp database, never the repo's ``data/state.db``.
``_helpers`` is imported first so the shared host shims are installed.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# _helpers installs the host shims (src on sys.path, Playwright stub); it must be
# imported before any cv-sender module below.
from _helpers import (  # noqa: F401
    PASSWORD_ENV,
    TEST_RECIPIENT_ENV,
    _fake_smtp,
    _test_recipient,
)

import monitor
import sender
from state import State

#: Distinct, non-routable identities. ``sender`` authenticates; ``applicant`` is
#: only ever a recipient. The password is a placeholder — never a real secret.
SENDER_EMAIL = "sender@example.com"
APPLICANT_EMAIL = "applicant@example.com"
ROW_RECIPIENT = "recipient@example.com"
APP_PASSWORD = "placeholder-app-password"

SIGNATURE_ENV = {
    "CV_SENDER_SIGNATURE_NAME": "Test User",
    "CV_SENDER_SIGNATURE_PHONE": "+45 12 34 56 78",
}


def _auth_config() -> dict:
    """A live-send config whose sender and applicant identities are DISTINCT."""
    return {
        "dry_run": False,  # both send paths short-circuit under dry_run
        "account": {
            "email": SENDER_EMAIL,
            "notify_email": APPLICANT_EMAIL,
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "imap_host": "imap.example.com",
        },
    }


class AuthInvariantTests(unittest.TestCase):
    """B-F8: every authenticated path uses ``account.email``, never the applicant."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="cv-sender-auth-")
        self.addCleanup(self._tmp.cleanup)

    # -- helpers ----------------------------------------------------------
    def _write_cv(self) -> str:
        path = Path(self._tmp.name) / "cv.pdf"
        path.write_bytes(b"%PDF-1.4\nfake cv for offline auth-invariant test\n")
        return str(path)

    def _state(self) -> State:
        state = State(str(Path(self._tmp.name) / "state.db"))
        state.init()
        self.addCleanup(state.close)
        return state

    def _env(self, **extra) -> dict:
        env = {PASSWORD_ENV: APP_PASSWORD, **SIGNATURE_ENV}
        env.update(extra)
        return env

    # -- B-F8 -------------------------------------------------------------
    def test_send_email_authenticates_as_account_email(self):
        """``send_email`` logs in as ``account.email`` — never the row recipient."""
        config = _auth_config()
        row = {"name": "X", "email": ROW_RECIPIENT}
        smtp_cls, _sent = _fake_smtp()

        with mock.patch.dict(os.environ, self._env()), \
                mock.patch("smtplib.SMTP", smtp_cls):
            message_id = sender.send_email(config, row, self._write_cv())

        self.assertIsNotNone(message_id)
        smtp_cls.return_value.login.assert_called_once_with(SENDER_EMAIL, APP_PASSWORD)

    def test_send_notification_authenticates_and_addresses_applicant(self):
        """``_send_notification`` authenticates as the account, addressed to the applicant."""
        config = _auth_config()
        smtp_cls, sent = _fake_smtp()

        with mock.patch.dict(os.environ, self._env()), \
                mock.patch("smtplib.SMTP", smtp_cls):
            monitor._send_notification(config, "subject line", "notification body")

        smtp_cls.return_value.login.assert_called_once_with(SENDER_EMAIL, APP_PASSWORD)
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]["From"], SENDER_EMAIL)
        self.assertEqual(sent[0]["To"], APPLICANT_EMAIL)

    def test_check_inbox_authenticates_as_account_email(self):
        """``check_inbox`` logs into IMAP as ``account.email``, not the applicant."""
        config = _auth_config()
        state = self._state()
        imap_cls = mock.MagicMock()
        client = imap_cls.return_value
        client.list.return_value = ("OK", [b""])
        client.select.return_value = ("OK", [b""])
        client.search.return_value = ("OK", [b""])

        with mock.patch.dict(os.environ, self._env()), \
                mock.patch("imaplib.IMAP4_SSL", imap_cls):
            replies, bounces = monitor.check_inbox(config, state)

        self.assertEqual((replies, bounces), ([], []))
        client.login.assert_called_once_with(SENDER_EMAIL, APP_PASSWORD)


class RecipientIndependenceTests(unittest.TestCase):
    """B-F9: the ``To`` header honours the row, not the sending account."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="cv-sender-recipient-")
        self.addCleanup(self._tmp.cleanup)

    def _write_cv(self) -> str:
        path = Path(self._tmp.name) / "cv.pdf"
        path.write_bytes(b"%PDF-1.4\nfake cv for offline recipient test\n")
        return str(path)

    def test_to_header_honours_row_over_sender(self):
        """With a distinct test recipient, ``To`` equals the row's address."""
        config = _auth_config()
        env = {
            PASSWORD_ENV: APP_PASSWORD,
            **SIGNATURE_ENV,
            TEST_RECIPIENT_ENV: "qa-recipient@example.com",
        }
        smtp_cls, sent = _fake_smtp()

        with mock.patch.dict(os.environ, env), \
                mock.patch("smtplib.SMTP", smtp_cls):
            recipient = _test_recipient(config)  # resolves the explicit override
            self.assertEqual(recipient, "qa-recipient@example.com")
            row = {"name": "Y", "email": recipient}
            message_id = sender.send_email(config, row, self._write_cv())

        self.assertIsNotNone(message_id)
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]["To"], row["email"])
        self.assertNotEqual(sent[0]["To"], SENDER_EMAIL)
        self.assertEqual(sent[0]["From"], SENDER_EMAIL)


if __name__ == "__main__":  # pragma: no cover - convenience runner
    unittest.main()
