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
    const eventSource = new EventSource('/api/sse/stream')
    eventSource.addEventListener('sync_progress', (e: any) => {
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
  const [syncProgress, setSyncProgress] = useState(0)
  const [syncMessage, setSyncMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    const eventSource = new EventSource('/api/sse/stream')
    eventSource.addEventListener('sync_progress', (e: any) => {
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
  const [syncProgress, setSyncProgress] = useState(0)
  const [syncMessage, setSyncMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    const eventSource = new EventSource('/api/sse/stream')
    eventSource.addEventListener('sync_progress', (e: any) => {
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

  useEffect(() => {
    const savedData = localStorage.getItem('estimate_defaults')
    if (savedData) {
      try {
        setSettings(JSON.parse(savedData))
      } catch (e) {
        // ignore
      }
    }
  }, [])

  const handleSave = () => {
    localStorage.setItem('estimate_defaults', JSON.stringify(settings))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow mt-8 p-6">
      <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">Impostazioni di Default Stime</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Target Profitto base (%)
          </label>
          <input
            type="number"
            className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={settings.targetProfitPercent}
            onChange={(e) => setSettings({ ...settings, targetProfitPercent: Number(e.target.value) })}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Stop Loss base (%)
          </label>
          <input
            type="number"
            className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={settings.stopLossPercent}
            onChange={(e) => setSettings({ ...settings, stopLossPercent: Number(e.target.value) })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Modello AI base
          </label>
          <select
            className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={settings.aiModel}
            onChange={(e) => setSettings({ ...settings, aiModel: e.target.value })}
          >
            <option value="gpt">GPT</option>
            <option value="gemini">Gemini</option>
            <option value="claude">Claude</option>
            <option value="ia studio">IA Studio</option>
            <option value="kimi">Kimi</option>
            <option value="perplexity">Perplexity</option>
            <option value="deepseek">DeepSeek</option>
            <option value="copilot">Copilot</option>
            <option value="grok">Grok</option>
            <option value="qwen">Qwen</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Default AI Version
          </label>
          <input
            type="text"
            className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={settings.aiVersion}
            onChange={(e) => setSettings({ ...settings, aiVersion: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Default AI Confidence (1-100)
          </label>
          <input
            type="number"
            min="1"
            max="100"
            className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={settings.aiConfidence}
            onChange={(e) => setSettings({ ...settings, aiConfidence: Number(e.target.value) })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Importo Base (&euro;)
          </label>
          <input
            type="number"
            className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={settings.baseAmount}
            onChange={(e) => setSettings({ ...settings, baseAmount: Number(e.target.value) })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Durata Base (Giorni)
          </label>
          <input
            type="number"
            className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={settings.baseDurationDays}
            onChange={(e) => setSettings({ ...settings, baseDurationDays: Number(e.target.value) })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Tempo di Refresh Widget di Stato (Secondi)
          </label>
          <input
            type="number"
            className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={settings.refreshInterval}
            onChange={(e) => setSettings({ ...settings, refreshInterval: Number(e.target.value) })}
          />
        </div>

        <button
          onClick={handleSave}
          className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          {saved ? 'Salvato!' : 'Salva Impostazioni'}
        </button>
      </div>
    </div>
  )
}


export const FinnhubSettings: React.FC = () => {
  const [apiKey, setApiKey] = useState('')
  const [visible, setVisible] = useState(false)
  const [status, setStatus] = useState<string | null>(null)
  const [quota, setQuota] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/admin/config/finnhub-key', {
      headers: { 'Authorization': Bearer  }
    })
      .then(res => res.json())
      .then(data => {
        if (data.exists) {
           setApiKey('********')
        }
      })
      .catch(() => {})
  }, [])

  const handleValidate = async () => {
    setLoading(true)
    setStatus(null)
    setQuota(null)
    try {
      const res = await fetch('/api/admin/config/finnhub-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': Bearer 
        },
        body: JSON.stringify({ api_key: apiKey })
      })
      const data = await res.json()
      if (res.ok && data.valid) {
         setStatus('Valida')
         setQuota(data.quota_remaining)
      } else {
         setStatus('Non valida')
      }
    } catch (e) {
      setStatus('Errore connessione')
    }
    setLoading(false)
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow mt-8 p-6">
      <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">Integrazioni Esterne</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Finnhub API Key
          </label>
          <div className="flex items-center space-x-2">
            <input
              data-testid="finnhub-api-key"
              type={visible ? "text" : "password"}
              className="flex-1 p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Inserisci API Key Finnhub"
            />
            <button 
              type="button" 
              onClick={() => setVisible(!visible)}
              className="px-3 py-2 bg-gray-200 dark:bg-slate-600 rounded text-sm"
              data-testid="toggle-visibility"
            >
              {visible ? 'Nascondi' : 'Mostra'}
            </button>
          </div>
        </div>

        <button
          data-testid="validate-finnhub"
          onClick={handleValidate}
          disabled={loading || !apiKey}
          className="mt-4 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded"
        >
          {loading ? 'Verifica in corso...' : 'Valida e Salva'}
        </button>

        {status && (
          <div className={mt-2 text-sm }>
            Stato: {status}
            {quota &&  (Quota residua: /60)}
          </div>
        )}
      </div>
    </div>
  )
}

export const FinnhubSettings: React.FC = () => {
  const [apiKey, setApiKey] = useState('')
  const [visible, setVisible] = useState(false)
  const [status, setStatus] = useState<string | null>(null)
  const [quota, setQuota] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/admin/config/finnhub-key', {
      headers: { 'Authorization': Bearer  }
    })
      .then(res => res.json())
      .then(data => {
        if (data.exists) {
           setApiKey('********')
        }
      })
      .catch(() => {})
  }, [])

  const handleValidate = async () => {
    setLoading(true)
    setStatus(null)
    setQuota(null)
    try {
      const res = await fetch('/api/admin/config/finnhub-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': Bearer 
        },
        body: JSON.stringify({ api_key: apiKey })
      })
      const data = await res.json()
      if (res.ok && data.valid) {
         setStatus('Valida')
         setQuota(data.quota_remaining)
      } else {
         setStatus('Non valida')
      }
    } catch (e) {
      setStatus('Errore connessione')
    }
    setLoading(false)
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow mt-8 p-6">
      <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">Integrazioni Esterne</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Finnhub API Key
          </label>
          <div className="flex items-center space-x-2">
            <input
              data-testid="finnhub-api-key"
              type={visible ? "text" : "password"}
              className="flex-1 p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Inserisci API Key Finnhub"
            />
            <button 
              type="button" 
              onClick={() => setVisible(!visible)}
              className="px-3 py-2 bg-gray-200 dark:bg-slate-600 rounded text-sm"
              data-testid="toggle-visibility"
            >
              {visible ? 'Nascondi' : 'Mostra'}
            </button>
          </div>
        </div>

        <button
          data-testid="validate-finnhub"
          onClick={handleValidate}
          disabled={loading || !apiKey}
          className="mt-4 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded"
        >
          {loading ? 'Verifica in corso...' : 'Valida e Salva'}
        </button>

        {status && (
          <div className={mt-2 text-sm }>
            Stato: {status}
            {quota &&  (Quota residua: /60)}
          </div>
        )}
      </div>
    </div>
  )
}

