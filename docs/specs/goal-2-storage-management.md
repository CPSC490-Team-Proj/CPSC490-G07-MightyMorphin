# Specification — Goal 2: Material and Source-Document Storage

Epic: [#17](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/17) · Stories: [#18](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/18), [#19](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/19), [#20](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/20), [#21](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21)<br>
Owner: Liam Wilson · Sprint: 3 · Status: draft

## Scope

**In scope.** Permanent storage of original CoCs and material test reports in an AWS S3 bucket; operational storage of document metadata, workflow status, candidate records, OCR confidence, validation results, review history, and source-document references; Snowflake insertion of approved material data; ingestion events; duplicate prevention; retry handling; and source-to-record traceability.

**Out of scope.** Document intake, extraction/OCR, validation implementation, and reviewer-interface implementation, which are covered by Goal 1; and user search, viewing, comparison, and analysis, which are covered by Goal 3.

## Functional requirements

| ID | Requirement | Story |
|---|---|---|
| FR-1 | When Goal 1 accepts a document, the system shall permanently store the original PDF without modification in the approved AWS S3 bucket and retain its document ID, checksum, filename, uploader, upload time, document type, S3 object key, and storage reference. | [#18](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/18) |
| FR-2 | When a source-document storage operation fails, the system shall record the failure and shall not represent the document as successfully stored. | [#18](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/18) |
| FR-3 | When Goal 1 returns a document-processing or review outcome, the operational database shall store its status, processing attempts, errors, retry count, timestamps, OCR confidence results, and responsible user where applicable. | [#19](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/19) |
| FR-4 | When Goal 1 returns a candidate record, the system shall store material identifiers, vendor, lot, source type, property values, units, normalized values, original extracted values where applicable, and validation results. | [#19](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/19) |
| FR-5 | When Goal 1 returns a reviewer decision, the system shall store the approval or rejection decision, reviewer, timestamp, and corrections. | [#20](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/20) |
| FR-6 | When a candidate record is approved, the system shall insert its material information, property values, units, and source-document reference into Snowflake and retain the resulting Snowflake record ID. | [#20](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/20) |
| FR-7 | When a candidate record is pending review, invalid, rejected, or has unresolved low-confidence fields, the system shall prevent it from being stored in Snowflake as approved material data. | [#20](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/20) |
| FR-8 | When Snowflake ingestion is attempted, the system shall record the outcome and link the document, candidate record, reviewer decision, ingestion event, and Snowflake record ID. | [#21](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21) |
| FR-9 | When an identical approved record revision is submitted more than once, the system shall prevent duplicate Snowflake records; when a retryable ingestion failure occurs, the system shall retry within the configured limit and record each attempt. | [#21](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21) |

## Non-functional requirements

| ID | Requirement | Why it matters here |
|---|---|---|
| NFR-1 | The operational database shall enforce keys, relationships, and integrity constraints that prevent orphaned documents, records, review events, and ingestion events. | Maintains complete source-to-record traceability. |
| NFR-2 | The AWS S3 bucket and source-document retrieval service shall require authorization based on assigned user role. | Protects source documents and review information. |
| NFR-3 | A failed multi-record operational-database or Snowflake write shall not leave a partial approved material record or broken traceability link. | Prevents inconsistent storage state. |
| NFR-4 | The system shall retain the original S3 object, its object key, and checksum so authorized users can verify that it has not been silently replaced. | Protects the evidence supporting material records. |

## Acceptance criteria (epic level)

- [ ] Accepted source documents are permanently stored in the approved AWS S3 bucket with unique identifiers, checksums, metadata, object keys, and retrievable storage references.
- [ ] Candidate records, OCR confidence, validation results, workflow status, and reviewer decisions are stored in the operational database.
- [ ] Only approved records are inserted into Snowflake.
- [ ] Approved Snowflake records contain material data, property values, units, and source-document references.
- [ ] Snowflake record IDs and ingestion outcomes are retained with their related operational records.
- [ ] Duplicate ingestion is prevented and retryable failures are retried and recorded.
- [ ] Authorized users can trace an approved Snowflake record to its candidate record and original source document.
- [ ] Tests cover FR-1 through FR-9 and the applicable non-functional requirements.
- [ ] `python .github/scripts/check_repo.py` is green and the prototype's tests pass.

## Open questions

| Question | Owner | Needed by |
|---|---|---|
| Which AWS S3 bucket, retention period, encryption configuration, and deletion policy are approved by the sponsor? | Sponsor and team | Before FR-1 implementation |
| What record revision rule should be used with the document checksum for duplicate prevention? | Sponsor and team | Before FR-9 implementation |
| What retry limit and delay are acceptable for temporary Snowflake failures? | Sponsor and team | Before FR-9 implementation |
