import { test, expect } from '@playwright/test';

test.describe('Portfolio Flow', () => {
  test('should display the portfolio correctly', async ({ page }) => {
    await page.goto('/portfolio');
    
    // Check main headings or elements
    await expect(page).toHaveTitle(/Ticker Tracker/i);
    const heading = page.locator('h1', { hasText: /Portfolio/i });
    if (await heading.count() > 0) {
      await expect(heading).toBeVisible();
    }
  });
});
