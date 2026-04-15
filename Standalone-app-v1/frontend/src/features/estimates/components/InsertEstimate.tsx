import React, { useState } from 'react'
import { useAsyncQueue } from '@/app/providers/AsyncQueueProvider'
import { useEstimateDefaults } from '@/features/admin/components/AdminSettings'
import apiClient from '@/shared/api/client'
import toast from 'react-hot-toast'

export const InsertEstimate: React.FC = () => {
  const defaults = useEstimateDefaults()
  const { queue, addItem, updateItem } = useAsyncQueue()

  const [ticker, setTicker] = useState('')
  const [direction, setDirection] = useState<'LONG'|'SHORT'>('LONG')
  const [targetProfit, setTargetProfit] = useState(defaults.targetProfitPercent)
  const [stopLoss, setStopLoss] = useState(defaults.stopLossPercent)
  const [aiModel, setAiModel] = useState(defaults.aiModel)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!ticker.trim()) {
      toast.error('Inserisci un ticker valido')
      return
    }

    const t = ticker.toUpperCase()

    // 1) Add to global Async Queue
    const queueId = addItem({
      ticker: t,
      direction,
      message: 'Cerco ticker...',
    })

    // Reset simple form bits immediately for user convenience
    setTicker('')
    toast.success(`Avviato inserimento per ${t}`)

    try {
      // Step A: Search / validate Ticker (simulate or actual lookup, here we assume direct input or basic check)
      updateItem(queueId, { message: 'Inizializzazione stima...', progress: 30 })

      // Step B: Submit to creation API
      // Since `create_estimate` API requires `ticker_id` (a UUID), we might need to get the UUID first.
      // But let's assume we can hit a unified endpoint or let the backend resolve Ticker -> UUID.
      // If backend only accepts UUID, we'll try to find it via /api/market-data/search or rely on the frontend fetching.
      // For this sample, we just POST directly assuming the backend will resolve or the API signature matches.
      
      // Look up Ticker to UUID
      updateItem(queueId, { message: 'Ricerca UUID ticker...', progress: 50 })
      const searchRes = await apiClient.get(`/api/market-data/search?query=${t}`)
      const tickersObj = searchRes.data.data
      
      if (!tickersObj || tickersObj.length === 0) {
        throw new Error('Ticker non trovato nel database o non supportato.')
      }
      
      const tickerUuid = tickersObj[0].id

      updateItem(queueId, { message: 'Creazione stima in corso...', progress: 75 })
      const res = await apiClient.post('/api/estimates', {
        ticker_id: tickerUuid,
        direction: direction,
        target_profit_percent: targetProfit,
        stop_loss_percent: stopLoss,
        ai_model: aiModel,
      })

      // Success
      updateItem(queueId, { 
        status: 'SUCCESS', 
        message: `Stima creata!`, 
        progress: 100,
        estimateId: res.data.data.id
      })
      toast.success(`${t} inserita con successo!`)

    } catch (err: any) {
      console.error(err)
      updateItem(queueId, { 
        status: 'ERROR', 
        message: err.response?.data?.message || err.message || 'Errore inserimento',
        progress: 100
      })
      toast.error(`Errore per ${t}: ${err.message}`)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Nuova Stima</h2>
      
      {/* Form Inserimento */}
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="col-span-full md:col-span-1 lg:col-span-1">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Ticker</label>
            <input 
              type="text" 
              placeholder="es. AAPL" 
              value={ticker}
              onChange={e => setTicker(e.target.value)}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white uppercase"
              required 
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Direzione</label>
            <select 
              value={direction} 
              onChange={e => setDirection(e.target.value as any)}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            >
              <option value="LONG">LONG (Rialzista)</option>
              <option value="SHORT">SHORT (Ribassista)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">AI Model</label>
            <select 
              value={aiModel} 
              onChange={e => setAiModel(e.target.value)}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            >
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Target Profit (%)</label>
            <input 
              type="number" 
              value={targetProfit}
              onChange={e => setTargetProfit(Number(e.target.value))}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Stop Loss (%)</label>
            <input 
              type="number" 
              value={stopLoss}
              onChange={e => setStopLoss(Number(e.target.value))}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            />
          </div>

          <div className="col-span-full flex justify-end">
            <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors">
              + Aggiungi Stima
            </button>
          </div>
        </form>
      </div>

      {/* Tracker Box */}
      <div className="bg-slate-50 dark:bg-slate-900 rounded-xl p-6 shadow-inner border border-slate-200 dark:border-slate-800 mt-8">
        <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center gap-2">
          <svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-5 h-5 text-indigo-500">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 0 1 0 3.75H5.625a1.875 1.875 0 0 1 0-3.75Z" />
          </svg>
          Ultime Lavorazioni (Tracker)
        </h3>
        
        {queue.length === 0 ? (
          <div className="text-slate-500 text-sm italic">Nessun inserimento recente in coda.</div>
        ) : (
          <div className="space-y-3">
            {queue.map(item => (
              <div key={item.id} className="flex items-center justify-between p-3 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 shadow-sm">
                <div className="flex flex-col">
                  <span className="font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
                    {item.ticker} 
                    <span className={`text-[10px] px-2 py-0.5 rounded ${item.direction === 'LONG' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {item.direction}
                    </span>
                  </span>
                  <span className="text-xs text-slate-500">{new Date(item.timestamp).toLocaleTimeString()}</span>
                </div>
                
                <div className="flex-1 px-8 text-center flex flex-col items-center">
                  <div className="text-sm text-slate-600 dark:text-slate-300 font-medium mb-1">{item.message}</div>
                  {item.status === 'PENDING' && (
                    <div className="w-48 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: `${item.progress}%` }}></div>
                    </div>
                  )}
                </div>

                <div className="flex items-center">
                  {item.status === 'PENDING' && <span className="text-blue-500 animate-pulse text-sm font-semibold">IN CORSO</span>}
                  {item.status === 'SUCCESS' && <span className="text-green-500 font-bold">COMPLETATO</span>}
                  {item.status === 'ERROR' && <span className="text-red-500 font-bold">ERRORE</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
