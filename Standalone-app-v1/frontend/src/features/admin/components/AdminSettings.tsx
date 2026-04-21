import React, { useState, useEffect } from 'react'

export interface EstimateDefaults {
  targetProfitPercent: number
  stopLossPercent: number
  aiModel: string
  aiVersion: string
  aiConfidence: number
  baseAmount: number
  baseDurationDays: number
  refreshInterval: number
}

const DEFAULT_SETTINGS: EstimateDefaults = {
  targetProfitPercent: 10,
  stopLossPercent: 10,
  aiModel: 'gpt-4o',
  aiVersion: 'gpt-4o-mini',
  aiConfidence: 60,
  baseAmount: 1000,
  baseDurationDays: 30,
  refreshInterval: 30
}

export const useEstimateDefaults = () => {
  const [defaults, setDefaults] = useState<EstimateDefaults>(DEFAULT_SETTINGS)

  useEffect(() => {
    const saved = localStorage.getItem('estimate_defaults')
    if (saved) {
      try {
        setDefaults(JSON.parse(saved))
      } catch (e) {
        console.error('Error parsing settings', e)
      }
    }
  }, [])

  return defaults
}

export const AdminSettings: React.FC = () => {
  const [settings, setSettings] = useState<EstimateDefaults>(DEFAULT_SETTINGS)
  const [saved, setSaved] = useState(false)
  const [syncProgress, setSyncProgress] = useState(0)
  const [syncMessage, setSyncMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    const savedData = localStorage.getItem('estimate_defaults')
    if (savedData) {
      try {
        setSettings(JSON.parse(savedData))
      } catch(e) {
        console.error(e)
      }
    }
    
    // SSE setup for sync progress
    const eventSource = new EventSource('/api/sse/stream')
    eventSource.addEventListener('sync_progress', (e) => {
      const data = JSON.parse(e.data)
      setSyncProgress(data.progress_pct)
      setSyncMessage(data.message)
      if (data.progress_pct === 100) setSyncing(false)
    })
    return () => eventSource.close()
  }, [])

  const triggerExport = async () => {
    setSyncing(true)
    setSyncProgress(0)
    setSyncMessage('Starting export...')
    await fetch('/api/sync/export', { method: 'POST' })
  }

  const triggerImport = async () => {
    setShowModal(false)
    setSyncing(true)
    setSyncProgress(0)
    setSyncMessage('Starting import...')
    await fetch('/api/sync/import', { method: 'POST' })
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Impostazioni Admin & GDrive Sync</h2>
      
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h3 className="text-xl font-semibold mb-4">Sincronizzazione GDrive</h3>
        
        <div className="space-x-4 mb-4">
           <button onClick={triggerExport} disabled={syncing} className="px-4 py-2 bg-blue-600 text-white rounded">Backup su GDrive</button>
           <button onClick={() => setShowModal(true)} disabled={syncing} className="px-4 py-2 bg-red-600 text-white rounded">Ripristina da GDrive</button>
        </div>

        {syncing && (
          <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
            <div className="bg-blue-600 h-4 rounded-full" style={{ width: \\%\ }}></div>
          </div>
        )}
        {syncMessage && <p className="text-sm text-gray-600">{syncMessage}</p>}
      </div>

      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded shadow-lg max-w-sm w-full">
            <h4 className="text-lg font-bold mb-4">Conferma Ripristino</h4>
            <p className="mb-6">Sei sicuro di voler sovrascrivere i dati correnti dal cloud?</p>
            <div className="flex justify-end space-x-2">
               <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded">Annulla</button>
               <button onClick={triggerImport} className="px-4 py-2 bg-red-600 text-white rounded">Conferma</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
