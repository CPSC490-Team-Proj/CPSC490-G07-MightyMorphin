## Design -- Use Case Diagram
Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Stories: [#36](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/36)<br>
Owner: Liam Wilson · Sprint: 2 · Status: draft 

```mermaid
flowchart LR
    %% Actors
    RD["R&D"]
    MFG["Manufacturing"]
    MDL["Modeling"]
    SYSAD["System Administrator"]

    %% System Boundary
    subgraph SYSTEM["Material Data Management System"]
        direction TB

        %% Document Processing
        subgraph DP["Document Processing"]
            UC1(["Import PDF Documents"])
            UC2(["Batch Process Documents"])
            UC3(["Extract Material Data"])
            UC4(["Validate Extracted Data"])
            UC5(["Import Material Records"])
        end

        %% Material Information Records
        subgraph MIR["Material Information Records"]
            UC6(["Search Material Records"])
            UC7(["Filter Material Records"])
            UC8(["View Material Specifications"])
            UC9(["View Material Properties"])
            UC10(["View Material Processing Information"])
        end

        %% Material Analysis
        subgraph MA["Material Analysis"]
            UC11(["Compare Data to Specifications"])
            UC12(["View Historical Material Trends"])
            UC13(["Identify Out-of-Spec Materials"])
            UC14(["View Mechanical Property Ranges"])
            UC17(["Export Results (PDF, DOC, CSV)"])
        end

        %% System Administration
        subgraph SA["System Administration"]
            UC15(["Manage User Permissions"])
            UC16(["Monitor Processing Jobs"])
            UC18(["Export Audit Logs"])
        end
    end

    %% R&D
    RD --- UC1
    RD --- UC2
    RD --- UC3
    RD --- UC6
    RD --- UC7
    RD --- UC8
    RD --- UC9
    RD --- UC10
    RD --- UC17

    %% Manufacturing
    MFG --- UC1
    MFG --- UC2
    MFG --- UC3
    MFG --- UC4
    MFG --- UC5
    MFG --- UC6
    MFG --- UC7
    MFG --- UC8
    MFG --- UC9
    MFG --- UC10
    MFG --- UC11
    MFG --- UC12
    MFG --- UC13
    MFG --- UC17

    %% Modeling
    MDL --- UC1
    MDL --- UC2
    MDL --- UC3
    MDL --- UC5
    MDL --- UC6
    MDL --- UC7
    MDL --- UC12
    MDL --- UC14
    MDL --- UC17

    %% System Administrator
    SYSAD --- UC15
    SYSAD --- UC16
    SYSAD --- UC18



    class RD,MFG,MDL,SYSAD actor
    class UC1,UC2,UC3,UC4,UC5,UC6,UC7,UC8,UC9,UC10,UC11,UC12,UC13,UC14,UC15,UC16,UC17,UC18 usecase
```

## What the diagram shows

Four groups of Edwards employees use the system. Any employee in R&D,
Manufacturing or Modeling can import and batch-process PDF documents (to be
confirmed with the sponsor); Manufacturing also validates extracted data and
compares it to specifications. All three groups search, view and export
results (PDF, DOC, CSV; export is planned as one of the last features). The
System Administrator manages permissions, monitors processing jobs, and is the
only role that can export the audit log, which records every user action and
is not shown elsewhere in the web app. Everyone signs in with Edwards'
Microsoft SSO.

## What is NOT designed yet

- **The role list** will be reviewed by the team later (#78); which role may
  validate and approve data is not final.
- **Specification comparisons** (Compare Data to Specifications, Identify
  Out-of-Spec Materials) depend on Edwards supplying specification limits.
