# Specification — Data Extraction

Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Stories: [#46](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/46)<br>
Owner: Liam Wilson · Sprint: 2 · Status: draft

## Scope

**In scope.** PDF ingestion, digital PDF text extraction, scanned PDF OCR, extraction across multiple document layouts, structured data output, validation of extracted information, and flagging uncertain or invalid results for review.

**Out of scope** Non-PDF formats, storing structured data, material data analysis, automated invalid data corrections, store documents after ingestion.

## Functional requirements
| ID | Requirement | Story |
|---|---|---|
| FR-1| When a user uploads a supported PDF document the system shall accept the document for automated ingestion | [#12](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/12) |
| FR-2 | When a user uploads a scanned images the system shall apply OCR to convert and extract data into a structured searchable format| [#14](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/14)|
| FR-3 | When a user uploads an unsupported PDF document the system shall flag the document as an unsupported document and reject the document from the automated pipeline | [#15](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/15) |
| FR-4 | When data extraction job fails the system shall flag the invalid field for additional review | [#16](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/16) |


## Non-functional requirements

| ID | Requirement | Why it matters here |
|---|---|---|
| NFR-1 |The system shall maintain a minimum of 95% field-level extraction accuracy for PDF documents|Misextracted data can cause manufacture and design failures down the line|
| NFR-2 | The system shall maintain a minimum of 90% character accuracy for OCR on scanned docuemnts| Misextracted data can cause manufacture and design failures down the line|


## Acceptance criteria (epic level)

- [ ] Users with permissions can upload PDF documents
- [ ] Tests written for all functional and non-functional requirments pass
- [ ] `python .github/scripts/check_repo.py` is green and the prototype's tests pass.

## Open questions

| Question | Owner | Needed by |
|---|---|---|
| Does the sponsor require data from documents to be extracted in a certain time frame? | Liam Wilson | Sprint 3 planning |
| Should the system have a file size limit | Liam Wilson | before FR-1 is implemented |