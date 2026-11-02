> Epic: #42 · Story: #48 · Task: #39

# System Architecture Diagram

This architecture shows the planned application components and their communication. The application is assumed to run in AWS, Snowflake is the materials data platform, and original PDFs remain in the organization's existing on-site document system. The SSO provider is shown as an external dependency; its specific product is not selected here.

```mermaid
flowchart TB
    user["Authorized user<br/>R&amp;D and manufacturing"]

    subgraph aws["AWS application environment<br/>hosting services to be finalized"]
        ui["Web UI<br/>Upload, search, review"]
        api["Backend API<br/>Routes requests and coordinates services"]
        extraction["Extraction module<br/>Parse, OCR when needed, validate"]
        analysis["Analysis module<br/>Search, filtering, comparison"]
    end

    sso["Organization SSO<br/>Provider not specified"]
    onsite["Existing on-site document system<br/>Stores original PDF files"]
    snowflake[("Snowflake<br/>Structured materials data")]

    user -->|Uses application| ui
    ui -->|Sign-in and access decision| sso
    ui -->|User requests| api
    api -->|Stores PDF and receives document reference| onsite
    onsite -->|Retrieves source PDF| extraction
    api -->|Document reference| extraction
    api -->|Analysis request| analysis
    extraction -->|Validated material records| snowflake
    analysis <-->|Queries and result sets| snowflake
    api <-->|Reads and writes records| snowflake
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
