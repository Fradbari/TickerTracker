/**
 * Application layout — root layout component.
 *
 * RootLayout wraps all pages with shared chrome:
 *   - Sidebar / top navigation (TASK 4.16)
 *   - Toast notification portal
 *   - Global error boundary
 *
 * Currently a pass-through — full implementation in TASK 4.16.
 */
import type { ReactNode } from 'react'

interface RootLayoutProps {
  children: ReactNode
}

/**
 * RootLayout — outer shell for every route.
 * Place navigation, sidebars, and modals here once designed.
 */
export function RootLayout({ children }: RootLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Navigation placeholder — TASK 4.16 */}
      <main>{children}</main>
    </div>
  )
}
