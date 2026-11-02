## Design -- Data Flow Diagram
Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Stories: [#40] (https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/40)
Owner: Christopher Pham · Sprint: 2 · Status: Draft


```mermaid
---
config:
  theme: base
---
---
config:
  theme: base
---
flowchart LR
    physicalMedia["Physical Media"] -- scan --> scanner["Scanner"]
    scanner -- conversion --> pdfFile["PDF File"]
    pdfFile -- store --> pdfArchive[("PDF Archive")]
    pdfArchive -- scraping --> pdfExtractor["PDF Data Scraper"]
    pdfExtractor -- raw data --> extractedData["Extracted Data"]
    extractedData -- review --> reviewer["Validate Data"]
    reviewer -- approve --> storedData[("AWS Database")]
    reviewer -- reject --> faulty["faulty Data"]
    storedData -- processing --> filterEngine["Filter Engine"]
    filterEngine -- cleaned data --> outputData["Filtered Output"]
    faulty -- "re-scrape archived PDF" --> pdfArchive

    reviewer@{ shape: diam}
```