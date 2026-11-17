# Design — Page 5 Analysis Results Sequence

Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Story: [#48](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/48) · Task: [#94](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/94)

Sprint: 3 · Status: draft for teammate review

![Sequence diagram for selecting and analyzing approved material records](analysis-sequence.png)

Page 4 passes selected record IDs to Page 5. Page 5 requests the active property and analysis view; the API checks authentication and permissions, and the analysis service reads only approved records the user may access. Results preserve stored precision and identify units. Trend and range views use dated points and minimum/maximum values, respectively. Unusable values are explained, never silently averaged across incompatible units. A service failure preserves the selection for retry.

This design covers FR-7, FR-8, NFR-1, NFR-2 and NFR-4 in the [analysis specification](../../specs/data-analysis-spec.md). See the [Page 5 wireframe](../ui-wireframe/ui-wireframe-analysis.png) and the [technology decision record](../technology-stack-decision.md). The diagram's **Materials store** represents **Snowflake**, the confirmed database for structured material records. API routes and unit conversion rules are not finalized. Export is deferred to later work.

Paste the Mermaid source below into a Mermaid editor to edit or re-export the diagram. The PNG above is the provided Mermaid export. Independent teammate review is pending.

```mermaid
sequenceDiagram
    actor User as Authorized user
    participant Materials as Page 4 - Materials
    participant UI as Page 5 - Analysis
    participant API as Backend API
    participant Analysis as Analysis service
    participant Store as Materials store

    User->>Materials: Select records and choose Compare
    Materials->>UI: Open Analysis with selected record IDs
    Note over User,UI: Run on entry and repeat when the property or view changes
    UI->>API: Request analysis (record IDs, property, view)
    API->>API: Check session, permissions, and request

    alt Session expired, access denied, or request invalid
        API-->>UI: Return sign-in, access, or validation error
        UI-->>User: Explain what to fix and keep the selection
    else Request authorized and valid
        API->>Analysis: Run selected view within authorized scope
        Analysis->>Store: Read selected approved records in scope
        alt Store read fails
            Store-->>Analysis: Read failure
            Analysis-->>API: Analysis unavailable
            API-->>UI: Service error
            UI-->>User: Offer retry and keep the selection
        else Store read succeeds
            Store-->>Analysis: Return matching values, units, and dates
            alt No eligible records or too little compatible data
                Analysis-->>API: No results with explanation
                API-->>UI: Empty result with reason
                UI-->>User: Explain why and offer another selection or view
            else Enough compatible data
                Analysis->>Analysis: Compute the selected view without rounding away stored precision
                Note over Analysis: Comparison = side-by-side values<br/>Trend = dated points<br/>Range = min and max
                Note over Analysis: Evaluate specification limits only if supplied by the sponsor and units are compatible
                Analysis-->>API: Results with units and warnings for excluded values
                API-->>UI: Return selected view and warnings
                UI-->>User: Display table or chart and explain any omissions
            end
        end
    end
```
