# Specification — Goal 1: Snowflake Setup and Document Ingestion

> Epic: [#11](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/11) · Stories: [#12](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/12), [#13](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/13), [#14](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/14), [#15](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/15), [#16](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/16)
> Owner: Liam Wilson · Sprint: TBD · Status: draft

## Scope

**In scope.** Snowflake development-environment setup; a schema for approved material data, property values, source-document references, and ingestion events; supported PDF upload; creation of document-processing jobs; routing of digital and scanned PDFs; ingestion of approved records into Snowflake; and ingestion status, duplicate prevention, and retry handling.

**Out of scope.** Long-term storage of original PDF files, operational document metadata storage, extraction implementation, human review implementation, and user-facing material search and analysis. These are covered by Goals 2 and 3.

## Functional requirements

| ID | Requirement | Story |
|---|---|---|
| FR-1 | The system shall provide a Snowflake development database, schema, warehouse, roles, and least-privilege grants required for approved material-data ingestion. | [#12](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/12) |
| FR-2 | When an authorized user uploads a supported CoC or material test report, the system shall create a document-processing job with a document identifier, checksum, and initial status. | [#13](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/13) |
| FR-3 | When an uploaded PDF contains an embedded text layer, the system shall route it to the digital extraction path; when it is scanned, the system shall route it to the OCR extraction path. | [#13](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/13) |
| FR-4 | When an approved candidate material record is received, the system shall ingest its material information, property values, units, and source-document reference into Snowflake. | [#14](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/14) |
| FR-5 | When a candidate record is pending review, invalid, or rejected, the system shall prevent that record from being ingested into Snowflake. | [#14](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/14) |
| FR-6 | When an ingestion attempt completes, the system shall record the outcome, timestamp, error details if applicable, and Snowflake record identifier. | [#15](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/15) |
| FR-7 | When the same approved document revision is submitted more than once, the system shall prevent duplicate Snowflake records by using an idempotency key. | [#16](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/16) |
| FR-8 | When a retryable Snowflake-ingestion failure occurs, the system shall retry the ingestion within the configured retry limit and record every attempt. | [#16](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/16) |

## Non-functional requirements

| ID | Requirement | Why it matters here |
|---|---|---|
| NFR-1 | Snowflake connection settings and credentials shall be supplied through secure environment-based configuration and shall not be committed to the repository. | Protects Snowflake access credentials. |
| NFR-2 | The Snowflake schema shall enforce record identity, relationship, and uniqueness constraints appropriate to the approved material-data model. | Prevents duplicate and inconsistent material records. |
| NFR-3 | The ingestion service shall report a clear success, validation failure, duplicate, or service-failure outcome for every request. | Makes ingestion failures actionable and auditable. |
| NFR-4 | Upload, processing-status, and ingestion actions shall be restricted to authorized users or services. | Protects potentially sensitive material information. |

## Acceptance criteria (epic level)

- [ ] A configured development Snowflake environment accepts approved material records through the application ingestion service.
- [ ] An authorized user can upload a supported PDF and receive a document-processing result.
- [ ] Digital and scanned PDFs are routed to their appropriate extraction paths.
- [ ] An approved candidate record is stored in Snowflake with its properties, units, and source-document reference.
- [ ] Pending, invalid, and rejected records cannot be ingested into Snowflake.
- [ ] Duplicate requests do not create duplicate Snowflake records.
- [ ] Retryable failures are recorded and retried within the configured limit.
- [ ] Tests cover FR-1 through FR-8 and the applicable non-functional requirements.
- [ ] `python .github/scripts/check_repo.py` is green and the prototype's tests pass.

## Open questions

| Question | Owner | Needed by |
|---|---|---|
| Which Snowflake account, role model, warehouse size, and network restrictions are approved by the sponsor? | Sponsor and team | Before FR-1 implementation |
| Which fields constitute the stable identity and revision of an approved material record for idempotency? | Sponsor and team | Before FR-7 implementation |
| What retry limit and delay are acceptable for temporary Snowflake failures? | Sponsor and team | Before FR-8 implementation |
