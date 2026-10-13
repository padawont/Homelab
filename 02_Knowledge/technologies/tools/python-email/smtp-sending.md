---
title: "Python stdlib — sending mail with smtplib and EmailMessage"
status: draft
author: "padawont"
date: 2026-10-12
tags: [python, email, smtp, smtplib, emailmessage]
sources:
  - url: "https://docs.python.org/3/library/email.examples.html"
    title: "email: Examples"
  - url: "https://docs.python.org/3/library/smtplib.html"
    title: "smtplib — SMTP protocol client"
  - url: "https://docs.python.org/3/library/email.message.html"
    title: "email.message — Representing an email message"
  - url: "https://docs.python.org/3/library/email.html"
    title: "email — An email and MIME handling package"
last_audit_date: 2026-10-12
related_docs:
  - "./05_Implementations/node-main/cv-sender/overview.md"
  - "./02_Knowledge/technologies/tools/python-email/imap-monitoring.md"
---

# Python stdlib — sending mail with smtplib and EmailMessage

## Overview

Sending mail from Python needs no third-party dependency: the standard library splits the job in two. The `email` package **builds** the message — headers, body, MIME structure — into an `EmailMessage` object. The `smtplib` module **sends** that object to a mail server over SMTP, using `starttls()` for transport encryption and `login()` for authentication. `send_message()` serialises the `EmailMessage` for you, so the two halves never need to be wired together by hand.

This is the pattern used by the cv-sender implementation (`./05_Implementations/node-main/cv-sender/overview.md`).

## Details

### Build the message with `EmailMessage`

`EmailMessage` (from `email.message`) replaces the older `MIMEText`/`MIMEMultipart` dance. Set headers like dict keys, then attach content:

- `set_content(body)` — plain-text (or HTML) body.
- `add_alternative(html, subtype="html")` — add an HTML version alongside the plain text; the receiving client picks.
- `add_attachment(data, maintype=..., subtype=..., filename=...)` — attach bytes; the library derives the MIME structure and encoding.
- Header assignment — `msg["Subject"]`, `msg["From"]`, `msg["To"]`, `msg["Cc"]`.

### Send with `smtplib.SMTP`

`smtplib.SMTP(host, port)` opens a connection. For submission ports (typically 587, sometimes 465 with implicit TLS via `SMTP_SSL`) you call `starttls()` to upgrade the plaintext connection before authenticating, then `login(user, password)`. `send_message(msg)` does the send; `with` on the SMTP object closes the connection cleanly.

Example — abstract:

```python
import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg["Subject"] = "Example subject"
msg["From"] = "sender@example.com"
msg["To"] = "recipient@example.com"
msg.set_content("Plain-text body.")
msg.add_alternative("<p>HTML body.</p>", subtype="html")
msg.add_attachment(b"file contents", maintype="application",
                   subtype="octet-stream", filename="example.bin")

with smtplib.SMTP("smtp.example.com", 587) as smtp:
    smtp.starttls()
    smtp.login("sender@example.com", "app-password")
    smtp.send_message(msg)
```

### Deliverability basics

> **General guidance — not from the Python stdlib docs.** The points below are
> operational advice about mail providers; verify them against your provider's
> current policy.

- **App passwords, not account passwords.** Providers with 2FA (e.g. Gmail) reject the normal account password; generate a dedicated app password and store it as a secret, never in source.
- **Sending caps and rate limits.** Consumer providers impose daily send quotas and per-message recipient limits. Exceeding them results in throttling or account flags — batch and back off rather than blasting.
- **Sender alignment.** `From` should match the authenticated account (or a verified alias/domain); mismatched senders are frequently marked spam or rejected outright.
- **TLS first.** Always upgrade with `starttls()` (or use `SMTP_SSL`) before `login()`, otherwise credentials cross the wire in the clear.

### Division of responsibility

Keep the separation in mind when debugging: a malformed message or missing MIME part is an `email` problem; a timeout, auth failure, or TLS error is an `smtplib`/server problem.

## Sources / Further Reading

- [email: Examples](https://docs.python.org/3/library/email.examples.html)
- [smtplib — SMTP protocol client](https://docs.python.org/3/library/smtplib.html)
- [email.message — Representing an email message](https://docs.python.org/3/library/email.message.html)
- [email — An email and MIME handling package](https://docs.python.org/3/library/email.html)
