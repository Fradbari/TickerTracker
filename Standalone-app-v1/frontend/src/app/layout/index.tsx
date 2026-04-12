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
import { ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { Menu } from 'lucide-react'

interface RootLayoutProps {
  children: ReactNode
}

export function RootLayout({ children }: RootLayoutProps) {
  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] transition-colors duration-200">
      <Sidebar />

      {/* Mobile Header */}
      <header className="md:hidden flex items-center justify-between p-4 bg-[var(--card)] border-b border-[var(--border)]">
        <button className="p-2 text-[var(--foreground)] hover:bg-slate-200 dark:hover:bg-slate-800 rounded-md">
          <Menu size={24} />
        </button>
        <h1 className="font-bold">2.5</h1>
      </header>

      {/* Main Content */}
      <main className="md:ml-64 flex-1">
        <div className="max-w-7xl mx-auto p-4 md:p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
