# Specification — Data Analysis

Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Stories: [#59](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/59)<br>
Owner: Liam Wilson · Sprint: 3 · Status: draft

## Scope

**In scope.** Authorized users can sign in with their Edwards Lifesciences issued Microsoft email.  Searching and filtering data by material or vendor.  Display material properties.  Compare material properties across different stored records.

**Out of scope** Ingesting and extracting data from uploaded documents.  Modifying records in the database.  

## Functional requirements
| ID | Requirement | Story |
|---|---|---|
|FR-1|When an authorized user logs in with their Edwards issued email the system shall redirect user to material database UI|[[story#23]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/23)|
|FR-2|When a user is inactive for a continuous period of 25 minutes the system shall automatically terminate a user session and log the user out| [[story#23]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/23)|
|FR-3| When an authorized user searches for a material using a supported search field, the system shall retrieve and display matching material records. | [[story#24]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/24)  |
|FR-4| When a user applies one or more material filters, the system shall display only records matching the specified criteria | [[story#24]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/24)|
|FR-5|When a user searches for material information that does not match any stored records, the system shall display a message indicating that no matching results were found.|  [[story#24]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/24) |
|FR-6| When a user selects a material record, the system shall display its stored material identification information, specifications, mechanical properties, and processing information. | [[story#26]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/26)  |
|FR-7| When a user selects multiple material records for comparison, the system shall display their corresponding material properties side by side. | [[story#27]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/26)  |
|FR-8|  When a user requests a material analysis, the system shall calculate and display the supported analysis results using stored material information.| [[story#27]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/26)  |

## Non-functional requirements

| ID | Requirement | Why it matters here |
|---|---|---|
| NFR-1 |The system shall not display material properties with unintentional rounding or loss of precision|Maintains accuracy for manufacturing decisions|
| NFR-2 | The system shall clearly display the unit of measure of material properties |Prevent the risk of misinterpreting material property data|
| NFR-3 | The system shall support current versions of web browsers |Ensures users can access the application without specialized software|
|NFR-4|The system shall restrict access to material information according to assigned user permissions|Protects sensitive material data|

## Acceptance criteria (epic level)

- [ ] An authorized user can sign in and access data
- [ ] Authorized users can search for material records using supported search fields.
- [ ] Users can filter material records using defined criteria.
- [ ] Users can view stored material specifications, mechanical properties, and processing information.
- [ ] Users can compare the properties of multiple material records.
- [ ] The system correctly handles searches that return no matching records.
- [ ] Analysis results use accurate stored values and appropriate units of measurement.
- [ ] Tests written for all functional and non-functional requirements pass
- [ ] `python .github/scripts/check_repo.py` is green and the prototype's
      tests pass.

## Open questions

| Question | Owner | Needed by |
|---|---|---|
|Should users be able to export comparison results|Liam Wilson|Before implementation of FR-6 and FR-7|
|What is the acceptable response time for searches and comparisons?|Liam Wilson|Before implementation of FR-3 - FR-5|

