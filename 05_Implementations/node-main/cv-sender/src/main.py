"""Command line entry point for the cv sender worker.

Modes
-----
``--discover``
    Inspect the TARGIT view (debug selectors).
``--inspect``
    Print the parsed rows.
``--dry-run``
    Scrape, filter and validate only; write the preview CSV and send nothing.
``--pilot [N]``
    Send at most ``N`` enquiries (default ``config['pilot_count']``). When
    ``config['dry_run']`` is true no mail is sent; the run validates candidates
    and writes the preview CSV instead.
``worker``
    Long-running loop that checks the inbox and sends within the daily cap.
    When ``config['dry_run']`` is true, the worker performs a single dry-run
    validation pass at startup (scrape, filter, validate, write the preview
    CSV) and then idles: no further scraping, no inbox check, no send batch, no
    daily digest and no reply notifications, so no mail leaves the container.

Run as ``python -m src.main <mode>``. Importing this module performs no I/O.
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("cv_sender")

ROW_FIELDS = (
    "name",
    "postdistrikt",
    "branche",
    "address",
    "email",
    "phone",
    "employees",
)
PREVIEW_FIELDS = (*ROW_FIELDS, "status", "reason")


# -- helpers ---------------------------------------------------------------
def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _ensure_src_on_path() -> None:
    """Make sibling modules importable as top-level names.

    The contract imports siblings as ``from config import ...`` while the CLI is
    invoked as ``python -m src.main``. Adding ``src/`` to ``sys.path`` keeps both
    true without needing a package ``__init__.py``.
    """
    src_dir = str(Path(__file__).resolve().parent)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def _state_db(config: dict) -> str:
    value = config.get("state", {}).get("db_path")
    return str(value) if value else "state.db"


def _preview_csv(config: dict) -> Path:
    return Path(config["paths"]["preview_csv"])


def _data_dir(config: dict) -> Path:
    """Return the export directory, preferring ``paths.data_dir``.

    ``scraper.export_companies`` refuses to write outside ``paths.data_dir``, so
    that key wins when present; otherwise fall back to the preview CSV's parent.
    """
    value = config.get("paths", {}).get("data_dir")
    if value:
        return Path(str(value))
    return _preview_csv(config).parent


def _cv_path(config: dict) -> str | None:
    value = config.get("email", {}).get("attachment")
    return str(value) if value else None


def _format_row(row: dict) -> str:
    return " | ".join(f"{field}={row.get(field, '')}" for field in ROW_FIELDS)


def _load_rows(config: dict) -> list[dict]:
    """Scrape the TARGIT export, normalise it, and apply the Branche filter.

    The export is downloaded unfiltered (the TARGIT slicer is not scriptable),
    so the Branche selection from ``filters.branche_query`` is applied here in
    Python after the workbook is read.
    """
    from normalize import filter_rows, read_rows
    from scraper import export_companies

    out_dir = _data_dir(config)
    out_dir.mkdir(parents=True, exist_ok=True)
    workbook = export_companies(config, str(out_dir))
    rows = read_rows(workbook)
    branche_query = (config.get("filters") or {}).get("branche_query", "") or ""
    rows = filter_rows(rows, branche_query)
    logger.info("loaded %d rows from %s", len(rows), workbook)
    return rows


# -- modes -----------------------------------------------------------------
def _run_discover(config: dict) -> int:
    import scraper

    discover = getattr(scraper, "discover", None)
    if callable(discover):
        discover(config)
        return 0

    logger.info("scraper.discover() unavailable; running an export as a smoke test")
    out_dir = _data_dir(config)
    out_dir.mkdir(parents=True, exist_ok=True)
    workbook = Path(scraper.export_companies(config, str(out_dir)))
    size = workbook.stat().st_size if workbook.exists() else 0
    logger.info("export written to %s (%d bytes)", workbook, size)
    return 0


def _run_inspect(config: dict) -> int:
    rows = _load_rows(config)
    for row in rows:
        logger.info("%s", _format_row(row))
    logger.info("inspected %d rows", len(rows))
    return 0


def _run_dry_run(config: dict) -> int:
    from state import State
    from validate import classify

    rows = _load_rows(config)
    preview = _preview_csv(config)
    preview.parent.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    state = State(_state_db(config))
    state.init()
    try:
        with preview.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=PREVIEW_FIELDS)
            writer.writeheader()
            for row in rows:
                status, reason = classify(row, config)
                state.record(row, status, reason)
                counts[status] = counts.get(status, 0) + 1
                writer.writerow(
                    {
                        **{field: row.get(field, "") for field in ROW_FIELDS},
                        "status": status,
                        "reason": reason,
                    }
                )
    finally:
        state.close()

    logger.info("dry run: %d rows written to %s", len(rows), preview)
    for status, count in sorted(counts.items()):
        logger.info("  %-22s %d", status, count)
    return 0


def _send_batch(config: dict, limit: int | None) -> int:
    if bool(config.get("dry_run", True)):
        logger.info("dry_run is true; skipping send batch")
        return 0

    from enrich import enrich
    from sender import send_email
    from state import State
    from validate import classify

    cv_path = _cv_path(config)
    if not cv_path:
        logger.error("config.email.attachment is not set; refusing to send")
        return 1

    rate = config.get("rate", {})
    daily_cap = int(rate.get("daily_cap", 400))
    delay = float(rate.get("delay_seconds", 0) or 0)

    rows = _load_rows(config)
    enrichment_cache: dict[str, object] = {}
    sent = 0

    state = State(_state_db(config))
    state.init()
    try:
        remaining = daily_cap - state.sent_today()
        if remaining <= 0:
            logger.info("daily cap of %d already reached; nothing to send", daily_cap)
            return 0

        for row in rows:
            if limit is not None and sent >= limit:
                break
            if sent >= remaining:
                logger.info("daily cap of %d reached; stopping batch", daily_cap)
                break

            name = str(row.get("name", ""))
            postdistrikt = str(row.get("postdistrikt", ""))
            if state.already_sent(name, postdistrikt):
                continue

            if not row.get("email"):
                found = enrich(row, config, enrichment_cache)
                if found:
                    row["email"] = found

            status, reason = classify(row, config)
            state.record(row, status, reason)
            if status != "valid":
                logger.info("skipped %s: %s (%s)", name, status, reason)
                continue

            try:
                message_id = send_email(config, row, cv_path)
            except Exception:  # noqa: BLE001 - keep the batch going
                logger.exception("failed to send to %s", name)
                continue
            if not message_id:
                continue

            state.mark_sent(name, postdistrikt, message_id, _utc_now())
            sent += 1
            logger.info("sent %d enquiry(ies)", sent)
            if delay and (limit is None or sent < limit):
                time.sleep(delay)
    finally:
        state.close()

    logger.info("send batch finished: %d sent", sent)
    return 0


def _run_pilot(config: dict, limit: int | None) -> int:
    if limit is None or limit < 0:
        limit = int(config.get("pilot_count", 3))
    if bool(config.get("dry_run", True)):
        logger.info("config dry_run is true; pilot will validate but not send")
        return _run_dry_run(config)
    return _send_batch(config, limit=limit)


def _run_worker(config: dict) -> int:
    from monitor import check_inbox, send_digest
    from state import State

    poll_seconds = max(1.0, float(config.get("rate", {}).get("poll_seconds", 300) or 300))
    dry_run = bool(config.get("dry_run", True))
    logger.info("worker started (poll every %.0fs)", poll_seconds)

    if dry_run:
        logger.info("dry_run is true; starting in dry-run mode")

    last_digest_day: str | None = None
    dry_run_done = False
    try:
        while True:
            try:
                if dry_run:
                    if not dry_run_done:
                        dry_run_done = True
                        _run_dry_run(config)
                        logger.info(
                            "dry-run preview written; worker is now idling "
                            "(no further scraping or mail)"
                        )
                else:
                    state = State(_state_db(config))
                    state.init()
                    try:
                        replies, bounces = check_inbox(config, state)
                        if replies or bounces:
                            logger.info(
                                "inbox: %d replies, %d bounces", len(replies), len(bounces)
                            )
                    except Exception:  # noqa: BLE001 - a poll failure must not kill the loop
                        logger.exception("inbox check failed")
                    finally:
                        state.close()

                    _send_batch(config, limit=None)

                    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                    if today != last_digest_day:
                        state = State(_state_db(config))
                        state.init()
                        try:
                            send_digest(config, state)
                        except Exception:  # noqa: BLE001
                            logger.exception("digest failed")
                        finally:
                            state.close()
                        last_digest_day = today
            except Exception:  # noqa: BLE001 - a poll failure must not kill the loop
                logger.exception("poll failed")

            time.sleep(poll_seconds)
    except KeyboardInterrupt:  # pragma: no cover - interactive shutdown
        logger.info("worker interrupted; shutting down")
        return 0


# -- CLI -------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.main",
        description=(
            "cv sender worker — scrape, validate and email erhvervspraktik enquiries"
        ),
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["worker"],
        help="run the long-running send/monitor loop",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="scrape, filter and validate; write the preview CSV; send nothing",
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="inspect the TARGIT view (debug selectors)",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="print the parsed rows",
    )
    parser.add_argument(
        "--pilot",
        nargs="?",
        const=-1,
        type=int,
        metavar="N",
        help="send at most N enquiries (default: config['pilot_count'])",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="logging level (default: INFO)",
    )
    return parser


def _resolve_mode(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    """Return the single selected mode, or exit via ``parser.error``.

    Explicit flags win over the default ``worker`` positional so the container
    ENTRYPOINT (``worker``) can be overridden by ``--dry-run`` / ``--pilot`` from
    the Makefile, e.g. ``python -m src.main worker --pilot``.
    """
    flag_modes: list[str] = []
    if args.discover:
        flag_modes.append("discover")
    if args.inspect:
        flag_modes.append("inspect")
    if args.dry_run:
        flag_modes.append("dry_run")
    if args.pilot is not None:
        flag_modes.append("pilot")

    if len(flag_modes) > 1:
        parser.error("choose at most one of: --discover, --inspect, --dry-run, --pilot")
    if flag_modes:
        return flag_modes[0]
    if args.command == "worker":
        return "worker"
    parser.error("select a mode: worker, --discover, --inspect, --dry-run or --pilot")
    raise AssertionError("unreachable")  # pragma: no cover - parser.error exits


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    mode = _resolve_mode(args, parser)

    _ensure_src_on_path()
    from config import load_config

    config = load_config()

    if mode == "worker":
        return _run_worker(config)
    if mode == "discover":
        return _run_discover(config)
    if mode == "inspect":
        return _run_inspect(config)
    if mode == "dry_run":
        return _run_dry_run(config)
    return _run_pilot(config, args.pilot)


if __name__ == "__main__":
    sys.exit(main())
