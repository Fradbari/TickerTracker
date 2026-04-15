import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/shared/api/client'
import { EstimateCard } from '@/features/estimates/components/EstimateCard'
import { Filter, Search, SortAsc, SortDesc, X } from 'lucide-react'

// Basic layout for the advanced portfolio page
export const PortfolioAdvanced: React.FC = () => {
  const [searchTerm, setSearchSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('ALL')
  const [sortField, setSortField] = useState('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [selectedEstimate, setSelectedEstimate] = useState<any | null>(null)

  // Example dataloader
  const { data, isLoading } = useQuery({
    queryKey: ['advanced-portfolio', filterStatus, sortField, sortOrder],
    queryFn: async () => {
      // Typically, we would build query params:
      let url = `/api/estimates?limit=100&sort_by=${sortField}&sort_order=${sortOrder}`
      if (filterStatus !== 'ALL') url += `&status=${filterStatus}`
      
      const res = await apiClient.get(url)
      return res.data.data.items || []
    }
  })

  const estimates = data || []
  const filtered = estimates.filter((est: any) => 
    (est.ticker?.symbol || '').toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleCardClick = (id: string) => {
    const est = estimates.find((e: any) => e.id === id)
    if (est) setSelectedEstimate(est)
  }

  const closeModal = () => setSelectedEstimate(null)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100 mt-2">Portafoglio Avanzato</h2>
      </div>

      <div className="bg-white dark:bg-slate-800 p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative flex-1 w-full min-w-[250px]">
          <Search className="absolute left-3 top-2.5 text-slate-400 w-4 h-4" />
          <input 
            type="text" 
            placeholder="Cerca ticker..." 
            className="w-full pl-9 pr-4 py-2 border rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={searchTerm}
            onChange={e => setSearchSearch(e.target.value)}
          />
        </div>

        <div className="flex flex-wrap items-center gap-4 w-full md:w-auto">
          <div className="flex items-center gap-2">
            <Filter className="text-slate-400 w-4 h-4" />
            <select 
              value={filterStatus}
              onChange={e => setFilterStatus(e.target.value)}
              className="p-2 border rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="ALL">Tutti gli stati</option>
              <option value="OPEN">Aperti</option>
              <option value="CLOSED_WIN">Chiusi (Win)</option>
              <option value="CLOSED_LOSS">Chiusi (Loss)</option>
              <option value="EXPIRED">Scaduti</option>
            </select>
          </div>

          <div className="flex items-center gap-2 border-l pl-4 border-slate-200 dark:border-slate-600">
            <select 
              value={sortField}
              onChange={e => setSortField(e.target.value)}
              className="p-2 border rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="created_at">Data Creazione</option>
              <option value="ai_confidence">Confidenza AI</option>
              <option value="target_profit_percent">Target Profit %</option>
            </select>
            <button 
              onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
              className="p-2 bg-slate-100 dark:bg-slate-700 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-white transition-colors"
              title="Ordine crescente/decrescente"
            >
              {sortOrder === 'asc' ? <SortAsc className="w-5 h-5"/> : <SortDesc className="w-5 h-5"/>}
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-full text-slate-500 py-10 text-center animate-pulse">Caricamento portafoglio...</div>
        ) : filtered.length === 0 ? (
          <div className="col-span-full text-slate-500 py-10 text-center">Nessuna stima trovata con i filtri attuali.</div>
        ) : (
          filtered.map((est: any) => (
            <EstimateCard key={est.id} estimate={est} onClick={handleCardClick} />
          ))
        )}
      </div>

      {/* Modal */}
      {selectedEstimate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
            <div className="sticky top-0 bg-white/90 dark:bg-slate-800/90 backdrop-blur-md px-6 py-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center z-10 rounded-t-2xl">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span className="text-xl font-black">{selectedEstimate.ticker?.symbol || selectedEstimate.ticker_id}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${selectedEstimate.direction === 'LONG' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {selectedEstimate.direction}
                </span>
              </h3>
              <button 
                onClick={closeModal} 
                className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
              >
                <X className="w-6 h-6 text-slate-500" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Detail section */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700/50">
                  <div className="text-xs text-slate-500 mb-1">Prezzo Iniziale</div>
                    <div className="font-mono font-bold">${selectedEstimate.start_price}</div>
                  </div>
                  <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700/50">
                    <div className="text-xs text-slate-500 mb-1">Target Profit</div>
                    <div className="font-mono font-bold text-green-600">${selectedEstimate.target_price}</div>
                  </div>
                  <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700/50">
                    <div className="text-xs text-slate-500 mb-1">Stop Loss</div>
                    <div className="font-mono font-bold text-red-600">${selectedEstimate.stop_loss_price}</div>
                  </div>
              </div>

               {/* AI Info */}
              <div className="bg-indigo-50 dark:bg-indigo-900/20 p-5 rounded-xl border border-indigo-100 dark:border-indigo-800/30">
                <h4 className="text-sm font-bold text-indigo-900 dark:text-indigo-300 mb-3 uppercase tracking-wider">AI Analysis</h4>
                <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                  <div><span className="text-indigo-600/70 dark:text-indigo-400/70">Model:</span> <span className="font-medium text-slate-800 dark:text-slate-200">{selectedEstimate.ai_model || 'N/A'}</span></div>
                  <div><span className="text-indigo-600/70 dark:text-indigo-400/70">Version:</span> <span className="font-medium text-slate-800 dark:text-slate-200">{selectedEstimate.ai_version || 'N/A'}</span></div>
                  <div><span className="text-indigo-600/70 dark:text-indigo-400/70">Confidence:</span> <span className="font-medium text-slate-800 dark:text-slate-200">{selectedEstimate.ai_confidence ? `${selectedEstimate.ai_confidence}%` : 'N/A'}</span></div>
                </div>
                {selectedEstimate.ai_reasoning && (
                  <div className="mt-4 pt-4 border-t border-indigo-200/50 dark:border-indigo-800/50">
                    <span className="text-xs font-bold text-indigo-500 dark:text-indigo-400 uppercase tracking-widest block mb-2">Reasoning</span>
                    <p className="text-sm text-slate-700 dark:text-slate-300 italic whitespace-pre-wrap leading-relaxed">
                      "{selectedEstimate.ai_reasoning}"
                    </p>
                  </div>
                )}
              </div>
            </div>
            
            <div className="p-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 rounded-b-2xl flex justify-end">
              <button 
                onClick={closeModal} 
                className="px-6 py-2 bg-slate-800 hover:bg-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600 text-white font-medium rounded-lg transition-colors shadow-sm"
              >
                Chiudi
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
