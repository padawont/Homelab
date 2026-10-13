"""Inbound mailbox monitoring for the cv sender worker.

Polls the applicant mailbox over IMAP, matches replies to previously sent
messages through ``In-Reply-To`` / ``References``, detects non-delivery reports
(bounces) and can emit a daily digest. Every mutation goes through the shared
:class:`state.State` store, so repeated polls stay idempotent.

Importing this module performs no I/O.
"""

from __future__ import annotations

import imaplib
import logging
import os
import re
import smtplib
from datetime import datetime, timezone
from email import message_from_bytes
from email.message import EmailMessage, Message
from email.utils import formatdate, parseaddr, parsedate_to_datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from state import State

logger = logging.getLogger(__name__)

PASSWORD_ENV = "GMAIL_APP_PASSWORD"

_MESSAGE_ID_RE = re.compile(r"<[^<>@\s]+@[^<>\s]+>")
_FINAL_RECIPIENT_RE = re.compile(
    r"Final-Recipient:\s*(?:rfc822;)?\s*([^\s;<>]+@[^\s;<>]+)", re.IGNORECASE
)
_NDR_LOCAL_PARTS = {"mailer-daemon", "postmaster"}
_NDR_SUBJECT_MARKERS = (
    "undelivered mail",
    "delivery status notification",
    "mail delivery failed",
    "delivery failure",
    "failure notice",
    "returned mail",
)


def _password() -> str:
    value = os.environ.get(PASSWORD_ENV)
    if not value:
        raise RuntimeError(f"{PASSWORD_ENV} environment variable is not set")
    return value


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _message_date(message: Message) -> str:
    raw = message.get("Date")
    if raw:
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            parsed = None
        if parsed is not None:
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return _utc_stamp()


def _reference_ids(message: Message) -> list[str]:
    ids: list[str] = []
    for header in ("In-Reply-To", "References"):
        for value in message.get_all(header, []):
            ids.extend(_MESSAGE_ID_RE.findall(value))
    return ids


def _is_bounce(message: Message) -> bool:
    """Heuristically decide whether ``message`` is a non-delivery report."""
    sender = parseaddr(message.get("From", ""))[1].lower()
    if sender and sender.split("@")[0] in _NDR_LOCAL_PARTS:
        return True
    if (message.get_content_type() or "").lower() == "multipart/report":
        for key, value in message.get_params() or []:
            if str(key).lower() == "report-type" and "delivery" in str(value).lower():
                return True
    subject = (message.get("Subject") or "").lower()
    return any(marker in subject for marker in _NDR_SUBJECT_MARKERS)


def _failed_recipient(message: Message) -> str | None:
    """Extract the recipient that bounced from an NDR, if present."""
    for part in message.walk():
        if part.get_content_type() == "message/delivery-status":
            payload = part.get_payload()
            if isinstance(payload, list):
                for section in payload:
                    match = _FINAL_RECIPIENT_RE.search(section.as_string())
                    if match:
                        return match.group(1).strip().lower()
    match = _FINAL_RECIPIENT_RE.search(message.as_string())
    if match:
        return match.group(1).strip().lower()
    return None


def _send_notification(config: dict, subject: str, body: str) -> None:
    account = config.get("account", {})
    notify = str(account.get("notify_email") or "").strip()
    if not notify:
        logger.warning("config.account.notify_email is not set; notification skipped")
        return
    sender = str(account.get("email") or "").strip()
    if not sender:
        raise ValueError("config.account.email is not set")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = notify
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=True)
    message.set_content(body)

    host = str(account.get("smtp_host", "smtp.gmail.com"))
    port = int(account.get("smtp_port", 587))
    with smtplib.SMTP(host, port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(sender, _password())
        smtp.send_message(message)


def _notify_reply(config: dict, reply: dict) -> None:
    subject = f"cv sender: reply from {reply.get('from') or 'unknown sender'}"
    body = (
        "A company replied to a cv sender enquiry.\n\n"
        f"From:    {reply.get('from', '')}\n"
        f"Subject: {reply.get('subject', '')}\n"
        f"Date:    {reply.get('date', '')}\n"
    )
    try:
        _send_notification(config, subject, body)
    except Exception:  # noqa: BLE001 - notification must not break polling
        logger.exception("failed to send reply notification")


def check_inbox(config: dict, state: "State") -> tuple[list[dict], list[dict]]:
    """Poll the mailbox once.

    Returns a ``(replies, bounces)`` tuple. Replies are matched against stored
    message ids; bounces are detected from NDR headers and mapped back to the
    failed recipient address.
    """
    account = config.get("account", {})
    host = account.get("imap_host")
    user = account.get("email")
    if not host or not user:
        raise ValueError("config.account.imap_host and config.account.email are required")

    sent_index = {
        row["message_id"]: row
        for row in state.iter_sent()
        if row.get("message_id")
    }

    replies: list[dict] = []
    bounces: list[dict] = []

    client = imaplib.IMAP4_SSL(host)
    try:
        client.login(user, _password())
        folder = account.get("imap_folder", "INBOX")
        client.select(folder)
        typ, data = client.search(None, "UNSEEN")
        if typ != "OK":
            logger.warning("IMAP search returned %s; skipping inbox check", typ)
            return replies, bounces

        for num in data[0].split():
            typ, payload = client.fetch(num, "(RFC822)")
            if typ != "OK" or not payload or not isinstance(payload[0], tuple):
                continue
            message = message_from_bytes(payload[0][1])

            if _is_bounce(message):
                failed_email = _failed_recipient(message)
                if failed_email:
                    state.mark_bounce(failed_email)
                bounces.append(
                    {
                        "email": failed_email or "",
                        "subject": message.get("Subject", ""),
                        "date": _message_date(message),
                    }
                )
                continue

            matched = next(
                (mid for mid in _reference_ids(message) if mid in sent_index), None
            )
            if matched is None:
                continue
            if sent_index[matched].get("reply_at"):
                continue

            replied_at = _message_date(message)
            state.mark_reply(matched, replied_at)
            reply = {
                "message_id": matched,
                "from": parseaddr(message.get("From", ""))[1],
                "subject": message.get("Subject", ""),
                "date": replied_at,
            }
            replies.append(reply)
            _notify_reply(config, reply)
    finally:
        try:
            client.logout()
        except Exception:  # pragma: no cover - best-effort teardown
            logger.debug("IMAP logout failed", exc_info=True)

    if replies or bounces:
        logger.info("inbox check: %d replies, %d bounces", len(replies), len(bounces))
    return replies, bounces


def send_digest(config: dict, state: "State") -> None:
    """Send a daily summary of sent / replied / bounced counts."""
    rows = state.iter_sent()
    sent_total = len(rows)
    sent_today = state.sent_today()
    replied = sum(1 for row in rows if row.get("reply_at"))
    bounced = sum(1 for row in rows if row.get("bounce"))

    body = (
        "cv sender — daglig digest\n\n"
        f"Sendt i alt: {sent_total}\n"
        f"Sendt i dag: {sent_today}\n"
        f"Svar:        {replied}\n"
        f"Bounces:     {bounced}\n"
    )
    _send_notification(config, "cv sender — daglig digest", body)
    logger.info(
        "digest sent: %d total, %d today, %d replies, %d bounces",
        sent_total,
        sent_today,
        replied,
        bounced,
    )
