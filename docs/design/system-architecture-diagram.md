> Epic: #42 · Stories: #48 · Task: #39

# System Architecture Diagram

This architecture shows the planned application components and their communication. The application is assumed to run in AWS, Snowflake is the materials data platform, and original PDFs remain in the organization's existing on-site document system. The SSO provider is shown as an external dependency; its specific product is not selected here.

```mermaid
flowchart TB
    user["Authorized user<br/>R&amp;D and manufacturing"]

    subgraph aws["AWS application environment"]
        direction TB
        ui["Web UI<br/>Upload · review · search"]
        api["Backend API<br/>Request routing · service coordination"]
        subgraph services["Application services"]
            direction LR
            extraction["Extraction<br/>Parse · OCR · validate"]
            analysis["Analysis<br/>Search · filter · compare"]
        end
        ui -->|Application requests| api
        api -->|Document reference| extraction
        api -->|Analysis request| analysis
    end

    sso["Organization SSO<br/>Provider not selected"]
    onsite["Existing on-site document system<br/>Original PDF storage"]
    snowflake[("Snowflake<br/>Structured materials data")]

    user -->|Uses| ui
    ui -->|Sign-in · access decision| sso
    api -->|Store PDF · return reference| onsite
    onsite -->|Read source PDF| extraction
    extraction -->|Validated records| snowflake
    analysis -->|Query · compare| snowflake
```

## Component Responsibilities

| Component | Responsibility |
|---|---|
| Web UI | Lets authorized users upload documents, review extraction results, search, filter, and compare material records. |
| Backend API | Routes UI requests and coordinates authentication, document references, extraction, and data access. |
| Extraction module | Reads source PDFs from the on-site document system, parses digital PDFs or applies OCR when needed, normalizes fields, and validates results. |
| Analysis module | Queries material data to provide search, filtering, trends, and comparisons. |
| Snowflake | Stores structured material records and supports application queries and analysis. |
| Existing on-site document system | Stores original PDFs and serves them to the application by document reference. |
| Organization SSO | Provides authentication and access decisions; the specific identity provider remains unspecified. |

*Figure 3 — High-level system architecture. Original PDF files stay in the existing on-site document system; extracted, validated material records are stored in Snowflake.*
