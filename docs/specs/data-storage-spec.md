# Specification — Data Storage

> Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Stories: [#58](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/58)
> Owner: Liam Wilson · Sprint: 2 · Status: draft

## Scope

**In scope.** Database designed in a relational schema, maintain reference to source document, hosted on AWS, data is able to be inserted, retrievied, and updated without direct access to the database.

**Out of scope** Docuemnt extraction, data analysis, on-site storage solution, storing source document.

## Functional requirements
| ID | Requirement | Story |
|---|---|---|
| FR-1 | When data is stored the system shall maintain a reference to the source document| [[story#20]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21) |
| FR-2 | When verified structured material information is received from the extraction workflow, the system shall store the information in the relational database.| [[story:#21]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21) |
| FR-3 |When an authorized user submits changes to an existing material record, the system shall update the corresponding database information.| [[story:#21]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21) |
| FR-4 | When an authorized user requests the removal of an existing material record, the system shall delete or deactivate the corresponding database record according to the defined retention policy. | [[story:#21]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21) |
| FR-5 | When an authorized user creates, retrieves, updates, or deletes a material record, the system shall record the user identifier, operation type, affected record, and timestamp in an audit log. | [[story:#21]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21) |
| FR-6 | When an authorized user requests an existing material record by its identifier, the system shall retrieve the corresponding information from the database. | [[story:#21]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21) |
| FR-7 | When an authorized user submits a new material record, the system shall insert the information into the database. | [[story:#21]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21) |


## Non-functional requirements

| ID | Requirement | Why it matters here |
|---|---|---|
| NFR-1 | he database shall use a relational schema with primary keys, foreign keys, and appropriate integrity constraints.| Maintains consistent relationships between stored material records.|
| NFR-2 | Database access shall require authentication, and modification privileges shall be restricted according to authorized user roles. | Protects stored material information from unauthorized access and modification. |
| NFR-3 | The database service shall maintain at least 95% availability during defined business hours, measured monthly.| Supports reliable access to material information during business operations. |
| NFR-4 | Committed database transactions shall remain persistent after application restarts.| Prevents unintended loss of stored material information.|

## Acceptance criteria (epic level)
- [ ] Users with permissions can insert, access, update, and delete records in the database
- [ ] Datebase is deployed and accessible through the web app on AWS
- [ ] Users can view source documents when accessing records
- [ ] Unauthorized user cannot access or modify and records on the database
- [ ] Tests written for all functional and non-functional requirments pass
- [ ] `python .github/scripts/check_repo.py` is green and the prototype's tests pass.

## Open questions

| Question | Owner | Needed by |
|---|---|---|
| How should duplicate rocrds be handled? | Liam Wilson | Before FR-1 and FR-2 inplimentation |
| How long should audit logs be reteained? | Liam Wilson |Before database implementation|


