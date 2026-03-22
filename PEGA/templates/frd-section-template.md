# FRD Section Template

> **Agent 06 uses this structure** for each section of the Functional Requirements Document.
> Copy the relevant section below when building the FRD incrementally.

---

## Section: Process Flow

```markdown
### [N.X] [Flow Name]

#### [N.X.1] Business Description
[2-3 paragraphs describing what this process does in business terms.
Who initiates it? What is the expected outcome? What business value does it deliver?]

#### [N.X.2] Actors and Roles
| Actor | Responsibilities |
|-------|-----------------|
| [Role] | [What they do in this flow] |

#### [N.X.3] Process Steps
1. [Actor] [action in active voice]
2. The system [automated action]
3. **DECISION**: If [condition], then [path A]. Otherwise, [path B].
4. [Continue numbering...]

#### [N.X.4] Decision Points
| Step | Condition | True Path | False Path |
|------|-----------|-----------|------------|
| [#] | [business condition] | [what happens] | [what happens] |

#### [N.X.5] Sub-Processes
| Sub-Process | Called At Step | Purpose | See Section |
|-------------|---------------|---------|-------------|
| [name] | [#] | [why] | [section ref] |

#### [N.X.6] Exceptions
| Scenario | Handling | Fallback |
|----------|----------|----------|
| [what can go wrong] | [how it's handled] | [last resort] |
```

## Section: Business Rule

```markdown
### [N.X] [Rule Name]

#### [N.X.1] Business Description
[What business question does this rule answer?]

#### [N.X.2] Conditions
| # | Business Condition | Check | Action if Met |
|---|-------------------|-------|---------------|
| 1 | [plain English] | [what's compared] | [outcome] |

#### [N.X.3] Examples
**Example 1**: [Scenario description]
- Input: [specific values]
- Result: [outcome and why]

**Example 2**: [Scenario description]
- Input: [specific values]
- Result: [outcome and why]

#### [N.X.4] Referenced By
- Used in [Flow Name] at step [N] (See Section [X.Y])
```

## Section: UI Screen

```markdown
### [N.X] [Screen Name]

#### [N.X.1] Purpose
[When does this screen appear? Which flow step shows it?]

#### [N.X.2] Layout
[Describe the screen layout — tabs, panels, column arrangement]

#### [N.X.3] Fields
| Field | Type | Required | Validation | Visibility Condition |
|-------|------|----------|------------|---------------------|
| [label] | [type] | [Y/N] | [rule] | [when shown] |

#### [N.X.4] Actions
| Button | Behavior |
|--------|----------|
| [label] | [what happens when clicked] |
```

## Section: Integration

```markdown
### [N.X] [Integration Name]

#### [N.X.1] Business Purpose
[Why does the application call this external system?]

#### [N.X.2] Data Exchanged
- **Sends**: [list of data sent to external system]
- **Receives**: [list of data received back]

#### [N.X.3] Error Handling
| Error | Business Impact | Fallback |
|-------|----------------|----------|
| [scenario] | [what breaks] | [how it's handled] |

#### [N.X.4] Referenced By
- Called from [Flow Name] at step [N] (See Section [X.Y])
```
