/**
 * App module — public barrel.
 *
 * @example
 *   import { AppProviders, queryClient } from '@/app'
 *   import { RootLayout } from '@/app'
 *   import { QueryProvider } from '@/app'
 */

export { AppProviders, queryClient } from './providers'
export { QueryProvider } from './providers/QueryProvider'
export { RootLayout } from './layout'
export { AppErrorBoundary } from './components/AppErrorBoundary'
// router exports added in TASK 4.16
