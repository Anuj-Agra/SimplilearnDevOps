# UI Test Patterns (Angular + Playwright)

## Locator Priority (use in this order)

1. `page.getByLabel('Field label')` — best for form inputs
2. `page.getByRole('button', { name: 'Submit' })` — best for buttons, links, headings
3. `page.getByText('Exact text')` — best for non-interactive text assertions
4. `page.getByPlaceholder('Search...')` — for inputs with placeholder
5. `page.getByTestId('submit-btn')` — only if `data-testid` attributes exist
6. **NEVER**: `page.locator('.btn-primary')`, `page.locator('#submit')`, XPath

## Angular Material Patterns

```typescript
// Mat-select dropdown
await page.getByLabel('Status').click();
await page.getByRole('option', { name: 'Active' }).click();

// Mat-datepicker
await page.getByLabel('Start Date').fill('01/15/2024');

// Mat-table row
const rows = page.getByRole('row').filter({ hasText: 'John Smith' });
await expect(rows).toHaveCount(1);

// Mat-dialog / modal
const dialog = page.getByRole('dialog');
await expect(dialog).toBeVisible();
await dialog.getByRole('button', { name: 'Confirm' }).click();

// Mat-snackbar / toast
await expect(page.getByRole('alert')).toContainText('Saved successfully');

// Mat-chip
await page.getByRole('listitem').filter({ hasText: 'Tag Name' });

// Mat-autocomplete
await page.getByLabel('Customer').fill('Joh');
await page.getByRole('option', { name: 'John Smith' }).click();
```

## Wait Strategies

```typescript
// Wait for API call to complete (use network idle over arbitrary timeouts)
await page.waitForLoadState('networkidle');

// Wait for specific network request
await Promise.all([
  page.waitForResponse(resp => resp.url().includes('/api/orders') && resp.status() === 200),
  page.getByRole('button', { name: 'Submit' }).click(),
]);

// Wait for navigation
await Promise.all([
  page.waitForURL(/\/orders\/\d+/),
  page.getByRole('button', { name: 'Save' }).click(),
]);

// Wait for element to appear
await expect(page.getByText('Order created')).toBeVisible({ timeout: 10000 });
```

## Table Assertions

```typescript
// Verify a row exists with specific content
await expect(
  page.getByRole('row').filter({ hasText: testData.customerName })
).toBeVisible();

// Count rows
const rowCount = await page.getByRole('row').count();
expect(rowCount).toBeGreaterThan(1); // >1 because header row counts

// Get specific cell in a row
const statusCell = page
  .getByRole('row', { name: testData.orderId })
  .getByRole('cell', { name: 'Pending' });
await expect(statusCell).toBeVisible();
```

## Form Interaction Patterns

```typescript
// Fill an entire form
async function fillOrderForm(page: Page, data: OrderData) {
  await page.getByLabel('Customer Name').fill(data.customerName);
  await page.getByLabel('Order Date').fill(data.orderDate);
  await page.getByLabel('Status').click();
  await page.getByRole('option', { name: data.status }).click();
  await page.getByLabel('Notes').fill(data.notes ?? '');
}

// Submit and wait for response
async function submitAndWait(page: Page) {
  const [response] = await Promise.all([
    page.waitForResponse(resp => resp.url().includes('/api/') && resp.status() < 400),
    page.getByRole('button', { name: 'Submit' }).click(),
  ]);
  return response;
}
```

## Role-Based Navigation Tests

```typescript
// Test that a menu item is/isn't visible based on role
test('admin sees Admin menu item', async ({ page }) => {
  await AuthHelper.loginAs(page, 'admin');
  await expect(page.getByRole('link', { name: 'Administration' })).toBeVisible();
});

test('viewer does not see Admin menu item', async ({ page }) => {
  await AuthHelper.loginAs(page, 'viewer');
  await expect(page.getByRole('link', { name: 'Administration' })).not.toBeVisible();
});

// Test guard redirect
test('unauthorised user is redirected from protected page', async ({ page }) => {
  await AuthHelper.loginAs(page, 'viewer');
  await page.goto('/admin/users');
  await expect(page).not.toHaveURL(/admin\/users/);
  await expect(page.getByText(/not have permission|not authorised|access denied/i)).toBeVisible();
});
```
