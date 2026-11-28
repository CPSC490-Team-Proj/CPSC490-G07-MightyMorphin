"""Backend API for page 3, following the page 3 sequence diagram (#87).

Run from ``prototype/``::

    uvicorn validation.app:create_app --factory

then open http://127.0.0.1:8000/ . The demo data is rebuilt on every start.

Mocked here (see prototype/README.md): Edwards SSO (a fixed demo reviewer),
Snowflake (SQLite), AWS S3 (a local folder) and extraction (fixture values).
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import checks, fixtures
from .documents import DocumentStore
from .store import (
    DECIDED_STATUSES,
    AlreadyDecided,
    Draft,
    FlagsStillOpen,
    RecordNotFound,
    Store,
    StoreUnavailable,
    ValueChange,
)

PROTOTYPE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = PROTOTYPE_DIR / ".data"
DATA_MARKER = ".page3-prototype-data"   # proves a data folder was made by this app
DB_FILE = "snowflake-standin.sqlite3"
MAX_ID = 2**63 - 1                      # largest SQLite integer


class DataDirNotSafe(RuntimeError):
    """The data folder holds files this prototype did not create."""


def require_json(request: Request) -> None:
    """Refuse plain form posts, so another website cannot trigger an approval
    or a demo reset from the reviewer's browser (a JSON request from another
    origin needs a CORS preflight, which this app never grants)."""
    media_type = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if media_type != "application/json":
        raise HTTPException(status_code=415, detail="Send JSON (Content-Type: application/json)")


class ValueIn(BaseModel):
    value_id: int
    value: str | None = None   # length and format are checked by checks.py
    unit: str | None = None
    confirm: bool = False      # reviewer checked the value against the PDF


class DraftIn(BaseModel):
    material_code: str | None = None
    lot_number: str | None = None
    values: list[ValueIn] = Field(default_factory=list, max_length=50)
    note: str = Field(default="", max_length=500)


def problem(status: int, code: str, message: str, **extra) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message, **extra})


def flag_list(values: list[dict]) -> list[dict]:
    return [
        {"value_id": v["value_id"], "property_name": v["property_name"], "flag_reason": v["flag_reason"]}
        for v in values
        if v["flag_reason"]
    ]


def create_app(data_dir: Path | str | None = None) -> FastAPI:
    data_dir = Path(data_dir or os.environ.get("VALIDATION_DATA_DIR") or DEFAULT_DATA_DIR)
    reviewer_id = fixtures.DEMO_REVIEWER_ID  # Edwards SSO is mocked: one fixed reviewer

    app = FastAPI(title="Materials Database - page 3 validation prototype")
    state: dict = {}

    def reset() -> None:
        """Rebuild the demo database and the PDF folder from the fixtures.

        Files are deleted only from a folder this app created (it holds the
        marker file); any other non-empty folder is refused untouched.
        """
        marker = data_dir / DATA_MARKER
        if data_dir.exists() and any(data_dir.iterdir()) and not marker.is_file():
            raise DataDirNotSafe(
                f"{data_dir} is not empty and was not created by this prototype; "
                "set VALIDATION_DATA_DIR to an empty or new folder"
            )
        if "store" in state:
            state["store"].close()
        db_file = data_dir / DB_FILE
        db_file.unlink(missing_ok=True)
        if (data_dir / "s3").exists():
            shutil.rmtree(data_dir / "s3")
        data_dir.mkdir(parents=True, exist_ok=True)
        marker.write_text("Demo data for the page 3 prototype; rebuilt on every start.\n")
        state["documents"] = DocumentStore(data_dir / "s3")
        state["store"] = Store(db_file)
        fixtures.load(state["store"], state["documents"])

    reset()
    app.state.data = state  # tests reach the store and documents through this

    def store() -> Store:
        return state["store"]

    def documents() -> DocumentStore:
        return state["documents"]

    def find(record_id: int) -> dict | None:
        if not 1 <= record_id <= MAX_ID:
            return None
        return store().get_record(record_id)

    @app.exception_handler(sqlite3.Error)
    def storage_error(_request: Request, _exc: sqlite3.Error) -> JSONResponse:
        # A read that fails (e.g. the database is locked) is the same storage
        # problem as a failed write: 503, try again.
        return problem(503, "storage_unavailable", "Storage is not available; try again")

    @app.exception_handler(DataDirNotSafe)
    def data_dir_error(_request: Request, exc: DataDirNotSafe) -> JSONResponse:
        return problem(500, "data_dir_not_safe", str(exc))

    @app.exception_handler(RequestValidationError)
    def invalid_request(_request: Request, exc: RequestValidationError) -> JSONResponse:
        # One error shape for the screen: {"code", "message", ...}.
        return problem(422, "invalid_request",
                       "The request was not in the expected format; nothing was saved",
                       details=[{"loc": list(e.get("loc", ())), "msg": e.get("msg", "")}
                                for e in exc.errors()])

    # ------------------------------------------------------------ web UI
    @app.get("/", include_in_schema=False)
    def home() -> RedirectResponse:
        return RedirectResponse("/ui-tabs/validation.html")

    @app.get("/logo.jpeg", include_in_schema=False)
    def logo() -> FileResponse:
        return FileResponse(PROTOTYPE_DIR / "logo.jpeg")

    # ------------------------------------------------------- load a record
    @app.get("/records")
    def list_records() -> list[dict]:
        """Small record picker for the demo; the real queue is page 2."""
        return store().list_records()

    @app.get("/records/{record_id}")
    def load_record(record_id: int):
        record = find(record_id)
        if record is None:
            return problem(404, "not_found", f"Record {record_id} does not exist")
        fields = record.pop("values")
        body = {
            "record": {k: record[k] for k in (
                "record_id", "review_status", "material_code", "lot_number", "filename",
                "doc_type", "input_type", "vendor", "extracted_at", "approved_by", "approved_at")},
            "fields": fields,
            "open_flags": flag_list(fields),
        }
        if record["review_status"] in DECIDED_STATUSES:
            body.update(read_only=True, source={"available": False, "problem": "not loaded for a decided record"})
            return body
        _, source_problem = documents().verified_get(record["s3_object_key"], record["checksum"])
        body["read_only"] = False
        body["source"] = {
            "available": not source_problem,
            "problem": source_problem,
            "pdf_url": None if source_problem else f"/records/{record_id}/pdf",
        }
        return body

    @app.get("/records/{record_id}/pdf")
    def source_pdf(record_id: int):
        record = find(record_id)
        if record is None:
            return problem(404, "not_found", f"Record {record_id} does not exist")
        pdf, source_problem = documents().verified_get(record["s3_object_key"], record["checksum"])
        if source_problem:
            return problem(409, "source_unavailable", f"Source PDF {source_problem}")
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{record["filename"]}"'},
        )

    # ------------------------------------------------------ save a draft
    @app.put("/records/{record_id}/draft")
    def save_draft(record_id: int, draft: DraftIn):
        record = find(record_id)
        if record is None:
            return problem(404, "not_found", f"Record {record_id} does not exist")
        if record["review_status"] in DECIDED_STATUSES:
            return problem(409, "already_decided",
                           f"Record is already {record['review_status']}; nothing was saved")

        # Automatic checks. Any error rejects the whole draft (422, nothing saved).
        errors: dict[str, str] = {}
        if draft.material_code is not None and (msg := checks.check_material_code(draft.material_code)):
            errors["material_code"] = msg
        if draft.lot_number is not None and (msg := checks.check_lot_number(draft.lot_number)):
            errors["lot_number"] = msg
        by_id = {v["value_id"]: v for v in record["values"]}
        changes: list[ValueChange] = []
        seen: set[int] = set()
        for item in draft.values:
            key = f"value:{item.value_id}"
            current = by_id.get(item.value_id)
            if current is None:
                errors[key] = "Not an editable value of this record"
                continue
            if item.value_id in seen:
                errors[key] = "This value is listed twice in the draft"
                continue
            seen.add(item.value_id)
            field = checks.PropertyField(key, current["property_name"], current["standard_unit"])
            if msg := checks.check_property(field, item.value, item.unit):
                errors[key] = msg
                continue
            changes.append(ValueChange(item.value_id, checks.parse_property_value(item.value), item.confirm))
        if errors:
            return problem(422, "check_failed", "Fix the highlighted fields; nothing was saved",
                           errors=errors)

        try:
            result = store().save_draft(
                record_id, reviewer_id,
                Draft(draft.material_code, draft.lot_number, changes, draft.note),
            )
        except AlreadyDecided:
            return problem(409, "already_decided", "Record was decided meanwhile; nothing was saved")
        except RecordNotFound:
            return problem(404, "not_found", f"Record {record_id} does not exist")
        except StoreUnavailable:
            return problem(503, "not_saved", "Draft not saved; the record is unchanged. Try again.")
        return {
            "message": "Draft saved",
            "review_status": record["review_status"],  # a draft never changes it
            "open_flags": result.open_flags,
            "events_recorded": result.events_recorded,
        }

    # ------------------------------------------------- approve the record
    @app.post("/records/{record_id}/approve", dependencies=[Depends(require_json)])
    def approve(record_id: int):
        record = find(record_id)
        if record is None:
            return problem(404, "not_found", f"Record {record_id} does not exist")
        open_flags = flag_list(record["values"])
        _, source_problem = documents().verified_get(record["s3_object_key"], record["checksum"])

        # Same order as the diagram's alt block.
        if record["review_status"] in DECIDED_STATUSES:
            return problem(409, "already_decided", f"Record is already {record['review_status']}")
        if source_problem:
            return problem(409, "source_unavailable",
                           f"Source PDF {source_problem}; the values cannot be checked against it")
        if open_flags:
            return problem(409, "flags_open", "Resolve required flags first", open_flags=open_flags)
        try:
            approved_at = store().approve(record_id, reviewer_id)
        except AlreadyDecided:
            return problem(409, "already_decided", "Record was decided meanwhile")
        except RecordNotFound:
            return problem(404, "not_found", f"Record {record_id} does not exist")
        except FlagsStillOpen:
            return problem(409, "flags_open", "Resolve required flags first",
                           open_flags=flag_list(store().property_values(record_id)))
        except StoreUnavailable:
            return problem(503, "not_approved",
                           "Not approved; the record is still pending or flagged. Try again.")
        return {
            "message": "Approved",
            "review_status": "APPROVED",
            "approved_by": store().user_name(reviewer_id),
            "approved_at": approved_at,
        }

    # ------------------------------------------------- approved data only
    @app.get("/materials")
    def approved_materials() -> list[dict]:
        """Records that search (page 4) and analysis (page 5) may use."""
        return store().approved_materials()

    # ------------------------------------------- Manager view (mocked auth)
    @app.get("/manager/records/{record_id}/audit-events")
    def audit_events(record_id: int):
        """Review history. Kept for the Manager; not shown on page 3.
        No access control in the prototype (SSO and roles are mocked)."""
        if find(record_id) is None:
            return problem(404, "not_found", f"Record {record_id} does not exist")
        return store().audit_events(record_id)

    # ----------------------------------------------- demo-only controls
    @app.get("/demo/state")
    def demo_state() -> dict:
        return {"fail_next_write": store().fail_next_write}

    @app.post("/demo/reset", dependencies=[Depends(require_json)])
    def demo_reset() -> dict:
        reset()
        return {"message": "Demo data reset"}

    @app.post("/demo/fail-next-write", dependencies=[Depends(require_json)])
    def demo_fail_next_write() -> dict:
        """Make the next draft save or approval fail inside its transaction."""
        store().fail_next_write = True
        return {"message": "The next write will fail and roll back"}

    app.mount("/ui-tabs", StaticFiles(directory=PROTOTYPE_DIR / "ui-tabs", html=True), name="ui-tabs")
    return app
