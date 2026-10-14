"""``config.load_config`` validation tests for the cv sender worker (issue #632).

Covers the two config-contract changes in the hardening PR:

* ``rate.poll_seconds`` must be a positive number, and ``bool`` is explicitly
  rejected (``True`` is an ``int`` subclass in Python, so a naive
  ``isinstance(x, (int, float))`` check would wrongly accept it).
* ``email.signature_name`` / ``email.signature_phone`` are no longer required —
  the applicant identity now comes from the environment in ``sender.py``.

Fixtures are temporary YAML files; no network, no real config. Importing
``_helpers`` first puts ``src`` on ``sys.path`` (and installs the Playwright
stub) so ``from config import load_config`` resolves, matching ``test_flows.py``.
"""

import tempfile
import unittest
from pathlib import Path

import yaml

import _helpers  # noqa: F401  # side effect: src on sys.path + Playwright stub

from config import load_config


class _Omit:
    """Sentinel marking a field that must be absent from the fixture."""


_OMIT = _Omit()


def _write_config(
    directory,
    *,
    poll_seconds=_OMIT,
    account_email="sender@example.com",
    extra=None,
):
    """Write a minimal valid config to ``directory`` and return its path.

    Always includes the still-required ``account.email``,
    ``filters.postdistrikter`` and ``rate.daily_cap``. Passing ``_OMIT`` for a
    field omits it, so the required-field test can drop ``account.email``.
    """
    doc = {
        "account": {},
        "filters": {"postdistrikter": ["Aarhus C"]},
        "rate": {"daily_cap": 400},
    }
    if account_email is not _OMIT:
        doc["account"]["email"] = account_email
    if poll_seconds is not _OMIT:
        doc["rate"]["poll_seconds"] = poll_seconds
    if extra:
        doc.update(extra)

    path = Path(directory) / "config.yaml"
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")
    return str(path)


class PollSecondsValidationTests(unittest.TestCase):
    """``rate.poll_seconds`` must be a finite, positive, non-bool number.

    ``NaN``/``inf`` are written into the fixture YAML as ``.nan``/``.inf``,
    which ``yaml.safe_load`` parses back to the corresponding floats. They are
    rejected on finiteness: ``NaN <= 0`` and ``inf <= 0`` are both ``False``, so
    a naive ``poll <= 0`` check would wrongly accept both.
    """

    def test_poll_seconds_must_be_a_positive_number(self):
        """Reject non-numbers, non-positive, bool and non-finite values.

        ``"soon"`` is a string, ``0``/``-1`` are non-positive, ``True`` is a
        bool, and ``NaN``/``inf`` are non-finite — all must raise
        ``ValueError``. ``300`` (int) and ``12.5`` (float) are valid and must
        load. Each case gets a fresh YAML fixture so a failure names the
        offending value.
        """
        for bad in ("soon", 0, -1, True, float("nan"), float("inf")):
            with self.subTest(poll_seconds=bad):
                with tempfile.TemporaryDirectory(prefix="cv-sender-cfg-") as tmp:
                    path = _write_config(tmp, poll_seconds=bad)
                    with self.assertRaises(ValueError):
                        load_config(path)

        for good in (300, 12.5):
            with self.subTest(poll_seconds=good):
                with tempfile.TemporaryDirectory(prefix="cv-sender-cfg-") as tmp:
                    path = _write_config(tmp, poll_seconds=good)
                    loaded = load_config(path)
                self.assertEqual(loaded["rate"]["poll_seconds"], good)


class RequiredFieldTests(unittest.TestCase):
    """The required-field set changed with the signature move to the env."""

    def test_signature_fields_are_no_longer_required(self):
        """A config without ``email.signature_*`` loads cleanly.

        The signature name/phone are read from the environment by ``sender.py``,
        so their absence from the config must not raise ``ValueError``. The
        assertion below checks the ``email`` section round-trips intact, so the
        test actually fails if ``load_config`` starts rejecting a
        signature-less config. A bare ``assertIsInstance(loaded, dict)`` could
        never fail — ``load_config`` already raises unless the document is a
        mapping — and the removed ``assertNotIn("signature_*")`` checks were
        trivially true because the fixture never adds those keys.
        """
        with tempfile.TemporaryDirectory(prefix="cv-sender-cfg-") as tmp:
            path = _write_config(
                tmp,
                extra={"email": {"attachment": "/x/cv.pdf"}},
            )
            loaded = load_config(path)  # must not raise

        self.assertEqual(loaded["email"]["attachment"], "/x/cv.pdf")

    def test_missing_required_field_raises(self):
        """Dropping ``account.email`` still raises ``ValueError``.

        Guards against the hardening PR accidentally loosening the required-field
        validation while removing ``email.signature_*``.
        """
        with tempfile.TemporaryDirectory(prefix="cv-sender-cfg-") as tmp:
            path = _write_config(tmp, account_email=_OMIT)
            with self.assertRaises(ValueError):
                load_config(path)


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    unittest.main()
