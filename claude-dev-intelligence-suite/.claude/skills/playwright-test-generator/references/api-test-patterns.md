# API Test Patterns (Java/Spring + Playwright APIRequestContext)

## APIRequestContext Setup

```typescript
// Global setup for API tests
import { test as setup } from '@playwright/test';
export const authFile = 'playwright/.auth/user.json';

setup('authenticate and save token', async ({ request }) => {
  const response = await request.post('/api/auth/login', {
    data: {
      username: process.env.API_TEST_USER,
      password: process.env.API_TEST_PASS,
    },
  });
  const { token } = await response.json();
  process.env.AUTH_TOKEN = token;
});
```

## CRUD Pattern (one set per controller)

```typescript
test.describe('[Resource] CRUD', () => {
  let createdId: string;

  // CREATE
  test('POST creates resource', async ({ request }) => {
    const response = await request.post('/api/[resource]', {
      headers: { Authorization: `Bearer ${process.env.AUTH_TOKEN}` },
      data: { /* valid payload */ },
    });
    expect(response.status()).toBe(201);
    const body = await response.json();
    createdId = body.id;
    expect(createdId).toBeDefined();
  });

  // READ ONE
  test('GET retrieves created resource', async ({ request }) => {
    const response = await request.get(`/api/[resource]/${createdId}`, {
      headers: { Authorization: `Bearer ${process.env.AUTH_TOKEN}` },
    });
    expect(response.status()).toBe(200);
  });

  // UPDATE
  test('PUT updates resource', async ({ request }) => {
    const response = await request.put(`/api/[resource]/${createdId}`, {
      headers: { Authorization: `Bearer ${process.env.AUTH_TOKEN}` },
      data: { /* updated payload */ },
    });
    expect(response.status()).toBe(200);
  });

  // DELETE
  test('DELETE removes resource', async ({ request }) => {
    const response = await request.delete(`/api/[resource]/${createdId}`, {
      headers: { Authorization: `Bearer ${process.env.AUTH_TOKEN}` },
    });
    expect(response.status()).toBe(204);

    // Verify it's gone
    const check = await request.get(`/api/[resource]/${createdId}`, {
      headers: { Authorization: `Bearer ${process.env.AUTH_TOKEN}` },
    });
    expect(check.status()).toBe(404);
  });
});
```

## Validation Test Pattern (one per @NotNull / @Size constraint)

```typescript
// Test each validation constraint found in the Java DTO
const validationTests = [
  { field: 'name',  value: null,    expectedError: 'Name is required' },
  { field: 'name',  value: 'x'.repeat(101), expectedError: 'Name must not exceed 100 characters' },
  { field: 'email', value: 'notanemail', expectedError: 'Must be a valid email address' },
  { field: 'amount', value: -1,    expectedError: 'Amount must be greater than 0' },
];

for (const { field, value, expectedError } of validationTests) {
  test(`POST returns 400 when ${field} is ${value === null ? 'missing' : 'invalid'}`, async ({ request }) => {
    const payload = { ...validPayload, [field]: value };
    const response = await request.post('/api/[resource]', {
      headers: { Authorization: `Bearer ${process.env.AUTH_TOKEN}` },
      data: payload,
    });
    expect(response.status()).toBe(400);
    const error = await response.json();
    const errorText = JSON.stringify(error);
    expect(errorText).toContain(expectedError);
  });
}
```

## Pagination Testing

```typescript
test('GET returns paginated results', async ({ request }) => {
  const response = await request.get('/api/[resource]?page=0&size=10', {
    headers: { Authorization: `Bearer ${process.env.AUTH_TOKEN}` },
  });
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.content || body.items).toBeDefined();
  expect(body.totalElements || body.total).toBeGreaterThanOrEqual(0);
  expect((body.content || body.items).length).toBeLessThanOrEqual(10);
});
```

## Business Rule Tests (from @PreAuthorize / service logic)

```typescript
// Pattern: set up the condition, make the call, assert the rule fired
test('POST returns 422 when [business rule condition]', async ({ request }) => {
  // Step 1: Set up the condition (e.g. create a prerequisite record)
  // Step 2: Make the call that should trigger the rule
  const response = await request.post('/api/[resource]', {
    headers: { Authorization: `Bearer ${process.env.AUTH_TOKEN}` },
    data: { /* data that triggers the rule */ },
  });
  // Step 3: Assert correct status (422 Unprocessable Entity for business rules)
  expect(response.status()).toBe(422);
  const error = await response.json();
  expect(error.message).toContain('[expected business error message]');
});
```

## Response Shape Validation

```typescript
import { z } from 'zod'; // or use jest-schema-validation

// Define schema from Java DTO
const [Resource]Schema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100),
  status: z.enum(['ACTIVE', 'INACTIVE', 'PENDING']),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

test('GET response matches expected schema', async ({ request }) => {
  const response = await request.get('/api/[resource]/1', {
    headers: { Authorization: `Bearer ${process.env.AUTH_TOKEN}` },
  });
  const body = await response.json();
  const result = [Resource]Schema.safeParse(body);
  expect(result.success).toBe(true);
});
```
