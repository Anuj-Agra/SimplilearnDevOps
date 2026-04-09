---
name: playwright-test-generator
description: >
  Generate complete, production-ready Playwright test suites from Java backend and
  Angular frontend codebases. Use this skill whenever a user wants to write automated
  tests, E2E tests, UI tests, API tests, or integration tests using Playwright.
  Triggers include: 'write playwright tests', 'generate test cases', 'automate tests',
  'E2E tests', 'UI automation', 'API test', 'test this feature', 'write tests for',
  'test suite', 'test script', 'automated test', 'regression tests'. Generates two
  separate but linked test suites: (1) Angular UI tests using Playwright browser
  automation with Page Object Model, and (2) Java API tests using Playwright's
  APIRequestContext for backend contract testing. Both suites share test data fixtures
  and can run independently or together. Uses repo-graph.json when available to
  prioritise test coverage by blast-radius risk.
---

# Playwright Test Generator

Generate complete, runnable Playwright test suites — one for the Angular UI,
one for the Java API — from real codebase analysis. Not boilerplate. Real tests
that actually cover the system's behaviour.

---

## Architecture: Two Suites, One Framework

```
tests/
├── ui/                     ← Angular frontend tests (browser automation)
│   ├── pages/              ← Page Object Models (one per Angular component)
│   ├── specs/              ← Test spec files (one per feature/module)
│   └── fixtures/           ← Shared test data and auth helpers
├── api/                    ← Java backend API tests
│   ├── specs/              ← API test specs (one per controller/resource)
│   └── fixtures/           ← Request builders, response validators
├── shared/                 ← Shared between UI and API
│   ├── test-data/          ← Data factories
│   └── helpers/            ← Auth, env config
├── playwright.config.ts    ← Root config
└── package.json
```

---

## Step 0 — Context Loading

```bash
# Check for graph
ls repo-graph.json 2>/dev/null && echo "GRAPH: yes"

# If graph available, get critical modules for test prioritisation
python3 scripts/project_graph.py --graph repo-graph.json --mode critical --top 10
python3 scripts/project_graph.py --graph repo-graph.json --mode entry-points
```

Ask user:
1. **Scope** — whole system, a module, or a specific feature?
2. **Both suites** — UI + API, or just one?
3. **Auth** — how does login work? (username/password, SSO, token?)
4. **Base URLs** — `ANGULAR_BASE_URL` and `API_BASE_URL`

---

## Step 1 — Code Reconnaissance

Read `references/code-extraction.md` for detailed extraction patterns.

### Java Backend — Extract Test Surface

```bash
# All API endpoints (each = one or more test cases)
grep -rn "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping\|@PatchMapping\|@RequestMapping" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test"

# Request/response DTOs (= test data shapes)
find <java_path> -name "*Request*.java" -o -name "*Response*.java" \
  -o -name "*Dto.java" -o -name "*DTO.java" | head -30

# Validation rules (= negative test cases)
grep -rn "@NotNull\|@NotBlank\|@Size\|@Min\|@Max\|@Pattern\|@Email" \
  <java_path> --include="*.java" | head -80

# Status/error codes thrown (= error scenario tests)
grep -rn "HttpStatus\.\|ResponseStatus\|throw new\|BusinessException\|ValidationException" \
  <java_path> --include="*.java" | head -60

# Security rules (= permission test cases)
grep -rn "@PreAuthorize\|@Secured\|hasRole\|ROLE_" \
  <java_path> --include="*.java" | head -40
```

### Angular Frontend — Extract UI Test Surface

```bash
# All routes (= page navigation test cases)
grep -rn "path:\|component:\|canActivate:" <angular_path> \
  --include="*.ts" | grep -i "rout" | head -80

# Form fields (= fill-in actions in tests)
grep -rn "formControlName\|formGroup\|name=\|\[formControl\]" \
  <angular_path> --include="*.html" | head -80

# Buttons and actions (= click events in tests)
grep -rn "<button\|mat-button\|mat-raised-button\|\(click\)=" \
  <angular_path> --include="*.html" | head -60

# Tables and lists (= assertion targets in tests)
grep -rn "<mat-table\|<table\|*ngFor\|dataSource" \
  <angular_path> --include="*.html" | head -40

# Error messages (= assertion text in tests)
grep -rn "mat-error\|errorMessage\|snackBar\|toast\|\*ngIf.*error" \
  <angular_path> --include="*.html" --include="*.ts" | head -50

# Route guards (= auth test scenarios)
grep -rn "canActivate\|AuthGuard\|RoleGuard" \
  <angular_path> --include="*.ts" | head -30
```

---

## Step 2 — Generate the Test Plan

Before writing any code, produce a test plan:

```
TEST PLAN: [Feature/Module Name]

UI Tests ([N] test files, [N] test cases):
  [Page/Screen] → [Test cases: happy path + N negatives]

API Tests ([N] test files, [N] test cases):
  [Endpoint pattern] → [Test cases: success + validation + auth + errors]

Shared fixtures: [auth, test data entities]
Total estimated coverage: [%] of identified scenarios
```

---

## Step 3 — Generate the Config Files

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['list']],

  use: {
    baseURL: process.env.ANGULAR_BASE_URL || 'http://localhost:4200',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },

  projects: [
    // API tests — no browser needed
    {
      name: 'api',
      testDir: './tests/api',
      use: { baseURL: process.env.API_BASE_URL || 'http://localhost:8080' },
    },
    // UI tests
    {
      name: 'ui-chrome',
      testDir: './tests/ui',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'ui-firefox',
      testDir: './tests/ui',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
});
```

---

## Step 4 — Generate UI Tests (Angular)

Read `references/ui-test-patterns.md` for the full pattern library.

### Page Object Model (one per Angular component)

```typescript
// tests/ui/pages/[feature]-page.ts
import { Page, Locator, expect } from '@playwright/test';

export class [FeatureName]Page {
  readonly page: Page;

  // Locators — use data-testid first, then aria roles, then text
  // NEVER use CSS classes or XPath
  readonly [fieldName]: Locator;
  readonly [buttonName]Button: Locator;
  readonly [tableName]Table: Locator;
  readonly errorMessage: Locator;
  readonly successMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.[fieldName] = page.getByLabel('[exact label text from HTML]');
    this.[buttonName]Button = page.getByRole('button', { name: '[exact button text]' });
    this.[tableName]Table = page.getByRole('table');
    this.errorMessage = page.getByRole('alert');
    this.successMessage = page.getByText('[exact success message text]');
  }

  async navigate() {
    await this.page.goto('/[route-path]');
  }

  async [doAction](data: [DataType]) {
    await this.[fieldName].fill(data.[field]);
    await this.[buttonName]Button.click();
  }

  async expectSuccess() {
    await expect(this.successMessage).toBeVisible();
  }

  async expectValidationError(field: string, message: string) {
    await expect(this.page.getByText(message)).toBeVisible();
  }
}
```

### UI Spec File (one per feature/module)

```typescript
// tests/ui/specs/[feature].spec.ts
import { test, expect } from '@playwright/test';
import { [FeatureName]Page } from '../pages/[feature]-page';
import { AuthHelper } from '../fixtures/auth-helper';
import { TestDataFactory } from '../../shared/test-data/factory';

test.describe('[Feature Name]', () => {

  test.beforeEach(async ({ page }) => {
    await AuthHelper.loginAs(page, '[role]');
  });

  test.afterEach(async ({ page }) => {
    await TestDataFactory.cleanup(page);
  });

  // ── Happy Path ──────────────────────────────────────────────────────────

  test('TC-UI-[MOD]-001: [role] can [action] successfully', async ({ page }) => {
    const featurePage = new [FeatureName]Page(page);
    const testData = TestDataFactory.create[Entity]();

    await featurePage.navigate();
    await featurePage.[doAction](testData);
    await featurePage.expectSuccess();

    // Verify the data was persisted
    await expect(page.getByText(testData.[keyField])).toBeVisible();
  });

  // ── Validation Failures ─────────────────────────────────────────────────

  test('TC-UI-[MOD]-002: shows error when [required field] is empty', async ({ page }) => {
    const featurePage = new [FeatureName]Page(page);
    const incompleteData = { ...TestDataFactory.create[Entity](), [field]: '' };

    await featurePage.navigate();
    await featurePage.[doAction](incompleteData);
    await featurePage.expectValidationError('[field]', '[exact error message from HTML]');
    await expect(page).not.toHaveURL(/success|confirmation/);
  });

  test('TC-UI-[MOD]-003: shows error when [field] exceeds maximum length', async ({ page }) => {
    // test for each @Size/@Max constraint found in code
  });

  // ── Business Rule Violations ────────────────────────────────────────────

  test('TC-UI-[MOD]-004: [business rule description]', async ({ page }) => {
    // Set up the specific condition that triggers the rule
    // Attempt the action
    // Assert the rule fires correctly
  });

  // ── Permission / Role Tests ─────────────────────────────────────────────

  test('TC-UI-[MOD]-005: [unauthorised role] cannot access [feature]', async ({ page }) => {
    await AuthHelper.loginAs(page, '[unauthorised role]');
    const featurePage = new [FeatureName]Page(page);
    await featurePage.navigate();
    await expect(page.getByText('You do not have permission')).toBeVisible();
  });

  // ── Navigation ──────────────────────────────────────────────────────────

  test('TC-UI-[MOD]-006: navigates to [next screen] after successful [action]', async ({ page }) => {
    // Complete the action
    // Assert URL changes to expected next page
    await expect(page).toHaveURL(/[next-route]/);
  });

});
```

---

## Step 5 — Generate API Tests (Java)

Read `references/api-test-patterns.md` for the full pattern library.

```typescript
// tests/api/specs/[resource]-api.spec.ts
import { test, expect, APIRequestContext } from '@playwright/test';
import { ApiAuthHelper } from '../fixtures/api-auth';
import { TestDataFactory } from '../../shared/test-data/factory';

test.describe('[Resource] API', () => {
  let request: APIRequestContext;
  let authToken: string;

  test.beforeAll(async ({ playwright }) => {
    request = await playwright.request.newContext({
      baseURL: process.env.API_BASE_URL || 'http://localhost:8080',
    });
    authToken = await ApiAuthHelper.getToken('[role]', request);
  });

  test.afterAll(async () => {
    await request.dispose();
  });

  // ── Success Scenarios ───────────────────────────────────────────────────

  test('TC-API-[MOD]-001: GET /[resource] returns list for authorised user', async () => {
    const response = await request.get('/api/[resource]', {
      headers: { Authorization: `Bearer ${authToken}` },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBeTruthy();
    // Assert shape of first item matches expected fields
    if (body.length > 0) {
      expect(body[0]).toMatchObject({
        [field1]: expect.any(String),
        [field2]: expect.any(Number),
      });
    }
  });

  test('TC-API-[MOD]-002: POST /[resource] creates resource with valid data', async () => {
    const payload = TestDataFactory.create[Entity]();

    const response = await request.post('/api/[resource]', {
      headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' },
      data: payload,
    });

    expect(response.status()).toBe(201);
    const created = await response.json();
    expect(created.id).toBeDefined();
    expect(created.[field]).toBe(payload.[field]);
  });

  // ── Validation Failures ─────────────────────────────────────────────────

  test('TC-API-[MOD]-003: POST /[resource] returns 400 when [required field] missing', async () => {
    const payload = { ...TestDataFactory.create[Entity](), [requiredField]: null };

    const response = await request.post('/api/[resource]', {
      headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' },
      data: payload,
    });

    expect(response.status()).toBe(400);
    const error = await response.json();
    expect(error.errors || error.message).toBeDefined();
  });

  // ── Authentication & Authorisation ──────────────────────────────────────

  test('TC-API-[MOD]-004: returns 401 when no token provided', async () => {
    const response = await request.get('/api/[resource]');
    expect(response.status()).toBe(401);
  });

  test('TC-API-[MOD]-005: returns 403 when [unauthorised role] accesses [protected endpoint]', async () => {
    const lowPrivToken = await ApiAuthHelper.getToken('[low-privilege-role]', request);
    const response = await request.delete('/api/[resource]/1', {
      headers: { Authorization: `Bearer ${lowPrivToken}` },
    });
    expect(response.status()).toBe(403);
  });

  // ── Business Rules ──────────────────────────────────────────────────────

  test('TC-API-[MOD]-006: [business rule — plain English description]', async () => {
    // Set up condition
    // Make API call
    // Assert correct response status and error message
  });

  // ── Not Found ───────────────────────────────────────────────────────────

  test('TC-API-[MOD]-007: GET /[resource]/:id returns 404 for non-existent id', async () => {
    const response = await request.get('/api/[resource]/99999999', {
      headers: { Authorization: `Bearer ${authToken}` },
    });
    expect(response.status()).toBe(404);
  });

});
```

---

## Step 6 — Shared Fixtures

```typescript
// shared/test-data/factory.ts
export class TestDataFactory {
  static create[Entity](overrides?: Partial<[EntityType]>): [EntityType] {
    return {
      [field1]: '[realistic test value]',
      [field2]: [realistic value],
      // ... all fields from the Java DTO/entity
      ...overrides,
    };
  }

  static async cleanup(page: Page) {
    // Clean up test data after each test
  }
}

// shared/helpers/auth-helper.ts
export class AuthHelper {
  static async loginAs(page: Page, role: string) {
    const credentials = AuthHelper.credentialsFor(role);
    await page.goto('/login');
    await page.getByLabel('Email').fill(credentials.username);
    await page.getByLabel('Password').fill(credentials.password);
    await page.getByRole('button', { name: 'Sign In' }).click();
    await page.waitForURL(/dashboard|home/);
  }

  private static credentialsFor(role: string) {
    const creds: Record<string, { username: string; password: string }> = {
      admin:   { username: process.env.ADMIN_USER!,   password: process.env.ADMIN_PASS! },
      manager: { username: process.env.MGR_USER!,     password: process.env.MGR_PASS! },
      viewer:  { username: process.env.VIEWER_USER!,  password: process.env.VIEWER_PASS! },
    };
    return creds[role] ?? creds['viewer'];
  }
}
```

---

## Step 7 — Test Coverage Matrix

After generating tests, produce this matrix:

| Feature | TC (UI happy) | TC (UI validation) | TC (UI permissions) | TC (API success) | TC (API validation) | TC (API auth) | Coverage |
|---|---|---|---|---|---|---|---|
| [Feature] | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Full |

---

## Quality Rules for Generated Tests

- [ ] Every test has a meaningful name describing what it tests (not "test1")
- [ ] Every test is independent — no test depends on another running first
- [ ] Every test cleans up its own data
- [ ] Locators use `getByLabel`, `getByRole`, `getByText` — never CSS selectors
- [ ] Assertions use `expect()` with clear failure messages
- [ ] Credentials and URLs come from `process.env` — never hardcoded
- [ ] Every happy path has at least one corresponding negative test
- [ ] Every `@PreAuthorize` rule has a corresponding 403 test
- [ ] Every `@NotNull`/`@NotBlank` field has a corresponding 400 test
