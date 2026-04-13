# Mermaid Diagram Templates

Ready-to-use Mermaid templates for mainframe code analysis. Copy and modify these templates when generating diagrams.

## Standard Colour Classes

Include these at the top of every diagram:

```mermaid
classDef prog fill:#4CAF50,color:#fff,stroke:#388E3C
classDef sub fill:#2196F3,color:#fff,stroke:#1565C0
classDef help fill:#FF9800,color:#fff,stroke:#EF6C00
classDef map fill:#9C27B0,color:#fff,stroke:#7B1FA2
classDef file fill:#607D8B,color:#fff,stroke:#455A64
classDef txn fill:#F44336,color:#fff,stroke:#C62828
classDef decision fill:#FFC107,color:#000,stroke:#F9A825
classDef readonly fill:#E3F2FD,stroke:#1565C0,color:#000
classDef editable fill:#FFF3E0,stroke:#EF6C00,color:#000
classDef confirm fill:#E8F5E9,stroke:#2E7D32,color:#000
classDef error fill:#FFEBEE,stroke:#C62828,color:#000
classDef step fill:#2196F3,color:#fff
classDef data fill:#FF9800,color:#000
classDef ok fill:#4CAF50,color:#fff
classDef fail fill:#F44336,color:#fff
```

## Template 1: Call Hierarchy

```mermaid
graph TD
    classDef prog fill:#4CAF50,color:#fff
    classDef sub fill:#2196F3,color:#fff
    classDef help fill:#FF9800,color:#fff
    classDef map fill:#9C27B0,color:#fff
    classDef file fill:#607D8B,color:#fff
    classDef decision fill:#FFC107,color:#000

    ENTRY[PGM-MAIN]:::prog
    ENTRY --> D1{condition?}:::decision
    D1 -->|Yes| S1[SUB-PROCESS]:::sub
    D1 -->|No| S2[SUB-ALTERNATE]:::sub
    S1 --> H1[HELP-FORMAT]:::help
    S1 --> DB1[(FILE-nnn: READ)]:::file
    S2 --> M1[/MAP-SCREEN/]:::map
    S2 --> DB2[(FILE-mmm: STORE)]:::file
```

## Template 2: Data Flow with Swimlanes

```mermaid
graph LR
    classDef ui fill:#9C27B0,color:#fff
    classDef logic fill:#2196F3,color:#fff
    classDef db fill:#607D8B,color:#fff

    subgraph User Interface
        M1[/MAP-INPUT/]:::ui
        M2[/MAP-RESULT/]:::ui
    end

    subgraph Business Logic
        P1[PGM-PROCESS]:::logic
        P2[SUB-VALIDATE]:::logic
    end

    subgraph Database
        F1[(FILE-nnn)]:::db
        F2[(FILE-mmm)]:::db
    end

    M1 -->|user data| P1
    P1 --> P2
    P2 -->|valid| F1
    F1 -->|result| M2
    P1 -->|audit log| F2
```

## Template 3: Screen Navigation

```mermaid
graph TD
    classDef readonly fill:#E3F2FD,stroke:#1565C0,color:#000
    classDef editable fill:#FFF3E0,stroke:#EF6C00,color:#000
    classDef confirm fill:#E8F5E9,stroke:#2E7D32,color:#000
    classDef error fill:#FFEBEE,stroke:#C62828,color:#000

    START((Start)) --> S1[Search Screen]:::editable
    S1 -->|ENTER| S2[Results]:::readonly
    S1 -->|PF3| EXIT((Exit))
    S2 -->|Select| S3[Detail]:::readonly
    S2 -->|PF3| S1
    S3 -->|PF5=Edit| S4[Edit Form]:::editable
    S3 -->|PF3| S2
    S4 -->|ENTER=Save| S5[Confirmation]:::confirm
    S4 -->|PF12=Cancel| S3
    S4 -.->|validation fail| ERR[Error]:::error
    ERR -.-> S4
```

## Template 4: JCL Job Flow

```mermaid
graph TD
    classDef step fill:#2196F3,color:#fff
    classDef data fill:#FF9800,color:#000
    classDef db fill:#607D8B,color:#fff
    classDef fail fill:#F44336,color:#fff
    classDef ok fill:#4CAF50,color:#fff

    START((JOB START)) --> S1[Step 1: EXTRACT]:::step
    S1 -->|RC=0| D1[/extract.file/]:::data
    S1 -->|RC>4| FAIL((ABEND)):::fail
    D1 --> S2[Step 2: PROCESS]:::step
    S2 --> DB[(FILE-nnn)]:::db
    S2 --> END((COMPLETE)):::ok
```

## Template 5: Bottom-Up File Access

```mermaid
graph RL
    classDef file fill:#607D8B,color:#fff
    classDef read fill:#4CAF50,color:#fff
    classDef write fill:#FF9800,color:#fff
    classDef update fill:#2196F3,color:#fff
    classDef delete fill:#F44336,color:#fff

    DB[(FILE-nnn: TABLE)]:::file
    P1[PGM-A: READ]:::read --> DB
    P2[PGM-B: UPDATE]:::update --> DB
    P3[PGM-C: STORE]:::write --> DB
    P4[PGM-D: DELETE]:::delete --> DB
```

## Template 6: Field Lineage

```mermaid
graph LR
    classDef input fill:#4CAF50,color:#fff
    classDef process fill:#2196F3,color:#fff
    classDef store fill:#607D8B,color:#fff
    classDef display fill:#9C27B0,color:#fff
    classDef copy fill:#F44336,color:#fff

    I1[MAP: user input]:::input --> V1[Validate]:::process
    V1 --> S1[(STORE field)]:::store
    S1 --> R1[READ field]:::store
    R1 --> D1[MAP: display]:::display
    R1 --> C1[Copy to FILE-mmm]:::copy
```

## Template 7: Entity Relationship

```mermaid
graph LR
    classDef file fill:#607D8B,color:#fff

    F1[(CUSTOMER<br/>FILE-152)]:::file
    F2[(ORDER<br/>FILE-200)]:::file
    F3[(ORDER-LINE<br/>FILE-201)]:::file
    F4[(PRODUCT<br/>FILE-300)]:::file

    F1 -->|CUST-ID| F2
    F2 -->|ORDER-ID| F3
    F3 -->|PROD-ID| F4
```

## Template 8: Validation Flow

```mermaid
graph TD
    classDef pass fill:#4CAF50,color:#fff
    classDef fail fill:#F44336,color:#fff
    classDef check fill:#2196F3,color:#fff

    INPUT[Input] --> M{Mandatory?}:::check
    M -->|empty| E1[Error: Required]:::fail
    M -->|filled| F{Format?}:::check
    F -->|invalid| E2[Error: Bad format]:::fail
    F -->|valid| R{Range?}:::check
    R -->|out| E3[Error: Out of range]:::fail
    R -->|in| L{Lookup?}:::check
    L -->|not found| E4[Error: Not found]:::fail
    L -->|found| OK[PASSED]:::pass
    OK --> DB[(Write to DB)]
```

## Complexity Guidelines

| Record Count | Approach |
|---|---|
| < 10 nodes | Single diagram, full detail |
| 10-25 nodes | One diagram, abbreviate labels |
| 25-50 nodes | Overview diagram + detail diagrams per subsystem |
| 50+ nodes | Multi-level: L0 overview, L1 per module, L2 per program |

## Node Label Conventions

- Programs: `[PGM-NAME<br/>brief purpose]`
- Files: `[(FILE-nnn<br/>TABLE-NAME)]`
- Maps: `[/MAP-NAME<br/>screen title/]`
- Decisions: `{condition?}`
- Data: `[/dataset.name/]`
- Start/End: `((label))`
