"""Tests for source-document traceability (#109).

Each test name starts with ``test_dodN_``, where N is the position (1-4) of
the #109 "Definition of done" item it checks:

1. Store the AWS/S3 document reference and distinguish CoC from test-report sources.
2. Retrieve the source association with its Snowflake material record.
3. Keep source references through extraction, validation, review, and approval transitions.
4. Test persistence and retrieval of the reference.

Snowflake is SQLite and S3 is a local folder in the prototype (see README).
"""

from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient

from validation import fixtures
from validation.app import DB_FILE, create_app
from validation.documents import checksum
from validation.store import RecordNotFound, Store

FLAGGED, PENDING, NO_SOURCE, APPROVED = 1, 2, 3, 4
REVIEWER = fixtures.DEMO_REVIEWER_ID


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "data")) as test_client:
        yield test_client


def store(client) -> Store:
    return client.app.state.data["store"]


def reference(client, record_id):
    """The fields that make up a record's link to its PDF."""
    source = store(client).source_reference(record_id)
    return (source["document_id"], source["s3_object_key"], source["checksum"], source["doc_type"])


def new_document(client, key="source-documents/9001-extra.pdf", doc_type="COC"):
    pdf = fixtures.make_pdf("Extra", ["Material ID: M-900"], ["page two"])
    client.app.state.data["documents"].put(key, pdf)
    return store(client).add_source_document(
        filename="extra.pdf", doc_type=doc_type, input_type="DIGITAL", s3_object_key=key,
        checksum=checksum(pdf), uploaded_by=REVIEWER, vendor=None)


# --- DoD 1: store the S3 reference and the source type ------------------------

def test_dod1_every_record_stores_its_s3_key_checksum_and_type(client):
    for record_id in (FLAGGED, PENDING, NO_SOURCE, APPROVED):
        source = store(client).source_reference(record_id)
        assert source["s3_object_key"].startswith("source-documents/")
        assert source["checksum"].startswith("sha256:")
        assert source["doc_type"] in ("COC", "TEST_REPORT")


def test_dod1_coc_and_test_report_are_distinguished(client):
    assert store(client).source_reference(FLAGGED)["doc_type"] == "COC"
    assert store(client).source_reference(PENDING)["doc_type"] == "TEST_REPORT"
    assert new_document(client, doc_type="TEST_REPORT")
    with pytest.raises(sqlite3.IntegrityError):
        new_document(client, key="source-documents/9002-bad.pdf", doc_type="INVOICE")


def test_dod1_one_s3_object_belongs_to_one_document(client):
    taken = store(client).source_reference(FLAGGED)["s3_object_key"]
    with pytest.raises(sqlite3.IntegrityError):
        new_document(client, key=taken)


# --- DoD 2: retrieve the source with its material record ----------------------

def test_dod2_source_endpoint_returns_the_association(client):
    body = client.get(f"/records/{PENDING}/source").json()
    assert body["record_id"] == PENDING
    assert body["filename"] == "vendor-test-report-002.pdf"
    assert body["doc_type"] == "TEST_REPORT"
    assert body["vendor"] == "Example Vendor B"
    assert body["s3_object_key"] == "source-documents/0002-vendor-test-report-002.pdf"
    assert body["copy_check"] == "ok"


def test_dod2_source_endpoint_reports_a_missing_or_replaced_copy(client):
    assert client.get(f"/records/{NO_SOURCE}/source").json()["copy_check"] == "missing"
    key = store(client).source_reference(FLAGGED)["s3_object_key"]
    client.app.state.data["documents"].put(key, b"%PDF-1.4 replaced")
    assert client.get(f"/records/{FLAGGED}/source").json()["copy_check"] == "checksum mismatch"


def test_dod2_unknown_record_has_no_source(client):
    assert client.get("/records/999/source").status_code == 404
    assert store(client).source_reference(999) is None


def test_dod2_approved_materials_carry_their_source(client):
    [item] = client.get("/materials").json()
    assert item["record_id"] == APPROVED
    assert item["source"]["doc_type"] == "COC"
    assert item["source"]["s3_object_key"] == "source-documents/0004-vendor-coc-004.pdf"


def test_dod2_page_3_load_shows_the_stored_copy(client):
    body = client.get(f"/records/{FLAGGED}").json()
    assert body["stored_copy"] == {"s3_object_key": "source-documents/0001-vendor-coc-001.pdf",
                                   "doc_type": "COC"}


# --- DoD 3: the reference survives every transition ----------------------------

def test_dod3_extraction_links_the_new_record_to_its_document(client):
    document_id = new_document(client)
    record_id = store(client).add_extracted_record(
        document_id, "M-900", None, [("Tensile strength", "700", 0.95, None)])
    source = store(client).source_reference(record_id)
    assert source["document_id"] == document_id
    assert source["s3_object_key"] == "source-documents/9001-extra.pdf"
    assert store(client).get_record(record_id)["review_status"] == "PENDING"


def test_dod3_extraction_needs_an_existing_document(client):
    with pytest.raises(RecordNotFound):
        store(client).add_extracted_record(999, "M-900", None,
                                           [("Tensile strength", "700", 0.95, None)])


def test_dod3_reference_unchanged_through_review_and_approval(client):
    before = reference(client, FLAGGED)
    # Validation rejects a bad value: nothing changes.
    rejected = client.put(f"/records/{FLAGGED}/draft",
                          json={"values": [{"value_id": 1, "value": "abc"}]})
    assert rejected.status_code == 422
    assert reference(client, FLAGGED) == before
    # Review: correct values, the material and the lot.
    reviewed = client.put(f"/records/{FLAGGED}/draft", json={
        "material_code": "M-001B", "lot_number": "L-022",
        "values": [{"value_id": 1, "value": "850", "confirm": True},
                   {"value_id": 2, "value": "18"}]})
    assert reviewed.status_code == 200
    assert reference(client, FLAGGED) == before
    # A failed approval is rolled back.
    client.post("/demo/fail-next-write", json={})
    assert client.post(f"/records/{FLAGGED}/approve", json={}).status_code == 503
    assert reference(client, FLAGGED) == before
    # Approval.
    assert client.post(f"/records/{FLAGGED}/approve", json={}).status_code == 200
    assert reference(client, FLAGGED) == before


@pytest.mark.parametrize("sql", [
    "UPDATE MATERIAL_RECORD SET document_id = 2 WHERE record_id = 1",
    "UPDATE SOURCE_DOCUMENT SET s3_object_key = 'elsewhere.pdf' WHERE document_id = 1",
    "UPDATE SOURCE_DOCUMENT SET checksum = 'sha256:0' WHERE document_id = 1",
    "UPDATE SOURCE_DOCUMENT SET doc_type = 'TEST_REPORT' WHERE document_id = 1",
    "DELETE FROM SOURCE_DOCUMENT WHERE document_id = 1",
    "UPDATE SOURCE_DOCUMENT SET document_id = 99 WHERE document_id = 1",
    "UPDATE MATERIAL_RECORD SET record_id = 99 WHERE record_id = 1",
    "DELETE FROM MATERIAL_RECORD WHERE record_id = 1",
    "REPLACE INTO MATERIAL_RECORD (record_id, document_id, material_id, review_status, extracted_at)"
    " VALUES (1, 2, 1, 'FLAGGED', 't')",
    "REPLACE INTO SOURCE_DOCUMENT (document_id, uploaded_by, filename, doc_type, input_type,"
    " s3_object_key, checksum, status, uploaded_at)"
    " VALUES (1, 1, 'x.pdf', 'TEST_REPORT', 'DIGITAL', 'elsewhere.pdf', 'sha256:0', 'DONE', 't')",
])
def test_dod3_database_refuses_to_break_the_link(client, sql):
    before = reference(client, FLAGGED)
    with pytest.raises(sqlite3.IntegrityError):
        store(client).execute(sql)
    assert reference(client, FLAGGED) == before


def test_dod3_link_holds_without_foreign_key_checks(client, tmp_path):
    # Another tool might open the database without turning foreign keys on;
    # the triggers still refuse.
    raw = sqlite3.connect(client.app.state.data["store"]._conn.execute(
        "PRAGMA database_list").fetchone()[2])
    try:
        for sql in ("UPDATE SOURCE_DOCUMENT SET document_id = 99 WHERE document_id = 1",
                    "DELETE FROM MATERIAL_RECORD WHERE record_id = 2"):
            with pytest.raises(sqlite3.IntegrityError):
                raw.execute(sql)
    finally:
        raw.close()
    assert reference(client, FLAGGED)[0] == 1


def test_dod3_extraction_needs_at_least_one_value(client):
    document_id = new_document(client)
    with pytest.raises(ValueError):
        store(client).add_extracted_record(document_id, "M-900", None, [])


# --- DoD 4: persistence and retrieval ------------------------------------------

def test_dod4_reference_is_persisted_to_disk(tmp_path):
    data = tmp_path / "data"
    with TestClient(create_app(data)) as test_client:
        test_client.put(f"/records/{FLAGGED}/draft", json={"values": [
            {"value_id": 1, "value": "850", "confirm": True}, {"value_id": 2, "value": "18"}]})
        test_client.post(f"/records/{FLAGGED}/approve", json={})
        expected = reference(test_client, FLAGGED)
        test_client.app.state.data["store"].close()
    # A fresh connection to the same database file sees the same link.
    reopened = Store(data / DB_FILE)
    source = reopened.source_reference(FLAGGED)
    assert (source["document_id"], source["s3_object_key"], source["checksum"],
            source["doc_type"]) == expected
    assert reopened.get_record(FLAGGED)["review_status"] == "APPROVED"
    reopened.close()
