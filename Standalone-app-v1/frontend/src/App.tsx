import { Routes, Route, Navigate } from 'react-router-dom'
import { RootLayout } from './app/layout'
import { Dashboard as PortfolioDashboard } from './features/portfolio'

function App() {
  return (
    <RootLayout>
      <Routes>
        <Route path="/" element={<PortfolioDashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </RootLayout>
  )
}

export default App
