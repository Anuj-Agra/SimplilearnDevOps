# Skill: Screenshot Navigator

> **Referenced by**: All agents
> **Purpose**: Guides analysis when user provides PEGA Designer Studio screenshots

---

## WHEN TO USE THIS SKILL

Use whenever the user provides a screenshot from PEGA Designer Studio, App Studio, or any PEGA UI. Screenshots are valuable for:
- Validating manifest-based analysis
- Filling gaps where manifest data is incomplete
- Understanding visual layout of screens
- Reading flow diagrams directly from the designer
- Resolving binary references that can't be read as JSON

## WHAT TO LOOK FOR IN SCREENSHOTS

### Flow Designer Screenshots
```
Identify in the screenshot:
  □ Shape types (rectangles, diamonds, rounded boxes, circles)
  □ Shape labels (text inside each shape)
  □ Connector lines and their labels
  □ Swim lanes (if present — indicate different actors/roles)
  □ Start/End points
  □ The flow name in the title bar
  □ The class name in the header
  □ Any error indicators (red shapes, broken connectors)

Map each visible element to your existing analysis:
  "I can see shape [X] in the screenshot which matches node [Y] in my analysis"
  "I found a new shape [Z] not in my manifest data — this may be inherited"
```

### Section/UI Designer Screenshots
```
Identify in the screenshot:
  □ Section name in the title
  □ Field labels visible on screen
  □ Field types (text boxes, dropdowns, checkboxes, radio buttons)
  □ Required field indicators (asterisks, red markers)
  □ Read-only fields (grayed out)
  □ Button labels and positions
  □ Tab labels if tabbed layout
  □ Section groupings / panels
  □ Any conditional visibility indicators
  □ Error messages if visible
```

### Decision Rule Screenshots
```
Identify in the screenshot:
  □ Decision table grid (columns = conditions, rows = cases)
  □ Decision tree branches
  □ Condition operators visible in cells
  □ Action/result columns
  □ The evaluation mode indicator
  □ Any "otherwise" row
```

### Properties Panel Screenshots
```
Identify in the screenshot:
  □ Property name and path
  □ Data type (Text, Integer, Date, etc.)
  □ Required indicator
  □ Default value
  □ Control type (text input, dropdown, etc.)
  □ Validation rules shown
```

## CROSS-REFERENCE PROTOCOL

When processing a screenshot:

```
1. IDENTIFY: "This screenshot shows [what — a flow, section, decision, etc.]"

2. MATCH: Compare against existing analysis:
   "Matching against my analysis of [flow/section/decision name]:"
   - Element [A] in screenshot matches [B] in my analysis ✓
   - Element [C] in screenshot is NEW — not in my manifest data
   - Element [D] in my analysis is NOT visible in screenshot (may be hidden)

3. SUPPLEMENT: Extract information only available from the screenshot:
   "From this screenshot I can additionally determine:"
   - [new finding 1]
   - [new finding 2]

4. FLAG DISCREPANCIES:
   "Discrepancies found between manifest and screenshot:"
   - [difference 1 — which source to trust?]
   - [difference 2]

5. UPDATE: Add new findings to the relevant analysis file
```

## ASKING FOR SPECIFIC SCREENSHOTS

When analysis is stuck, ask the user for a specific screenshot:

```
"To complete this analysis, I need a screenshot of:
  WHERE: PEGA Designer Studio → [specific navigation path]
  WHAT:  [what rule/screen to open]
  VIEW:  [which tab or view to show]

To get there:
  1. Open PEGA Designer Studio
  2. Navigate to [App] → [Category] → [Rule name]
  3. [Click on specific tab if needed]
  4. Take a screenshot and paste/attach it here"
```

## COMMON SCREENSHOT REQUESTS

```
For flows:
  "Open the flow rule [name] in App Studio → Processes → [flow name].
   I need to see the visual flow diagram with all shapes and connectors."

For UI:
  "Open the section rule [name] in Dev Studio → User Interface → Section.
   Switch to the Design tab so I can see the field layout."

For decisions:
  "Open the decision table [name] in Dev Studio → Decision → Decision Table.
   I need to see the full grid with all conditions and results."

For connectors:
  "Open the Connect-REST rule [name] in Dev Studio → Integration → Connectors.
   Show the Service tab with endpoint details and the Request/Response tabs."

For data pages:
  "Open the data page [name] in Dev Studio → Data Model → Data Page.
   I need the Definition tab showing load activity and parameters."
```
