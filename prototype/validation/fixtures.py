"""Synthetic demo data: four records and generated PDFs.

Nothing here comes from Edwards. Material IDs, lots, vendors and values are
invented for the demo, and every generated PDF is stamped as a synthetic
sample. The extraction step is mocked: the values below stand in for what the
OCR passes would have produced, with a made-up confidence for each.

Record 1  FLAGGED   low-confidence tensile strength, missing elongation (the wireframe example)
Record 2  PENDING   no flags, ready to approve
Record 3  FLAGGED   its PDF copy is missing from storage, so it cannot be approved
Record 4  APPROVED  opens read-only
"""

from __future__ import annotations

from .documents import DocumentStore, checksum
from .store import Store

SYNTHETIC_MARK = "SYNTHETIC SAMPLE - NOT A REAL CERTIFICATE"
DEMO_REVIEWER_ID = 1
EXTRACTED_AT = "2026-11-20T16:00:00Z"
APPROVED_AT = "2026-11-21T17:30:00Z"

PROPERTY_TYPES = [
    ("Tensile strength", "MPa"),
    ("Yield strength", "MPa"),
    ("Elongation", "%"),
]

# (record_id, filename, doc_type, input_type, vendor, material, lot, status,
#  values [(property, value or None, confidence, flag_reason or None)],
#  printed values shown in the PDF, store the PDF?)
RECORDS = [
    (1, "vendor-coc-001.pdf", "COC", "SCANNED", "Example Vendor A", "M-001", "L-021", "FLAGGED",
     [("Tensile strength", "850", 0.72, "Low confidence"),
      ("Elongation", None, 0.0, "Missing value")],
     [("Tensile strength", "850 MPa"), ("Elongation", "18 %")], True),
    (2, "vendor-test-report-002.pdf", "TEST_REPORT", "DIGITAL", "Example Vendor B", "M-002", "L-105", "PENDING",
     [("Tensile strength", "910", 0.97, None),
      ("Yield strength", "780", 0.95, None),
      ("Elongation", "14", 0.96, None)],
     [("Tensile strength", "910 MPa"), ("Yield strength", "780 MPa"), ("Elongation", "14 %")], True),
    (3, "vendor-coc-003.pdf", "COC", "SCANNED", "Example Vendor A", "M-003", "L-330", "FLAGGED",
     [("Tensile strength", "640", 0.93, None),
      ("Yield strength", "410", 0.81, "Low confidence")],
     [("Tensile strength", "640 MPa"), ("Yield strength", "410 MPa")], False),
    (4, "vendor-coc-004.pdf", "COC", "DIGITAL", "Example Vendor B", "M-004", "L-412", "APPROVED",
     [("Tensile strength", "720", 0.98, None),
      ("Elongation", "22", 0.97, None)],
     [("Tensile strength", "720 MPa"), ("Elongation", "22 %")], True),
]


def make_pdf(title: str, lines: list[str], page_two: list[str]) -> bytes:
    """Build a small, valid two-page PDF using only the standard library."""

    def page_stream(text_lines: list[str]) -> bytes:
        out = ["BT", "/F1 12 Tf", "16 TL", "56 760 Td"]
        for line in text_lines:
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            out.append(f"({safe}) Tj T*")
        out.append("ET")
        return "\n".join(out).encode("latin-1")

    pages = [page_stream([title, SYNTHETIC_MARK, "", *lines]),
             page_stream([title + " (page 2)", SYNTHETIC_MARK, "", *page_two])]
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [4 0 R 6 0 R] /Count 2 >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    for index, stream in enumerate(pages):
        content_ref = 5 + index * 2
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_ref} 0 R >>".encode()
        )
        objects.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(pdf)
    pdf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        pdf += b"%010d 00000 n \n" % offset
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    return bytes(pdf)


def load(store: Store, documents: DocumentStore) -> None:
    """Create the schema and the four demo records."""
    store.create_schema()
    role = store.execute("INSERT INTO ROLE (name) VALUES ('R_AND_D')")
    store.execute(
        "INSERT INTO APP_USER (user_id, role_id, email, display_name) VALUES (?, ?, ?, ?)",
        (DEMO_REVIEWER_ID, role, "demo.reviewer@example.com", "Demo Reviewer"),
    )
    for name, unit in PROPERTY_TYPES:
        store.execute("INSERT INTO PROPERTY_TYPE (name, standard_unit) VALUES (?, ?)", (name, unit))
    for (record_id, filename, doc_type, input_type, vendor, material, lot, status,
         values, printed, keep_pdf) in RECORDS:
        pdf = make_pdf(
            f"{'Certificate of Conformance' if doc_type == 'COC' else 'Test report'} - {filename}",
            [f"Vendor: {vendor}", f"Material ID: {material}", f"Lot number: {lot}", "",
             "Mechanical properties"] + [f"  {name}: {shown}" for name, shown in printed],
            ["Illustrative values for the CPSC 490 page 3 prototype.",
             "Not derived from any real certificate or test report."],
        )
        object_key = f"source-documents/{record_id:04d}-{filename}"
        # The checksum is recorded either way; record 3's PDF copy is left
        # out of storage to demonstrate a missing source.
        if keep_pdf:
            documents.put(object_key, pdf)
        document_id = store.add_source_document(
            filename=filename, doc_type=doc_type, input_type=input_type,
            s3_object_key=object_key, checksum=checksum(pdf),
            uploaded_by=DEMO_REVIEWER_ID, vendor=vendor, uploaded_at=EXTRACTED_AT,
        )
        # Mocked extraction: the fixture values stand in for the OCR passes.
        created = store.add_extracted_record(document_id, material, lot, values, EXTRACTED_AT)
        if created != record_id:
            raise RuntimeError("fixture record ids must stay 1-4")
        if status == "APPROVED":
            store.approve(record_id, DEMO_REVIEWER_ID, APPROVED_AT)
        elif store.get_record(record_id)["review_status"] != status:
            raise RuntimeError(f"fixture record {record_id}: flags do not give status {status}")
