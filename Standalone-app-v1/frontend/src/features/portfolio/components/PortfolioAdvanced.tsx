import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/shared/api/client'
import { EstimateCard } from '@/features/estimates/components/EstimateCard'
import { Filter, Search, SortAsc, SortDesc } from 'lucide-react'

// Basic layout for the advanced portfolio page
export const PortfolioAdvanced: React.FC = () => {
  const [searchTerm, setSearchSearch] = useState('')
  const [filterDirection, setFilterDirection] = useState<string>('ALL')
  const [filterStatus, setFilterStatus] = useState<string>('ALL')
  const [sortField, setSortField] = useState('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Example dataloader
  const { data, isLoading } = useQuery({
    queryKey: ['advanced-portfolio', filterDirection, filterStatus, sortField, sortOrder],
    queryFn: async () => {
      // Typically, we would build query params:
      let url = `/api/estimates?limit=100&sort_by=${sortField}&sort_order=${sortOrder}`
      if (filterDirection !== 'ALL') url += `&direction=${filterDirection}`
      if (filterStatus !== 'ALL') url += `&status=${filterStatus}`
      
      const res = await apiClient.get(url)
      return res.data.data.items || []
    }
  })

  const estimates = data || []
  const filtered = estimates.filter((est: any) => 
    (est.ticker?.symbol || '').toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Portafoglio Avanzato</h2>
      </div>

      <div className="bg-white dark:bg-slate-800 p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 flex flex-wrap gap-4 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-2.5 text-slate-400 w-4 h-4" />
          <input 
            type="text" 
            placeholder="Cerca ticker..." 
            className="w-full pl-9 pr-4 py-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
            value={searchTerm}
            onChange={e => setSearchSearch(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="text-slate-400 w-4 h-4" />
          <select 
            value={filterStatus}
            onChange={e => setFilterStatus(e.target.value)}
            className="p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white text-sm"
          >
            <option value="ALL">Tutti gli stati</option>
            <option value="OPEN">Aperti</option>
            <option value="CLOSED_WIN">Chiusi (Win)</option>
            <option value="CLOSED_LOSS">Chiusi (Loss)</option>
            <option value="EXPIRED">Scaduti</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <select 
            value={filterDirection}
            onChange={e => setFilterDirection(e.target.value)}
            className="p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white text-sm"
          >
            <option value="ALL">Tutte le direzioni</option>
            <option value="LONG">Solo LONG</option>
            <option value="SHORT">Solo SHORT</option>
          </select>
        </div>

        <div className="flex items-center gap-2 border-l pl-4 border-slate-200 dark:border-slate-600">
          <select 
            value={sortField}
            onChange={e => setSortField(e.target.value)}
            className="p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white text-sm"
          >
            <option value="created_at">Data Creazione</option>
            <option value="ai_confidence">Confidenza AI</option>
            <option value="target_profit_percent">Target Profit %</option>
          </select>
          <button 
            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
            className="p-2 bg-slate-100 dark:bg-slate-700 rounded hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-white"
            title="Ordine crescente/decrescente"
          >
            {sortOrder === 'asc' ? <SortAsc className="w-5 h-5"/> : <SortDesc className="w-5 h-5"/>}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-full text-slate-500 py-10 text-center animate-pulse">Caricamento portafoglio...</div>
        ) : filtered.length === 0 ? (
          <div className="col-span-full text-slate-500 py-10 text-center">Nessuna stima trovata con i filtri attuali.</div>
        ) : (
          filtered.map((est: any) => (
            <EstimateCard key={est.id} estimate={est} />
          ))
        )}
      </div>
    </div>
  )
}
