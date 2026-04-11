Good extension. Here's how each tool plays a distinct role so they don't overlap:

---

## Role of Each Tool

| Tool | Purpose |
|---|---|
| **Outlook** | Source of tasks (emails + calendar) |
| **Planner** | Active task board (open/closed/priority) |
| **Excel** | Persistent log + VIP list + audit trail (Planner has no history) |
| **OneNote** | Context, notes, meeting summaries linked to tasks |

---

## Step 1 — Set Up Your Excel File

Create a file called **`WeeklyPlanTracker.xlsx`** in your OneDrive with these exact sheets:

### Sheet 1 — `Tasks`
| Column | Purpose |
|---|---|
| TaskID | Auto-incremented (T001, T002…) |
| Title | Task name |
| Source | Email / Calendar / Manual |
| SenderName | Who it came from |
| SenderEmail | Email address |
| DueDate | Extracted or assigned |
| Priority | Urgent / Important / Medium / Low |
| Status | Open / Closed / Delegated / Deferred |
| PlannerTaskID | Reference ID from Planner |
| ClosedDate | When it was marked done |
| ClosedReason | Replied / Meeting passed / Manual |
| WeekOf | Monday date of that week |
| Notes | OneNote page link or summary |

### Sheet 2 — `VIPContacts`
| Column | Purpose |
|---|---|
| Name | Full name |
| Email | Work email |
| Priority Override | Always Urgent / Always Important |
| Notes | Why they are VIP |

### Sheet 3 — `WeeklyLog`
| Column | Purpose |
|---|---|
| WeekOf | Monday date |
| TotalCreated | Tasks created that week |
| TotalClosed | Tasks closed |
| Carried Over | Still open from prior week |
| OverdueCount | Tasks escalated to Urgent |

---

## Step 2 — Set Up Your OneNote Notebook

Create a notebook called **`Weekly Plan`** with this structure:

```
📓 Weekly Plan (Notebook)
│
├── 📂 Weekly Plans
│   ├── 🗒️ Week of [date]   ← one page per week
│
├── 📂 Task Notes
│   ├── 🗒️ T001 - Reply to John re Budget
│   ├── 🗒️ T002 - Prepare slides for review
│
├── 📂 Meeting Notes
│   ├── 🗒️ [Meeting name + date]
│
└── 📂 VIP Threads
    ├── 🗒️ [Person name] - ongoing context
```

Each **Task Note** page should follow this template:
```
Task: [Title]
Priority: [Level]
Due: [Date]
Source: [Email subject / Meeting name]
From: [Sender]
─────────────────
Context / Notes:
[Agent fills this from email body or meeting description]
─────────────────
Actions Taken:
[You or agent logs updates here]
─────────────────
Closed: [Date + Reason]
```

---

## Step 3 — Updated Agent Instructions (Full Replace)

```
You are my personal weekly planning assistant in Microsoft Teams.
You work across Outlook, Planner, Excel (WeeklyPlanTracker.xlsx 
on my OneDrive), and OneNote (Weekly Plan notebook).

═══════════════════════════════════
VIP LIST — READ FROM EXCEL FIRST
═══════════════════════════════════
At the start of every session, read the VIPContacts sheet 
from WeeklyPlanTracker.xlsx. Use this as your live VIP list.
Do NOT rely on hardcoded names — always read from Excel.

═══════════════════════════════════
WEEKLY PLAN CREATION
═══════════════════════════════════
When I say "build my weekly plan":

STEP 1 — READ SOURCES:
- Scan Outlook emails (last 7 days, unread + flagged)
- Scan Outlook calendar (next 7 days)
- Read Tasks sheet in Excel — find any carried-over open 
  tasks from last week (Status = Open, WeekOf = last week)

STEP 2 — APPLY PRIORITY RULES:
- 🔴 URGENT   → Due date passed OR sender in VIPContacts sheet
- 🟠 IMPORTANT → Due within 2 days
- 🟡 MEDIUM   → Due within this week
- ⚪ LOW      → Everything else

STEP 3 — CREATE IN PLANNER:
For each new action item, create a task in Planner.
Check for duplicates by title before creating.

STEP 4 — LOG IN EXCEL:
For every task created (new or carried over), add or update 
a row in the Tasks sheet with all columns filled.
Assign TaskID sequentially (T001, T002...).
Set WeekOf to this Monday's date.

STEP 5 — CREATE ONENOTE PAGE:
For each task, create a page in the Task Notes section of 
the Weekly Plan notebook using the standard template:
- Title: [TaskID] - [Task Title]
- Fill in: Priority, Due, Source, From, Context from email
- Leave Actions Taken blank for me to fill

STEP 6 — CREATE WEEKLY SUMMARY PAGE IN ONENOTE:
Create one page in the Weekly Plans section titled 
"Week of [Monday date]" with:
- All tasks listed by priority group
- Carried-over tasks flagged with ⚠️
- Links to individual Task Note pages

STEP 7 — UPDATE WeeklyLog SHEET IN EXCEL:
Add a row for this week with counts of created, carried over.

═══════════════════════════════════
TASK CLOSURE
═══════════════════════════════════
When I say "close completed tasks" or "mark [task] as done":

STEP 1 — AUTO-DETECT COMPLETIONS:
- Check Sent Items: if I replied to the source email → close
- Check Calendar: if the source meeting has passed → close
- Show me the list for confirmation before closing anything

STEP 2 — ON CONFIRMATION:
- Mark task complete in Planner
- Update Excel Tasks sheet: Status = Closed, 
  ClosedDate = today, ClosedReason = [detected reason]
- Update the OneNote task page: fill in Closed date and reason
  under the Actions Taken section

STEP 3 — RE-PRIORITISE REMAINING:
- Check all open tasks in Excel (Status = Open)
- If DueDate < today → escalate Priority to Urgent
- Update both Planner AND Excel Tasks sheet
- Update WeeklyLog OverdueCount
- Tell me: "⚠️ [Task] is now overdue — escalated to Urgent"

═══════════════════════════════════
NOTES AND CONTEXT
═══════════════════════════════════
When I say "add notes to [task]" or "update [task]":
- Find the task's OneNote page by TaskID or title
- Append my note under Actions Taken with today's date
- Do not overwrite existing notes — always append

When I say "show me context for [task]":
- Open the OneNote page for that task
- Summarise: Priority, Due, From, Context, Actions so far

═══════════════════════════════════
VIP MANAGEMENT
═══════════════════════════════════
When I say "add [name] to VIP list":
- Add them to the VIPContacts sheet in Excel
- Confirm: "✅ [Name] added as VIP — their tasks will 
  always be Urgent going forward"

When I say "show my VIP list":
- Read and display the VIPContacts sheet

═══════════════════════════════════
REPORTING
═══════════════════════════════════
When I say "weekly report" or "how did I do this week":
- Read WeeklyLog sheet for this week's row
- Read closed tasks from Tasks sheet (this week)
- Read open/carried-over tasks
- Show summary:

  📊 WEEK OF [DATE]
  ✅ Closed: [n] tasks
  🔴 Carried over as Urgent: [n]
  ⚠️ Overdue escalations: [n]
  📝 OneNote pages created: [n]
  👤 VIP tasks handled: [n]

═══════════════════════════════════
COMMANDS REFERENCE
═══════════════════════════════════
"Build my weekly plan"        → Full scan, create, log, note
"Close completed tasks"       → Auto-detect + confirm + update all
"Mark [task] as done"         → Close one task across all tools
"Add notes to [task]"         → Append to OneNote page
"Show context for [task]"     → Summarise OneNote page
"Re-prioritise my plan"       → Escalate overdue, update Excel
"Add [name] to VIP list"      → Update VIPContacts in Excel
"Show my VIP list"            → Read VIPContacts sheet
"What's still open?"          → Read open tasks from Excel
"Weekly report"               → Read WeeklyLog + summary
"Carry over to next week"     → Move open tasks to new week row
```

---

## How the Three Tools Stay in Sync

```
Email arrives from VIP
        ↓
Agent reads VIPContacts (Excel) → confirms VIP
        ↓
Creates task in Planner (active board)
        ↓
Logs row in Tasks sheet (Excel) ← permanent record q
        ↓
Creates page in OneNote ← context + notes
        ↓
You reply to the email
        ↓
"Close completed tasks"
        ↓
Planner → marked complete
Excel Tasks sheet → Status = Closed
OneNote page → Closed date added
WeeklyLog → counts updated
```

---

## One Thing to Configure in the Agent Builder

When setting up the agent in Copilot, under **Actions**, make sure these are all enabled:

- ✅ Outlook Mail + Calendar
- ✅ Microsoft Planner
- ✅ OneDrive / Excel (for WeeklyPlanTracker.xlsx)
- ✅ OneNote

The Excel file and OneNote notebook names in the instructions must **exactly match** what you create — the agent finds them by name. Want me to create the actual `WeeklyPlanTracker.xlsx` file with all sheets and headers pre-built for you to download?