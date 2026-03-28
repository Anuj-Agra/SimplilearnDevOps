# Skill: Deep Search Linker

> **Referenced by**: Agent 11 (Target Scanner)
> **Purpose**: Connects to the user's existing deep search agent project and translates
>   PEGA RE requirements into effective search queries for the target codebase.

---

## WHEN TO USE

Use when Agent 11 needs to search the new project codebase. This skill translates a PEGA requirement into one or more search queries tailored to the target technology.

## REQUIREMENT → SEARCH QUERY TRANSLATION

### Flow Requirements → Code Search

```
Source: "Capture applicant personal information (FirstName, LastName, DOB, SSN)"
Search queries:
  1. "Find form components or pages handling applicant information"
  2. "Find input fields for firstName, lastName, dateOfBirth, ssn"
  3. "Find API endpoints accepting applicant personal data"
  4. "Find database models or schemas with applicant fields"

Source: "Route to underwriter work queue for manual review"
Search queries:
  1. "Find task queue or workflow assignment logic"
  2. "Find role-based routing for underwriter or reviewer"
  3. "Find work queue or task list components"
  4. "Find state machine transitions involving review or approval states"
```

### Decision Requirements → Logic Search

```
Source: "Check applicant age >= 18"
Search queries:
  1. "Find conditional logic checking age or dateOfBirth for minimum"
  2. "Find validation rules for minimum age"
  3. "Find eligibility or qualification check functions"

Source: "Use FIRST_MATCH evaluation mode"
Search queries:
  1. "Find if-else chains or switch statements in eligibility logic"
  2. "Find early return patterns in rule evaluation"
  3. "Check if rules engine evaluates first match or all rules"
```

### Integration Requirements → API Search

```
Source: "POST to /api/v2/credit-check with API key auth"
Search queries:
  1. "Find HTTP POST calls to credit check or credit bureau"
  2. "Find API client configurations with API key headers"
  3. "Find service classes named CreditBureau or CreditCheck"
  4. "Find environment variables for credit API keys or URLs"

Source: "Handle HTTP 500 with fallback to manual assessment"
Search queries:
  1. "Find error handling for HTTP 500 or server errors in credit service"
  2. "Find try-catch blocks around credit bureau API calls"
  3. "Find fallback or manual queue routing on API failure"
```

### UI Requirements → Component Search

```
Source: "Field: LoanAmount (Currency, Required, Min $1000 Max $500K)"
Search queries:
  1. "Find input field for loanAmount or loan_amount"
  2. "Find currency input or money input components"
  3. "Find validation for loan amount minimum maximum range"
  4. "Find form schema or Yup/Zod schema with loanAmount"

Source: "CollateralType visible only when LoanAmount > 100000"
Search queries:
  1. "Find conditional rendering or visibility for collateral"
  2. "Find watch or dependency between loanAmount and collateral fields"
  3. "Find show/hide logic based on loan amount threshold"
```

## MULTI-LEVEL SEARCH STRATEGY

```
Level 1: KEYWORD SEARCH (broadest)
  Search for exact property names, function names, component names
  → Finds direct matches

Level 2: SEMANTIC SEARCH (broader)
  Search for business concept descriptions
  → Finds renamed/refactored implementations

Level 3: STRUCTURAL SEARCH (deepest)
  Search for code patterns (if-else chains, API calls, form fields)
  → Finds implementations that don't use similar naming

Level 4: DEPENDENCY SEARCH (cross-cutting)
  Search imports, package.json, config files for relevant libraries
  → Finds framework-level implementations (e.g., rules engine, form library)
```

## SEARCH RESULT INTERPRETATION

```
STRONG MATCH:
  - File name directly relates to the feature
  - Code contains the exact business logic described
  - Tests exist that validate the expected behavior
  → Status: IMPLEMENTED

PARTIAL MATCH:
  - File exists but only some conditions/fields/paths are present
  - Code structure is there but incomplete (TODOs, stubs, missing branches)
  → Status: PARTIAL — list what's present and what's missing

WEAK MATCH:
  - Similar naming but different purpose
  - Generic utility that COULD handle this but isn't configured for it
  → Status: NEEDS VERIFICATION — ask user to confirm

NO MATCH:
  - No relevant files, no related code, no tests
  - Multiple search levels all returned nothing
  → Status: MISSING — gap confirmed
```

## CONNECTING TO USER'S DEEP SEARCH AGENTS

Ask the user to describe their deep search agent's capabilities:

```
"To connect to your deep search agents, I need to know:

1. INVOCATION: How do I start a search?
   [ ] Paste a prompt into Copilot Chat
   [ ] Run a CLI command
   [ ] Open a specific file and use inline suggestions
   [ ] Use @workspace or #file references

2. SEARCH TYPES available:
   [ ] File name search (find files matching a pattern)
   [ ] Content search (grep-like text search in files)
   [ ] Semantic search (natural language description of what to find)
   [ ] AST search (find code patterns like function calls, class definitions)
   [ ] Dependency search (find what imports/uses a module)

3. OUTPUT FORMAT:
   [ ] File paths with line numbers
   [ ] Code snippets with context
   [ ] Structured JSON results
   [ ] Natural language descriptions

4. SCOPE CONTROL:
   [ ] Can search entire project
   [ ] Can limit to specific folders
   [ ] Can exclude patterns (node_modules, build, etc.)
   [ ] Can filter by file type

Once I know this, I'll format all my search requests to match your agent's expected input."
```
