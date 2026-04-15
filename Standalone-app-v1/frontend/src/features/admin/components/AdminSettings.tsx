import React, { useState, useEffect } from 'react'

export interface EstimateDefaults {
  targetProfitPercent: number
  stopLossPercent: number
  aiModel: string
  baseAmount: number
  baseDurationDays: number
  refreshInterval: number
}

const DEFAULT_SETTINGS: EstimateDefaults = {
  targetProfitPercent: 10,
  stopLossPercent: 10,
  aiModel: 'gpt-4o',
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
