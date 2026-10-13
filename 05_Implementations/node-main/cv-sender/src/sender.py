"""Outbound email for the cv sender worker.

Builds a personalised erhvervspraktik enquiry with the CV attached and delivers
it over SMTP (STARTTLS). The Gmail App Password is read from the
``GMAIL_APP_PASSWORD`` environment variable only — it is never taken from the
config dict and never logged.

Importing this module performs no I/O; the templates are read when a message is
actually built.
"""

from __future__ import annotations

import logging
import mimetypes
import os
import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
SUBJECT_PATH = TEMPLATE_DIR / "subject.txt"
BODY_PATH = TEMPLATE_DIR / "body.txt"

PASSWORD_ENV = "GMAIL_APP_PASSWORD"


def _subject() -> str:
    return SUBJECT_PATH.read_text(encoding="utf-8").strip()


def _body(config: dict, company: str) -> str:
    email_cfg = config.get("email", {})
    template = BODY_PATH.read_text(encoding="utf-8")
    return template.format(
        company=company,
        signature_name=email_cfg.get("signature_name", ""),
        signature_phone=email_cfg.get("signature_phone", ""),
    )


def send_email(config: dict, row: dict, cv_path: str) -> str | None:
    """Send one enquiry for ``row`` with ``cv_path`` attached.

    Returns the generated ``Message-ID`` on success, or ``None`` when the row has
    no recipient address or when ``dry_run`` is true. Configuration and transport
    errors are raised.
    """
    if bool(config.get("dry_run", True)):
        logger.info("dry_run is true; refusing to send to %s", row.get("name"))
        return None

    email_cfg = config.get("email", {})
    signature_name = str(email_cfg.get("signature_name") or "").strip()
    signature_phone = str(email_cfg.get("signature_phone") or "").strip()
    if not signature_name or not signature_phone:
        raise ValueError(
            "refusing to send: config.email.signature_name and "
            "config.email.signature_phone must both be set"
        )

    recipient = str(row.get("email") or "").strip()
    if not recipient:
        logger.warning("skipping send: row has no email address")
        return None

    account = config.get("account", {})
    sender = str(account.get("email") or "").strip()
    if not sender:
        raise ValueError("refusing to send: config.account.email is not set")

    password = os.environ.get(PASSWORD_ENV)
    if not password:
        raise RuntimeError(f"{PASSWORD_ENV} environment variable is not set")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = _subject()
    message["Date"] = formatdate(localtime=True)
    message_id = make_msgid(domain=sender.rpartition("@")[2] or None)
    message["Message-ID"] = message_id
    message.set_content(_body(config, str(row.get("name", ""))))

    cv = Path(cv_path)
    content_type, _encoding = mimetypes.guess_type(cv.name)
    maintype, _, subtype = (content_type or "application/octet-stream").partition("/")
    message.add_attachment(
        cv.read_bytes(),
        maintype=maintype or "application",
        subtype=subtype or "octet-stream",
        filename=cv.name,
    )

    host = str(account.get("smtp_host", "smtp.gmail.com"))
    port = int(account.get("smtp_port", 587))
    with smtplib.SMTP(host, port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(sender, password)
        smtp.send_message(message)

    logger.info("sent enquiry to %s", row.get("name", "unknown company"))
    return message_id
