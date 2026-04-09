# Scenario Gap Detector — Full Checklist

## Universal Scenarios (check for EVERY feature)

### Double-Submit / Race Conditions
- What happens if the user clicks Submit twice rapidly?
- What happens if two users create the same record simultaneously?
- What happens if a background job updates a record while a user is editing it?
- Is there an optimistic/pessimistic lock? What is the user told if the record changed?

### Session & Auth
- User session expires mid-form → data lost with no warning?
- User role is demoted while logged in → can they still access pages they're currently on?
- User is disabled while logged in → what happens on next action?
- JWT/token expires during a long background operation?

### Navigation & Bookmarks
- User bookmarks a detail page URL → still works after the record is deleted?
- User uses browser Back button after a form submit → does it re-submit?
- User uses browser Refresh on a multi-step form → where do they land?
- Deep link to a page that requires context (e.g. order detail without order in session)?

### Data Boundary Conditions (for every validated field)
| Boundary | Test scenario |
|---|---|
| Minimum allowed value | Enter exactly the minimum |
| One below minimum | Enter minimum − 1 |
| Maximum allowed value | Enter exactly the maximum |
| One above maximum | Enter maximum + 1 |
| Empty / null | Submit with field blank |
| Whitespace only | Enter "   " (spaces only) |
| Special characters | Enter `<script>alert(1)</script>` |
| Very long string | Enter 10,000 characters |
| Unicode / emoji | Enter "José 👍 Ñoño" |
| Leading/trailing spaces | Enter " John " |
| Negative numbers | Enter -1 where positive expected |
| Zero | Enter 0 where >0 is expected |
| Decimal in integer field | Enter 1.5 where whole number expected |
| Future date where past required | Enter tomorrow's date |
| Past date where future required | Enter yesterday's date |

### Status / Lifecycle
For every entity with a status field, ask:
- Can a user get to a status that blocks them with no way out? (Stuck states)
- Can a user skip statuses? (e.g. go from Draft straight to Completed)
- Can a record in a terminal status (Cancelled, Closed) be reopened? Is this documented?
- What happens to child records when a parent is deleted/archived?
- Can two records be in conflicting states simultaneously?

### Business Rule Boundaries
For every business rule with a threshold:
- What happens at exactly the threshold? (≥ or >?)
- What if the threshold changes (e.g. approval limit from £10k to £5k) — what about existing records?

### File Uploads (if feature exists)
- Upload file at exactly the size limit
- Upload file 1 byte above the size limit
- Upload zero-byte file
- Upload file with no extension
- Upload file with wrong extension but valid MIME type
- Upload file with correct extension but wrong MIME type (e.g. .pdf that is actually .exe)
- Upload 100 files at once (if batch upload exists)

### Search & Filtering
- Search with no results → empty state shown? No null pointer?
- Search with SQL injection characters: `'; DROP TABLE`
- Search with wildcard characters: `%`, `*`, `_`
- Search with regex special characters: `[`, `(`, `\`
- Search returning 100,000+ results → pagination? Memory?
- Filter by a combination that produces 0 results
- Filter and then sort — does sort apply correctly after filter?

### Notifications & Emails (if feature exists)
- Email to a deleted user
- Email to a user with an invalid email address
- Email template with missing merge fields (e.g. order number is null)
- What if the email service is down — does the transaction roll back or continue?

### Concurrent Access
- Two users edit the same record simultaneously — last write wins? Error shown?
- User A deletes a record while User B is viewing it
- User A changes a status while User B submits an approval for the same record

### Import / Bulk Operations (if feature exists)
- Import file with 0 records
- Import file with 1,000,000 records
- Import file with 1 invalid record in the middle — does the whole batch fail?
- Import the same file twice — duplicate handling?
- Import cancelled midway — partial data in system?

---

## Module-Specific Patterns

### User Management
- Register with an email that already exists
- Reset password for a non-existent email (should not reveal whether email is registered)
- Change email to one already in use by another account
- User with no roles — what can they see?
- User is in multiple roles — which takes precedence?
- Admin deletes their own account

### Order / Transaction Processing
- Order with zero line items
- Order with negative quantities
- Order total changes between submission and approval
- Approve an order that was already cancelled by someone else
- Cancel an order that is already in shipment
- Duplicate order reference submitted

### Approval Workflows
- Approver approves their own request
- Approver is removed from the system mid-approval
- All approvers are removed from a pending approval
- Approval sent to group — multiple people approve simultaneously
- Approval timeout — what happens if nobody acts?

### Reporting / Export
- Export with 0 records
- Export with 1,000,000 records — timeout? Memory?
- Export while records are being modified — consistency?
- Report with a date range spanning timezone changes
- Report filtered to a date with no records
