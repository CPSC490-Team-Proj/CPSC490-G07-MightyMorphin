## Design -- Use Case Diagram
Epic: [#42](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/42) · Stories: [#36](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/36)<br>
Owner: Liam Wilson · Sprint: 2 · Status: draft 

```mermaid
flowchart LR
    %% Actors
    EMP["Employee"]
    MNG["Manager"]

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

    %% All operational capabilities are available to every Employee
    EMP --- UC1
    EMP --- UC2
    EMP --- UC3
    EMP --- UC4
    EMP --- UC5
    EMP --- UC6
    EMP --- UC7
    EMP --- UC8
    EMP --- UC9
    EMP --- UC10
    EMP --- UC11
    EMP --- UC12
    EMP --- UC13
    EMP --- UC14
    EMP --- UC17

    %% Administrative capabilities
    MNG --- UC15
    MNG --- UC16
    MNG --- UC18

    class EMP,MNG actor
    class UC1,UC2,UC3,UC4,UC5,UC6,UC7,UC8,UC9,UC10,UC11,UC12,UC13,UC14,UC15,UC16,UC17,UC18 usecase
```
