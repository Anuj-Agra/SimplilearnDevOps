# Smell & Opportunity Detectors

Full extraction patterns for the interactive refactoring agent to run during
the ANALYSE phase. Read this file before presenting the breakdown menu.

---

## Java Detectors

### D1 — Responsibility Groups (drives Extract Class decisions)

Group the class's methods by which fields they touch. Methods that only
touch {fieldA, fieldB} = one responsibility. Methods that only touch
{fieldC, fieldD, fieldE} = a different responsibility = a new class.

```bash
# Step 1: list all instance fields
grep -n "private\|protected" <target_file> | \
  grep -v "static final\|void\|class\|interface\|@" | head -30

# Step 2: for each method, which fields does it reference?
grep -n "this\.\w\+" <target_file> | head -60
```

**Decision rule**: If you can describe a group of methods in one sentence
without the word "and", that group belongs in its own class.

### D2 — Long Method Scanner

```python
# scripts/find_long_methods.py
import re, sys

def scan(filepath, threshold=30):
    lines = open(filepath).readlines()
    results, depth, start, name = [], 0, 0, ''
    for i, line in enumerate(lines, 1):
        m = re.search(
            r'(public|private|protected)\s+[\w<>\[\]?,\s]+\s+(\w+)\s*\([^)]*\)\s*(\{|throws)',
            line)
        if m:
            name, start, depth = m.group(2), i, 0
        if start:
            depth += line.count('{') - line.count('}')
            if depth <= 0:
                length = i - start
                if length > threshold:
                    results.append((length, name, start))
                start = 0
    return sorted(results, reverse=True)

for length, name, line in scan(sys.argv[1]):
    print(f"  {length:4d} lines  {name}()  line {line}")
```

```bash
python3 scripts/find_long_methods.py <target_file>
```

### D3 — Cyclomatic Complexity

```bash
# Count decision points per method block
# Each if/else if/for/while/catch/&&/|| adds 1 to complexity
grep -n "\bif\b\|\belse if\b\|\bfor\b\|\bwhile\b\|\bcatch\b\|\b&&\b\|\b||\b" \
  <target_file> | wc -l
# Complexity > 10 per method = refactoring candidate
# Complexity > 15 = urgent
```

### D4 — Feature Envy (method belongs in another class)

```bash
# Methods calling another class more than their own data
grep -on "\b[A-Z][a-zA-Z]*\." <target_file> | \
  grep -v "$(basename <target_file> .java)\.\|String\.\|System\.\|Math\.\|Objects\.\|Optional\.\|log\." | \
  sed 's/:[0-9]*://' | sort | uniq -c | sort -rn | head -10
# High count for ExternalClass → method envies ExternalClass → move it there
```

### D5 — Primitive Obsession (parameter lists that should be objects)

```bash
# Methods with 4+ String/primitive parameters
grep -n "public\|private\|protected" <target_file> | \
  python3 -c "
import sys, re
for line in sys.stdin:
    params = re.findall(r'(String|int|long|boolean|double|Integer|Long)\s+\w+', line)
    if len(params) >= 4:
        print(f'  {len(params)} primitives: {line.strip()[:100]}')
"
```

### D6 — Deep Nesting (arrow anti-pattern)

```bash
# Lines with 5+ levels of indentation (20+ spaces)
grep -n "^                    [^ /]" <target_file> | \
  grep -v "//\|annotation\|import" | head -10
```

### D7 — Magic Numbers

```bash
# Numeric literals in logic (not in constants or annotations)
grep -n "[^@\"'a-zA-Z_]\b[0-9]\{2,\}\b" <target_file> | \
  grep -v "//\|static final\|@\|\".*\"\|test\|Test\|0L\|0D\|100L" | head -20
```

### D8 — Duplicate Code Blocks

```bash
# Find repeated patterns of 3+ lines
python3 -c "
lines = open('<target_file>').readlines()
blocks = {}
window = 4
for i in range(len(lines) - window):
    block = ''.join(l.strip() for l in lines[i:i+window] if l.strip())
    if len(block) > 50:
        blocks.setdefault(block, []).append(i+1)
for block, lnums in blocks.items():
    if len(lnums) > 1:
        print(f'  Duplicate block at lines: {lnums}')
        print(f'  Preview: {block[:80]}')
        print()
" 2>/dev/null | head -30
```

### D9 — God Class Indicators

```bash
# Total methods count
grep -c "public\|private\|protected" <target_file>

# Imports (many imports = many dependencies = too many responsibilities)
grep -c "^import" <target_file>

# Threshold: >20 methods OR >15 imports = likely God Class
```

---

## Angular / TypeScript Detectors

### D10 — Business Logic in Component

```bash
# Services being called from component with complex logic inline
grep -n "if\|for\|switch\|\.map\|\.filter\|\.reduce" \
  <target_file>.component.ts | \
  grep -v "ngOnInit\|ngOnDestroy\|constructor\|//" | head -20
# Each line = business logic that belongs in a service
```

### D11 — Template Complexity

```bash
# Count logic operators in template
grep -c "?\|&&\||||\|*ngIf\|*ngFor\|*ngSwitch" \
  <target_file>.component.html
# > 15 = template is doing too much — extract sub-components
```

### D12 — Injected Dependencies Count

```bash
# Count constructor params = number of dependencies
grep -n "constructor(" <target_file>.component.ts -A20 | \
  grep -c "private\|public\|readonly"
# > 5 dependencies = God Component
```

### D13 — Subscription Without Cleanup

```bash
grep -n "\.subscribe(" <target_file>.component.ts | \
  grep -v "this\.subscription\|takeUntil\|takeUntilDestroyed\|async\|destroy\$" | head -20
# Any result = memory leak risk
```

---

## Scoring Each Opportunity

Score each finding before presenting to user:

```
impactScore  = (fanIn × 2) + (linesOfCode / 50) + (complexity / 5)
effortScore  = estimatedHours × 2
priorityRank = impactScore - effortScore
```

Sort by `priorityRank` descending for the menu ordering.
Quick wins (high impact, low effort) surface to the top.
