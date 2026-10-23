# Project Proposal — Online Material Database

**Department of Computer Science**
**CPSC 490 Undergraduate Seminar in Computer Science — Proposal for Capstone Project**

**Group 07 — Mighty Morphins** · Sponsor: EL-1
Authors: Nguyen Nguyen (GwenNguyen2604), Christopher Pham (cpham2005), 
Bhavesh Malhi (Bhavesh1024), Fidelis Okorie (Kameo101), Liam Wilson 
(liamw5265) Date: 〈2026-09-18〉

## 0. Abstract 
&emsp;At Edwards Lifesciences, material information is contained in documents such as Certificates of Conformance (CoCs) received from external vendors and material test reports generated internally. Although these documents contain information about materials and their mechanical properties, the data contained within them is not currently maintained in a centralized, structured database. When users need to analyze material data across different samples or requests, they must locate the relevant reports and manually extract the necessary information. This process makes retrieving and comparing historical material information time consuming and prone to user mistakes, particularly when information from many documents is required.<br><br>
&emsp;The Online Materials Database project proposes a web application that converts information contained in these documents into structured and searchable material records. The proposed system will accept material documentation in PDF format, and extract relevant information such as material identification and mechanical properties. Extracted information will be verified where possible and stored in a relational database hosted using AWS services. The web application will provide authorized users with a centralized interface for accessing this information and searching or filtering records.<br><br>
&emsp;Developing such a system presents challenges beyond simply storing and displaying documents. Test documents and CoCs generated across a long period of time spanning years, with CoCs being from multiple vendors, can have inconsistent document format. This requires the system to accommodate different methods of obtaining and interpreting their contents. The accuracy of extracted information is particularly important because incorrectly interpreted material properties could affect the reliability of the resulting database. Automating this process while supporting heterogeneous documents therefore requires consideration of document processing, information extraction and verification, database design, and usability. A successful system would reduce repeated manual extraction of historical material data and make information more readily available for retrieval and analysis.
<br><br>
&emsp;The primary goals of the project are to develop a data extraction workflow for supported CoCs and test reports, establish centralized relational storage for the resulting material information, provide mechanisms for verifying extracted information, and develop an internal web application through which users can access the database. The expected outcome is a functional system that transforms supported material documents into structured records and allows authorized users to search, filter, and view historical material information. The system is intended to provide a foundation that can be expanded as additional document formats, material attributes, and analysis requirements are identified.<br><br>
&emsp;This proposal describes the problems motivating the Online Materials Database, the project's goals and objectives, and the proposed technical approach for addressing them.<br><br>
[#7](https://github.com/orgs/CPSC490-Team-Proj/projects/1/views/1?pane=issue&itemId=261452481&issue=CPSC490-Team-Proj%7CCPSC490-G07-MightyMorphin%7C7)

## 1. Introduction 
&emsp;Engineering and manufacturing decisions rely heavily on accurate information for verifying material quality compliance, and performance. Important information such as vendor information, material properties and specifications is primarily recorded in the form of test reports and Certificates of Conformance (CoC). Although these documents are archived, the data itself is not stored in a structured format therefore you need to search for individual documents rather than querying a database.<br><br>
&emsp;The current method of storing documents creates several problems, Engineers need to manually locate individual documents and manually search through them to find specific data points. Comparing information across vendors or material types requires manual reviewing of multiple documents. This process becomes significantly inefficient as the number of records increases.<br><br>
&emsp;The goal of this project is to design and develop a centralized system for managing materials information contained in these CoC and test reports. The system focuses on extracting data from existing and future documents and stores them in a structured format. This data can be easily queried and analyzed to support better informed engineering decisions. The main problem that this project solves is the significant amount of manual data entry and searching required by the current process.<br><br>
&emsp;This project differs from a traditional document-management system like Dropbox or a cloud file server, because the primary focus is not simply storing documents. Instead, relevant data is extracted from the documents and stored in a structured database. The system also maintains references between the structured data and the original documents, allowing engineers to access the original PDF file whenever for further review..


### 1.1 Related Work
&emsp;Several existing technologies address parts of the problem involved with extracting and managing information from material documents. Google Cloud Document AI and Microsoft Azure Document Intelligence provide tools for extracting information from documents, while Ansys Granta ML focuses specifically on storing and managing materials data. Altho these systems function similarly to the proposed software, our approach to the problem is a more specific solution while the other softwares are more general.<br><br>
&emsp;<b>Google Cloud Document AI</b> provides document-processing tools that can extract text, key-value pairs, tables, and other structured information from PDF files and images[1]. Its Form Parser is designed to recognize information from structured documents requiring a custom model to be trained[4]. Google also provided custom extractors that allow users to define a schema containing the information they want to extract. The make Cloud Document AI useful when documents contain similar information but use different layouts. However, Cloud Document AI only provides a solution for the data extraction problem, the extracted data still needs to be stored somewhere. An additional application would still be needed to store this data after it is extracted.<br><br>
&emsp;<b>Microsoft Azure Document Intelligence</b> provides similar document-processing capabilities. It combines Optical Character Recognition (OCR) and document-analysis models to extract text, tables, key-values pairs, and document structure[2]. Microsoft also supports custom document extractions, making this service useful when extracting data from documents that have different layouts. Similar to Google Cloud Document AI these softwares are general purpose document processing softwares, the data extracted still needs to be stored somewhere.<br><br>
&emsp;<b>Ansys Granta MI</b> provides a solution to the storing of the data problem rather than data extraction. Granta MI is designed to create, store, manage, search, compare, and analyze material information[3]. It can combine an organization's material information with the built-in materials information and integrate the information with softwares like CAD or DAE. Granta MI is a solution to the materials database and analysis tool but it lacks the function of extracting information. A major feature of the proposed software is that it can extract data from different formatted documents but Granta MI can't do that.<br><br>
&emsp;<b>Shape Memory Materials Database</b> provides a reliable and accessible location for storing and displaying data on materials. The information pertains to the shape memory of the metals in the form of a chart. By utilizing a charting illustration researchers can compare the material's extremes to find the prime material for specific situations. Using the element table there are several selections to choose from and provides a simple choice board that researchers know and use. There is also a search filter to differentiate the data that is used to create the so the users know the data is reliable.<br><br>

| Existing approach | What it does | Pros | Cons | Why ours differs |
|---|---|---|---|---|
| Google Cloud Document AI / paper [1] | Extracts text, key-value pairs, tables, and structured fields from PDFs and images | Handles scanned and digital documants supports custom extraction schemas and differering document layouts | Primarly solves document extraction, a separate materials database, validations system, and user interface are key requirments | The proposed project integrates document extraction with data validation, storage, searching, and analysis |
| Microsoft Azure Document Intelligence / paper [2] | Uses OCR and document-analysis models to extract text, tables, structures and kay-value pairs. | Supports structured, semi-semi structred, and unstructured docuemnts.  Provides pretrained and customizable extraction capabilities | Primarly solves document extraction, a separate materials database, validations system, and user interface are key requirments| Our system is designed around specific feilds and workflows found in material CoCs and test repots. |
| Ansys Grnta MI / paper [3] | Centralized materials spec database, provides tools for searching, comparing, and analysis.  Allows for intrgration with custome materials inforamtion | Designed specifically for materials information.  Supports analysis and intrgration with Other softwares such as CAD and CAE | Focuses primaly on materials data management rahter than data extration. | The proposed project connects data extration with data storage for data analysis |
| Shape Memory Materials Database / product [4] | This product outputs data and structures the chart to reprsent the data on shape memory alloys | The chart proivided can compare two major attributes (temperature and structure) to find best materials for two extremes | The program is not open to providing your own data; and its all public information | The product we want to create allows for implementation of Edward's own unique documenation and data collection; which is privately accessible to Edwards affiliates |

[#6](https://github.com/orgs/CPSC490-Team-Proj/projects/1/views/1?pane=issue&itemId=261446190&issue=CPSC490-Team-Proj%7CCPSC490-G07-MightyMorphin%7C6)

### 1.2 Problem Statements 
- <b>P.1 Unstructured Material Data:</b> Data from CoCs and test documents are primarily stored as either scanned documents or PDFs, making information difficult to query, analyze, and reuse.
- <b>P.2 Manual Data Extraction:</b> Extracting data from documents manually requires significant effort because there is no automated process for consistently extracting data from CoCs and testing documents.
- <b>P.3 Inconsistent Document Formats:</b> CoCs and test data documents come from many different sources, the data is not all in the same structured format.  This makes repeated extractions of data difficult.
- <b>P.4 Lack of Centralized Data Access:</b> There is no centralized materials repository that allows users to efficiently query historical records.  This causes overhead if users need to look to multiple sources for this data. 
- <b>P.5 Limited Material Data Analysis:</b> Data is stored in scanned documents and PDFs rather than in a structured format.  Progress is negatively affected as users cannot efficiently query, analyze, and visualize historical data for engineering decisions.

| Problem | Addressed by |
|---|---|
| P1 Unstructured Material Data | Scanning and scraping the data from the PDFs and storing that data into a cloud database and implementing that data into a GUI that illustrates patterns in the material as well as allows users to filter search query |
| P2 Manual Data Extraction | Automated scanning programming that allows users to drag and drop file to extract metadata into database |
| P3 Inconsistent Document Formats | Take into account that there are several formats of data and forms we would first need to identify form types and keywords to extract necessary data |
| P4 Lack of Centralized Data Access | During GUI creation we will implement search filters for materials, dates, providers, and more upon stakeholder request |
| P5 Limited Material Data Analysis | Creation of this program will allow reliably and efficient work flow with centralized and organized data. Users will be able to look up material data, compare them in specific situations, and filter searches for relevant material |

[#5](https://github.com/orgs/CPSC490-Team-Proj/projects/1/views/1?pane=issue&itemId=261443686&issue=CPSC490-Team-Proj%7CCPSC490-G07-MightyMorphin%7C5)

## 2. Goals and Objectives
The Online Materials Database project aims to reduce the manual effort required to retrieve and analyze material information from Certificates of Conformance (CoCs) and material test reports. The project will accomplish this by developing an automated document-processing pipeline, establishing centralized structured storage for extracted material information, and providing an internal web application through which authorized users can access and analyze the collected data. The following goals and objectives define the primary capabilities to be developed and provide measurable criteria for evaluating the completed system. <br><br>

- **Goal: Edward Lifescience project Objectives** [[epic:#1]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/1)

- **Goal: Edwards Lifescience Project Forms** [[epic:#45]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/45)

- **Goal: Rough draft Proposal.md** [[epic:#4]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)

- **Goal 0: Design and Specification Documents** [[epic:#42]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42)
  - Objective 0.1: Design and Architecture [[story:#48]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/48)
  - Objective 0.2: Epic Specification Documents [[story:#49]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/49)

- **Goal 1: Automated Material Data Extraction and Verification** [[epic:#11]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/11)
  The first goal is to automate the process of converting material information contained in PDF documents into structured data suitable for storage and analysis. This goal addresses the current dependence on manual data extraction as well as the challenges created by scanned documents and inconsistent document formats.

  - Objective 1.1: Implement PDF document ingestion for supported CoCs and material test reports [[story:#12]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/12)

  - Objective 1.2: Extract material and mechanical-property data from digital PDFs [[story:#13]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/13)

  - Objective 1.3: Extract material data from scanned PDF documents using OCR [[story:#14]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/14)

  - Objective 1.4: Support extraction from multiple CoC and test-report layouts [[story:#15]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/15)

  - Objective 1.5: Objective 1.5: Verify and flag uncertain extraction results [[story:#16]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/16)

- **Goal 2: Centralized Material Data Storage and Management** [[epic:#17]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/17)
  The second goal is to provide centralized, structured storage for material information extracted from CoCs and test reports. Rather than requiring users to repeatedly retrieve individual PDF documents, extracted information will be converted into relational records that can be efficiently retrieved and reused by other components of the system.

  - Objective 2.1: Design and implement the relational materials data model [[story:#18]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/18)

  - Objective 2.2: Store material information in an AWS-hosted relational database [[story:#19]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/19)

  - Objective 2.3: Maintain traceability between material records and source documents [[story:#20]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/20)

  - Objective 2.4: Implement application-level material record operations [[story:#21]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/21)

- **Goal 3: Material Data Access and Analysis** [[epic:#22]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/22)
  The third goal is to provide authorized Edwards Lifesciences users with an internal web application for accessing material information stored by the system. The application will reduce the need to manually locate and review individual reports when searching for historical material information and will provide a foundation for comparing information across multiple records.

  - Objective 3.1: Develop an internal web application for authorized users [[story:#23]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/23)

  - Objective 3.2: Implement material and vendor search and filtering [[story:#24]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/24)

  - Objective 3.3: Distinguish CoC data from internal test-report data [[story:#25]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/25)

  - Objective 3.4: Display material properties and source information [[story:#26]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/26)

  - Objective 3.5: Compare material-property data across stored records [[story:#27]](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/27)
  

## 3. Proposed Approaches

The proposed system replaces manual lookup of Certificates of Conformance(COC) and
test reports. This uses a pipeline that is made of four stages: document ingestion,
data extraction, verification, and structured storage with web access. Each
stage addresses one or more of the problems that were identified in §1.2.

**Digital and scanned documents.** All of the incoming PDFs fall into two categories which are:

- Documents generated digitally, which contain an embedded text layer

- Scanned documents, which are images of paper forms.

The system will detect
which category a document belongs to on upload and route it accordingly.
Digital documents will have their text and tables read directly, which is
fast and using this method also avoids recognition errors that scanned documents may have. These Scanned documents will first be cleaned
up (straightened and contrast adjusted as well as other methods) and then passed through optical
character recognition before entering the same extraction step. Using two
paths rather than applying OCR to every document keeps accuracy high for the
majority of documents while still supporting older scanned records that may need to be added.

**Handling different document formats.** Because CoCs and test reports come
from many vendors, the same information appears in different positions and
under different labels. To solve this the system will first identify the type and source of
each document, then apply a field mapping for that format, falling back on
label based matching for layouts it has not seen before. All
results are normalized into a single common record with consistent field
names and units, regardless of the source format. New vendor formats can then
be supported by adding a mapping rather than changing the extraction logic. This approach may change once the team has actual test documents to reference, since some formats may already be standardized, but those documents are not yet in the team's possession.

**Verifying extracted data.** Automated extraction will not be correct every
time. To make sure no error chance is overlooked, the program will ensure no extracted value is treated as trustworthy by default. Each result
will be checked for missing required fields, incorrect data types or units,
values outside plausible ranges, and low recognition confidence.
Records that fail any check are flagged for review. A user can then compare the
extracted values against the original document, correct them, and approve the
record. Only approved records are stored as verified material data, and
each correction and approval is logged, which should minimize any and all errors the program could possibly produce.

**Storage and access.** Verified data will be stored in a relational database
that models materials, mechanical properties, documents, vendors, and lots as
related records. A relational design suits this data because it is highly
structured and repetitive, and because users need to filter and compare
values across many records. Every record keeps a reference to the original
PDF so that users can always trace a value back to its source and verify if highly sensitive data is included. Authorized
Edwards users will access the system through an internal web application
that supports document upload, the review queue, search and filtering by
material and vendor, and side by side comparison of material properties. A
web application was chosen because it requires no installation, centralizes
access control, and gives every user the same source of truth.

**Alternatives considered.** Four alternatives were considered. First,
general purpose cloud document extraction services [1][2] extract text and
fields well but provide no materials database, verification workflow, or
user interface, so most of the system would still need to be built. Second,
a dedicated materials data platform [3] offers strong storage and analysis
but no extraction, which leaves manual data entry (P.2) unsolved. Third,
keeping the current manual process costs nothing but addresses none of the
stated problems. Fourth, the sponsor's existing cloud data platform (Snowflake), which
includes AI-based document processing, could handle document ingestion
directly. This option is attractive because the sponsor already uses and
supports the platform, the data would stay within the sponsor's environment,
and the team would only need to build the code that verifies the ingested
results. However, the team has not yet confirmed how well the platform
handles scanned documents and varied vendor formats, and the option depends
on the sponsor's platform access and setup. This option is still under
evaluation with the sponsor, and a final decision will be made in
sprint 3. The team therefore proposes an integrated pipeline
that connects extraction, verification, storage, and analysis and is
tailored to the fields found in CoCs and test reports. The ingestion step
will either be built by the team or handled by the sponsor's platform,
depending on the outcome of that evaluation; the verification, storage, and
web application components are required in either case.

The implementation stack, hosting environment, and design diagrams are
detailed in §4.

[#52](https://github.com/orgs/CPSC490-Team-Proj/projects/1/views/2?pane=issue&itemId=278577328&issue=CPSC490-Team-Proj%7CCPSC490-G07-MightyMorphin%7C52)

## 4. Required Environment, Resources, and Planned Activities
The development of the Edwards Lifescience Materials Database requires various software technologies, development environment, and technical skills.  The table below outlines the planned resources and their purpose within the project
|Category|Technology/Resource|Purpose|
|-----|-----|-----|
|Programming Language|Python| - Backend development <br>- Document extraction <br>- Data processing|
|Database Management System|TDB|Store extracted data|
Backend Framework|TBD|- Handles application logic <br>- Communication between components|
|Frontend Framework|TBD|User Interface|
|Document Processing|TDB|Extract data from uploaded documents|
|Development Environment|Visual Studio Code|Write, debug, test code|
|Version Control|Git and Github|Track sprint progress, tasks, and assignments|


![Use Case Diagram]()

*Figure 1. Use Case Diagram.*

![ER Diagram]()

*Figure 2. ER Diagram.*

![System Architecture]()

*Figure 3. System Architecture Diagram.*

![Data Flow Diagram]()

*Figure 4. Data Flow Diagram.*

### Specification and design documents
| Document | Kind | Covers | Issues |
|----------|------|--------|--------|
|[Use Case Diagram]()|Design|Maps interactions between external users or systems with the software application's core functions within the system| [#36](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/36) |
|[ER Diagram]()|Design|Maps out relationships between entities within the database system|[#38](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/38)|
|[System Architecture]()|Design|Maps out relationships between core components within the system|[#39](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/39)|
|[Data Flow Diagram]()|Design|Maps how information moves, transforms, and stored within the system|[#40](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/40)|
|[Goal 1 Specification Document]()|Specification|Specification document for Goal 1: Automated Material Data Extraction and Verification|[#46](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/46)|
|[Goal 2 Specification Document]()|Specification|Specification document for Goal 2: Centralized Material Data Storage and Management|[#58](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/58)|
|[Goal 3 Specification Document]()|Specification|Specification document for Goal 3: Material Data Access and Analysis|[#59](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/59)|
### Planned activities — the work items

| Issue | Type | Activity | Parent | Owner | Sprint |
|---|---|---|---|---|---|
|[#5](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/5)|Task|Draft §1 Introduction Problem Statements|[#4](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)|[@Kameo101](https://github.com/Kameo101)<br>[@cpham2005](https://github.com/cpham2005)|Sprint 1|
|[#6](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/6)|Task|Draft §1 Introduction background|[#4](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)|[@liamw5265](https://github.com/liamw5265)|Sprint 1|
|[#7](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/7)|Task|Draft §0 Abstract|[#4](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)|[@GwenNguyen2604](https://github.com/GwenNguyen2604)<br>[@Bhavesh1024](https://github.com/Bhavesh1024)|Sprint 1|
|[#37](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/37)|Task|Draft §2 Goals and Objectives|[#4](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)|[@GwenNguyen2604](https://github.com/GwenNguyen2604)|Sprint 1|
|[#52](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/52)|Task|Complete Section 3: Proposed Approaches|[#4](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)|[@Kameo101](https://github.com/Kameo101)|Sprint 1|
|[#53](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/53)|Task|Complete Section 4: Required Environment, Resources, and Planned Activities|[#4](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)|[@liamw5265](https://github.com/liamw5265)|Sprint 1|
|[#29](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/29)|Task|Sync develop with main|[#1](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/1)|[@Kameo101](https://github.com/Kameo101)|Sprint 1|
|[#54](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/54)|Task|Synchronize Section 2 Goals and Objectives with GitHub issues|[#4](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)|[@cpham2005](https://github.com/cpham2005)|Sprint 1|
|[#34](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/34)|Task|Add hyperlinks and credits to Proposal.md|[#4](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)|[@Kameo101](https://github.com/Kameo101)<br>[@cpham2005](https://github.com/cpham2005)<br>[@Bhavesh1024](https://github.com/Bhavesh1024)<br>[@liamw5265](https://github.com/liamw5265)|Sprint 1|
|[#51](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/51)|Task|Fix typed hyperlink references in proposal.md|[#4](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/4)|[@Bhavesh1024](https://github.com/Bhavesh1024)|Sprint 1|
|[#57](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/57)|Task|Update README.md with Project Information and Sprint Board||[@Bhavesh1024](https://github.com/Bhavesh1024)|Sprint 1|
|[#55](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/55)|Task|Complete Sprint 1 Review||[@cpham2005](https://github.com/cpham2005)|Sprint 1|
|[#36](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/36)|Task|Task 0.1.1: Create Use Case Diagram|[#48](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/48)|[@liamw5265](https://github.com/liamw5265)|Sprint 2|
|[#38](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/38)|Task|Task 0.1.2: Create ER Diagram|[#48](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/48)|[@Kameo101](https://github.com/Kameo101)|Sprint 2|
|[#39](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/39)|Task|Task 0.1.3: Create Systems Architecture Diagram|[#48](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/48)|[@Bhavesh1024](https://github.com/Bhavesh1024)|Sprint 2|
|[#40](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/40)|Task|Task 0.1.4: Create Data Flow Diagram|[#48](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/48)|[@cpham2005](https://github.com/cpham2005)|Sprint 2|
|[#41](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/41)|Task|Task 0.1.5: Create UI Wireframe|[#48](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/48)|[@GwenNguyen2604](https://github.com/GwenNguyen2604)|Sprint 2|
|[#46](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/46)|Task|Task 0.2.1: Complete Goal 1 Spec Document|[#49](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/49)|[@]()|Sprint 2|
|[#58](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/85)|Task|Task 0.2.2: Complete Goal 2 Spec Document|[#49](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/49)|[@]()|Sprint 2|
|[#59](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/59)|Task|Task 0.2.3: Complete Goal 3 Spec Document|[#49](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/49)|[@]()|Sprint 2|
|[#63](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/63)|Bug|Cherry pick develop revision to main branch|[#1](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/1)|[@GwenNguyen2604](https://github.com/GwenNguyen2604)|Spring 1|
|[#47](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/47)|Task|Task: Define the tech stack and AWS services|[#49](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/49)|[@cpham2005](https://github.com/cpham2005)|Spring 2|
|[#43](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/43)|Task|Task: Project Intake Form|[#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42)|[@Kameo101](https://github.com/Kameo101)|Spring 3|
|[#44](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/44)|Task|Task: Solution Architecture Form|[#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42)|[@cpham2005](https://github.com/cpham2005)|Spring 3|


## 5. Project Outcomes

> Describe the outcomes or deliverables, e.g., final project report, user
> manuals, source code, data or database files, etc.
>
> Note: the deliverables always include the team GitHub repository, which
> must already contain prototype v0 (a thin end-to-end proof-of-concept,
> however small, running when this proposal is submitted). Briefly describe
> what your v0 demonstrates and how to run it.

〈**One or two paragraphs** explaining the project outcome overall — what will
exist when the project is finished, and what it will let someone do. Keep it
prose, not a checklist; name the deliverables inside the paragraphs, and say
briefly what prototype v0 demonstrates today and how to run it.〉

## 6. Project Timeline

> Identifies tasks (project objectives) to be performed, milestones to be
> met, and the estimated number of hours for each task.

〈**This is the plan for CPSC 491 next semester — the implementation timeline,
not this semester's proposal work.** Identify the tasks (your objectives from
§2), the milestones, and the estimated hours for each, in the order they will
be built. State the assumptions it rests on (sponsor availability, data
access, hardware).〉

| Task (objective) | Milestone | Owner | Est. hours | Spring phase |
|---|---|---|---|---|
| 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 |
| 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 |

〈Do **not** put this fall's four proposal sprints here — those live on the
project board and in `docs/sprint-reviews/`. This section answers "how does
the system actually get built next semester?"〉

## 7. AI Usage

> Per the course AI policy (see the syllabus, Use of AI Tools), disclose the
> AI tools used in preparing this proposal and the prototype: which tools,
> for what tasks (e.g., code generation, test writing, debugging,
> diagramming), and approximately what fraction of each artifact was
> AI-assisted.
>
> Reminder: the prose of this proposal must be your own writing. You remain
> fully responsible for the correctness of all AI-assisted work, including
> the prototype code.

〈Your disclosure. Naming the tool is not disclosure — name what it drafted,
what fraction of each artifact was AI-assisted, and how you verified it.〉

## 8. References

[1] Google Cloud Document AI Documentation.
    <https://docs.cloud.google.com/document-ai/docs/overview?hl=en>. [Accessed: Oct. 3, 2026].<br><br>
[2] Microsoft, "General Document Model," Azure AI Document
    Intelligence Documentation.<https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/general-document?view=doc-intel-4.0.0&utm_source=chatgpt.com>.
    [Accessed: Oct. 3, 2026].<br><br>
[3] Ansys, "Granta MI Pro," Ansys Materials.
    <https://ansys.synopsys.com/products/materials/granta-mi>. [Accessed: Oct. 3, 2026].<br><br>
[4] Google Cloud "Form Parser" Document AI Documentation.
  <https://docs.cloud.google.com/document-ai/docs/processors-list?hl=en#processor_form-parser>. [Accessed: Oct. 3, 2026].<br><br>
