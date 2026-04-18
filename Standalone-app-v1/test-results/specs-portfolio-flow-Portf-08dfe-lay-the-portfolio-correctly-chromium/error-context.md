# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: specs\portfolio-flow.spec.ts >> Portfolio Flow >> should display the portfolio correctly
- Location: e2e\specs\portfolio-flow.spec.ts:4:7

# Error details

```
Error: expect(page).toHaveTitle(expected) failed

Expected pattern: /Ticker Tracker/i
Received string:  "TickerTracker v3.0"
Timeout: 5000ms

Call log:
  - Expect "toHaveTitle" with timeout 5000ms
    8 × unexpected value "TickerTracker v3.0"

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - heading "Ticker Tracker" [level=1] [ref=e6]
        - button "Toggle theme" [ref=e7]:
          - img [ref=e8]
      - navigation [ref=e14]:
        - link "Dashboard" [ref=e15] [cursor=pointer]:
          - /url: /
          - img [ref=e16]
          - text: Dashboard
        - link "Nuova Stima" [ref=e21] [cursor=pointer]:
          - /url: /insert
          - img [ref=e22]
          - text: Nuova Stima
        - link "Portfolio" [ref=e24] [cursor=pointer]:
          - /url: /portfolio
          - img [ref=e25]
          - text: Portfolio
        - link "AI Analysis" [ref=e28] [cursor=pointer]:
          - /url: /analysis
          - img [ref=e29]
          - text: AI Analysis
        - link "Admin" [ref=e41] [cursor=pointer]:
          - /url: /admin
          - img [ref=e42]
          - text: Admin
    - main [ref=e45]:
      - generic [ref=e47]:
        - heading "Portafoglio Avanzato" [level=2] [ref=e49]
        - generic [ref=e50]:
          - generic [ref=e51]:
            - img [ref=e52]
            - textbox "Cerca ticker..." [ref=e55]
          - generic [ref=e56]:
            - generic [ref=e57]:
              - img [ref=e58]
              - combobox [ref=e60]:
                - option "Tutti gli stati" [selected]
                - option "Aperti"
                - option "Chiusi (Win)"
                - option "Chiusi (Loss)"
                - option "Scaduti"
            - generic [ref=e61]:
              - combobox [ref=e62]:
                - option "Data Creazione" [selected]
                - option "Confidenza AI"
                - option "Target Profit %"
              - button "Ordine crescente/decrescente" [ref=e63]:
                - img [ref=e64]
        - generic [ref=e67]: Nessuna stima trovata con i filtri attuali.
    - generic [ref=e68]:
      - generic [ref=e69]:
        - generic [ref=e70]:
          - img [ref=e71]
          - generic [ref=e73]: "API: Healthy"
        - generic [ref=e74]:
          - img [ref=e75]
          - generic [ref=e79]: "PostgreSQL: Connesso"
      - generic [ref=e80]:
        - generic [ref=e81]:
          - img [ref=e82]
          - generic [ref=e84]: "GDrive: Non configurato"
        - generic [ref=e85] [cursor=pointer]:
          - img [ref=e86]
          - generic [ref=e91]: Sync Now
  - button "Open System Log Console" [ref=e92]:
    - img [ref=e93]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Portfolio Flow', () => {
  4  |   test('should display the portfolio correctly', async ({ page }) => {
  5  |     await page.goto('/portfolio');
  6  |     
  7  |     // Check main headings or elements
> 8  |     await expect(page).toHaveTitle(/Ticker Tracker/i);
     |                        ^ Error: expect(page).toHaveTitle(expected) failed
  9  |     const heading = page.locator('h1', { hasText: /Portfolio/i });
  10 |     if (await heading.count() > 0) {
  11 |       await expect(heading).toBeVisible();
  12 |     }
  13 |   });
  14 | });
  15 | 
```