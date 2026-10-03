# Project Proposal — 〈Project Title〉

**Department of Computer Science**
**CPSC 490 Undergraduate Seminar in Computer Science — Proposal for Capstone Project**

**Group 07 — Mighty Morphins** · Sponsor: EL-1
Authors: Nguyen, Nguyen (GwenNguyen2604), Christopher Pham (cpham2005), 
Bhavesh Malhi (Bhavesh1024), Fidelis Okorie (Kameo101), Liam Wilson 
(liamw5265) Date: 〈2026-09-18〉

> **This file is the proposal document, not a README.** Its section numbers,
> titles, and guidance are copied from the course Word template, so it
> converts cleanly for Canvas submission. Write continuous academic prose —
> no task lists, no emoji, no repo jargon.
>
> Each section below opens with the template's own guidance in a quote block.
> **Delete the quote blocks and every 〈bracket〉 before submitting.**
>
> **Getting this into the Word template for Canvas.** The template numbers
> its headings **automatically** (a multilevel list: top-level sections at
> level 1, *Related Work* and *Problem Statements* at level 2). The numbers
> typed below exist so the repo copy is readable and checkable — so when you
> move the text into Word, do not end up with both sets.
>
> The reliable route, and the one most teams should use: **open the course
> template and paste your prose section by section**, leaving Word's own
> numbering to do the numbering. Ten minutes, no surprises.
>
> If you prefer to convert, `pandoc` can do it (install with
> `winget install pandoc`):
>
>     pandoc proposal/proposal.md -o proposal.docx --reference-doc="CPSC 490 Project Proposal Template Fall 2026.docx"
>
> Then in Word: delete the typed `0.` / `1.` / `1.1` prefixes (Word re-adds
> them from the list), and set *Related Work* and *Problem Statements* to the
> template's level-2 heading so they number as 1.1 and 1.2. Check figure
> placement, then submit.
>
> **Formatting requirements — the submitted Word document is graded against
> these, explicitly:**
>
> - **Cover page: use the template's cover page, unchanged in layout.** Fill
>   in only its fields — project title, group number and name, sponsor,
>   authors, date — and keep the template's own placement, fonts and spacing
>   for it. The header block at the top of this file carries the same fields
>   so the paste is a transcription, not a redesign.
> - **Font: Times New Roman, 11-point.** Body text, headings and captions
>   take their size and style from the template's own styles — do not
>   restyle anything by hand.
> - **Line spacing: 1.5.** **Margins: 1.0 inch** on all four sides.
> - **Section format, numbering and indentation must match the Word template
>   exactly** — the multilevel-list numbering, heading levels, and paragraph
>   indentation are the template's, not yours. If your document's §1.1 looks
>   different from the template's §1.1, fix yours.
> - **Length: the Final Project Proposal Paper (due Sun Dec 20) must exceed
>   50 pages** under exactly this formatting — font, spacing and margins are
>   fixed above precisely so page count means the same thing for every team.
>   The Preview paper (due Sun Nov 29) is the same document part-way; it has
>   no minimum, but it is graded on the same formatting.
>
> A paste into the template inherits all of this automatically **if you paste
> as text and let Word's styles apply** (Home → Paste → *Keep Text Only*, or
> apply the template's styles after pasting). A pandoc conversion with
> `--reference-doc` inherits it too — but verify font, spacing and margins
> afterward rather than assuming.
>
> Either way, keep this Markdown copy current — it is what peer review and CI
> can actually read. If your team writes in Word instead, commit the `.docx`
> here as well.

---

## 0. Abstract

> The primary purpose of abstract is to help the reader understand the main
> message of current document (proposal in this case) without reading the
> entire document. Therefore an abstract should include at least one or two
> paragraph of background (or motivation) information for the project, a
> brief description of the problem you are trying to solve in this proposal,
> a proposed ideas or solutions, the significance of your proposed idea
> elaborating why the proposed idea is non-trivial, significant, or
> beneficial in one or two paragraphs, the project goals and outcomes in one
> paragraph, and a brief description of what you will discuss in this
> proposal, giving a brief outline of this document in 1-2 sentences in one
> paragraph. Abstract should not exceed one page. Any abstract exceeded
> one-page limit must be shortened.

&emsp;At Edwards Lifesciences, material information is contained in documents such as Certificates of Conformance (CoCs) received from external vendors and material test reports generated internally. Although these documents contain information about materials and their mechanical properties, the data contained within them is not currently maintained in a centralized, structured database. When users need to analyze material data across different samples or requests, they must locate the relevant reports and manually extract the necessary information. This process makes retrieving and comparing historical material information time consuming, and prone to user mistakes, particularly when information from many documents is required.<br><br>
&emsp;The Online Materials Database project proposes a web application that converts information contained in these documents into structured and searchable material records. The proposed system will accept material documentation in PDF format, and extract relevant information such as material identification and mechanical properties. Extracted information will be verified where possible and stored in a relational database hosted using AWS services. The web application will provide authorized users with a centralized interface for accessing this information and searching or filtering records.<br><br>
&emsp;Developing such a system presents challenges beyond simply storing and displaying documents. Test documents and CoCs generated accross a long period of times spanning years, with CoCs being from multiple vendors, can have inconsistent document format. This requires the system to accommodate different methods of obtaining and interpreting their contents. The accuracy of extracted information is particularly important because incorrectly interpreted material properties could reduce the usefulness and reliability of the resulting database. Automating this process while supporting heterogeneous documents therefore requires consideration of document processing, information extraction, data verification, database design, and usability. A successful system would reduce repeated manual extraction of historical material data and make information from previously independent documents more readily available for retrieval and analysis.<br><br>
&emsp;The primary goals of the project are to develop a data extraction workflow for supported CoCs and test reports, establish centralized relational storage for the resulting material information, provide mechanisms for verifying extracted information, and develop an internal web application through which users can access the database. The expected outcome is a functional system that transforms supported material documents into structured records and allows authorized users to search, filter, and view historical material information. The system is intended to provide a foundation that can be expanded as additional document formats, material attributes, and analysis requirements are identified.<br><br>
&emsp;This proposal describes the problems motivating the Online Materials Database, the project's goals and objectives, and the proposed technical approach for addressing them.<br><br>

## 1. Introduction
&emsp;Engineering and manufacturing decisions rely heavily on accurate information for verifying material quality compliance, and performance.  Important information such as vendor information, material properties and specifications is primarily recorded in the form of test reports and Certificates of Conformance (CoC). Although these documents are archived, the data itself is not stored in a structured format therefore you need to search for individual documents rather than querying a database.<br><br>
&emsp;The current method of storing documents creates several problems, Engineers need to manually locate individual documents and manually search through them to find specific data points.  Comparing information across vendors or material types requires manual reviewing multiple documents.  This process becomes significantly inefficient as the number of records increases.<br><br>
&emsp;The goal of this project is to design and develop a centralized system for managing materials information contained in these CoC and test reports.  The system focuses on extracting data from existing and future documents and stores them in a structed format.  This data can be easily queried and analyzed to support better informed engineering decisions.  The main problem that this project solves is the significant amount of manual data entry and searching required by the current process.<br><br>
&emsp;This project differs from a traditional document-management system like Dropbox or a cloud file server, because the primary focus is not simply storing documents. Instead, relevant data is extracted from the documents and stored in a structured database.  The system also maintains references between the structured data and the original documents, allowing engineers to access the original PDF file whenever for further review.


### 1.1 Related Work
&emsp;Several existing technologies address parts of the problem involdved with extracting and managing information from material documents. Google Cloud Document AI and Microsoft Azure Document Intelligence provide tools for extracting information from documents, while Ansys Granta ML focuses specifily on storing and managing materials data.  Altho these systems funcation similarly to the propoded software, our approach to the probelem is a more speficic solution while the other softwares are more general.<br><br>
&emsp;<b>Google Cloud Document AI</b> provides document-prcoessing tools that can extract text, key-value pairs, tables, and other structured information form PDF files nad images[1].  Its Form Parser is designed to recognize information from structured documetns with requiring a custom model to be trained[4].  Google also provided custome extractors that allow users to define a schema containing the information they want to extract.  The make Cloud Document AI useful when documents contain similar information but use different layouts.  However, Cloud Document AI only provides a solution for the data extractin problem, the extracted data still needs to be stored somewhere.  An additional application wouls still be needed to store this data after it is extracted.<br><br>
&emsp;<b>Microsoft Azure Document Intelligence</b> provides similar document-processing capabilities.  It combines Optical Character Recogniction (OCR) and document-analysis models to extract text, tables, key-values pairs, and document structure[2].  Microsoft also suppert for custome document extractions, making this service useful when extracting data from documents that have different layouts.  Similar to Google Cloud Document AI these softwares are general purpose document processing softwares, the data extracted still needs to be stored somewhere.<br><br>
&emsp;<b>Ansys Granta MI</b> provides a solution to the storing of the data probelm rather data extration.  Granta MI is designed to create store, manage, search, compare, and analyzie material information[3].  It can combine an orginization's material information with the built-in materials information and intregrate the inforamtion with softwares like CAD or DAE.  Granta MI is a solution to the materials database and analysis tool but it lacks the function of extracting information.  A major feature of the proposed software is that it can extract data from different formated documents but Granta MI can't do that.<br><br>
&emsp;<b>Shape Memory Materials Database</b> provides a reliable and accessible location for storing and displaying data on materials. The information pretains to the shape memory of the metals in the form of a chart. By utilizing a charting illustration researchers can compare the materials extremes to find the prime material for specific situations. Using the element table there are several selections to choose from and provides a simple choice board that researchers know and use. There is also a search filter to different the data that is used to create the so the users know the data is reliable.<br><br>

| Existing approach | What it does | Pros | Cons | Why ours differs |
|---|---|---|---|---|
| Google Cloud Document AI / paper [1] | Extracts text, key-value pairs, tables, and structured fields from PDFs and images | Handles scanned and digital documants supports custom extraction schemas and differering document layouts | Primarly solves document extraction, a separate materials database, validations system, and user interface are key requirments | The proposed project integrates document extraction with data validation, storage, searching, and analysis |
| Microsoft Azure Document Intelligence / paper [2] | Uses OCR and document-analysis models to extract text, tables, structures and kay-value pairs. | Supports structured, semi-semi structred, and unstructured docuemnts.  Provides pretrained and customizable extraction capabilities | Primarly solves document extraction, a separate materials database, validations system, and user interface are key requirments| Our system is designed around specific feilds and workflows found in material CoCs and test repots. |
| Ansys Grnta MI / paper [3] | Centralized materials spec database, provides tools for searching, comparing, and analysis.  Allows for intrgration with custome materials inforamtion | Designed specifically for materials information.  Supports analysis and intrgration with Other softwares such as CAD and CAE | Focuses primaly on materials data management rahter than data extration. | The proposed project connects data extration with data storage for data analysis |
| Shape Memory Materials Database / product [4] | This product outputs data and structures the chart to reprsent the data on shape memory alloys | The chart proivided can compare two major attributes (temperature and structure) to find best materials for two extremes | The program is not open to providing your own data; and its all public information | The product we want to create allows for implementation of Edward's own unique documenation and data collection; which is privately accessible to Edwards affiliates |

### 1.2 Problem Statements
- <b>P.1 Unstructured Material Data:</b> Data from CoCs and test documents are primarily stored as either scanned documents or PDFs, making information difficult to query, analyze, and reuse.
- <b>P.2 Manual Data Extraction:</b> Extracting data from documents manually requires significant effort because there is no automated process for consistently extracting data from CoCs and testing documents.
- <b>P.3 Inconsistent Document Formants:</b> CoCs and test data documents come from many different sources, the data is not all in the same structured format.  This makes repeated extractions of data difficult.
- <b>P.4 Lack of Centralized Data Access:</b> There is no centralized materials repository that allows users to efficiently query historical records.  This causes overhead if users need to look to multiple sources for this data. 
- <b>P.5 Limited Material Data Analysis:</b> Data is stored in scanned documents and PDFs rather in a structured format.  Progress is negatively affected as users cannot efficiently query, analyze, and visualize historical data for engineering decisions.


| Problem | Addressed by |
|---|---|
| P1 Unstructured Material Data | Scanning and scraping the data from the PDFs and storing that data into a cloud database and implementing that data into a GUI that illustrates patters in the material as well as allows uesers to filter search query |
| P2 Manual Data Extraction | Automated scanning programming that allows users to drag and drop file to extract metadata into database |
| P3 Inconsistent Document Formats | Take in to account that there are several formats of data and forms we would first need to identify form types and keywords to extract necessary data |
| P4 Lack of Centralized Data Access | During GUI creation we will implement search filters for materials, dates, providers, and more upon stakeholder request |
| P5 Limited Material Data Analysis | Creation of this program will allow reliably and efficient work flow with centralized and organized data. Users will be able to look up material data, compare them in specific situations, and filter searches for relevent material |

## 2. Goals and Objectives

> Describe goals and objectives. Goals are general statements of what you are
> trying to accomplish with the project or problems to solve. Objectives are
> specific, measurable statements of what you want to complete to reach the
> project goals. Most projects have 2-3 goals.
>
> List the objectives for each goal. To write objectives, look at the goal
> statement and list what you need to complete using action words like use
> case names in order to meet the goal.
>
> Note that the goals and objectives in a proposal will be an important
> metric to evaluate whether or not you successfully finished your project
> when you turn in your final project report.

Each **goal** is tracked as an **Epic** issue and each **objective** as a
**User Story** issue in the team repository (see the setup guide's *Epics and user stories* section).
**Every epic and user story in the repository is linked from this section** —
CI gate G8 fails if one exists that this section does not link. That is what
keeps the goals in this document and the work on the board from drifting
apart.

Write each objective the way the guidance above asks — **an action word plus
the measure that says it is done**, not a role-play sentence:

- **Goal 1: 〈e.g. Secure account management〉** (Epic #〈n〉)
  - Objective 1.1: 〈Implement member registration and login with hashed
    credentials, session expiry, and rejection of malformed input.〉 (#〈n〉)
  - Objective 1.2: 〈Demonstrate the login round-trip in a runnable prototype
    at the Week-8 in-class check.〉 (#〈n〉)
- **Goal 2: 〈your second goal〉** (Epic #〈n〉)
  - Objective 2.1: 〈Action word + what you will complete + how it will be
    measured〉 (#〈n〉)

〈Replace the brackets with your own 2–3 goals and their objectives, and put
the **real issue numbers** in as you file them — gate G8 checks that every
epic and story in your repository is linked from this section. A fully worked
version of this, with live issues and a populated board, is in the course
example repository.〉

## 3. Proposed Approaches

> Describe your proposed approach to solve the problem, specifying how you
> will achieve the stated goals. List some possible strategies.

〈Your approach — **clear and concise**. State the strategy you chose, the
alternatives you considered, and the reasoning that decided between them.
Think of this as the argument, not the manual: a reader should finish this
section understanding *what* you will do and *why that* rather than the
alternatives.〉

**Keep the details out of this section.** Tooling, platforms, frameworks,
DBMS choices, environment setup, diagrams, and the work breakdown all belong
in §4 (Required Environment, Resources, and Planned Activities). If a
sentence here names a version number, a library, or a configuration, it
probably belongs in §4 — leave a pointer instead ("the implementation stack
is detailed in §4").

〈A few paragraphs, or a short list of candidate strategies with one line of
trade-off each. If it runs past a page, you are writing §4.〉

## 4. Required Environment, Resources, and Planned Activities

> Review the required and available resources and environment to complete
> your project. For example, server, platform, software tools, operating
> systems, DBMS, or any required skills.
>
> Describe the expected activities to achieve the stated goals, e.g.,
> software development process.

〈Your environment, resources, and planned activities.〉

**Diagrams belong in this section.** Include at minimum a high-level
architecture diagram and a system (context) diagram; add the ER/EER model and
a data-flow diagram where they help the reader understand what you are
building and what it depends on. Draw them with any graphical tool
(Lucidchart, draw.io, Miro, Mermaid, ERDPlus, Figma), keep the authoritative
copies in `docs/design/` with both editable source and exported image, and
reference them here.

〈Number every figure, caption it, and point at it from the prose — "Figure 1
shows the three deployment tiers and the trust boundary between them." A
figure the text never mentions is decoration. See `docs/design/DIAGRAMS.md`
for tools, conventions, and the rule that every box and arrow must be
verified against reality.〉

### Specification and design documents

**Every specification and design document the team writes is listed here**
with the objective it serves. This section is the index of the project's
technical detail: §3 holds the argument, §4 holds the documents that make it
buildable. CI gate G9 fails if a document exists in `docs/specs/` or
`docs/design/` that this section does not link.

| Document | Kind | Covers | Issues |
|---|---|---|---|
| 〈docs/specs/account-management.md〉 | specification | 〈account management requirements〉 | 〈#n, #n〉 |
| 〈docs/design/architecture.md〉 | design | 〈system architecture + data model〉 | 〈#n〉 |

〈The scaffold ships `docs/specs/example-spec.md` and
`docs/design/example-design.md` as worked examples — read them, then delete
them once you have your own, and list yours here.〉

〈Replace these rows with your own. Each document names its epic and stories
in its own first lines too (gate G2), so the trail runs both ways.〉

### Planned activities — the work items

The goals and objectives live in §2 as epics and user stories. **This section
links every *other* work item: features, enhancements, bugs, tasks, and
sub-tasks** — the concrete activities that deliver those objectives. CI gate
G8 fails if such an issue exists that this section does not link.

| Issue | Type | Activity | Parent | Owner | Sprint |
|---|---|---|---|---|---|
| 〈#n〉 | 〈task〉 | 〈stand up the prototype login endpoint〉 | 〈#story〉 | 〈owner〉 | 〈Sprint 1〉 |
| 〈#n〉 | 〈feature/enhancement/bug/task/sub-task〉 | 〈…〉 | 〈#story〉 | 〈…〉 | 〈…〉 |

〈Replace these rows with your own, and keep the table current as you file new
issues — with §2 it gives a reader every planned activity in one place, each
traceable to the objective it serves.〉

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
