---
title: "Python stdlib — monitoring a mailbox with imaplib"
status: draft
author: "padawont"
date: 2026-10-12
tags: [python, email, imap, imaplib, monitoring]
sources:
  - url: "https://docs.python.org/3/library/imaplib.html"
    title: "imaplib — IMAP4 protocol client"
  - url: "https://docs.python.org/3/library/email.message.html"
    title: "email.message — Representing an email message"
  - url: "https://docs.python.org/3/library/email.html"
    title: "email — An email and MIME handling package"
last_audit_date: 2026-10-12
related_docs:
  - "./05_Implementations/node-main/cv-sender/overview.md"
  - "./02_Knowledge/technologies/tools/python-email/smtp-sending.md"
---

# Python stdlib — monitoring a mailbox with imaplib

## Overview

`imaplib` is the Python standard-library IMAP4 client. It lets a script log
into a mailbox, search for messages, fetch their raw RFC822 bytes, and hand
those bytes to the `email` package for parsing. Typical homelab use: watch a
`cv-sender` mailbox for replies and bounce notifications instead of polling a
web UI by hand.

Keeping this in the stdlib avoids extra dependencies; the trade-off is a
low-level protocol wrapper where you assemble search criteria and interpret
server responses yourself.

## Details

### Connect, log in, select a folder

Use `imaplib.IMAP4_SSL` so the session is TLS-wrapped. `login` authenticates
and `select("INBOX")` opens a mailbox (`readonly=True` keeps a monitor from
setting `\Seen`). `select` returns server status plus the message count.

```python
import imaplib

conn = imaplib.IMAP4_SSL("imap.example.com")
conn.login("user@example.com", "app-password")
status, count = conn.select("INBOX", readonly=True)
```

### Search with UIDs, not message numbers

`search` takes an IMAP search string and returns message *sequence numbers*.
The `imaplib` docs recommend **UIDs** instead: sequence numbers shift as mail
arrives or is deleted mid-session, while UIDs stay stable. Use `uid` for all
follow-up operations.

```python
status, data = conn.uid("search", None, "UNSEEN", "FROM", "alice@example.com")
uids = data[0].split()          # e.g. [b'4211', b'4212']
```

Criteria combine like IMAP: `'SINCE', '01-Oct-2026'`,
`'HEADER', 'In-Reply-To', '<id@example.com>'`, `'SUBJECT', '"Re:"'`.

### Fetch the raw message

`fetch` retrieves the body. Fetch `RFC822` (or `BODY.PEEK[]`, which avoids
setting `\Seen`) for untouched bytes, then parse with the `email` package. The
docs warn a FETCH response may include **unsolicited data** beyond what you
asked for, so match the literal markers instead of assuming a tuple shape.

```python
status, data = conn.uid("fetch", uid, "(BODY.PEEK[])")
raw = next(part[1] for part in data if isinstance(part, tuple))
```

### Parse with message_from_bytes / BytesParser

`email.message_from_bytes` returns an `email.message.Message`; use
`BytesParser` with `policy=default` for the modern API. Headers like `From`,
`Subject`, and `Message-ID` come back as strings; multipart and non-ASCII
payloads decode lazily.

```python
from email import message_from_bytes

msg = message_from_bytes(raw)
print(msg["From"], msg["Subject"], msg["Message-ID"])
```

### Matching replies and detecting bounces

Every reply carries threading headers pointing back at the original:

- **`In-Reply-To`** — `Message-ID` of the message being replied to.
- **`References`** — the full chain of ancestor `Message-ID`s.

Compare those against the `Message-ID` recorded when you sent the mail. A
reply's `In-Reply-To` equals your original ID; its `References` contains that
ID somewhere in the chain.

Bounces arrive as ordinary messages, usually from `MAILER-DAEMON@…` or the
postmaster. **Heuristic — not sourced from the Python stdlib docs.** Detect them
from headers and body:

- `From:` is `MAILER-DAEMON`/`postmaster`, or the envelope is `<>`.
- `Subject:` starts with `Undelivered Mail Returned to Sender` or
  `Delivery Status Notification`.
- Body is typically `multipart/report; report-type=delivery-status`, so check
  `Content-Type` and parse the `message/delivery-status` part for the failed
  recipient and status code.

```python
def is_bounce(msg):
    if msg.get_content_type() == "multipart/report":
        return True
    sender = (msg["From"] or "").lower()
    subject = (msg["Subject"] or "").lower()
    return "mailer-daemon" in sender or "undelivered" in subject
```

The `In-Reply-To`/`References` comparison is the reliable path for real
replies; bounce heuristics are best-effort since formats vary by mail server.

### Disconnect

Close the mailbox before logging out so the server releases the selection, and
wrap the session in `try/finally` so a failure still logs out:

```python
conn.close()
conn.logout()
```

## Sources / Further Reading

- imaplib — IMAP4 protocol client — https://docs.python.org/3/library/imaplib.html
- email.message — Representing an email message — https://docs.python.org/3/library/email.message.html
- email — An email and MIME handling package — https://docs.python.org/3/library/email.html
