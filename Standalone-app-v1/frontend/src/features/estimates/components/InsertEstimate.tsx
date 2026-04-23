import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAsyncQueue } from '@/app/providers/AsyncQueueProvider'
import { useEstimateDefaults } from '@/features/admin/components/AdminSettings'
import apiClient from '@/shared/api/client'
import toast from 'react-hot-toast'

/**
 * Componente principale per inserire una nuova stima.
 */

type FinnhubStatus = {
  finnhub_key_configured: boolean
}

type SymbolValidationState = 'idle' | 'valid' | 'invalid' | 'unavailable'

const fetchFinnhubStatus = async (): Promise<FinnhubStatus | null> => {
  try {
    const adminToken = localStorage.getItem('admin_token') ?? ''
    const response = await apiClient.get('/api/admin/config/finnhub-key', {
      headers: {
        'x-admin-token': adminToken,
      },
    })

    return {
      finnhub_key_configured: Boolean(response.data?.valid),
    }
  } catch {
    return null
  }
}

export const InsertEstimate: React.FC = () => {
  const defaults = useEstimateDefaults()
  const { queue, addItem, updateItem, removeItem } = useAsyncQueue()

  const { data: finnhubStatus } = useQuery({
    queryKey: ['finnhub-status'],
    queryFn: fetchFinnhubStatus,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: false,
  })

  const finnhubKeyConfigured = finnhubStatus?.finnhub_key_configured ?? null

  const [tickerQuery, setTickerQuery] = useState('')
  const [selectedTickerId, setSelectedTickerId] = useState<string | null>(null)
  
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const [symbolValidationState, setSymbolValidationState] = useState<SymbolValidationState>('idle')
  const [symbolValidationMessage, setSymbolValidationMessage] = useState<string>('')
  const [isValidatingSymbol, setIsValidatingSymbol] = useState(false)

  const [targetProfit, setTargetProfit] = useState(defaults.targetProfitPercent)
  const [stopLoss, setStopLoss] = useState(defaults.stopLossPercent)
  const [aiModel, setAiModel] = useState(defaults.aiModel)
  const [aiVersion, setAiVersion] = useState(defaults.aiVersion)
  const [aiConfidence, setAiConfidence] = useState<number | ''>(defaults.aiConfidence || 60)
  
  const [amount, setAmount] = useState(defaults.baseAmount)
  const [durationDays, setDurationDays] = useState(defaults.baseDurationDays)

  useEffect(() => {
    setTargetProfit(defaults.targetProfitPercent)
    setStopLoss(defaults.stopLossPercent)
    setAiModel(defaults.aiModel)
    setAiVersion(defaults.aiVersion)
    setAiConfidence(defaults.aiConfidence)
  }, [defaults])

  useEffect(() => {
    if (tickerQuery.length < 2) {
      setSearchResults([])
      setShowDropdown(false)
      return
    }
    
    // If the user already selected something, don't trigger search
    if (selectedTickerId) return

    const delayDebounceFn = setTimeout(async () => {
      setIsSearching(true)
      try {
        const res = await apiClient.get(`/api/market/symbol-search?q=${tickerQuery}`)
        setSearchResults(res.data.data?.results || [])
        setShowDropdown(true)
      } catch (err) {
        console.error('Error fetching tickers', err)
      } finally {
        setIsSearching(false)
      }
    }, 400)

    return () => clearTimeout(delayDebounceFn)
  }, [tickerQuery, selectedTickerId])

  const handleSelectTicker = (t: any) => {
    setTickerQuery(t.symbol)
    setSelectedTickerId(t.id || t.uuid || t.symbol) // Use id if available, else fallback
    setShowDropdown(false)
  }

  const handleTickerBlurValidation = async () => {
    const normalizedTicker = tickerQuery.trim().toUpperCase()
    if (!normalizedTicker) {
      setSymbolValidationState('idle')
      setSymbolValidationMessage('')
      return
    }

    // Se Finnhub e presente, lasciamo la UX esistente senza fallback manuale extra.
    if (finnhubKeyConfigured !== false) {
      setSymbolValidationState('idle')
      setSymbolValidationMessage('')
      return
    }

    setIsValidatingSymbol(true)
    try {
      const response = await apiClient.get('/api/market/symbol-validate', {
        params: { symbol: normalizedTicker },
      })

      const validationData = response.data?.data
      if (validationData?.valid) {
        setSymbolValidationState('valid')
        setSymbolValidationMessage('Simbolo valido')
      } else {
        setSymbolValidationState('invalid')
        setSymbolValidationMessage('Simbolo non trovato')
      }
    } catch {
      // Fallback silenzioso: nessun blocco submit, solo hint non intrusivo.
      setSymbolValidationState('unavailable')
      setSymbolValidationMessage('Verifica simbolo non disponibile al momento')
    } finally {
      setIsValidatingSymbol(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!tickerQuery.trim()) {
      toast.error('Inserisci un ticker valido')
      return
    }

    const t = tickerQuery.toUpperCase()

    const queueId = addItem({
      ticker: t,
      
      message: 'Cerco ticker...',
    })

    setTickerQuery('')
    setSelectedTickerId(null)
    toast.success(`Avviato inserimento per ${t}`)

    try {
      updateItem(queueId, { message: 'Inizializzazione stima...', progress: 30 })
      
      let tickerUuid = selectedTickerId
      
      if (!tickerUuid) {
        updateItem(queueId, { message: 'Ricerca UUID ticker...', progress: 50 })
        const searchRes = await apiClient.get(`/api/market/symbol-search?q=${t}`)
        const tickersObj = searchRes.data.data?.results
        
        if (!tickersObj || tickersObj.length === 0) {
          throw new Error('Ticker non trovato nel database o non supportato.')
        }
        tickerUuid = tickersObj[0].id || tickersObj[0].uuid
      }

      updateItem(queueId, { message: 'Creazione stima in corso...', progress: 75 })
      const res = await apiClient.post('/api/estimates', {
        ticker_id: tickerUuid,
        target_profit_percent: targetProfit,
        stop_loss_percent: stopLoss,
        ai_model: aiModel,
        ai_version: aiVersion || undefined,
        ai_confidence: aiConfidence ? Number(aiConfidence) : undefined,
        amount: amount,
        duration_days: durationDays
      })

      updateItem(queueId, { 
        status: 'SUCCESS', 
        message: `Stima creata!`, 
        progress: 100,
        estimateId: res.data.data?.id
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
      
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700 overflow-visible">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Ticker Autocomplete */}
          <div className="col-span-full md:col-span-1 lg:col-span-1 relative">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Ticker / Azienda</label>
            <input 
              type="text" 
              placeholder="es. AAPL o Apple..." 
              value={tickerQuery}
              onChange={e => {
                setTickerQuery(e.target.value)
                setSelectedTickerId(null)
                setSymbolValidationState('idle')
                setSymbolValidationMessage('')
                if(!showDropdown) setShowDropdown(true)
              }}
              onBlur={() => {
                void handleTickerBlurValidation()
              }}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white uppercase"
              required 
            />
            {isSearching && (
              <div className="absolute right-3 top-[34px] text-slate-400">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              </div>
            )}
            {showDropdown && searchResults.length > 0 && (
              <ul className="absolute z-50 w-full bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded mt-1 max-h-48 overflow-y-auto shadow-lg">
                {searchResults.map((t, idx) => (
                  <li 
                    key={idx} 
                    onClick={() => handleSelectTicker(t)}
                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-600 cursor-pointer border-b last:border-0 border-slate-100 dark:border-slate-600"
                  >
                    <div className="font-bold text-slate-800 dark:text-white uppercase">{t.symbol}</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 truncate">{t.short_name || t.long_name || ''}</div>
                  </li>
                ))}
              </ul>
            )}
            {showDropdown && tickerQuery.length >= 2 && searchResults.length === 0 && !isSearching && !selectedTickerId && (
              <div className="absolute z-50 w-full bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded mt-1 p-3 text-sm text-slate-500 shadow-lg">
                Nessun risultato trovato in Yahoo Finance.
              </div>
            )}
            {isValidatingSymbol && finnhubKeyConfigured === false && (
              <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                Verifica simbolo in corso...
              </p>
            )}
            {!isValidatingSymbol && symbolValidationMessage && finnhubKeyConfigured === false && (
              <p
                className={`mt-2 text-xs ${
                  symbolValidationState === 'valid'
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : symbolValidationState === 'invalid'
                      ? 'text-amber-600 dark:text-amber-400'
                      : 'text-slate-500 dark:text-slate-400'
                }`}
              >
                {symbolValidationMessage}
              </p>
            )}
          </div>

          {finnhubKeyConfigured === false && (
            <div className="col-span-full rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-200">
              <p className="font-medium">
                Ricerca automatica simboli non disponibile: Finnhub non configurata.
              </p>
              <p className="mt-1">
                Puoi comunque inserire manualmente il ticker (es. AAPL, MSFT, ENI.MI).
              </p>
              <Link to="/admin" className="mt-2 inline-flex text-xs font-semibold underline underline-offset-2 hover:no-underline">
                Vai ad Admin per configurare Finnhub
              </Link>
            </div>
          )}

          {/* Model Model block */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">AI Model</label>
            <select 
              value={aiModel} 
              onChange={e => setAiModel(e.target.value)}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
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
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">AI Version</label>
            <input 
              type="text" 
              placeholder="es. 4-turbo" 
              value={aiVersion}
              onChange={e => setAiVersion(e.target.value)}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">AI Confidence (1-100)</label>
            <input
              type="number"
              min="1"
              max="100"
              value={aiConfidence}
              onChange={e => setAiConfidence(e.target.value === '' ? '' : Number(e.target.value))}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Importo Base (&euro;)</label>
            <input 
              type="number" 
              value={amount}
              onChange={e => setAmount(Number(e.target.value))}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Durata Base (Giorni)</label>
            <input 
              type="number" 
              value={durationDays}
              onChange={e => setDurationDays(Number(e.target.value))}
              className="w-full p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            />
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

                <div className="flex items-center gap-3">
                  {item.status === 'PENDING' && <span className="text-blue-500 animate-pulse text-sm font-semibold">IN CORSO</span>}
                  {item.status === 'SUCCESS' && (
                    <div className="flex items-center gap-3">
                      <span className="text-green-500 font-bold">COMPLETATO</span>
                      {item.estimateId && (
                        <div className="flex gap-2">
                          <button 
                            onClick={() => {
                              // Simulate quick delete using the API (You can wire this to useMutation proper later)
                              if(window.confirm('Eliminare questa stima appena creata?')) {
                                apiClient.delete(`/api/estimates/${item.estimateId}`)
                                  .then(() => toast.success('Stima eliminata correttamente.'))
                                  .catch(err => toast.error('Errore durante eliminazione stima.'))
                              }
                            }}
                            className="p-1 px-3 text-xs bg-red-100 hover:bg-red-200 text-red-700 dark:bg-red-900/30 dark:hover:bg-red-800/50 dark:text-red-400 rounded transition"
                          >
                            Elimina
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                  {item.status === 'ERROR' && <span className="text-red-500 font-bold">ERRORE</span>}
                  
                  <button 
                    onClick={() => removeItem(item.id)} 
                    className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition ml-2"
                    title="Rimuovi dalla coda"
                  >
                    Ã—
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

