# Specification — Goal 3: Material Search, Viewing, and Analysis

Epic: [#22](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/22) · Stories: [#23](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/23), [#24](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/24), [#25](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/25), [#26](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/26), [#27](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/27) <br>
Owner: Liam Wilson · Sprint: 3 · Status: draft

## Scope

**In scope.** Authorized access to the internal application; search and filtering of approved Snowflake material records; viewing material properties, units, source-document references, and available review context; comparing selected approved records; and displaying compatible property trends and ranges.

**Out of scope.** Document upload, extraction/OCR, candidate validation, reviewer correction, source-document storage, operational workflow storage, and Snowflake ingestion. These are covered by Goals 1 and 2.

## Functional requirements

| ID | Requirement | Story |
|---|---|---|
| FR-1 | When an authorized user authenticates through the approved internal identity flow, the system shall provide access to the material-data application. | [#23](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/23) |
| FR-2 | When a user lacks the role required for a protected action, record, source-document reference, or review-history item, the system shall deny the request and provide appropriate feedback. | [#23](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/23) |
| FR-3 | When an authorized user searches by a supported material identifier, vendor, lot, or source type, the system shall display matching approved Snowflake records. | [#24](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/24) |
| FR-4 | When an authorized user applies supported material-property, vendor, document-type, or date filters, the system shall display only approved records matching all selected criteria. | [#24](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/24) |
| FR-5 | When no approved records match a search or filter request, the system shall display a no-results message. | [#24](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/24) |
| FR-6 | When a user selects an approved material record, the system shall display material identity, vendor, lot, source type, property values, units, source-document reference, and available review and ingestion context. | [#25](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/25) |
| FR-7 | When a user selects multiple approved records for comparison, the system shall display corresponding property values and units side by side and identify missing or incompatible values. | [#26](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/26) |
| FR-8 | When selected records contain compatible values for a supported property, the system shall display the selected trend or range visualization; otherwise, it shall explain why visualization is unavailable. | [#27](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/27) |

## Non-functional requirements

| ID | Requirement | Why it matters here |
|---|---|---|
| NFR-1 | The system shall display stored numeric property values without unintended rounding or loss of precision and shall show the unit for each value. | Engineering decisions depend on correctly interpreted values. |
| NFR-2 | The application shall apply assigned permissions before displaying protected material data, source-document references, or review context. | Protects material and document information. |
| NFR-3 | The system shall provide clear loading, no-results, missing-data, incompatible-unit, and retrieval-failure feedback. | Users need to distinguish lack of data from an application failure. |
| NFR-4 | The system shall measure search, comparison, and visualization response time against a sponsor-approved target and representative approved dataset. | Performance claims must be measurable. |

## Acceptance criteria (epic level)

- [ ] Authorized users can access the internal material-data application; unauthorized users cannot access protected actions or records.
- [ ] Users can search and filter approved material records using supported criteria.
- [ ] Users can view material identity, property values, units, source-document reference, and available review context.
- [ ] Users can select multiple approved records and compare compatible values side by side.
- [ ] Users can view supported trend or range visualizations for compatible selected values.
- [ ] The application explains empty results, missing data, incompatible units, and retrieval failures.
- [ ] Tests cover FR-1 through FR-8 and the applicable non-functional requirements.
- [ ] `python .github/scripts/check_repo.py` is green and the prototype's tests pass.

## Open questions

| Question | Owner | Needed by |
|---|---|---|
| Which identity provider and role definitions are approved for the internal application? | Sponsor and team | Before FR-1 and FR-2 implementation |
| Which search fields, filters, and source-document details may be shown to each role? | Sponsor and team | Before FR-3 through FR-6 implementation |
| Which properties, units, chart types, and response-time targets are approved for the first analysis release? | Sponsor and team | Before FR-7, FR-8, and NFR-4 implementation |
