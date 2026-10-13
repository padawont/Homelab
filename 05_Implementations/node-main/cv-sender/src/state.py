"""SQLite-backed, idempotent state store for the cv sender worker.

The store keeps one row per (company ``name``, ``postdistrikt``) pair and tracks
whether the enquiry was sent and how the conversation evolved (reply / bounce).
The ``UNIQUE(name, postdistrikt)`` constraint is what makes restarts safe: a
worker that comes back up can never send the same company twice.

Importing this module performs no I/O. The database file is only touched once a
method is called, and the tables are created by :meth:`State.init`.
"""

from __future__ import annotations

import logging
import sqlite3

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    postdistrikt TEXT    NOT NULL,
    branche      TEXT,
    email        TEXT,
    status       TEXT,
    reason       TEXT,
    message_id   TEXT,
    sent_at      TEXT,
    reply_at     TEXT,
    bounce       INTEGER NOT NULL DEFAULT 0,
    UNIQUE (name, postdistrikt)
);
CREATE INDEX IF NOT EXISTS idx_companies_message_id ON companies (message_id);
CREATE INDEX IF NOT EXISTS idx_companies_email ON companies (email);
"""

_SELECT_COLUMNS = (
    "id, name, postdistrikt, branche, email, status, reason, "
    "message_id, sent_at, reply_at, bounce"
)


class State:
    """Idempotent SQLite state for sent enquiries, replies and bounces."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    # -- lifecycle ---------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def init(self) -> None:
        """Create the schema if it does not exist yet (idempotent)."""
        conn = self._connect()
        conn.executescript(_SCHEMA)
        conn.commit()
        logger.debug("state initialised at %s", self.db_path)

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "State":
        self.init()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    # -- queries -----------------------------------------------------------
    def already_sent(self, name: str, postdistrikt: str) -> bool:
        """Return ``True`` when this company already has a sent message."""
        row = self._connect().execute(
            "SELECT sent_at, message_id FROM companies "
            "WHERE name = ? AND postdistrikt = ?",
            (name, postdistrikt),
        ).fetchone()
        if row is None:
            return False
        return row["sent_at"] is not None or row["message_id"] is not None

    def sent_today(self) -> int:
        """Count messages sent today (UTC), for the daily rate cap."""
        row = self._connect().execute(
            "SELECT COUNT(*) AS n FROM companies "
            "WHERE sent_at IS NOT NULL AND substr(sent_at, 1, 10) = date('now')"
        ).fetchone()
        return int(row["n"])

    def iter_sent(self) -> list[dict]:
        """Return every row that carries a ``message_id``."""
        rows = self._connect().execute(
            f"SELECT {_SELECT_COLUMNS} FROM companies "
            "WHERE message_id IS NOT NULL ORDER BY sent_at, id"
        ).fetchall()
        return [dict(row) for row in rows]

    # -- mutations ---------------------------------------------------------
    def record(self, row: dict, status: str, reason: str) -> None:
        """Upsert the classification for a company without clobbering send state."""
        conn = self._connect()
        conn.execute(
            """
            INSERT INTO companies (name, postdistrikt, branche, email, status, reason)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (name, postdistrikt) DO UPDATE SET
                branche = COALESCE(NULLIF(excluded.branche, ''), companies.branche),
                email   = COALESCE(NULLIF(excluded.email, ''), companies.email),
                status  = excluded.status,
                reason  = excluded.reason
            """,
            (
                str(row.get("name", "")),
                str(row.get("postdistrikt", "")),
                row.get("branche"),
                row.get("email"),
                status,
                reason,
            ),
        )
        conn.commit()

    def mark_sent(
        self, name: str, postdistrikt: str, message_id: str, sent_at: str
    ) -> None:
        """Record a successful send, creating the row if it does not exist yet."""
        conn = self._connect()
        conn.execute(
            """
            INSERT INTO companies (name, postdistrikt, message_id, sent_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (name, postdistrikt) DO UPDATE SET
                message_id = excluded.message_id,
                sent_at    = excluded.sent_at
            """,
            (name, postdistrikt, message_id, sent_at),
        )
        conn.commit()

    def mark_reply(self, message_id: str, reply_at: str) -> None:
        """Attach a reply timestamp to the sent message it answers."""
        conn = self._connect()
        cursor = conn.execute(
            "UPDATE companies SET reply_at = ? WHERE message_id = ?",
            (reply_at, message_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning("mark_reply: no sent row for the given message id")

    def mark_bounce(self, email: str) -> None:
        """Flag every row for a bounced recipient address."""
        conn = self._connect()
        cursor = conn.execute(
            "UPDATE companies SET bounce = 1 WHERE email COLLATE NOCASE = ?",
            (email,),
        )
        conn.commit()
        if cursor.rowcount == 0:
            logger.warning("mark_bounce: no row for the failed recipient")
