# Session State & Conversation Examples

## State Object (maintain across every turn)

After each user interaction, update this state mentally:

```json
{
  "targetFile": "src/main/java/com/yourorg/orders/OrderService.java",
  "targetClass": "OrderService",
  "language": "java",
  "originalLines": 487,
  "originalMethods": 23,
  "currentLines": 487,
  "hasTests": true,
  "testFile": "OrderServiceTest.java",
  "callerCount": 8,
  "callerFiles": ["OrderController.java", "BatchJobService.java", "..."],
  "opportunities": [
    {
      "id": "A",
      "label": "Extract OrderValidationService",
      "priority": 1,
      "status": "pending",
      "impact": "HIGH",
      "effortHours": 4,
      "priorityScore": 84
    },
    {
      "id": "B",
      "label": "Split processOrder() into 4 methods",
      "priority": 1,
      "status": "pending",
      "impact": "MED",
      "effortHours": 2,
      "priorityScore": 71
    },
    { "id": "C", "label": "Replace fee switch with polymorphism", "priority": 2, "status": "pending" },
    { "id": "D", "label": "Introduce CustomerRequest parameter object", "priority": 2, "status": "pending" },
    { "id": "E", "label": "Replace 6 magic numbers", "priority": 3, "status": "pending" },
    { "id": "F", "label": "Flatten 3 nested methods", "priority": 3, "status": "pending" }
  ],
  "completedSteps": [],
  "modifiedFiles": [],
  "testsAdded": 0
}
```

---

## Conversation Flow Examples

### Example 1: Happy path selection

```
User: "Refactor this class: [pastes OrderService.java]"

Agent: [ANALYSE phase — reads file, runs detectors]
       [Presents breakdown menu — A through F]

User: "Start with E and F, they're quick wins"

Agent: [WRITE phase for E — shows magic number constants]
       "Here's the code for E. Please review, test, and commit.
        Ready to continue with F?"

User: "Looks good, done"

Agent: [WRITE phase for F — shows guard clause refactoring]
       [Updates state: E=complete, F=complete]
       Progress: ████████░░░░░░░░ 33% complete
       Done: [E] Magic numbers, [F] Guard clauses
       Remaining: [A] Extract class, [B] Split method, [C] Polymorphism, [D] Parameter object
       "Recommended next: B (extract methods from processOrder) — 2 hours"

User: "Do B then A"

Agent: [WRITE phase for B — shows extracted methods]
...
```

### Example 2: User wants to see code first, then decide

```
User: "Show me what extracting the validation logic would look like"

Agent: [Shows PREVIEW of Pattern A — Extract Class for validation only]
       "This is what the extracted OrderValidationService would look like.
        Want me to also show the updated OrderService, or are you ready
        to commit to this approach?"

User: "Yes show the full change"

Agent: [Shows complete 3-step output: new class + updated original + tests]
       "Shall I treat this as step A — mark it complete and move to next?"
```

### Example 3: User wants all quick wins first

```
User: "Do all the quick wins first"

Agent: [Identifies E + F as quick wins (effort < 1 hour each)]
       [Writes E — magic numbers]
       "Done. Commit E, then I'll write F."

User: "Committed"

Agent: [Writes F — guard clauses]
       "Done. Now for the bigger refactorings. Recommended order: B → A → D → C"
```

### Example 4: User pushes back on a suggestion

```
User: "I don't want to do the polymorphism refactoring (C), it's too risky right now"

Agent: [Removes C from the plan, marks as DEFERRED]
       "Understood — C deferred. Updated plan: B → A → D
        The switch statement stays as-is for now — consider adding a
        TODO comment to revisit when you have more test coverage."
```

### Example 5: User provides partial class

```
User: "Here's the problematic method [pastes a single method, not the full class]"

Agent: "I can see the method but I need the full class context to:
        1. Understand which fields the method uses
        2. Find the callers to check for breaking changes
        3. See if there are related methods to extract together

        Can you share the full file path or paste the complete class?"
```

---

## Warning Conditions (block or warn before proceeding)

### BLOCK — do not write code if:
- No tests exist for the target class → "I can see there are no tests for this class.
  Refactoring without tests is risky — any change could break behaviour silently.
  Shall I generate a characterisation test suite first, or do you want to proceed anyway
  with the understanding that you'll need to manually verify?"

- The file has been modified since analysis → Re-read the file before writing.

- User requests refactoring steps out of safe order → Warn: "Step C depends on step A
  being complete. Doing C first would require updating the callers twice. Suggest A first."

### WARN — flag but allow if user confirms:
- Callers > 10 → "This class has [N] callers. The Extract Class refactoring keeps the
  original class as a facade, so callers won't change. But it's a lot of moving parts —
  confirm you want to proceed?"

- No `@Transactional` detected on the original but extracted methods touch a repository →
  "The methods being extracted call the database. Make sure the new class is also
  annotated with `@Transactional` where needed — I've included it in the generated code,
  but verify the transaction boundaries are correct."

---

## Progress Display (show after every step)

```
────────────────────────────────────────────────────
REFACTORING PROGRESS: OrderService.java
────────────────────────────────────────────────────
Original:  487 lines | 23 methods | 8 callers
Current:   [N] lines | [N] methods (reducing)

[████████████░░░░░░░░░░░░] [N]/6 complete

✅ [E] Magic numbers → named constants        (30 min)
✅ [F] Guard clauses flattened                (45 min)
🔄 [B] Extract methods from processOrder()   ← IN PROGRESS
⬜ [A] Extract OrderValidationService
⬜ [D] Introduce CustomerRequest object
⬜ [C] Replace fee switch with polymorphism

Tests added: [N] | Files modified: [N]
────────────────────────────────────────────────────
```
