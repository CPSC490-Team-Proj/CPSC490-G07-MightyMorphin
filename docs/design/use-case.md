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
            UC10(["View Material Processing Info"])
        end

        %% Material Analysis
        subgraph MA["Material Analysis"]
            UC11(["Compare Data to Specifications"])
            UC12(["View Historical Material Trends"])
            UC13(["Identify Out-of-Spec Materials"])
            UC14(["View Mechanical Property Ranges"])
        end

        %% System Administration
        subgraph SA["System Administration"]
            UC15(["Manage User Accounts"])
            UC16(["Manage User Permissions"])
            UC17(["Monitor Processing Jobs"])
        end
    end

    %% R&D
    RD --- UC3
    RD --- UC6
    RD --- UC7
    RD --- UC8
    RD --- UC9
    RD --- UC10

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

    %% Modeling
    MDL --- UC1
    MDL --- UC2
    MDL --- UC3
    MDL --- UC5
    MDL --- UC6
    MDL --- UC7
    MDL --- UC12
    MDL --- UC14

    %% System Administrator
    SYSAD --- UC15
    SYSAD --- UC16
    SYSAD --- UC17



    class RD,MFG,MDL,SYSAD actor
    class UC1,UC2,UC3,UC4,UC5,UC6,UC7,UC8,UC9,UC10,UC11,UC12,UC13,UC14,UC15,UC16,UC17 usecase
```