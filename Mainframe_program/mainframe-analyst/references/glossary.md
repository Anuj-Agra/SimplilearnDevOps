# Mainframe Glossary & Quick Reference

## Natural Program Types

| Extension | Type | Description |
|-----------|------|-------------|
| .NSP | Program | Top-level Natural program, can be invoked directly |
| .NSN | Subprogram | Called via CALLNAT, cannot run independently |
| .NSL | Local Data Area | Data structure definition (local scope) |
| .NSG | Global Data Area | Data structure definition (session scope) |
| .NSA | Parameter Data Area | Data structure for CALLNAT parameters |
| .NSH | Helproutine | Called via HELP-ROUTINE, typically for field-level help |
| .NSM | Map | Screen layout definition (INPUT/WRITE) |
| .NSC | Copycode | Reusable code fragment (INCLUDE) |

## Natural Statement Quick Reference

### Database Access
| Statement | Operation | Description |
|-----------|-----------|-------------|
| `FIND records IN file WITH criteria` | Search | Returns set of records matching criteria |
| `READ file BY descriptor` | Sequential read | Reads records in descriptor order |
| `GET file ISN` | Direct read | Reads single record by ISN |
| `STORE file` | Insert | Creates new record |
| `UPDATE file` | Modify | Updates current record in loop |
| `DELETE file` | Remove | Deletes current record in loop |
| `HISTOGRAM file FOR descriptor` | Statistics | Returns value distribution |
| `END TRANSACTION` | Commit | Commits Adabas ET (end transaction) |
| `BACKOUT TRANSACTION` | Rollback | Rolls back Adabas BT |

### Program Flow
| Statement | Description |
|-----------|-------------|
| `CALLNAT 'name' params` | Call subprogram, returns to caller |
| `FETCH 'name'` | Transfer control, does not return |
| `PERFORM subroutine` | Call internal subroutine |
| `ESCAPE TOP` | Jump to top of current loop |
| `ESCAPE BOTTOM` | Exit current loop |
| `ESCAPE ROUTINE` | Exit current subroutine/program |
| `STOP` | Terminate program |

### Screen Interaction
| Statement | Description |
|-----------|-------------|
| `INPUT USING MAP 'name'` | Display map and wait for input |
| `INPUT (AD=M) field` | Inline input (mandatory) |
| `WRITE 'text' / field` | Display output line |
| `REINPUT 'message'` | Redisplay map with error message |
| `SET CONTROL 'attribute'` | Set screen attributes |

### Map Attributes
| Code | Meaning |
|------|---------|
| `AD=A` | Editable (modifiable by user) |
| `AD=M` | Mandatory editable (must be filled) |
| `AD=O` | Output only (display, not editable) |
| `AD=P` | Protected (not visible, not editable) |
| `CD=RE` | Red (error) |
| `CD=YE` | Yellow (warning/highlight) |
| `CD=GR` | Green (normal) |
| `CD=BL` | Blue (information) |
| `EM=` | Edit mask (e.g., EM=9999-99-99 for date) |

## COBOL Quick Reference

### Key Divisions
- IDENTIFICATION DIVISION: Program name and metadata
- ENVIRONMENT DIVISION: File assignments
- DATA DIVISION: WORKING-STORAGE, LINKAGE SECTION, FILE SECTION
- PROCEDURE DIVISION: Executable code

### CICS Commands
| Command | Description |
|---------|-------------|
| `EXEC CICS LINK PROGRAM('name')` | Call program, return here |
| `EXEC CICS XCTL PROGRAM('name')` | Transfer control, no return |
| `EXEC CICS RETURN TRANSID('txid')` | Return, set next transaction |
| `EXEC CICS SEND MAP('name')` | Display BMS map |
| `EXEC CICS RECEIVE MAP('name')` | Receive user input from map |
| `EXEC CICS READ FILE('name')` | Read VSAM/Adabas record |
| `EXEC CICS WRITE FILE('name')` | Write new record |
| `EXEC CICS REWRITE FILE('name')` | Update existing record |
| `EXEC CICS DELETE FILE('name')` | Delete record |

## Adabas Concepts

| Concept | Description |
|---------|-------------|
| ISN | Internal Sequence Number — unique record identifier |
| FDT | Field Definition Table — physical file structure |
| DDM | Data Definition Module — logical view of file for Natural |
| Descriptor | Indexed field for efficient searching (FIND/READ BY) |
| Superdescriptor | Compound index combining multiple fields/ranges |
| Subdescriptor | Index on a portion of a field |
| MU field | Multiple-value field (array within a record) |
| PE group | Periodic group (repeating group of fields) |
| ET logic | End Transaction — Adabas commit |
| BT logic | Backout Transaction — Adabas rollback |

## JCL Quick Reference

| Element | Description |
|---------|-------------|
| `//jobname JOB` | Job card — defines the job |
| `//stepname EXEC PGM=` | Execute a program |
| `//stepname EXEC PROC=` | Execute a catalogued procedure |
| `//ddname DD DSN=` | Dataset allocation |
| `DISP=(NEW,CATLG,DELETE)` | Create new, catalogue on success, delete on failure |
| `DISP=SHR` | Share existing dataset |
| `DISP=OLD` | Exclusive access to existing dataset |
| `COND=(4,LT)` | Skip step if RC < 4 from any prior step |
| `PARM='value'` | Pass parameter to program |
