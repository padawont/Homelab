"""Outbound email for the cv sender worker.

Builds a personalised erhvervspraktik enquiry with the CV attached and delivers
it over SMTP (STARTTLS). The Gmail App Password (``GMAIL_APP_PASSWORD``) and the
signature name/phone (``CV_SENDER_SIGNATURE_NAME`` / ``CV_SENDER_SIGNATURE_PHONE``)
are read from environment variables only — they are never taken from the config
dict and the password is never logged.

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
SIGNATURE_NAME_ENV = "CV_SENDER_SIGNATURE_NAME"
SIGNATURE_PHONE_ENV = "CV_SENDER_SIGNATURE_PHONE"


def _subject() -> str:
    return SUBJECT_PATH.read_text(encoding="utf-8").strip()


def _signature() -> tuple[str, str]:
    name = (os.environ.get(SIGNATURE_NAME_ENV) or "").strip()
    phone = (os.environ.get(SIGNATURE_PHONE_ENV) or "").strip()
    if not name or not phone:
        raise RuntimeError(
            f"refusing to send: {SIGNATURE_NAME_ENV} and {SIGNATURE_PHONE_ENV} must both be set"
        )
    return name, phone


def _body(company: str) -> str:
    name, phone = _signature()
    template = BODY_PATH.read_text(encoding="utf-8")
    return template.format(company=company, signature_name=name, signature_phone=phone)


def send_email(config: dict, row: dict, cv_path: str) -> str | None:
    """Send one enquiry for ``row`` with ``cv_path`` attached.

    Returns the generated ``Message-ID`` on success, or ``None`` when the row has
    no recipient address or when ``dry_run`` is true. Configuration and transport
    errors are raised.
    """
    if bool(config.get("dry_run", True)):
        logger.info("dry_run is true; refusing to send to %s", row.get("name"))
        return None

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
    message.set_content(_body(str(row.get("name", ""))))

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
