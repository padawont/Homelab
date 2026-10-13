"""Normalize a TARGIT Excel export into typed company rows.

The export is a cross-tab with a handful of title/padding rows above the real
column header, so the header is located heuristically by matching Danish and
English column fragments. Field values are returned as strings; addresses are
reduced to the first e-mail address found in the cell.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

logger = logging.getLogger(__name__)

#: The exact key set every returned row carries.
ROW_KEYS: tuple[str, ...] = (
    "name",
    "postdistrikt",
    "branche",
    "address",
    "email",
    "phone",
    "employees",
)

#: Canonical field -> header fragments, ordered most-specific first so a broad
#: key such as ``name`` cannot steal a column from a narrower one.
_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "postdistrikt": ("postdistrikt", "postnummer", "post nr", "postal", "zip"),
    "branche": ("branche", "branchekode", "industry"),
    "address": ("adresse", "address"),
    "email": ("e-mail", "email", "mail"),
    "phone": ("telefon", "tlf", "phone", "mobil"),
    "employees": ("ansatte", "medarbejdere", "employees"),
    "name": ("virksomhed", "navn", "name", "company"),
}

_MATCH_ORDER: tuple[str, ...] = tuple(_COLUMN_ALIASES)

_HEADER_SCAN_LIMIT = 25
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def read_rows(xlsx_path: str) -> list[dict]:
    """Read ``xlsx_path`` and return one dict per company row.

    Every dict exposes exactly the keys in :data:`ROW_KEYS`; all values are
    strings, and ``email`` is ``""`` when the export contains no address.

    Raises
    ------
    FileNotFoundError
        If ``xlsx_path`` does not point to an existing file.
    """

    path = Path(xlsx_path)
    if not path.is_file():
        raise FileNotFoundError(f"company export not found: {xlsx_path}")

    workbook = load_workbook(filename=str(path), read_only=True, data_only=True)
    try:
        worksheet = workbook.active
        rows = list(worksheet.iter_rows(values_only=True))
    finally:
        workbook.close()

    header_index, columns = _locate_header(rows)
    if header_index is None:
        logger.warning("No recognisable header row found in %s", xlsx_path)
        return []

    records: list[dict] = []
    for raw in rows[header_index + 1:]:
        record = _build_record(raw, columns)
        if record is not None:
            records.append(record)

    logger.info("Normalized %d company rows from %s", len(records), xlsx_path)
    return records


def _locate_header(rows: list[tuple[Any, ...]]) -> tuple[int | None, dict[str, int]]:
    """Find the header row and the column index for each canonical field."""

    for index in range(min(len(rows), _HEADER_SCAN_LIMIT)):
        columns = _match_columns(rows[index])
        if len(columns) >= 3 or (
            "name" in columns and ("email" in columns or "postdistrikt" in columns)
        ):
            return index, columns
    return None, {}


def _match_columns(cells: tuple[Any, ...]) -> dict[str, int]:
    """Map canonical fields to column indexes using header fragments."""

    headers = [_normalize_header(cell) for cell in cells]
    columns: dict[str, int] = {}
    assigned: set[int] = set()

    for key in _MATCH_ORDER:
        for index, header in enumerate(headers):
            if index in assigned or not header:
                continue
            if any(alias in header for alias in _COLUMN_ALIASES[key]):
                columns[key] = index
                assigned.add(index)
                break
    return columns


def _build_record(cells: tuple[Any, ...], columns: dict[str, int]) -> dict | None:
    """Build a single normalised row, or ``None`` for blank/padding rows."""

    record: dict = {key: "" for key in ROW_KEYS}
    for key, index in columns.items():
        if index < len(cells):
            record[key] = _cell_to_str(cells[index])
    record["email"] = _extract_email(record["email"])

    if not record["name"] and not record["postdistrikt"]:
        return None
    return record


def _normalize_header(value: Any) -> str:
    """Lower-case and collapse a header cell for fragment matching."""

    text = _cell_to_str(value).lower().replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip().strip(":")


def _cell_to_str(value: Any) -> str:
    """Render a worksheet cell as a trimmed string."""

    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _extract_email(text: str) -> str:
    """Return the first e-mail address found in ``text`` (lower-cased)."""

    match = _EMAIL_RE.search(text or "")
    return match.group(0).lower() if match else ""
