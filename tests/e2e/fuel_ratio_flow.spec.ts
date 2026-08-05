import { test, expect } from '@playwright/test';

test('User can submit fuel ratio calculation form and view history', async ({ page }) => {
  await page.goto('http://localhost:8000/fuel-ratio');

  await expect(page.locator('h1')).toContainText('Fuel Ratio & Capacity Analytics');

  // Fill out form fields
  await page.fill('input[placeholder="e.g. EXCA-001"]', 'EXCA-TEST-01');
  await page.fill('input[placeholder="e.g. 10.5"]', '12.0');
  await page.fill('input[placeholder="e.g. 250.0"]', '300.0');
  await page.fill('input[placeholder="e.g. 100.0"]', '120.0');

  // Submit form
  await page.click('button[type="submit"]');

  // Verify record appears in logs table
  await expect(page.locator('td')).toContainText('EXCA-TEST-01');
});
