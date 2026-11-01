## Design -- Data Flow Diagram
Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Stories: [#40] (https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/40)
Owner: Christopher Pham · Sprint: 2 · Status: Draft


```mermaid
---
config:
  theme: base
---
flowchart LR
    physicalMedia["Physical Media"] -- scanning --> scanner["Scanner"]
    scanner -- conversion --> pdfFile["PDF File"]
    pdfFile -- scraping --> pdfExtractor["PDF Data Scraper"]
    pdfExtractor -- raw data --> extractedData["Extracted Data"]
    extractedData -- processing --> filterEngine["Filter Engine"]
    filterEngine -- cleaned data --> outputData["Filtered Output"]

     physicalMedia
     scanner
     pdfFile
     pdfExtractor
     extractedData
     filterEngine
     outputData
```