---
name: impact-analysis
description: "Assesses the impact of proposed changes to mainframe systems: field modifications, program retirements, file structure changes, new requirements. Use when the user says 'IMPACT CHECK', 'what if we change', 'impact analysis', 'change assessment', 'retire this program', 'modify this field', 'add a field', 'remove a field', 'what would break', or any request to understand the ripple effects of a proposed modification."
---

# Impact Analysis

Assess the full ripple effects of proposed changes to mainframe components.

## Change Types and Analysis Paths

### Type 1: Field Modification

**Triggers:** change length, change format, add/remove descriptor, rename field, add new field, remove field

#### Analysis Template

```
PROPOSED CHANGE: [describe the change]
TARGET:          [FILE-nnn.FIELD-NAME via DDM-xxx]
CHANGE TYPE:     [length / format / descriptor / rename / add / remove]
```

**Step 1: Direct References** — Find every program referencing this field
| Program | Library | Usage (R/W/Search/Display) | Code Change Needed | Effort |
|---------|---------|---------------------------|-------------------|--------|

**Step 2: DDM Changes**
- DDM regeneration required? [Y/N]
- New DDM definition: [show changed field]
- Copybook/LDA updates needed: [list]

**Step 3: Map/Screen Changes**
| Map | Field on Screen | Change Needed | Layout Impact |
|-----|----------------|---------------|---------------|

**Step 4: JCL/Batch Impact**
| Job | Step | Program | Change Needed |
|-----|------|---------|---------------|
- Dataset layout changes?
- SORT card field position changes?

**Step 5: Cross-File Propagation**
If this field is copied to other files, trace those:
| Source | Copy Program | Target File.Field | Change Also Needed? |
|--------|-------------|-------------------|-------------------|

**Step 6: Superdescriptor Impact**
If the field is part of a superdescriptor:
- Superdescriptor name and definition
- Programs using FIND/READ BY this superdescriptor
- Key format change implications

**Step 7: Downstream Systems**
- Extracts or interfaces that include this field
- External systems that consume data from this file
- Reports that display this field

### Type 2: Program Retirement

**Triggers:** retire, remove, decommission, replace a program

#### Analysis Template

```
PROGRAM TO RETIRE: [PGM-name]
LIBRARY:           [library]
```

**Step 1: Callers** — Who calls this program?
| Caller | Library | Call Statement | Parameters | Can Caller Be Modified? |
|--------|---------|---------------|------------|------------------------|

Trace callers recursively up to top-level entry points.

**Step 2: Transaction Impact**
| Transaction | Role of Retired Program | Alternative? |
|-------------|----------------------|-------------|

**Step 3: JCL Impact**
| Job | Step | What Happens Without This Program |
|-----|------|---------------------------------|

**Step 4: Unique Functions** — What does ONLY this program do?
| Function | Adabas Operations | Replacement Needed? |
|----------|------------------|-------------------|

**Step 5: Data Integrity** — Will removing this program leave data orphaned or unprocessed?

**Step 6: Retirement Sequence**
Ordered list of prerequisite changes before retirement is safe.

### Type 3: New Requirement

**Triggers:** add functionality, new screen, new field, new validation, new report

#### Analysis Template

```
REQUIREMENT:     [describe what needs to be added]
AFFECTED AREA:   [transaction / batch / both]
```

**Step 1: Where to Add** — Which existing programs should be modified?
| Program | What to Add | Complexity |

**Step 2: New Components Needed**
| Component | Type | Purpose | Interfaces With |

**Step 3: Database Changes**
| File | Change | New Fields | DDM Regen? |

**Step 4: Testing Scope**
- Transactions to regression test
- Batch jobs to validate
- Edge cases to verify

## Risk Scoring

Rate each affected component:

| Risk Level | Criteria | Action |
|-----------|---------|--------|
| 🔴 HIGH | Core business logic affected, data integrity risk, many callers | Full code review + testing |
| 🟡 MEDIUM | Secondary logic, display changes, few callers | Code review + targeted testing |
| 🟢 LOW | Cosmetic, unused path, single caller | Quick review |

## Output: Prioritised Action Plan

| Priority | Component | Change Required | Risk | Effort (S/M/L) | Dependencies |
|----------|-----------|----------------|------|-----------------|-------------|

**Effort scale:**
- S (Small): < 1 day, single file change
- M (Medium): 1-3 days, multiple files, testing needed
- L (Large): 3+ days, structural change, extensive testing
