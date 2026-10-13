"""Normalize a TARGIT Excel export into typed company rows.

The export is a cross-tab whose company data lives on the ``Tabel`` worksheet;
the other sheets are empty or small summaries, so the sheet is chosen by name
rather than via ``workbook.active``. openpyxl 3.1.5 rejects the
``defaultColWidthPt`` attribute TARGIT emits on worksheet XML, so the workbook
is re-packaged in memory with that attribute stripped before it is handed to
openpyxl (the file on disk is never modified). The header is located
heuristically by matching Danish and English column fragments. Field values are
returned as strings; addresses are reduced to the first e-mail address found in
the cell. The Branche filter lives here too (``filter_rows``) so the export can
be downloaded unfiltered and selected in Python.
"""

from __future__ import annotations

import io
import logging
import re
import zipfile
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

#: The worksheet that holds the company data in a TARGIT export.
PREFERRED_SHEET = "Tabel"

#: ``defaultColWidthPt`` on a worksheet ``<sheetFormatPr>`` element, which
#: openpyxl 3.1.5 cannot parse. It is cosmetic, so it is stripped in memory.
_DEFAULT_COL_WIDTH_PT_RE = re.compile(rb'\sdefaultColWidthPt="[^"]*"')

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

    workbook = _load_workbook(path)
    try:
        worksheet = _select_sheet(workbook)
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


def filter_rows(rows: list[dict], branche_query: str) -> list[dict]:
    """Return only rows whose ``branche`` contains ``branche_query``.

    Matching is case-insensitive and substring-based, so ``"computer"`` selects
    both ``Computerprogrammering`` and ``Computerkonsulentbistand ...``. An empty
    ``branche_query`` returns ``rows`` unchanged (no filter applied).
    """

    query = (branche_query or "").strip().lower()
    if not query:
        return rows
    return [row for row in rows if query in (row.get("branche") or "").lower()]


def _load_workbook(path: Path):
    """Open ``path`` with openpyxl after sanitising the worksheet XML in memory.

    openpyxl 3.1.5 raises ``TypeError: SheetFormatProperties.__init__() got an
    unexpected keyword argument 'defaultColWidthPt'`` on TARGIT's worksheet
    ``<sheetFormatPr>`` elements. The attribute is cosmetic, so the ``.xlsx`` is
    read as a zip, the attribute is stripped from each ``xl/worksheets/*.xml``
    entry, and openpyxl is handed a ``BytesIO`` -- the file on disk is never
    modified.
    """

    with zipfile.ZipFile(path) as zin:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith("xl/worksheets/") and item.filename.endswith(".xml"):
                    data = _DEFAULT_COL_WIDTH_PT_RE.sub(b"", data)
                zout.writestr(item, data)
    buffer.seek(0)
    return load_workbook(buffer, read_only=True, data_only=True)


def _select_sheet(workbook):
    """Choose the worksheet that holds the company data, logging the choice.

    The data always lives on the ``Tabel`` sheet; the other sheets
    (``Du kan også finde virksomhedern``, ``Udforsk``, ``Virksomhedsliste``) are
    empty or small summaries. ``Tabel`` wins when present; otherwise fall back to
    the sheet with the most used rows × columns so a changed export shape still
    normalises something useful rather than silently reading an empty sheet.
    """

    if PREFERRED_SHEET in workbook.sheetnames:
        logger.info("Reading worksheet %r (company data sheet)", PREFERRED_SHEET)
        return workbook[PREFERRED_SHEET]

    chosen = None
    best = -1
    for name in workbook.sheetnames:
        sheet = workbook[name]
        score = sheet.max_row * sheet.max_column
        if score > best:
            chosen, best = sheet, score
    logger.info(
        "Reading worksheet %r (largest sheet; %r absent)",
        chosen.title if chosen is not None else None,
        PREFERRED_SHEET,
    )
    return chosen


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
