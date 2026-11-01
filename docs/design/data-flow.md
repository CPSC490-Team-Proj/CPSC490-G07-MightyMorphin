## Design -- Data Flow Diagram
Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Stories: [#40] (https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/40)
Owner: Christopher Pham · Sprint: 2 · Status: Draft


```mermaid
flowchart LR
  physicalMedia[Physical Media]:::orange
  scanner[Scanner]:::orange
  pdfFile[PDF File]:::yellow
  pdfExtractor[PDF Data Scraper]:::indigo
  extractedData[Extracted Data]:::indigo
  filterEngine[Filter Engine]:::teal
  outputData[Filtered Output]:::green

  physicalMedia -->|scanning| scanner
  scanner -->|conversion| pdfFile
  pdfFile -->|scraping| pdfExtractor
  pdfExtractor -->|raw data| extractedData
  extractedData -->|processing| filterEngine
  filterEngine -->|cleaned data| outputData

  classDef orange stroke:#fb923c,fill:#fff7ed
  classDef yellow stroke:#facc15,fill:#fefce8
  classDef indigo stroke:#818cf8,fill:#eef2ff
  classDef teal stroke:#2dd4bf,fill:#f0fdfa
  classDef green stroke:#4ade80,fill:#f0fdf4
```