---
name: flowchart-gen
description: "Generates Mermaid-syntax flowcharts and diagrams from mainframe code analysis. Supports call hierarchies, data flow diagrams, screen navigation flows, entity-relationship diagrams, and job flow diagrams. Use when the user says 'FLOW CHART', 'draw a diagram', 'generate a flowchart', 'visualise', 'mermaid diagram', 'call tree diagram', 'data flow diagram', 'screen flow', 'navigation diagram', or wants any visual representation of mainframe code structure or data movement."
---

# Flowchart & Diagram Generation

Generate production-ready Mermaid diagrams from mainframe code analysis.

## Diagram Types

### Type 1: Call Hierarchy (graph TD)

Shows program call chains, top-down.

```mermaid
graph TD
    classDef prog fill:#4CAF50,color:#fff,stroke:#388E3C
    classDef sub fill:#2196F3,color:#fff,stroke:#1565C0
    classDef help fill:#FF9800,color:#fff,stroke:#EF6C00
    classDef map fill:#9C27B0,color:#fff,stroke:#7B1FA2
    classDef file fill:#607D8B,color:#fff,stroke:#455A64
    classDef ext fill:#F44336,color:#fff,stroke:#C62828
    classDef decision fill:#FFC107,color:#000,stroke:#F9A825

    ENTRY[PGM-MAIN<br/>Main Program]:::prog
    ENTRY --> D1{Customer exists?}:::decision
    D1 -->|Yes| S1[SUB-GETDATA<br/>Retrieve customer]:::sub
    D1 -->|No| S2[SUB-CREATE<br/>New customer]:::sub
    S1 --> H1[HELP-FORMAT<br/>Format display]:::help
    S1 --> DB1[(FILE-152<br/>READ)]:::file
    S2 --> M1[/MAP-CUSTENTRY<br/>Input screen/]:::map
    S2 --> DB2[(FILE-152<br/>STORE)]:::file
    H1 --> M2[/MAP-CUSTDISP<br/>Display screen/]:::map
```

**Rules:**
- Entry program at top
- Rectangles for programs (with class)
- Rounded rectangles or cylinders for Adabas files
- Parallelograms for maps/screens
- Diamonds for decisions
- Edge labels for conditions and key parameters
- Shared subprograms shown once with multiple incoming edges

### Type 2: Data Flow Diagram (graph LR)

Shows how data moves through the system, left-to-right.

```mermaid
graph LR
    classDef ui fill:#9C27B0,color:#fff
    classDef logic fill:#2196F3,color:#fff
    classDef db fill:#607D8B,color:#fff
    classDef ext fill:#FF9800,color:#fff

    subgraph User Interface
        M1[/MAP-SEARCH/]:::ui
        M2[/MAP-RESULT/]:::ui
        M3[/MAP-EDIT/]:::ui
    end

    subgraph Business Logic
        P1[PGM-SEARCH]:::logic
        P2[SUB-VALIDATE]:::logic
        P3[PGM-UPDATE]:::logic
    end

    subgraph Database
        F1[(FILE-152<br/>CUSTOMER)]:::db
        F2[(FILE-200<br/>AUDIT-LOG)]:::db
    end

    M1 -->|#SEARCH-KEY| P1
    P1 -->|FIND BY KEY| F1
    F1 -->|customer data| P1
    P1 -->|display fields| M2
    M3 -->|edited fields| P2
    P2 -->|validated data| P3
    P3 -->|UPDATE| F1
    P3 -->|STORE audit| F2
```

**Rules:**
- Use swimlane subgraphs: User Interface, Business Logic, Database
- Edge labels show field names or operation types
- Direction of arrow shows data movement
- Bidirectional flows use two separate edges

### Type 3: Screen Navigation (graph TD)

Shows the user's journey through screens.

```mermaid
graph TD
    classDef readonly fill:#E3F2FD,stroke:#1565C0,color:#000
    classDef editable fill:#FFF3E0,stroke:#EF6C00,color:#000
    classDef confirm fill:#E8F5E9,stroke:#2E7D32,color:#000
    classDef error fill:#FFEBEE,stroke:#C62828,color:#000
    classDef entry fill:#F3E5F5,stroke:#7B1FA2,color:#000

    START((TXN Start)):::entry --> S1
    S1[Search Screen<br/>3 editable fields]:::editable
    S1 -->|ENTER: search| S2[Results List<br/>display only]:::readonly
    S1 -->|PF3| EXIT((Exit))
    S2 -->|Select row| S3[Detail View<br/>15 display fields]:::readonly
    S2 -->|PF3| S1
    S3 -->|PF5=Edit| S4[Edit Form<br/>8 editable fields]:::editable
    S3 -->|PF3| S2
    S4 -->|ENTER=Save| S5[Saved OK]:::confirm
    S4 -->|PF12=Cancel| S3
    S4 -.->|validation fail| ERR[Error Message<br/>highlighted fields]:::error
    ERR -.-> S4
    S5 -->|ENTER| S3
```

**Rules:**
- Annotate each screen node with field counts
- Colour-code: blue=read-only, orange=editable, green=confirmation, red=error
- Solid arrows for normal flow, dashed for error/exception flow
- PF-key labels on edges
- Round nodes for entry/exit points

### Type 4: Entity Relationship (graph LR)

Shows Adabas file relationships.

```mermaid
graph LR
    classDef file fill:#607D8B,color:#fff

    F1[(FILE-152<br/>CUSTOMER)]:::file
    F2[(FILE-200<br/>ORDER)]:::file
    F3[(FILE-201<br/>ORDER-LINE)]:::file
    F4[(FILE-300<br/>PRODUCT)]:::file
    F5[(FILE-050<br/>REF-STATUS)]:::file

    F1 -->|CUST-ID| F2
    F2 -->|ORDER-ID| F3
    F3 -->|PRODUCT-ID| F4
    F1 -->|CUST-STATUS → STATUS-CODE| F5
    F2 -->|ORDER-STATUS → STATUS-CODE| F5
```

### Type 5: Job Flow (graph TD)

Shows batch JCL execution flow.

```mermaid
graph TD
    classDef step fill:#2196F3,color:#fff
    classDef data fill:#FF9800,color:#000
    classDef db fill:#607D8B,color:#fff
    classDef fail fill:#F44336,color:#fff
    classDef ok fill:#4CAF50,color:#fff

    START((JOB START)) --> S1[Step 1: EXTRACT<br/>PGM-EXTCUST]:::step
    S1 -->|RC=0| D1[/CUST.EXTRACT.FILE/]:::data
    S1 -->|RC>4| FAIL((ABEND)):::fail
    D1 --> S2[Step 2: SORT<br/>SORT utility]:::step
    S2 -->|RC=0| D2[/CUST.SORTED.FILE/]:::data
    D2 --> S3[Step 3: VALIDATE<br/>PGM-VALCUST]:::step
    S3 --> D3[/CUST.VALID.FILE/]:::data
    S3 --> D4[/CUST.REJECT.FILE/]:::data
    D3 --> S4[Step 4: LOAD<br/>PGM-LOADCUST]:::step
    S4 -->|UPDATE| DB[(FILE-152)]:::db
    S4 --> END((JOB END)):::ok
    D4 --> S5[Step 5: REPORT<br/>PGM-ERRPT]:::step
```

## Complexity Guidelines

- **Simple** (< 10 nodes): Single diagram, all detail
- **Medium** (10-25 nodes): One main diagram with annotations
- **Complex** (25+ nodes): Break into multiple diagrams — overview + detail views
  - Overview: top-level programs and files only
  - Detail: one diagram per major branch/subsystem

## Common Patterns to Recognise

When generating diagrams, look for and label these patterns:
- **Hub**: One program called by many others (shared utility)
- **Pipeline**: Linear A→B→C→D processing chain
- **Fan-out**: One program calls many subprograms
- **Fan-in**: Many programs call one shared subprogram
- **Loop**: READ/FIND loop processing multiple records
- **Master-Detail**: Parent record lookup followed by child record processing
