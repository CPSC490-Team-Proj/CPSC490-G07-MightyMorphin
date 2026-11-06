> Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Story: [#48](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/48) · Task: [#39](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/39)
> Owner: Bhavesh Malhi · Sprint: 2 · Status: draft

# System Architecture Diagram

This architecture shows the planned application components and their communication. The application is assumed to run in AWS, Snowflake is the materials data platform, and original PDFs remain in the organization's existing on-site document system. The SSO provider is shown as an external dependency; its specific product is not selected here.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff", "primaryColor": "#eef1ff", "primaryTextColor": "#263238", "primaryBorderColor": "#5268b3", "lineColor": "#59645e", "secondaryColor": "#f0efe9", "tertiaryColor": "#e3f3ed"}}}%%
flowchart LR
    user["Authorized user<br/>R&amp;D and manufacturing"]

    subgraph aws["AWS application environment"]
        direction LR
        ui["Web UI<br/>Upload · review queue · search · trends"]
        api["Backend API<br/>Request routing · service coordination"]
        subgraph services["Application services"]
            direction LR
            extraction["Extraction<br/>Parse · OCR · normalize · validate"]
            review["Data review<br/>Pending queue · correct · approve"]
            analysis["Analysis<br/>Search · filter · compare · trends"]
        end
        ui -->|Application requests| api
        api -->|Document reference| extraction
        api -->|Review and correction requests| review
        api -->|Analysis request| analysis
    end

    sso["Organization SSO<br/>Provider not selected"]
    onsite["Existing on-site document system<br/>Original PDF storage"]
    snowflake[("Snowflake<br/>Structured materials data")]

    user -->|Uses| ui
    ui -->|Sign-in · access decision| sso
    api -->|Store PDF · return reference| onsite
    onsite -->|Read source PDF| extraction
    extraction -->|Candidate records · pending status| snowflake
    snowflake -->|Pending review queue| review
    review -->|Corrections · approval status| snowflake
    analysis -->|Search · comparison · historical trends| snowflake
```

## Component Responsibilities

| Component | Responsibility |
|---|---|
| Web UI | Lets authorized users upload documents, review and correct extracted records, search and filter materials, compare records, and view historical trends. |
| Backend API | Routes UI requests and coordinates authentication, document references, extraction, and data access. |
| Extraction module | Reads source PDFs from the on-site document system, parses digital PDFs or applies OCR when needed, normalizes and validates fields, and submits candidate records for review. |
| Data review module | Presents pending extracted records for human review, persists corrections and approval status, and preserves review history. |
| Analysis module | Queries structured material data for search, filtering, comparisons, and historical trend monitoring. |
| Snowflake | Stores candidate and approved material records, review status, and history; supports application queries and analysis. |
| Existing on-site document system | Stores original PDFs and serves them to the application by document reference. |
| Organization SSO | Provides authentication and access decisions; the specific identity provider remains unspecified. |

*Figure 3 — High-level system architecture. Original PDF files stay in the existing on-site document system; extracted records enter a review queue before approval, and historical trends are queried from Snowflake.*
