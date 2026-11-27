"""Tests for the page 3 validation prototype (#88).

Each test names the #88 acceptance criterion (AC1-AC9) it checks, and the
sequence diagram (#87) branch where one applies. Run from ``prototype/``:

    python -m pytest -q
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from validation import fixtures
from validation.app import DataDirNotSafe, create_app
from validation.documents import checksum
from validation.store import AlreadyDecided, Draft, FlagsStillOpen, ValueChange

PROTOTYPE = Path(__file__).resolve().parent.parent

FLAGGED = 1        # low-confidence tensile strength (value 1), missing elongation (value 2)
PENDING = 2        # no flags
NO_SOURCE = 3      # PDF copy missing from storage
APPROVED = 4       # already approved


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "data")) as test_client:
        yield test_client


def store(client):
    return client.app.state.data["store"]


def documents(client):
    return client.app.state.data["documents"]


def resolve_record_1(client, note="Checked against the PDF"):
    return client.put(f"/records/{FLAGGED}/draft", json={
        "values": [{"value_id": 1, "value": "850", "confirm": True},
                   {"value_id": 2, "value": "18"}],
        "note": note,
    })


# --- AC1: load extracted fields and the original PDF -------------------------

def test_ac1_loads_flagged_record_with_fields_flags_and_pdf(client):
    body = client.get(f"/records/{FLAGGED}").json()
    assert body["read_only"] is False
    assert body["record"]["review_status"] == "FLAGGED"
    assert body["record"]["filename"] == "vendor-coc-001.pdf"
    assert [f["property_name"] for f in body["fields"]] == ["Tensile strength", "Elongation"]
    assert [f["flag_reason"] for f in body["open_flags"]] == ["Low confidence", "Missing value"]
    assert body["source"] == {"available": True, "problem": "", "pdf_url": f"/records/{FLAGGED}/pdf"}

    pdf = client.get(body["source"]["pdf_url"])
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF-")


def test_ac1_missing_pdf_is_reported_and_not_served(client):
    body = client.get(f"/records/{NO_SOURCE}").json()
    assert body["source"]["available"] is False
    assert body["source"]["problem"] == "missing"
    assert client.get(f"/records/{NO_SOURCE}/pdf").status_code == 409


def test_ac1_replaced_pdf_fails_the_checksum(client):
    record = store(client).get_record(FLAGGED)
    documents(client).put(record["s3_object_key"], b"%PDF-1.4 a different file")
    body = client.get(f"/records/{FLAGGED}").json()
    assert body["source"] == {"available": False, "problem": "checksum mismatch", "pdf_url": None}


def test_ac1_unknown_record_is_404(client):
    assert client.get("/records/999").status_code == 404


# --- AC2: save corrections as a draft, resolve flags, approve -----------------

def test_ac2_draft_save_does_not_approve(client):
    response = client.put(f"/records/{FLAGGED}/draft", json={
        "values": [{"value_id": 2, "value": "18"}], "note": "Elongation read from page 1"})
    assert response.status_code == 200
    assert response.json()["review_status"] == "FLAGGED"
    assert [f["flag_reason"] for f in response.json()["open_flags"]] == ["Low confidence"]
    record = store(client).get_record(FLAGGED)
    assert record["review_status"] == "FLAGGED"
    assert record["approved_at"] is None


def test_ac2_corrected_value_resolves_flag_and_is_stored(client):
    response = client.put(f"/records/{FLAGGED}/draft", json={
        "values": [{"value_id": 1, "value": "855.5"}], "note": "Digit misread"})
    assert response.status_code == 200
    values = store(client).property_values(FLAGGED)
    assert values[0]["value"] == "855.5"
    assert values[0]["flag_reason"] is None


def test_ac2_unchanged_flagged_value_stays_flagged_unless_confirmed(client):
    client.put(f"/records/{FLAGGED}/draft", json={"values": [{"value_id": 1, "value": "850"}]})
    assert store(client).property_values(FLAGGED)[0]["flag_reason"] == "Low confidence"
    client.put(f"/records/{FLAGGED}/draft",
               json={"values": [{"value_id": 1, "value": "850", "confirm": True}]})
    assert store(client).property_values(FLAGGED)[0]["flag_reason"] is None


def test_ac2_blank_value_saves_as_missing_and_blocks_approval(client):
    client.put(f"/records/{PENDING}/draft", json={"values": [{"value_id": 4, "value": ""}]})
    record = store(client).get_record(PENDING)
    assert record["review_status"] == "PENDING"  # a draft never changes the status
    assert record["values"][1]["flag_reason"] == "Missing value"
    assert client.post(f"/records/{PENDING}/approve", json={}).json()["code"] == "flags_open"


def test_ac2_resolving_all_flags_then_approving(client):
    response = resolve_record_1(client)
    assert response.json() == {"message": "Draft saved", "review_status": "FLAGGED",
                               "open_flags": [], "events_recorded": 2}
    approved = client.post(f"/records/{FLAGGED}/approve", json={})
    assert approved.status_code == 200
    assert approved.json()["review_status"] == "APPROVED"
    assert approved.json()["approved_by"] == "Demo Reviewer"


def test_ac2_lot_can_be_cleared_and_is_audited(client):
    assert client.put(f"/records/{PENDING}/draft", json={"lot_number": "  "}).status_code == 200
    assert store(client).get_record(PENDING)["lot_number"] is None
    event = store(client).audit_events(PENDING)[0]
    assert (event["field_name"], event["old_value"], event["new_value"]) == ("lot_number", "L-105", None)


def test_ac2_material_and_lot_corrections(client):
    response = client.put(f"/records/{PENDING}/draft", json={
        "material_code": "M-002A", "lot_number": "L-106", "note": "Header misread"})
    assert response.status_code == 200
    record = store(client).get_record(PENDING)
    assert (record["material_code"], record["lot_number"]) == ("M-002A", "L-106")


# --- AC3: review history with reviewer and timestamp; failed saves never approve

def test_ac3_corrections_and_approval_are_audited(client):
    resolve_record_1(client, note="Checked")
    client.post(f"/records/{FLAGGED}/approve", json={})
    events = client.get(f"/manager/records/{FLAGGED}/audit-events").json()
    assert [(e["action"], e["field_name"], e["old_value"], e["new_value"]) for e in events] == [
        ("CORRECT", "Tensile strength", "850", "850"),
        ("CORRECT", "Elongation", None, "18"),
        ("APPROVE", "review_status", "FLAGGED", "APPROVED"),
    ]
    assert events[0]["note"] == "Confirmed without change: Checked"
    assert events[1]["note"] == "Checked"
    for event in events:
        assert event["reviewer"] == "Demo Reviewer"
        assert event["created_at"].endswith("Z")


def test_ac3_failed_draft_write_rolls_back_everything(client):
    before = store(client).get_record(FLAGGED)
    client.post("/demo/fail-next-write", json={})
    response = resolve_record_1(client)
    assert response.status_code == 503
    assert response.json()["code"] == "not_saved"
    assert store(client).get_record(FLAGGED) == before
    assert store(client).audit_events(FLAGGED) == []
    # The failure is one-off: a retry saves.
    assert resolve_record_1(client).status_code == 200


def test_ac3_failed_draft_with_new_material_and_lot_rolls_back(client):
    def count(table):
        return len(store(client)._query(f"SELECT * FROM {table}"))
    before = {t: count(t) for t in ("MATERIAL", "LOT", "AUDIT_EVENT")}
    client.post("/demo/fail-next-write", json={})
    response = client.put(f"/records/{PENDING}/draft",
                          json={"material_code": "M-NEW", "lot_number": "L-NEW"})
    assert response.status_code == 503
    assert {t: count(t) for t in before} == before
    assert store(client).get_record(PENDING)["material_code"] == "M-002"


def test_ac3_note_without_a_change_records_nothing(client):
    response = client.put(f"/records/{FLAGGED}/draft", json={"note": "Looked at it"})
    assert response.json()["events_recorded"] == 0
    assert store(client).audit_events(FLAGGED) == []


def test_ac3_failed_approval_write_leaves_record_unapproved(client):
    client.post("/demo/fail-next-write", json={})
    response = client.post(f"/records/{PENDING}/approve", json={})
    assert response.status_code == 503
    record = store(client).get_record(PENDING)
    assert record["review_status"] == "PENDING"
    assert record["approved_by"] is None and record["approved_at"] is None
    assert store(client).audit_events(PENDING) == []
    assert all(m["record_id"] != PENDING for m in client.get("/materials").json())
    # The failure is one-off: a retry succeeds.
    assert client.post(f"/records/{PENDING}/approve", json={}).status_code == 200


def test_ac3_rejected_draft_writes_no_history(client):
    response = client.put(f"/records/{FLAGGED}/draft",
                          json={"values": [{"value_id": 1, "value": "abc"}]})
    assert response.status_code == 422
    assert store(client).audit_events(FLAGGED) == []


# --- AC4: wireframe inputs, actions, table, navigation and feedback ----------

def test_ac4_page_has_the_wireframe_controls(client):
    html = client.get("/ui-tabs/validation.html").text
    for needed in ('Original PDF preview', 'id="open-pdf"', '<th scope="col">Field</th>',
                   '<th scope="col">Editable value</th>', '<th scope="col">Review flag</th>',
                   'Correction note', 'id="save-draft"', 'Re-extract / replace',
                   'id="approve"', 'id="feedback"', 'Review queue', 'Materials', 'Analysis',
                   '--red-deep: #80001f'):
        assert needed in html, needed
    home = client.get("/", follow_redirects=False)
    assert home.headers["location"] == "/ui-tabs/validation.html"


# --- AC5: synthetic data, documented mocks ------------------------------------

def test_ac5_fixture_pdfs_are_marked_synthetic(client):
    for record_id in (FLAGGED, PENDING, APPROVED):
        record = store(client).get_record(record_id)
        pdf = documents(client).get(record["s3_object_key"])
        assert fixtures.SYNTHETIC_MARK.encode() in pdf
        assert checksum(pdf) == record["checksum"]


def test_ac5_readme_documents_the_mocks():
    readme = (PROTOTYPE / "README.md").read_text(encoding="utf-8")
    for mocked in ("Snowflake", "S3", "SSO", "extraction"):
        assert mocked in readme


# --- AC6: pending/flagged data is never presented as approved ----------------

def test_ac6_materials_lists_only_approved_records(client):
    assert [m["record_id"] for m in client.get("/materials").json()] == [APPROVED]
    resolve_record_1(client)
    assert [m["record_id"] for m in client.get("/materials").json()] == [APPROVED]
    client.post(f"/records/{FLAGGED}/approve", json={})
    assert [m["record_id"] for m in client.get("/materials").json()] == [FLAGGED, APPROVED]


# --- AC7: setup files exist without secrets -----------------------------------

def test_ac7_requirements_are_pinned_and_env_example_has_no_secrets():
    requirements = [line.strip() for line in
                    (PROTOTYPE / "requirements.txt").read_text().splitlines()
                    if line.strip() and not line.startswith("#")]
    assert requirements and all("==" in line for line in requirements)
    settings = [line for line in (PROTOTYPE / ".env.example").read_text().splitlines()
                if line.strip() and not line.lstrip().startswith("#")]
    assert settings == ["VALIDATION_DATA_DIR=.data"]


# --- AC8 / AC9: failure cases and the sequence diagram's branches -------------

@pytest.mark.parametrize("value, unit, message", [
    ("abc", None, "Enter a plain number"),
    ("NaN", None, "Enter a plain number"),
    ("1e3", None, "Enter a plain number"),
    ("1_000", None, "Enter a plain number"),
    ("\u0661\u0662\u0663", None, "Enter a plain number"),
    ("-5", None, "Enter a plain number"),
    ("5000", None, "between 50 and 3000 MPa"),
    ("850", "ksi", "Unit must be MPa"),
])
def test_ac8_automatic_checks_reject_bad_values(client, value, unit, message):
    response = client.put(f"/records/{FLAGGED}/draft",
                          json={"values": [{"value_id": 1, "value": value, "unit": unit}]})
    assert response.status_code == 422
    assert message in response.json()["errors"]["value:1"]
    assert store(client).property_values(FLAGGED)[0]["value"] == "850"


def test_ac8_material_id_is_required_and_foreign_values_are_refused(client):
    response = client.put(f"/records/{FLAGGED}/draft", json={
        "material_code": "  ", "values": [{"value_id": 4, "value": "1"}]})
    errors = response.json()["errors"]
    assert response.status_code == 422
    assert errors["material_code"] == "Material ID is required"
    assert errors["value:4"] == "Not an editable value of this record"


def test_ac9_approve_with_open_flags_lists_them(client):
    response = client.post(f"/records/{FLAGGED}/approve", json={})
    assert response.status_code == 409
    assert response.json()["code"] == "flags_open"
    assert len(response.json()["open_flags"]) == 2
    assert store(client).get_record(FLAGGED)["review_status"] == "FLAGGED"


def test_ac9_approve_refused_when_source_cannot_be_checked(client):
    # Resolve record 3's flag first so only the missing PDF stands in the way.
    draft = client.put(f"/records/{NO_SOURCE}/draft",
                       json={"values": [{"value_id": 7, "value": "410", "confirm": True}]})
    assert draft.status_code == 200 and draft.json()["open_flags"] == []
    response = client.post(f"/records/{NO_SOURCE}/approve", json={})
    assert response.status_code == 409
    assert response.json()["code"] == "source_unavailable"


def test_ac9_source_check_comes_before_flag_check(client):
    # Diagram order: already decided, then source, then flags.
    response = client.post(f"/records/{NO_SOURCE}/approve", json={})
    assert response.json()["code"] == "source_unavailable"


def test_ac9_already_decided_comes_before_source_check(client):
    record = store(client).get_record(APPROVED)
    (documents(client).folder / record["s3_object_key"]).unlink()
    assert client.post(f"/records/{APPROVED}/approve", json={}).json()["code"] == "already_decided"


def test_ac9_store_rechecks_inside_the_transaction(client):
    # A stale page or second tab: the app's pre-checks are bypassed, and the
    # store itself must still refuse.
    with pytest.raises(AlreadyDecided):
        store(client).approve(APPROVED, fixtures.DEMO_REVIEWER_ID)
    with pytest.raises(FlagsStillOpen):
        store(client).approve(FLAGGED, fixtures.DEMO_REVIEWER_ID)
    with pytest.raises(AlreadyDecided):
        store(client).save_draft(APPROVED, fixtures.DEMO_REVIEWER_ID,
                                 Draft(values=[ValueChange(8, None)]))
    assert store(client).get_record(FLAGGED)["review_status"] == "FLAGGED"
    assert not store(client)._conn.in_transaction


def test_ac9_rejected_record_is_read_only(client):
    store(client).execute("UPDATE MATERIAL_RECORD SET review_status = 'REJECTED' WHERE record_id = ?",
                          (PENDING,))
    assert client.get(f"/records/{PENDING}").json()["read_only"] is True
    assert client.post(f"/records/{PENDING}/approve", json={}).json()["code"] == "already_decided"


@pytest.mark.parametrize("method, path", [
    ("get", "/records/999"), ("get", "/records/999/pdf"), ("put", "/records/999/draft"),
    ("post", "/records/999/approve"), ("get", "/manager/records/999/audit-events"),
    ("get", "/records/99999999999999999999999"), ("get", "/records/0"),
])
def test_ac8_unknown_records_are_404(client, method, path):
    assert client.request(method, path, json={}).status_code == 404


def test_ac8_writes_must_be_json(client):
    # A plain form post (what another website could send) is refused.
    response = client.post(f"/records/{PENDING}/approve", data={"x": "1"})
    assert response.status_code == 415
    assert store(client).get_record(PENDING)["review_status"] == "PENDING"
    assert client.post("/demo/reset", data={"x": "1"}).status_code == 415


def test_ac8_malformed_draft_gets_the_same_error_shape(client):
    response = client.put(f"/records/{FLAGGED}/draft", json={"values": [{"value_id": "x"}]})
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_request"
    long_value = client.put(f"/records/{FLAGGED}/draft",
                            json={"values": [{"value_id": 1, "value": "1" * 41}]})
    assert long_value.json()["errors"]["value:1"].startswith("Value is longer than 40")


def test_ac8_duplicate_value_is_refused(client):
    response = client.put(f"/records/{FLAGGED}/draft", json={"values": [
        {"value_id": 1, "value": "850"}, {"value_id": 1, "value": "851"}]})
    assert response.json()["errors"]["value:1"] == "This value is listed twice in the draft"


def test_ac7_reset_refuses_a_folder_it_did_not_create(tmp_path):
    (tmp_path / "s3").mkdir()
    (tmp_path / "s3" / "precious.txt").write_text("keep me")
    with pytest.raises(DataDirNotSafe):
        create_app(tmp_path)
    assert (tmp_path / "s3" / "precious.txt").read_text() == "keep me"


def test_ac9_decided_record_is_read_only_and_cannot_change(client):
    body = client.get(f"/records/{APPROVED}").json()
    assert body["read_only"] is True
    assert "pdf_url" not in body["source"]
    draft = client.put(f"/records/{APPROVED}/draft", json={"values": [{"value_id": 8, "value": "1"}]})
    assert draft.status_code == 409 and draft.json()["code"] == "already_decided"
    again = client.post(f"/records/{APPROVED}/approve", json={})
    assert again.status_code == 409 and again.json()["code"] == "already_decided"


def test_ac9_cannot_approve_twice(client):
    assert client.post(f"/records/{PENDING}/approve", json={}).status_code == 200
    assert client.post(f"/records/{PENDING}/approve", json={}).json()["code"] == "already_decided"


def test_ac7_demo_reset_restores_fixtures(client):
    client.post(f"/records/{PENDING}/approve", json={})
    client.post("/demo/reset", json={})
    assert store(client).get_record(PENDING)["review_status"] == "PENDING"


def test_ac8_storage_read_failure_is_503(client, monkeypatch):
    # A read that fails (for example a locked database) is reported like a
    # failed write: 503, try again; never a 500.
    import sqlite3

    def locked(*_args, **_kwargs):
        raise sqlite3.OperationalError("database is locked")
    monkeypatch.setattr(store(client), "_query", locked)
    response = client.get(f"/records/{FLAGGED}")
    assert response.status_code == 503
    assert response.json()["code"] == "storage_unavailable"


def test_ac8_json_check_ignores_case_and_parameters(client):
    response = client.post(f"/records/{PENDING}/approve", content=b"{}",
                           headers={"Content-Type": "Application/JSON; charset=utf-8"})
    assert response.status_code == 200
