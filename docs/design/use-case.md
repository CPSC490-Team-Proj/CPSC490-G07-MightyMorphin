@startuml
left to right direction

skinparam packageStyle rectangle
skinparam shadowing false
skinparam actorStyle stickman

actor "R&D" as rd
actor "Manufacturing" as mfg
actor "Modeling" as mdl
actor "System Administrator" as sysad


rectangle "Material Data Management System" {
  ' Document Processing
  package "Document Processing"{
    usecase "Import PDF Documents" as UC1
    usecase "Batch Process Documents" as UC2
    usecase "Extract Material Data" as UC3
    usecase "Validate Extracted Data" as UC4
    usecase "Import Material Records" as UC5
  }
  
  ' Material Information Records
  package "Material Information Records" {
    usecase "Search Material Records" as UC6
    usecase "Filter Material Records" as UC7
    usecase "View Material Specifications" as UC8
    usecase "View Material Properties" as UC9
    usecase "View Material Processing Info" as UC10
  }
  
  ' Material Analysis
  package "Material Analysis" {
    usecase "Compare Data to Specifications" as UC11
    usecase "View Historical Material Trends" as UC12
    usecase "Identify Out-of-Spec Materials" as UC13
    usecase "View Mechanical Property Ranges" as UC14
  }
  
  ' System Administration
  package "System Administration" {
    usecase "Manage User Accounts" as UC15
    usecase "Manage User Permissions" as UC16
    usecase "Monitor Processing Jobs" as UC17
  }
  

}

' R&D
rd -- UC3
rd -- UC6
rd -- UC7
rd -- UC8
rd -- UC9
rd -- UC10

' Manufacturing
mfg -- UC1
mfg -- UC2
mfg -- UC3
mfg -- UC4
mfg -- UC5
mfg -- UC6
mfg -- UC7
mfg -- UC8
mfg -- UC9
mfg -- UC10
mfg -- UC11
mfg -- UC12
mfg -- UC13

' Modeling
mdl -- UC1
mdl -- UC2
mdl -- UC3
mdl -- UC5
mdl -- UC6
mdl -- UC7
mdl -- UC12
mdl -- UC14

' System Administrator
sysad -- UC15
sysad -- UC16
sysad -- UC17


@enduml