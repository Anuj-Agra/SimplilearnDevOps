---
name: code-smell-detector
description: >
  Find structural rot before it becomes a rewrite: God classes, methods over 50 lines,
  cyclomatic complexity above 10, feature envy, primitive obsession, deep nesting,
  data clumps, and shotgun surgery candidates. Use when asked: 'code smells',
  'code quality', 'God class', 'long methods', 'complexity', 'hard to change',
  'messy code', 'structural rot', 'refactoring candidates', 'worst code', 'debt
  hotspots'. Scores each finding so you can prioritise. Essential before any
  migration or modernisation effort — know which modules are hardest to change.
---
# Code Smell Detector

Find structural rot systematically. Score it. Prioritise the fix.

---

## Step 1 — Discovery Scans

### God Classes (do too much)
```bash
# Classes over 300 lines
find <java_path> -name "*.java" | while read f; do
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 300 ]; then
    echo "$lines $f"
  fi
done | sort -rn | head -20

# Classes with too many methods (>20 public methods)
grep -rn "public " <java_path> --include="*.java" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20
```

### Long Methods (over 30 lines)
```bash
# Extract method lengths across all Java files
python3 - <<'EOF'
import os, re

def method_lengths(path):
    results = []
    for root, _, files in os.walk(path):
        for f in files:
            if not f.endswith('.java'): continue
            fp = os.path.join(root, f)
            lines = open(fp).readlines()
            depth, start, name = 0, 0, ''
            for i, line in enumerate(lines):
                m = re.search(r'(public|private|protected)\s+\S+\s+(\w+)\s*\(', line)
                if m and '{' in line:
                    depth, start, name = 1, i, m.group(2)
                elif start and '{' in line: depth += 1
                elif start and '}' in line:
                    depth -= 1
                    if depth == 0:
                        length = i - start
                        if length > 30:
                            results.append((length, name, fp))
                        start = 0
    return sorted(results, reverse=True)[:20]

for length, name, fp in method_lengths('<java_path>'):
    print(f"{length:4d} lines  {name}()  {fp.split('src/main')[-1]}")
EOF
```

### High Cyclomatic Complexity
```bash
# Count decision points per method (if, else, for, while, catch, &&, ||, ?)
grep -rn "\bif\b\|\belse\b\|\bfor\b\|\bwhile\b\|\bcatch\b\|\b&&\b\|\b||\b\|? " \
  <java_path> --include="*.java" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20
```

### Feature Envy (class obsessed with another class's data)
```bash
# Methods that call getters on another class more than their own
grep -rn "\.\(get\|is\)[A-Z]" <java_path> --include="*.java" | \
  grep -v "this\.\|super\.\|test\|Test" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20
```

### Primitive Obsession (raw types where domain objects belong)
```bash
# Method signatures with 4+ primitive/String params
grep -rn "public.*\(.*String.*String.*String\|.*int.*int.*int\|.*String.*int.*String\)" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -20

# Magic numbers (raw literals in logic — not in constants/annotations)
grep -rn "[^@\"'a-zA-Z0-9_]\(365\|100\|1000\|86400\|24\|60\|3600\|9999\|9[0-9][0-9][0-9]\)" \
  <java_path> --include="*.java" | \
  grep -v "//\|@\|\".\|test\|Test\|final.*=\|static" | head -30
```

### Deep Nesting (arrow anti-pattern)
```bash
# Find methods with 5+ levels of indentation
grep -rn "^                    [^ ]" <java_path> --include="*.java" | \
  grep -v "//\|test\|Test\|annotation\|import" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -15
```

### Data Clumps (same 3+ fields always appear together)
```bash
# Find parameter groups that repeat across methods
grep -rn "String.*customerId.*String.*accountId\|String.*userId.*String.*sessionId\|\
  String.*firstName.*String.*lastName.*String.*email" \
  <java_path> --include="*.java" | grep -v "//\|test" | head -20
```

### Shotgun Surgery (one change forces edits in many classes)
```bash
# Classes with many tiny methods that all reference the same field name
grep -rn "private.*[A-Za-z]*Id\b\|private.*[A-Za-z]*Code\b\|private.*[A-Za-z]*Type\b" \
  <java_path> --include="*.java" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20
```

### Angular Smells
```bash
# Components with too many injected services (>5 = God Component)
grep -rn "constructor(" <angular_path> --include="*.ts" -A10 | \
  grep "private\|public" | awk -F: '{print $1}' | \
  sort | uniq -c | sort -rn | head -10

# Deeply nested template logic (>3 levels of *ngIf/*ngFor)
grep -c "\*ngIf\|\*ngFor" <angular_path>/src --include="*.html" -r | \
  sort -t: -k2 -rn | head -10

# Components over 400 lines
find <angular_path> -name "*.component.ts" | while read f; do
  lines=$(wc -l < "$f")
  [ "$lines" -gt 400 ] && echo "$lines $f"
done | sort -rn | head -10
```

---

## Step 2 — Debt Score Per Finding

Assign a score to each finding:

| Smell | Base Score | Multiplier |
|---|---|---|
| God class (>500 lines) | 8 | × fanIn (dependents) |
| Long method (>80 lines) | 5 | × calls from other classes |
| Cyclomatic complexity >15 | 7 | × test coverage gap |
| Feature envy | 4 | × coupling count |
| Primitive obsession (>4 params) | 3 | × usage count |
| Deep nesting (>5 levels) | 5 | × 1 |
| Magic numbers | 2 | × occurrence count |
| Data clumps | 3 | × repetition count |

`debtScore = baseScore × multiplier`

---

## Step 3 — Output: Code Smell Register

```
CODE SMELL REPORT: [System]
Total findings: [N] | Total debt score: [N] | Estimated fix days: [N]

TOP 10 WORST OFFENDERS:
┌──────────────────────────────────────────────────────────────────────┐
│ Rank │ File/Class          │ Smell          │ Score │ Est. Fix  │
├──────┼─────────────────────┼────────────────┼───────┼───────────┤
│  1   │ OrderService.java   │ God class 847L │  64   │  5 days   │
│  2   │ CustomerMapper.java │ Long method    │  35   │  2 days   │
│  3   │ PaymentUtil.java    │ Complexity=18  │  28   │  1 day    │
└──────────────────────────────────────────────────────────────────────┘

BY SMELL CATEGORY:
  God Classes:          [N] found — [total score]
  Long Methods:         [N] found — [total score]
  High Complexity:      [N] found — [total score]
  Feature Envy:         [N] found — [total score]
  Primitive Obsession:  [N] found — [total score]
  Deep Nesting:         [N] found — [total score]

HOTSPOT MAP (modules with highest debt concentration):
  [module-a]:  score 142 — recommend refactoring sprint before migration
  [module-b]:  score  87 — address before adding new features
  [module-c]:  score  23 — acceptable, monitor

QUICK WINS (high score, low fix effort — do these first):
  1. Extract 3 magic numbers in [File] → [estimated 30 min]
  2. Split [Method] into 3 smaller methods → [estimated 2 hours]
  3. Extract parameter object from [Method] → [estimated 1 hour]
```
