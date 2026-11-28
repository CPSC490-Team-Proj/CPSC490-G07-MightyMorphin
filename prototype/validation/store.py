"""Snowflake stand-in: SQLite tables that follow the ER diagram (#38, #172).

Only the tables page 3 needs are created, with the ER diagram's table and
column names: ROLE, APP_USER, VENDOR, MATERIAL, LOT, PROPERTY_TYPE,
SOURCE_DOCUMENT, MATERIAL_RECORD, PROPERTY_VALUE and AUDIT_EVENT.
PROCESSING_JOB, PROCESSING_STEP and MATERIAL_SPEC are left out, as are
columns page 3 does not use. One column is added that the ER diagram lacks:
SOURCE_DOCUMENT.filename, shown in the page title.

Source traceability (#109): every MATERIAL_RECORD points at the
SOURCE_DOCUMENT it was extracted from, and that document row holds the S3
object key, the checksum and whether it is a CoC or a test report. Database
triggers make the link permanent: a record cannot be moved to another
document, replaced or deleted; a document's id, key, checksum and type cannot
be edited; and a document cannot be replaced or deleted while records point
at it. Replacing a PDF (not built yet) is therefore meant to add a new
SOURCE_DOCUMENT row, never an overwrite.

Every change is one transaction, as in the sequence diagram: if any statement
fails, the whole change is rolled back and the record keeps its previous
values and its PENDING or FLAGGED status. ``fail_next_write`` forces such a
failure part-way through a transaction so the rollback can be demonstrated
and tested.
"""

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

OPEN_STATUSES = ("PENDING", "FLAGGED")
DECIDED_STATUSES = ("APPROVED", "REJECTED")

SCHEMA = """
CREATE TABLE ROLE (
    role_id      INTEGER PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE
);
CREATE TABLE APP_USER (
    user_id      INTEGER PRIMARY KEY,
    role_id      INTEGER NOT NULL REFERENCES ROLE(role_id),
    email        TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    is_active    INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE VENDOR (
    vendor_id    INTEGER PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE
);
CREATE TABLE MATERIAL (
    material_id   INTEGER PRIMARY KEY,
    material_code TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL
);
CREATE TABLE LOT (
    lot_id       INTEGER PRIMARY KEY,
    material_id  INTEGER NOT NULL REFERENCES MATERIAL(material_id),
    vendor_id    INTEGER REFERENCES VENDOR(vendor_id),
    lot_number   TEXT NOT NULL
);
CREATE TABLE PROPERTY_TYPE (
    property_type_id INTEGER PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE,
    standard_unit    TEXT NOT NULL
);
CREATE TABLE SOURCE_DOCUMENT (
    document_id   INTEGER PRIMARY KEY,
    vendor_id     INTEGER REFERENCES VENDOR(vendor_id),
    uploaded_by   INTEGER NOT NULL REFERENCES APP_USER(user_id),
    filename      TEXT NOT NULL,
    doc_type      TEXT NOT NULL CHECK (doc_type IN ('COC', 'TEST_REPORT')),
    input_type    TEXT NOT NULL CHECK (input_type IN ('DIGITAL', 'SCANNED')),
    s3_object_key TEXT NOT NULL UNIQUE,
    checksum      TEXT NOT NULL,
    status        TEXT NOT NULL,
    uploaded_at   TEXT NOT NULL
);
CREATE TABLE MATERIAL_RECORD (
    record_id     INTEGER PRIMARY KEY,
    document_id   INTEGER NOT NULL REFERENCES SOURCE_DOCUMENT(document_id),
    material_id   INTEGER NOT NULL REFERENCES MATERIAL(material_id),
    lot_id        INTEGER REFERENCES LOT(lot_id),
    approved_by   INTEGER REFERENCES APP_USER(user_id),
    review_status TEXT NOT NULL
        CHECK (review_status IN ('PENDING', 'FLAGGED', 'APPROVED', 'REJECTED')),
    extracted_at  TEXT NOT NULL,
    approved_at   TEXT
);
CREATE TABLE PROPERTY_VALUE (
    value_id         INTEGER PRIMARY KEY,
    record_id        INTEGER NOT NULL REFERENCES MATERIAL_RECORD(record_id),
    property_type_id INTEGER NOT NULL REFERENCES PROPERTY_TYPE(property_type_id),
    value            TEXT,
    unit_as_printed  TEXT NOT NULL,
    confidence       REAL NOT NULL,
    flag_reason      TEXT
);
CREATE TABLE AUDIT_EVENT (
    event_id     INTEGER PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES APP_USER(user_id),
    action       TEXT NOT NULL,
    entity_type  TEXT NOT NULL,
    entity_id    INTEGER NOT NULL,
    field_name   TEXT,
    old_value    TEXT,
    new_value    TEXT,
    note         TEXT,
    created_at   TEXT NOT NULL
);

-- #109: the link from a record to its source PDF never changes or disappears.
-- The triggers fire whether or not a connection turns foreign keys on.
CREATE TRIGGER source_reference_is_fixed
BEFORE UPDATE OF document_id, s3_object_key, checksum, doc_type ON SOURCE_DOCUMENT
BEGIN
    SELECT RAISE(ABORT, 'a source document reference cannot be changed');
END;
CREATE TRIGGER source_document_not_replaced
BEFORE INSERT ON SOURCE_DOCUMENT
WHEN EXISTS (SELECT 1 FROM SOURCE_DOCUMENT WHERE document_id = NEW.document_id)
BEGIN
    -- REPLACE INTO would otherwise delete and re-insert the row unnoticed.
    SELECT RAISE(ABORT, 'a source document cannot be replaced');
END;
CREATE TRIGGER record_keeps_its_source
BEFORE UPDATE OF record_id, document_id ON MATERIAL_RECORD
BEGIN
    SELECT RAISE(ABORT, 'a material record cannot change its source document');
END;
CREATE TRIGGER record_not_replaced
BEFORE INSERT ON MATERIAL_RECORD
WHEN EXISTS (SELECT 1 FROM MATERIAL_RECORD WHERE record_id = NEW.record_id)
BEGIN
    SELECT RAISE(ABORT, 'a material record cannot be replaced');
END;
CREATE TRIGGER record_is_kept
BEFORE DELETE ON MATERIAL_RECORD
BEGIN
    SELECT RAISE(ABORT, 'material records are not deleted; they keep their source');
END;
CREATE TRIGGER referenced_source_is_kept
BEFORE DELETE ON SOURCE_DOCUMENT
WHEN EXISTS (SELECT 1 FROM MATERIAL_RECORD WHERE document_id = OLD.document_id)
BEGIN
    SELECT RAISE(ABORT, 'a source document with material records cannot be deleted');
END;
"""

SOURCE_COLUMNS = """d.document_id, d.filename, d.doc_type, d.input_type, d.s3_object_key,
                   d.checksum, d.status AS document_status, d.uploaded_at, vd.name AS vendor"""


class StoreUnavailable(Exception):
    """The write failed and was rolled back (the diagram's 503 branch)."""


class AlreadyDecided(Exception):
    """The record is no longer PENDING or FLAGGED (the diagram's 409 branch)."""


class FlagsStillOpen(Exception):
    """Approval was attempted while a required flag is still open."""


class RecordNotFound(LookupError):
    """No record, or no property value of this record, with that id."""


@dataclass
class ValueChange:
    value_id: int
    value: Decimal | None
    confirm: bool = False


@dataclass
class DraftResult:
    open_flags: list[dict]
    events_recorded: int  # CORRECT audit events written by this save


@dataclass
class Draft:
    material_code: str | None = None   # None = unchanged
    lot_number: str | None = None      # None = unchanged, "" = clear
    values: list[ValueChange] = field(default_factory=list)
    note: str = ""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _same_number(old: str | None, new: Decimal | None) -> bool:
    if old is None or new is None:
        return old is None and new is None
    return Decimal(old) == new


class Store:
    def __init__(self, path: Path | str = ":memory:") -> None:
        self._conn = sqlite3.connect(str(path), check_same_thread=False, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._lock = threading.Lock()
        self.fail_next_write = False

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # ---------------------------------------------------------------- setup
    def create_schema(self) -> None:
        with self._lock:
            self._conn.executescript(SCHEMA)

    def execute(self, sql: str, params: tuple = ()) -> int:
        """Run one insert during fixture setup and return the new row id."""
        with self._lock:
            return self._conn.execute(sql, params).lastrowid

    # ---------------------------------------------------------------- reads
    def _query(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self._lock:
            return self._conn.execute(sql, params).fetchall()

    def list_records(self) -> list[dict]:
        rows = self._query(
            """
            SELECT r.record_id, r.review_status, d.filename, m.material_code,
                   (SELECT COUNT(*) FROM PROPERTY_VALUE v
                     WHERE v.record_id = r.record_id AND v.flag_reason IS NOT NULL) AS open_flags
              FROM MATERIAL_RECORD r
              JOIN SOURCE_DOCUMENT d ON d.document_id = r.document_id
              JOIN MATERIAL m ON m.material_id = r.material_id
             ORDER BY r.record_id
            """
        )
        return [dict(row) for row in rows]

    def get_record(self, record_id: int) -> dict | None:
        rows = self._query(
            """
            SELECT r.record_id, r.review_status, r.extracted_at, r.approved_at,
                   u.display_name AS approved_by,
                   m.material_code, l.lot_number,
                   d.document_id, d.filename, d.doc_type, d.input_type,
                   d.s3_object_key, d.checksum, vd.name AS vendor
              FROM MATERIAL_RECORD r
              JOIN SOURCE_DOCUMENT d ON d.document_id = r.document_id
              JOIN MATERIAL m ON m.material_id = r.material_id
              LEFT JOIN LOT l ON l.lot_id = r.lot_id
              LEFT JOIN VENDOR vd ON vd.vendor_id = d.vendor_id
              LEFT JOIN APP_USER u ON u.user_id = r.approved_by
             WHERE r.record_id = ?
            """,
            (record_id,),
        )
        if not rows:
            return None
        record = dict(rows[0])
        record["values"] = self.property_values(record_id)
        return record

    def property_values(self, record_id: int) -> list[dict]:
        rows = self._query(
            """
            SELECT v.value_id, t.name AS property_name, t.standard_unit,
                   v.value, v.unit_as_printed, v.confidence, v.flag_reason
              FROM PROPERTY_VALUE v
              JOIN PROPERTY_TYPE t ON t.property_type_id = v.property_type_id
             WHERE v.record_id = ?
             ORDER BY v.value_id
            """,
            (record_id,),
        )
        return [dict(row) for row in rows]

    def audit_events(self, record_id: int) -> list[dict]:
        """Correction and approval history of one record (Manager use only)."""
        rows = self._query(
            """
            SELECT e.event_id, u.display_name AS reviewer, e.action, e.entity_type,
                   e.entity_id, e.field_name, e.old_value, e.new_value, e.note, e.created_at
              FROM AUDIT_EVENT e
              JOIN APP_USER u ON u.user_id = e.user_id
             WHERE (e.entity_type = 'MATERIAL_RECORD' AND e.entity_id = ?)
                OR (e.entity_type = 'PROPERTY_VALUE' AND e.entity_id IN
                      (SELECT value_id FROM PROPERTY_VALUE WHERE record_id = ?))
             ORDER BY e.event_id
            """,
            (record_id, record_id),
        )
        return [dict(row) for row in rows]

    def source_reference(self, record_id: int) -> dict | None:
        """The source document a record was extracted from (#109)."""
        rows = self._query(
            f"""
            SELECT r.record_id, {SOURCE_COLUMNS}
              FROM MATERIAL_RECORD r
              JOIN SOURCE_DOCUMENT d ON d.document_id = r.document_id
              LEFT JOIN VENDOR vd ON vd.vendor_id = d.vendor_id
             WHERE r.record_id = ?
            """,
            (record_id,),
        )
        return dict(rows[0]) if rows else None

    def approved_materials(self) -> list[dict]:
        """What search and analysis may use: APPROVED records only."""
        rows = self._query(
            """
            SELECT r.record_id, m.material_code, l.lot_number, d.filename,
                   r.approved_at, u.display_name AS approved_by
              FROM MATERIAL_RECORD r
              JOIN MATERIAL m ON m.material_id = r.material_id
              JOIN SOURCE_DOCUMENT d ON d.document_id = r.document_id
              LEFT JOIN LOT l ON l.lot_id = r.lot_id
              LEFT JOIN APP_USER u ON u.user_id = r.approved_by
             WHERE r.review_status = 'APPROVED'
             ORDER BY r.record_id
            """
        )
        result = []
        for row in rows:
            item = dict(row)
            item["values"] = [
                {k: v[k] for k in ("property_name", "value", "standard_unit")}
                for v in self.property_values(item["record_id"])
            ]
            source = self.source_reference(item["record_id"])
            item["source"] = {k: source[k] for k in (
                "document_id", "doc_type", "s3_object_key", "checksum", "vendor")}
            result.append(item)
        return result

    def user_name(self, user_id: int) -> str:
        rows = self._query("SELECT display_name FROM APP_USER WHERE user_id = ?", (user_id,))
        return rows[0]["display_name"]

    # --------------------------------------------------------------- writes
    def _rollback(self) -> None:
        # SQLite may already have rolled back on its own (e.g. disk full);
        # a second ROLLBACK would raise and hide the original error.
        if self._conn.in_transaction:
            self._conn.execute("ROLLBACK")

    def _maybe_fail(self) -> None:
        if self.fail_next_write:
            self.fail_next_write = False
            raise sqlite3.OperationalError("simulated storage failure")

    def _status(self, conn: sqlite3.Connection, record_id: int) -> str:
        row = conn.execute(
            "SELECT review_status FROM MATERIAL_RECORD WHERE record_id = ?", (record_id,)
        ).fetchone()
        if row is None:
            raise RecordNotFound(record_id)
        return row["review_status"]

    def _audit(self, conn, user_id, action, entity_type, entity_id,
               field_name=None, old=None, new=None, note=None, when=None) -> None:
        conn.execute(
            """INSERT INTO AUDIT_EVENT (user_id, action, entity_type, entity_id,
                   field_name, old_value, new_value, note, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, action, entity_type, entity_id, field_name, old, new,
             note or None, when or utc_now()),
        )

    def _material_id(self, conn, code: str) -> int:
        row = conn.execute(
            "SELECT material_id FROM MATERIAL WHERE material_code = ?", (code,)
        ).fetchone()
        if row:
            return row["material_id"]
        return conn.execute(
            "INSERT INTO MATERIAL (material_code, name) VALUES (?, ?)", (code, code)
        ).lastrowid

    def _lot_id(self, conn, material_id: int, vendor_id, lot_number: str) -> int:
        row = conn.execute(
            """SELECT lot_id FROM LOT WHERE material_id = ? AND lot_number = ?
                 AND vendor_id IS ?""",
            (material_id, lot_number, vendor_id),
        ).fetchone()
        if row:
            return row["lot_id"]
        return conn.execute(
            "INSERT INTO LOT (material_id, vendor_id, lot_number) VALUES (?, ?, ?)",
            (material_id, vendor_id, lot_number),
        ).lastrowid

    def add_source_document(self, *, filename: str, doc_type: str, input_type: str,
                            s3_object_key: str, checksum: str, uploaded_by: int,
                            vendor: str | None, uploaded_at: str | None = None) -> int:
        """Record a PDF saved to S3 at processing time and return its document_id."""
        with self._lock:
            conn = self._conn
            try:
                conn.execute("BEGIN IMMEDIATE")
                vendor_id = None
                if vendor:
                    row = conn.execute("SELECT vendor_id FROM VENDOR WHERE name = ?",
                                       (vendor,)).fetchone()
                    vendor_id = row["vendor_id"] if row else conn.execute(
                        "INSERT INTO VENDOR (name) VALUES (?)", (vendor,)).lastrowid
                document_id = conn.execute(
                    """INSERT INTO SOURCE_DOCUMENT (vendor_id, uploaded_by, filename, doc_type,
                           input_type, s3_object_key, checksum, status, uploaded_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'DONE', ?)""",
                    (vendor_id, uploaded_by, filename, doc_type, input_type,
                     s3_object_key, checksum, uploaded_at or utc_now()),
                ).lastrowid
                conn.execute("COMMIT")
                return document_id
            except BaseException:
                self._rollback()
                raise

    def add_extracted_record(self, document_id: int, material_code: str,
                             lot_number: str | None,
                             values: list[tuple[str, str | None, float, str | None]],
                             extracted_at: str | None = None) -> int:
        """The extraction step's hand-off: store a candidate record linked to
        the document it came from, in one transaction, and return its id.

        ``values`` holds (property name, value or None, confidence, flag reason
        or None). The record starts FLAGGED if any value is flagged, otherwise
        PENDING; it is never stored as approved data.
        """
        with self._lock:
            conn = self._conn
            try:
                conn.execute("BEGIN IMMEDIATE")
                if not values:
                    raise ValueError("an extracted record needs at least one property value")
                document = conn.execute(
                    "SELECT vendor_id FROM SOURCE_DOCUMENT WHERE document_id = ?", (document_id,)
                ).fetchone()
                if document is None:
                    raise RecordNotFound(document_id)
                material_id = self._material_id(conn, material_code)
                lot_id = (self._lot_id(conn, material_id, document["vendor_id"], lot_number)
                          if lot_number else None)
                flagged = any(flag for _, _, _, flag in values)
                record_id = conn.execute(
                    """INSERT INTO MATERIAL_RECORD (document_id, material_id, lot_id,
                           review_status, extracted_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (document_id, material_id, lot_id,
                     "FLAGGED" if flagged else "PENDING", extracted_at or utc_now()),
                ).lastrowid
                for name, value, confidence, flag in values:
                    ptype = conn.execute(
                        "SELECT property_type_id, standard_unit FROM PROPERTY_TYPE WHERE name = ?",
                        (name,),
                    ).fetchone()
                    if ptype is None:
                        raise ValueError(f"unknown property type: {name!r}")
                    conn.execute(
                        """INSERT INTO PROPERTY_VALUE (record_id, property_type_id, value,
                               unit_as_printed, confidence, flag_reason)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (record_id, ptype["property_type_id"], value, ptype["standard_unit"],
                         confidence, flag),
                    )
                conn.execute("COMMIT")
                return record_id
            except BaseException:
                self._rollback()
                raise

    def save_draft(self, record_id: int, user_id: int, draft: Draft) -> DraftResult:
        """Write a checked draft in one transaction.

        The status is re-read inside the transaction, so a record decided by
        someone else in the meantime raises AlreadyDecided and nothing is saved.
        As in the sequence diagram, a draft never changes the review status:
        the record stays PENDING or FLAGGED until it is approved.
        """
        when = utc_now()
        note = draft.note.strip()
        events = 0
        with self._lock:
            conn = self._conn
            try:
                conn.execute("BEGIN IMMEDIATE")
                if self._status(conn, record_id) not in OPEN_STATUSES:
                    raise AlreadyDecided()

                rec = conn.execute(
                    """SELECT r.material_id, r.lot_id, m.material_code, l.lot_number,
                              d.vendor_id
                         FROM MATERIAL_RECORD r
                         JOIN MATERIAL m ON m.material_id = r.material_id
                         JOIN SOURCE_DOCUMENT d ON d.document_id = r.document_id
                         LEFT JOIN LOT l ON l.lot_id = r.lot_id
                        WHERE r.record_id = ?""",
                    (record_id,),
                ).fetchone()
                old_code, old_lot = rec["material_code"], rec["lot_number"] or ""
                new_code = draft.material_code.strip() if draft.material_code is not None else old_code
                new_lot = draft.lot_number.strip() if draft.lot_number is not None else old_lot

                if new_code != old_code or new_lot != old_lot:
                    material_id = self._material_id(conn, new_code)
                    lot_id = (self._lot_id(conn, material_id, rec["vendor_id"], new_lot)
                              if new_lot else None)
                    conn.execute(
                        "UPDATE MATERIAL_RECORD SET material_id = ?, lot_id = ? WHERE record_id = ?",
                        (material_id, lot_id, record_id),
                    )
                    for name, old, new in (("material_code", old_code, new_code),
                                           ("lot_number", old_lot, new_lot)):
                        if old != new:
                            self._audit(conn, user_id, "CORRECT", "MATERIAL_RECORD", record_id,
                                        name, old or None, new or None, note, when)
                            events += 1

                current = {
                    row["value_id"]: row
                    for row in conn.execute(
                        """SELECT v.value_id, v.value, v.flag_reason, t.name
                             FROM PROPERTY_VALUE v
                             JOIN PROPERTY_TYPE t ON t.property_type_id = v.property_type_id
                            WHERE v.record_id = ?""",
                        (record_id,),
                    )
                }
                for change in draft.values:
                    row = current.get(change.value_id)
                    if row is None:
                        raise RecordNotFound(change.value_id)
                    changed = not _same_number(row["value"], change.value)
                    if change.value is None:
                        flag = "Missing value"
                    elif changed or change.confirm:
                        flag = None
                    else:
                        flag = row["flag_reason"]
                    new_text = None if change.value is None else str(change.value)
                    if changed or flag != row["flag_reason"]:
                        conn.execute(
                            "UPDATE PROPERTY_VALUE SET value = ?, flag_reason = ? WHERE value_id = ?",
                            (new_text if changed else row["value"], flag, change.value_id),
                        )
                    if changed:
                        self._audit(conn, user_id, "CORRECT", "PROPERTY_VALUE", change.value_id,
                                    row["name"], row["value"], new_text, note, when)
                        events += 1
                    elif row["flag_reason"] and flag is None:
                        # The reviewer checked a flagged value against the PDF
                        # and kept it: record that decision too.
                        confirm_note = "Confirmed without change" + (f": {note}" if note else "")
                        self._audit(conn, user_id, "CORRECT", "PROPERTY_VALUE", change.value_id,
                                    row["name"], row["value"], row["value"], confirm_note, when)
                        events += 1

                open_flags = conn.execute(
                    """SELECT v.value_id, t.name AS property_name, v.flag_reason
                         FROM PROPERTY_VALUE v
                         JOIN PROPERTY_TYPE t ON t.property_type_id = v.property_type_id
                        WHERE v.record_id = ? AND v.flag_reason IS NOT NULL
                        ORDER BY v.value_id""",
                    (record_id,),
                ).fetchall()
                self._maybe_fail()  # after every write, so a failure must undo all of them
                conn.execute("COMMIT")
                return DraftResult([dict(row) for row in open_flags], events)
            except sqlite3.Error as exc:
                self._rollback()
                raise StoreUnavailable(str(exc)) from exc
            except BaseException:
                self._rollback()
                raise

    def approve(self, record_id: int, user_id: int, when: str | None = None) -> str:
        """Set APPROVED, approved_by, approved_at and add an APPROVE event.

        Status and flags are checked again inside the transaction, so the
        record cannot be approved twice or with a flag that opened meanwhile.
        Returns the approval timestamp.
        """
        when = when or utc_now()
        with self._lock:
            conn = self._conn
            try:
                conn.execute("BEGIN IMMEDIATE")
                status = self._status(conn, record_id)
                if status not in OPEN_STATUSES:
                    raise AlreadyDecided()
                still_open = conn.execute(
                    "SELECT COUNT(*) FROM PROPERTY_VALUE WHERE record_id = ? AND flag_reason IS NOT NULL",
                    (record_id,),
                ).fetchone()[0]
                if still_open:
                    raise FlagsStillOpen()
                conn.execute(
                    """UPDATE MATERIAL_RECORD
                          SET review_status = 'APPROVED', approved_by = ?, approved_at = ?
                        WHERE record_id = ?""",
                    (user_id, when, record_id),
                )
                self._audit(conn, user_id, "APPROVE", "MATERIAL_RECORD", record_id,
                            "review_status", status, "APPROVED", None, when)
                self._maybe_fail()  # after every write, so a failure must undo all of them
                conn.execute("COMMIT")
                return when
            except sqlite3.Error as exc:
                self._rollback()
                raise StoreUnavailable(str(exc)) from exc
            except BaseException:
                self._rollback()
                raise
