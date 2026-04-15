import { Routes, Route, Navigate } from 'react-router-dom'
import { RootLayout } from './app/layout'
import { ErrorBoundary } from './shared/components/ErrorBoundary'
import { Dashboard as PortfolioDashboard } from './features/portfolio/components/Dashboard'
import { AdminDashboard } from './features/admin/components/AdminDashboard'
import { InsertEstimate } from './features/estimates/components/InsertEstimate'
import { SystemLogViewer } from './shared/components/SystemLogViewer'

function App() {
  return (
    <ErrorBoundary>
      <SystemLogViewer>
        <RootLayout>
          <Routes>
            <Route path="/" element={<PortfolioDashboard />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/insert" element={<InsertEstimate />} />
            {/* Placeholder routes */}
            <Route path="/portfolio" element={<div className="p-4 text-center">Portfolio in arrivo...</div>} />
            <Route path="/analysis" element={<div className="p-4 text-center">AI Analysis in arrivo...</div>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </RootLayout>
      </SystemLogViewer>
    </ErrorBoundary>
  )
}

export default App
