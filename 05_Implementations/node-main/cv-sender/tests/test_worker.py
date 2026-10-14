"""``main._run_worker`` loop tests for the cv sender worker (issue #632).

These tests pin the worker's two operating modes without a mailbox, a network or
a real sleep:

* ``dry_run: true`` must run ``main._run_dry_run`` exactly once and then idle —
  no inbox check, no send batch, no digest (so no mail can leave the container).
* ``dry_run: false`` must poll in the order ``check_inbox -> _send_batch ->
  send_digest`` and emit the digest at most once per UTC day.
* a digest that fails to send must be retried on the next poll, and the day is
  marked as done only on success — so the attempt is neither lost nor spent
  twice.

``time.sleep`` is patched with a ``KeyboardInterrupt`` so the otherwise infinite
loop exits after a deterministic number of polls; ``_run_worker`` catches it and
returns ``0``. The live-mode test points ``state.db_path`` at a temporary
directory, never the repository's own state database.

Importing ``_helpers`` first puts ``src`` on ``sys.path`` and installs the
Playwright stub, matching the import contract used by ``test_flows.py``.
"""

import os
import tempfile
import unittest
from unittest import mock

import _helpers  # noqa: F401  # side effect: src on sys.path + Playwright stub

import main
import monitor


class RunWorkerTests(unittest.TestCase):
    """Deterministic coverage of the worker loop's branching and ordering."""

    def test_run_worker_dry_run_calls_only_the_dry_run_pass(self):
        """Dry-run worker: one validation pass, then idle with no polling.

        ``_run_dry_run`` is patched so the test does not scrape or write a
        preview CSV; ``check_inbox``/``send_digest`` are patched on the
        ``monitor`` module (``_run_worker`` binds them with a function-local
        ``from monitor import ...``) while ``_run_dry_run``/``_send_batch`` are
        patched on ``main`` (module-level names). ``time.sleep`` raises
        ``KeyboardInterrupt`` immediately, so exactly one loop iteration runs.
        """
        config = {"dry_run": True, "rate": {"poll_seconds": 1}}

        with mock.patch.object(main, "_run_dry_run") as run_dry_run, \
                mock.patch.object(main, "_send_batch") as send_batch, \
                mock.patch.object(monitor, "check_inbox") as check_inbox, \
                mock.patch.object(monitor, "send_digest") as send_digest, \
                mock.patch.object(main.time, "sleep", side_effect=KeyboardInterrupt):
            result = main._run_worker(config)

        self.assertEqual(result, 0)
        run_dry_run.assert_called_once_with(config)
        send_batch.assert_not_called()
        check_inbox.assert_not_called()
        send_digest.assert_not_called()

    def test_run_worker_live_poll_order_and_daily_digest(self):
        """Live worker: two same-day polls send the digest exactly once.

        ``time.sleep`` returns ``None`` on the first poll and raises
        ``KeyboardInterrupt`` on the second, so exactly two iterations run. Each
        poll must call ``check_inbox`` then ``_send_batch``; the digest is sent
        only on the first poll because the UTC day has not changed. A call log
        records the relative order, which also proves the digest fires *after*
        the batch rather than before it.
        """
        calls: list[str] = []

        def fake_check_inbox(_config, _state):
            calls.append("check_inbox")
            return [], []

        def fake_send_batch(_config, limit=None):
            calls.append("send_batch")
            return 0

        def fake_send_digest(_config, _state):
            calls.append("digest")

        with tempfile.TemporaryDirectory(prefix="cv-sender-worker-") as tmp:
            config = {
                "dry_run": False,
                "rate": {"poll_seconds": 1},
                "state": {"db_path": os.path.join(tmp, "state.db")},
            }

            with mock.patch.object(monitor, "check_inbox", side_effect=fake_check_inbox) as check_inbox, \
                    mock.patch.object(main, "_send_batch", side_effect=fake_send_batch), \
                    mock.patch.object(monitor, "send_digest", side_effect=fake_send_digest) as send_digest, \
                    mock.patch.object(main.time, "sleep", side_effect=[None, KeyboardInterrupt]):
                result = main._run_worker(config)

        self.assertEqual(result, 0)
        self.assertEqual(
            calls,
            ["check_inbox", "send_batch", "digest", "check_inbox", "send_batch"],
        )
        self.assertEqual(check_inbox.call_count, 2)
        self.assertEqual(send_digest.call_count, 1)

    def test_run_worker_retries_digest_after_failure(self):
        """A failed digest is retried next poll, then never again that same day.

        ``send_digest`` raises on the first poll and succeeds on the second.
        ``_run_worker`` records ``last_digest_day`` only *after* a successful
        send, so a failed attempt must not consume the day: the second poll has
        to retry the digest. Once that retry succeeds the third (still
        same-day) poll must not attempt it a third time. This pins the
        ``last_digest_day``-only-on-success fix in ``src/main.py``: without it
        the digest would never be retried after a failure
        (``send_digest.call_count == 1``); if the day were instead recorded
        *before* the send it would be retried on every poll
        (``call_count == 3``).

        ``time.sleep`` returns ``None`` twice and then raises
        ``KeyboardInterrupt``, so exactly three same-day polls run before the
        loop exits with ``0``. ``check_inbox`` and ``_send_batch`` are patched
        so no mailbox, network or scrape is touched, and ``state.db_path``
        points at a throwaway temp database.
        """
        with tempfile.TemporaryDirectory(prefix="cv-sender-worker-") as tmp:
            config = {
                "dry_run": False,
                "rate": {"poll_seconds": 1},
                "state": {"db_path": os.path.join(tmp, "state.db")},
            }

            with mock.patch.object(monitor, "check_inbox", return_value=([], [])) as check_inbox, \
                    mock.patch.object(main, "_send_batch"), \
                    mock.patch.object(
                        monitor,
                        "send_digest",
                        side_effect=[RuntimeError("smtp down"), None],
                    ) as send_digest, \
                    mock.patch.object(main.time, "sleep", side_effect=[None, None, KeyboardInterrupt]):
                result = main._run_worker(config)

        self.assertEqual(result, 0)
        self.assertEqual(send_digest.call_count, 2)
        self.assertEqual(check_inbox.call_count, 3)


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    unittest.main()
