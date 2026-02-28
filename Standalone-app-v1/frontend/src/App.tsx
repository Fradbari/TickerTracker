import { Routes, Route, Navigate } from 'react-router-dom'

function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <Routes>
        {/* Placeholder routes — will be implemented in subsequent feature tasks */}
        <Route path="/" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

function Dashboard() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-blue-400 mb-4">TickerTracker v3.0</h1>
        <p className="text-slate-400 text-lg">
          Trading estimates tracking system
        </p>
        <p className="text-slate-600 text-sm mt-8">
          Frontend scaffolding pronto — features in sviluppo
        </p>
      </div>
    </main>
  )
}

export default App
