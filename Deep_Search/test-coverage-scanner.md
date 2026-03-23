# Sub-Agent: Test Coverage Scanner

A focused sub-agent that finds all tests related to a piece of code and assesses coverage quality.

## When to invoke
The parent agent needs to know if code under investigation is tested, and how well.

## Protocol

Given a file or function:

1. **Find direct tests**
   - Search: `test.*{functionName}` / `describe.*{functionName}` / `it.*{functionName}`
   - Search: `Test{ClassName}` / `test_{function_name}` (language-specific patterns)
   - Search in: `**/test*/**`, `**/__tests__/**`, `**/*_test.*`, `**/*_spec.*`

2. **Find indirect tests** (integration/e2e that exercise this code)
   - Search: tests that import the containing module
   - Search: tests that call functions which call the target function

3. **Assess coverage quality**
   - Does each test verify behavior (assertions) or just exercise code?
   - Are edge cases covered? (empty input, null, boundary values, errors)
   - Are async paths tested? (success, timeout, error, retry)
   - Are concurrent scenarios tested? (race conditions, deadlocks)

4. **Identify gaps**
   - Code branches with no test (if/else, switch cases, error handlers)
   - Scenarios with no test (missing edge cases)
   - Integration points with no test (API calls, DB queries, events)

## Output

```
TEST COVERAGE: {file or function}

DIRECT TESTS:
- {test_file:line} — {test_name} — tests: {what it verifies}
- {test_file:line} — {test_name} — tests: {what it verifies}

INDIRECT TESTS:
- {test_file:line} — {test_name} — exercises target via {path}

COVERAGE QUALITY: Good | Partial | Minimal | None
EDGE CASES TESTED: {list of covered} | MISSING: {list of uncovered}

GAPS:
- {uncovered branch/scenario} — suggested test location: {file}
```
