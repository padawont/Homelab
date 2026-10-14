"""Innermost ``dry_run`` guard tests for the cv sender worker (issue #632).

T5/T6 in ``test_flows.py`` exercise the *outer* interlocks: T5 calls
``main._send_batch``, whose first action returns ``0`` when ``dry_run`` is true,
so ``sender.send_email`` is never reached and the guard *inside* ``send_email``
is never exercised. T6 routes through ``main._run_pilot`` and inherits the same
masking.

The tests here deliberately call the guarded leaf functions directly, so the
innermost ``dry_run`` guard is UNMASKED: deleting it from ``sender.send_email``
or ``monitor._send_notification`` would make these tests fail even though T5/T6
would still pass. Both tests are fully offline — no config file, no credentials,
no mailbox, and ``smtplib.SMTP`` patched so any accidental transport raises.

Importing ``_helpers`` first puts ``src`` on ``sys.path`` and installs the
Playwright stub, matching the import contract used by ``test_flows.py``.
"""

import os
import unittest
from unittest import mock

import _helpers  # noqa: F401  # side effect: src on sys.path + Playwright stub

import monitor
import sender


class DryRunGuardTests(unittest.TestCase):
    """The leaf-level ``dry_run`` interlocks must short-circuit before transport."""

    def test_send_email_dry_run_returns_none_without_smtp(self):
        """``sender.send_email`` returns ``None`` and builds no SMTP client.

        UNMASKED (unlike T5): ``main._send_batch`` is bypassed entirely, so this
        asserts the guard that lives *inside* ``send_email``. The CV path points
        at a nonexistent file on purpose — the guard is the first action, so the
        attachment must never be read. ``smtplib.SMTP`` is patched so a removed
        guard produces a call on the mock rather than a real network connection.
        """
        config = {"dry_run": True}

        with mock.patch("smtplib.SMTP") as smtp_cls:
            result = sender.send_email(
                config, {"name": "X", "email": "a@b.dk"}, "/nonexistent/cv.pdf"
            )

        self.assertIsNone(result)
        smtp_cls.assert_not_called()

    def test_send_notification_dry_run_returns_without_smtp(self):
        """``monitor._send_notification`` returns early and builds no SMTP client.

        UNMASKED: the config carries a complete, real account — a sender address,
        a notify address and SMTP host/port — so the ``dry_run`` guard is the
        ONLY thing that can stop the send. Delete that guard and control falls
        straight through the message-building path, constructs ``smtplib.SMTP``
        and authenticates, so ``assert_not_called`` fails. The earlier, weaker
        version passed a bare ``{"dry_run": True}``: deleting the guard would
        then have been caught by the *later* ``account.notify_email is not set``
        early return, which also skips SMTP — so the test passed for the wrong
        reason and did not pin the ``dry_run`` guard at all.

        ``GMAIL_APP_PASSWORD`` is patched too, so the password lookup inside the
        transport path cannot short-circuit the fall-through either (it would
        raise ``RuntimeError`` before reaching the SMTP mock). ``smtplib.SMTP``
        is patched so any accidental transport is observable on the mock rather
        than becoming a real network connection.
        """
        config = {
            "dry_run": True,
            "account": {
                "email": "sender@example.com",
                "notify_email": "applicant@example.com",
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
            },
        }

        with mock.patch.dict(os.environ, {"GMAIL_APP_PASSWORD": "placeholder-app-password"}), \
                mock.patch("smtplib.SMTP") as smtp_cls:
            result = monitor._send_notification(config, "subj", "body")

        self.assertIsNone(result)
        smtp_cls.assert_not_called()


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    unittest.main()
