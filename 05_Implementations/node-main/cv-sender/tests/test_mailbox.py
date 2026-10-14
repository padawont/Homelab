"""Offline unit tests for the IMAP mailbox helpers in ``tests/_helpers.py``.

Covers the mailbox hardening added for issue #632 — ``_discover_sent_folder``
(B-F4) and the ``SEARCH ALL`` fallback in ``_poll_for_message_id`` (B-F5) — plus
the explicit-quoting fix in ``_quote_mailbox`` (A-F3).

Every test is fully offline: a hand-written fake IMAP object stands in for
``imaplib.IMAP4_SSL``, so no socket is ever opened and no real mailbox is read.
``_helpers`` is imported first so the shared host shims (``src`` on
``sys.path``, the Playwright stub) are installed exactly as the rest of the
suite expects.
"""
import unittest
from unittest import mock

# _helpers must be imported before any cv-sender module; here it is also the
# module under test.
from _helpers import (  # noqa: F401
    _discover_sent_folder,
    _poll_for_message_id,
    _quote_mailbox,
)


class _FakeIMAP:
    """Minimal stand-in for ``imaplib.IMAP4_SSL`` for the mailbox helpers.

    ``list`` returns the canned LIST response; ``search`` answers the
    ``HEADER Message-ID`` probe and the ``ALL`` fallback from separate canned
    UID strings, and records every call so a test can prove which code path ran.
    ``fetch`` returns an ``(RFC822)`` tuple for UIDs present in ``payloads`` and
    an empty (non-matching) payload otherwise.
    """

    def __init__(
        self,
        list_data=None,
        header_uids=b"",
        all_uids=b"",
        payloads=None,
        header_status="OK",
        all_status="OK",
    ):
        self.list_data = list_data if list_data is not None else []
        self.header_uids = header_uids
        self.all_uids = all_uids
        self.payloads = payloads or {}
        self.header_status = header_status
        self.all_status = all_status
        self.search_calls = []
        self.fetch_calls = []

    def list(self):
        return "OK", self.list_data

    def search(self, charset, *criteria):
        self.search_calls.append((charset, criteria))
        if criteria[:1] == ("HEADER",):
            return self.header_status, [self.header_uids]
        if criteria[:1] == ("ALL",):
            return self.all_status, [self.all_uids]
        raise AssertionError(f"unexpected IMAP search criteria: {criteria!r}")

    def fetch(self, num, spec):
        self.fetch_calls.append((num, spec))
        raw = self.payloads.get(num)
        if raw is None:
            return "OK", [(b"0 (RFC822 {0}", b"unrelated payload")]
        return "OK", [(num + b" (RFC822 {20}", raw)]


class DiscoverSentFolderTests(unittest.TestCase):
    """B-F4: the Sent folder is discovered, never hardcoded."""

    def test_special_use_flag_is_preferred(self):
        """A ``\\Sent`` folder wins even when other folders are present.

        Prerequisite for this to hold against real Gmail: the account must keep
        sent mail (Gmail's IMAP "Store sent mail" setting enabled) and expose the
        Sent folder over IMAP with the RFC 6154 ``\\Sent`` special-use attribute.
        """
        imap = _FakeIMAP(
            list_data=[
                b'(\\HasNoChildren) "/" "INBOX"',
                b'(\\HasNoChildren \\Drafts) "/" "Drafts"',
                b'(\\HasNoChildren \\Sent) "/" "[Gmail]/Sent Mail"',
            ]
        )
        folder = _discover_sent_folder(imap)
        self.assertEqual(folder, b'"[Gmail]/Sent Mail"')

    def test_sent_named_folder_fallback(self):
        """Without ``\\Sent``, a folder literally named ``Sent`` is used.

        Some servers omit the special-use flag; the helper then falls back to a
        folder whose name contains "sent".
        """
        imap = _FakeIMAP(
            list_data=[
                b'(\\HasNoChildren) "/" "INBOX"',
                b'(\\HasNoChildren) "/" "Sent"',
            ]
        )
        folder = _discover_sent_folder(imap)
        self.assertEqual(folder, b'"Sent"')

    def test_raises_when_no_sent_folder(self):
        """Neither the ``\\Sent`` flag nor a "sent"-named folder → RuntimeError."""
        imap = _FakeIMAP(
            list_data=[
                b'(\\HasNoChildren) "/" "INBOX"',
                b'(\\HasNoChildren \\Drafts) "/" "Drafts"',
                b'(\\HasNoChildren \\Junk) "/" "[Gmail]/Spam"',
            ]
        )
        with self.assertRaises(RuntimeError):
            _discover_sent_folder(imap)


class QuoteMailboxTests(unittest.TestCase):
    """A-F3: ``_quote_mailbox`` quotes idempotently and escapes embedded bytes."""

    def test_plain_name_is_quoted(self):
        self.assertEqual(_quote_mailbox(b"[Gmail]/Sent Mail"), b'"[Gmail]/Sent Mail"')

    def test_already_quoted_name_is_unchanged(self):
        self.assertEqual(_quote_mailbox(b'"[Gmail]/Sent Mail"'), b'"[Gmail]/Sent Mail"')

    def test_embedded_quote_and_backslash_are_escaped(self):
        self.assertEqual(_quote_mailbox(b'we"ird\\name'), b'"we\\"ird\\\\name"')

    def test_empty_and_none_pass_through(self):
        self.assertEqual(_quote_mailbox(b""), b"")
        self.assertIsNone(_quote_mailbox(None))


class PollForMessageIdTests(unittest.TestCase):
    """B-F5: polling falls back to ``SEARCH ALL`` when the header search is empty."""

    def test_all_fallback_finds_message_when_header_search_is_empty(self):
        """The ``HEADER Message-ID`` probe returns nothing, so ``ALL`` is scanned.

        Gmail (and others) can treat ``SEARCH HEADER Message-ID`` as a no-op and
        return no UIDs even for a delivered message; the payload must still be
        found by scanning recent UIDs from the ``ALL`` search.
        """
        message_id = "<abc123@example.com>"
        payload = b"Message-ID: <abc123@example.com>\r\nSubject: hi\r\n\r\nbody"
        imap = _FakeIMAP(
            header_uids=b"",              # header search finds nothing
            all_uids=b"1 2 3",            # fallback sees three recent messages
            payloads={b"3": payload},     # only the newest matches the needle
        )
        raw = _poll_for_message_id(imap, message_id, timeout=1, interval=0)

        self.assertEqual(raw, payload)
        criteria = [call[1][:1] for call in imap.search_calls]
        self.assertIn(("HEADER",), criteria, "header search should have been attempted")
        self.assertIn(("ALL",), criteria, "ALL fallback should have been used")

    def test_zero_timeout_returns_none_without_sleeping(self):
        """``timeout=0`` gives up on the first pass and never calls ``time.sleep``.

        Both searches come back empty, so the deadline check fires immediately.
        ``time.sleep`` is patched specifically so the test cannot really wait.
        """
        imap = _FakeIMAP(header_uids=b"", all_uids=b"")
        with mock.patch("time.sleep") as sleep:
            raw = _poll_for_message_id(imap, "<missing@example.com>", timeout=0)

        self.assertIsNone(raw)
        sleep.assert_not_called()


if __name__ == "__main__":  # pragma: no cover - convenience runner
    unittest.main()
