/**
 * Application router — route definitions.
 *
 * Route tree is defined here and consumed by App.tsx.
 * Implementation is deferred to TASK 4.16 (Setup React Router e Layout).
 *
 * Planned route structure:
 *   /                    → PortfolioDashboard (TASK 4.11)
 *   /estimates           → EstimateList       (TASK 4.6)
 *   /estimates/:id       → EstimateDetail     (TASK 4.7)
 *   /estimates/new       → CreateEstimateForm (TASK 4.8)
 *   /market-data         → TickerWatchlist    (TASK 4.14)
 *   /market-data/:ticker → MarketDataChart    (TASK 4.13)
 *   /chat                → ChatAI Panel       (TASK 4.15)
 *   *                    → Redirect to /
 *
 * TASK 4.16 will:
 *   - Move Routes from App.tsx into this file
 *   - Add lazy() + Suspense for code-splitting
 *   - Integrate RootLayout from @/app/layout
 */

// Placeholder — exported so App.tsx can import from '@/app/router' once ready
export {}
