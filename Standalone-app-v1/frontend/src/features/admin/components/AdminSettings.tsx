import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DEFAULT_SETTINGS: EstimateDefaults = {
  targetProfitPercent: 10,
  stopLossPercent: 10,
  aiModel: 'gpt-4o',
  aiVersion: 'gpt-4o-mini',
  aiConfidence: 60,
  baseAmount: 1000,
  baseDurationDays: 30,
  refreshInterval: 30,
}

const ADMIN_TOKEN_STORAGE_KEY = 'admin_token'
const ADMIN_TOKEN_CHANGED_EVENT = 'admin-token-changed'

const readAdminToken = (): string => {
  if (typeof window === 'undefined') return ''
  return (localStorage.getItem(ADMIN_TOKEN_STORAGE_KEY) || '').trim()
}

const saveAdminToken = (token: string): void => {
  if (typeof window === 'undefined') return
  localStorage.setItem(ADMIN_TOKEN_STORAGE_KEY, token)
  window.dispatchEvent(new Event(ADMIN_TOKEN_CHANGED_EVENT))
}

const removeAdminToken = (): void => {
  if (typeof window === 'undefined') return
  localStorage.removeItem(ADMIN_TOKEN_STORAGE_KEY)
  window.dispatchEvent(new Event(ADMIN_TOKEN_CHANGED_EVENT))
}

const useAdminToken = () => {
  const [adminToken, setAdminTokenState] = useState<string>('')

  useEffect(() => {
    const syncToken = () => setAdminTokenState(readAdminToken())
    syncToken()

    window.addEventListener(ADMIN_TOKEN_CHANGED_EVENT, syncToken)
    window.addEventListener('storage', syncToken)
    return () => {
      window.removeEventListener(ADMIN_TOKEN_CHANGED_EVENT, syncToken)
      window.removeEventListener('storage', syncToken)
    }
  }, [])

  return {
    adminToken,
    setAdminToken: (token: string) => saveAdminToken(token.trim()),
    clearAdminToken: () => removeAdminToken(),
  }
}

// ---------------------------------------------------------------------------
// AdminTokenSettings — setup token admin per chiamate protette
// ---------------------------------------------------------------------------

export const AdminTokenSettings: React.FC = () => {
  const { adminToken, setAdminToken, clearAdminToken } = useAdminToken()
  const [inputToken, setInputToken] = useState('')

  const handleSetToken = () => {
    const token = inputToken.trim()
    if (!token) {
      toast.error('Inserisci un token admin valido.')
      return
    }
    setAdminToken(token)
    setInputToken('')
    toast.success('Token admin impostato')
  }

  const handleLogout = () => {
    clearAdminToken()
    toast.success('Token admin rimosso')
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow mt-8 p-6">
      <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">
        Token Admin
      </h2>

      {adminToken ? (
        <div className="space-y-3">
          <p className="text-sm text-green-600 dark:text-green-400">Token admin impostato.</p>
          <button
            onClick={handleLogout}
            className="bg-amber-600 hover:bg-amber-700 text-white font-bold py-2 px-4 rounded"
          >
            Logout / Cambia token
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Inserisci il token admin per abilitare le chiamate protette (/api/admin/*).
          </p>
          <input
            type="password"
            className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={inputToken}
            onChange={(e) => setInputToken(e.target.value)}
            placeholder="Inserisci token admin"
          />
          <button
            onClick={handleSetToken}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Imposta token admin
          </button>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Hook: useEstimateDefaults
// ---------------------------------------------------------------------------

export const useEstimateDefaults = () => {
  const [defaults, setDefaults] = useState<EstimateDefaults>(DEFAULT_SETTINGS)

  useEffect(() => {
    const saved = localStorage.getItem('estimate_defaults')
    if (saved) {
      try {
        setDefaults(JSON.parse(saved) as EstimateDefaults)
      } catch {
        // ignore parse errors silently
      }
    }
  }, [])

  return defaults
}

// ---------------------------------------------------------------------------
// AdminSettings — impostazioni default stime + intervallo prezzi
// ---------------------------------------------------------------------------

export const AdminSettings: React.FC = () => {
  const [settings, setSettings] = useState<EstimateDefaults>(DEFAULT_SETTINGS)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const savedData = localStorage.getItem('estimate_defaults')
    if (savedData) {
      try {
        setSettings(JSON.parse(savedData) as EstimateDefaults)
      } catch {
        // ignore
      }
    }
  }, [])

  const handleSave = () => {
    try {
      localStorage.setItem('estimate_defaults', JSON.stringify(settings))
      setSaved(true)
      toast.success('Configurazione salvata')
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Errore sconosciuto'
      toast.error(`Salvataggio configurazione fallito: ${msg}.`)
    }
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow mt-8 p-6">
      <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">
        Impostazioni di Default Stime
      </h2>

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

// ---------------------------------------------------------------------------
// PriceIntervalSettings — Intervallo aggiornamento prezzi
// ---------------------------------------------------------------------------

export const PriceIntervalSettings: React.FC = () => {
  const { adminToken } = useAdminToken()
  const [intervalMinutes, setIntervalMinutes] = useState<number>(5)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!adminToken) return

    // Carica il valore corrente dal backend
    fetch('/api/admin/config', {
      headers: { 'X-Admin-Token': adminToken },
    })
      .then(res => res.json())
      .then((data: { price_update_interval_minutes?: number }) => {
        if (data.price_update_interval_minutes !== undefined) {
          setIntervalMinutes(data.price_update_interval_minutes)
        }
      })
      .catch(() => {})
  }, [adminToken])

  const handleSave = async () => {
    if (!adminToken) {
      toast.error('Imposta prima il token admin.')
      return
    }

    setSaving(true)
    try {
      const res = await fetch('/api/admin/config', {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'X-Admin-Token': adminToken 
        },
        body: JSON.stringify({ price_update_interval_minutes: intervalMinutes }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({})) as { detail?: string }
        throw new Error(data.detail ?? `HTTP ${res.status}`)
      }
      toast.success('Configurazione salvata')
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Errore sconosciuto'
      toast.error(`Salvataggio configurazione fallito: ${msg}.`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow mt-8 p-6">
      <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">
        Intervallo Aggiornamento Prezzi
      </h2>

      {!adminToken && (
        <p className="text-sm text-amber-600 dark:text-amber-400 mb-3">
          Imposta il token admin nella sezione Token Admin per modificare questa configurazione.
        </p>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            PRICE_UPDATE_INTERVAL_MINUTES
          </label>
          <div className="flex items-center gap-3">
            <input
              type="number"
              min="1"
              max="60"
              className="w-32 p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={intervalMinutes}
              onChange={(e) => setIntervalMinutes(Number(e.target.value))}
            />
            <span className="text-sm text-slate-500">minuti</span>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Frequenza con cui il backend controlla i prezzi di mercato per le stime attive.
          </p>
        </div>

        <button
          onClick={() => void handleSave()}
          disabled={saving || !adminToken}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded"
        >
          {saving ? 'Salvataggio...' : 'Salva Intervallo'}
        </button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// GDriveSettings — Backup e Ripristino via Google Drive
// ---------------------------------------------------------------------------

export const GDriveSettings: React.FC = () => {
  const [syncProgress, setSyncProgress] = useState(0)
  const [syncMessage, setSyncMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [driveConfigured, setDriveConfigured] = useState<boolean | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then((data: { components?: Array<{ name: string; message?: string }> }) => {
        const googleDrive = data.components?.find(c => c.name === 'google_drive')
        if (!googleDrive) {
          setDriveConfigured(null)
          return
        }
        const message = (googleDrive.message || '').toLowerCase()
        setDriveConfigured(!message.includes('not configured'))
      })
      .catch(() => setDriveConfigured(null))

    // TODO: riabilitare quando /api/sse/stream sarà implementato nel backend
    /*
    const eventSource = new EventSource('/api/sse/stream')
    eventSource.addEventListener('sync_progress', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as { progress_pct: number; message: string }
      setSyncProgress(data.progress_pct)
      setSyncMessage(data.message)
      if (data.progress_pct === 100) {
        setSyncing(false)
        toast.success('Backup completato')
      }
    })
    return () => eventSource.close()
    */
  }, [])

  const triggerExport = async () => {
    setSyncing(true)
    setSyncProgress(0)
    setSyncMessage('Avvio backup...')
    toast.success('Backup avviato...')
    try {
      const res = await fetch('/api/sync/export', { method: 'POST' })
      if (!res.ok) {
        const data = await res.json().catch(() => ({})) as { detail?: string }
        throw new Error(data.detail ?? `HTTP ${res.status}`)
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Errore sconosciuto'
      toast.error(`Backup fallito: ${msg}. Riprova.`)
      setSyncing(false)
    }
  }

  const triggerImport = async () => {
    setShowModal(false)
    setSyncing(true)
    setSyncProgress(0)
    setSyncMessage('Avvio ripristino...')
    try {
      const res = await fetch('/api/sync/import', { method: 'POST' })
      if (!res.ok) {
        const data = await res.json().catch(() => ({})) as { detail?: string }
        throw new Error(data.detail ?? `HTTP ${res.status}`)
      }
      toast.success('Ripristino completato')
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Errore sconosciuto'
      toast.error(`Ripristino fallito: ${msg}. Riprova.`)
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow mt-8 p-6">
      <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">
        Sincronizzazione GDrive
      </h2>

      <p className="text-sm text-slate-600 dark:text-slate-300 mb-4">
        {driveConfigured === null
          ? 'Google Drive: Stato non disponibile'
          : driveConfigured
            ? 'Google Drive: Configurato'
            : 'Google Drive: Non configurato (richiede variabile env)'}
      </p>

      <div className="space-y-4">
        <div className="flex gap-3">
          <button
            onClick={() => void triggerExport()}
            disabled={syncing}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded"
          >
            {syncing ? 'In corso...' : 'Backup su GDrive'}
          </button>

          <button
            onClick={() => setShowModal(true)}
            disabled={syncing}
            className="bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded"
          >
            Ripristina da GDrive
          </button>
        </div>

        {syncing && (
          <div className="space-y-1">
            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${syncProgress}%` }}
              />
            </div>
            <p className="text-xs text-slate-500">{syncMessage}</p>
          </div>
        )}
      </div>

      {/* Modale conferma ripristino */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-6 max-w-sm w-full shadow-xl">
            <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 mb-2">
              Conferma Ripristino
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-300 mb-4">
              Vuoi sovrascrivere i dati attuali con l&apos;ultimo backup da GDrive? Questa azione è irreversibile.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 rounded border border-slate-300 dark:border-slate-600 text-sm"
              >
                Annulla
              </button>
              <button
                onClick={() => void triggerImport()}
                className="px-4 py-2 rounded bg-amber-600 hover:bg-amber-700 text-white text-sm font-bold"
              >
                Conferma Ripristino
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// FinnhubSettings — chiave API Finnhub con validazione
// ---------------------------------------------------------------------------

export const FinnhubSettings: React.FC = () => {
  const { adminToken } = useAdminToken()
  const [apiKey, setApiKey] = useState('')
  const [visible, setVisible] = useState(false)
  const [status, setStatus] = useState<string | null>(null)
  const [quota, setQuota] = useState<string | null>(null)
  const [updatedAt, setUpdatedAt] = useState<string | null>(null)
  const [isConfigured, setIsConfigured] = useState(false)
  const [loading, setLoading] = useState(false)

  const loadFinnhubStatus = () => {
    if (!adminToken) {
      setStatus(null)
      setIsConfigured(false)
      return
    }

    fetch('/api/admin/config/finnhub-key', {
      headers: { 'X-Admin-Token': adminToken },
    })
      .then(res => res.json())
      .then((data: { valid?: boolean; updated_at?: string | null; quota_remaining?: string | null }) => {
        const valid = Boolean(data.valid)
        setIsConfigured(valid)
        setUpdatedAt(data.updated_at ?? null)
        setQuota(data.quota_remaining ?? null)
        if (valid) {
          setStatus('Valida')
          setApiKey('********')
        } else {
          setStatus(null)
        }
      })
      .catch(() => {})
  }

  useEffect(() => {
    loadFinnhubStatus()
  }, [adminToken])

  const handleValidate = async () => {
    if (!adminToken) {
      toast.error('Imposta prima il token admin.')
      return
    }

    setLoading(true)
    setStatus(null)
    setQuota(null)
    try {
      const res = await fetch('/api/admin/config/finnhub-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Token': adminToken,
        },
        body: JSON.stringify({ api_key: apiKey }),
      })
      const data = await res.json() as { valid?: boolean; quota_remaining?: string; detail?: string }
      if (res.ok && data.valid) {
        setStatus('Valida')
        setQuota(data.quota_remaining ?? null)
        loadFinnhubStatus()
        toast.success('Chiave Finnhub verificata e salvata')
      } else {
        const msg = data.detail ?? 'Chiave non valida'
        setStatus('Non valida')
        toast.error(`Verifica Finnhub fallita: ${msg}.`)
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Errore di connessione'
      setStatus('Errore connessione')
      toast.error(`Verifica Finnhub fallita: ${msg}.`)
    }
    setLoading(false)
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow mt-8 p-6">
      <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">
        Integrazioni Esterne
      </h2>
      <div className="space-y-4">
        {isConfigured ? (
          <div className="text-sm text-green-600 dark:text-green-400">
            Chiave configurata ✓ | Aggiornata: {updatedAt ?? '-'} | Quota: {quota ?? '-'}
          </div>
        ) : (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Finnhub API Key
              </label>
              <div className="flex items-center space-x-2">
                <input
                  data-testid="finnhub-api-key"
                  type={visible ? 'text' : 'password'}
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
              onClick={() => void handleValidate()}
              disabled={loading || !apiKey}
              className="mt-4 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded"
            >
              {loading ? 'Verifica in corso...' : 'Verifica e Salva'}
            </button>

            {status && (
              <div className={`mt-2 text-sm ${status === 'Valida' ? 'text-green-500' : 'text-red-500'}`}>
                Stato: {status}
                {quota && <span className="ml-2 text-slate-400">(Quota residua: {quota}/60)</span>}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
