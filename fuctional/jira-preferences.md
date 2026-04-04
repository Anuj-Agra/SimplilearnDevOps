# JIRA Preferences

Questions to ask the user to customise ticket output. Use sensible defaults so the user only needs to answer if they want something different.

---

## Questions (only ask if not already clear from context)

### 1. Ticket hierarchy

**Default:** Epic → Stories (no sub-tasks)

Ask only if the requirement is large or the user mentions sub-tasks:
"Should I break this into Epics → Stories, or do you also want Sub-tasks under the Stories?"

### 2. Story points / sizing

**Default:** Not included

Ask only if the user mentions estimation:
"Would you like me to include story point estimates? I can suggest T-shirt sizes (S/M/L/XL) or numeric points (1/2/3/5/8/13)."

If yes:
- **S (1-2 pts):** Single field/label/rule change, no new screens
- **M (3-5 pts):** New screen section, new workflow step, moderate logic
- **L (8 pts):** New screen, new integration, complex rules
- **XL (13 pts):** New feature area, multiple screens, multiple roles

### 3. Labels and components

**Default:** Module name as the only label

Ask only if the user mentions team structure:
"Do you have specific JIRA labels or component names you'd like me to use?"

### 4. Sprint or release target

**Default:** Not included

### 5. Assignee

**Default:** Not included (never assume)

### 6. Priority definitions

| Priority | When to use |
|----------|------------|
| Critical | System broken, data loss risk, security issue |
| High | Core workflow blocked, affects many users, compliance |
| Medium | Enhancement to existing feature, affects some users |
| Low | Nice-to-have, cosmetic, affects few users |

### 7. Markdown vs JIRA wiki markup

**Default:** Markdown (JIRA renders it natively)

If user asks for wiki markup, convert:
- `**bold**` → `*bold*`
- `## Heading` → `h2. Heading`
- `- bullet` → `* bullet`
- `| table |` → `|| header ||` / `| cell |`
