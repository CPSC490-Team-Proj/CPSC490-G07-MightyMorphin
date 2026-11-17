# Specification — Goal 1: Snowflake Setup and Document Ingestion/Validation

Epic: [#11](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/11) · Stories: [#12](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/12), [#13](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/13), [#14](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/14), [#15](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/15), [#16](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/16)<br>
Owner: Liam Wilson · Sprint: 3 · Status: draft

## Scope

**In scope.** A Snowflake account hosted on AWS; an AWS EC2-hosted application or processing component that connects to Snowflake; Snowflake development-environment setup; supported PDF intake; processing handoff; digital-PDF extraction; scanned-PDF Snowflake OCR; candidate-record normalization; unsupported-document and processing-failure handling; validation; and authorized review/approval.

**Out of scope.** Permanent storage of original PDFs, document metadata, candidate records, review history, and approved material data. Goal 2 stores those records and performs Snowflake insertion after approval.

## Functional requirements

| ID | Requirement | Story |
|---|---|---|
| FR-1 | The system shall provide a Snowflake account hosted on AWS with a development database, schema, warehouse, roles, least-privilege grants, and secure connection configuration for later approved-material storage. | [#12](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/12) |
| FR-1a | The application or document-processing component shall run on a sponsor-approved AWS EC2 instance and connect to Snowflake using the approved secure configuration. | [#12](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/12) |
| FR-2 | When an authorized user uploads a supported CoC or material test-report PDF, the system shall validate the upload, generate an intake reference and checksum, and submit the document for automated processing. | [#13](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/13) |
| FR-3 | When an uploaded PDF contains embedded text, the system shall route it to digital extraction; when it is scanned, the system shall route it to the OCR extraction path. | [#13](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/13) |
| FR-4 | When a supported document is processed, the system shall extract material identifiers, vendor information, lot information, material-property values, and units into a normalized candidate record. | [#14](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/14) |
| FR-5 | When a scanned PDF is processed, the system shall run Snowflake OCR three times and retain the confidence result from each run. If the document does not meet the 90% confidence threshold after the third run, the system shall flag the document for reviewer attention. | [#14](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/14) |
| FR-6 | When a document is corrupt, encrypted, unreadable, unsupported, or unsuccessfully processed, the system shall return an actionable failure result and shall not represent the document as successfully processed. | [#15](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/15) |
| FR-7 | When a candidate record contains missing, malformed, incompatible-unit, out-of-range, or unresolved low-confidence values, the system shall flag the record for reviewer attention. | [#16](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/16) |
| FR-8 | When an authorized reviewer approves, rejects, or corrects a candidate record, the system shall pass the approved candidate data or review outcome to Goal 2 for permanent storage. | [#16](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/16) |

## Non-functional requirements

| ID | Requirement | Why it matters here |
|---|---|---|
| NFR-1 | Snowflake credentials shall be supplied through secure environment-based configuration and shall not be committed to the repository. | Protects Snowflake access credentials. |
| NFR-2 | OCR confidence results from all three runs and the resulting document-review flag shall be available to the reviewer and downstream storage workflow. | Makes the 90% confidence decision auditable. |
| NFR-3 | The system shall provide a clear intake, processing, unsupported-document, extraction-failure, low-confidence, or review-required result for every submitted document. | Users need actionable processing feedback. |
| NFR-4 | Upload, processing, and review actions shall be restricted to authorized users or services. | Material documents and their extracted data may be sensitive. |

## Acceptance criteria (epic level)

- [ ] The Snowflake account is hosted on AWS, and the application or processing component runs on the approved AWS EC2 instance.
- [ ] The Snowflake development environment and material-data schema are configured without committing credentials.
- [ ] An authorized user can upload a supported PDF and receive a processing handoff result.
- [ ] Digital PDFs follow the text-extraction path and scanned PDFs follow the OCR path.
- [ ] Snowflake OCR runs three times for a scanned PDF; documents below 90% confidence after the third run are flagged for review.
- [ ] A supported document produces a normalized candidate material record.
- [ ] Unsupported, unusable, and failed documents return a recorded actionable result.
- [ ] Reviewers can correct, approve, or reject candidate records.
- [ ] No document, candidate, review, or approved material business record is permanently stored by this goal.
- [ ] Tests cover FR-1 through FR-8 and the applicable non-functional requirements.
- [ ] `python .github/scripts/check_repo.py` is green and the prototype's tests pass.

## Open questions

| Question | Owner | Needed by |
|---|---|---|
| How should the three OCR confidence results be combined to determine whether a document meets the 90% threshold? | Sponsor and team | Before FR-5 implementation |
| Which document layouts, fields, units, and plausible ranges are approved for the first release? | Sponsor and team | Before FR-4 and FR-7 implementation |
| Which reviewer roles may correct, approve, and reject candidate records? | Sponsor and team | Before FR-8 implementation |
