import React, { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/shared/api/client'
import { Filter, Search, SortAsc, SortDesc, X, Loader2, ArrowUp, ArrowDown } from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { DataTable, ColumnDef } from '@/shared/components/DataTable'
import { theme } from '@/styles/theme'
import { EstimateCard } from '@/features/estimates/components/EstimateCard'
import { EstimateDetailDrawer } from './EstimateDetailDrawer'

import { format, differenceInDays, parseISO } from 'date-fns'

// Calculate mock pnl for testing layout
const calculateLocalPnl = (entry: string, current: string, direction: string) => {
  const e = parseFloat(entry || '0');
  const c = parseFloat(current || '0');
  if (e === 0) return 0;
  const pct = ((c - e) / e) * 100;
  return direction === 'LONG' ? pct : -pct;
};
import { DataTable, ColumnDef } from '@/shared/components/DataTable'
import { theme } from '@/styles/theme'
import { EstimateCard } from '@/features/estimates/components/EstimateCard'
import { EstimateDetailDrawer } from './EstimateDetailDrawer'

import { format, differenceInDays, parseISO } from 'date-fns'

// Calculate mock pnl for testing layout
const calculateLocalPnl = (entry: string, current: string, direction: string) => {
  const e = parseFloat(entry || '0');
  const c = parseFloat(current || '0');
  if (e === 0) return 0;
  const pct = ((c - e) / e) * 100;
  return direction === 'LONG' ? pct : -pct;
};

// Basic layout for the advanced portfolio page
export const PortfolioAdvanced: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  
  // Params state
  const searchTerm = searchParams.get('ticker') || ''
  const statusParam = searchParams.get('status')
  const multiStatus = statusParam ? statusParam.split(',') : ['ALL']
  
  const sortField = searchParams.get('sort') || 'created_at'
  const sortOrder = searchParams.get('dir') || 'desc'
  
  const dateFrom = searchParams.get('dateFrom') || ''
  const dateTo = searchParams.get('dateTo') || ''
  const pnlMin = searchParams.get('pnlMin') || ''
  const pnlMax = searchParams.get('pnlMax') || ''

  const [selectedEstimate, setSelectedEstimate] = useState<any | null>(null)

  const updateParam = (key: string, value: string) => {
    const nextParams = new URLSearchParams(searchParams)
    if (value) nextParams.set(key, value)
    else nextParams.delete(key)
    setSearchParams(nextParams)
  }

  const toggleSort = (field: string) => {
    if (sortField === field) {
      updateParam('dir', sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      const next = new URLSearchParams(searchParams)
      next.set('sort', field)
      next.set('dir', 'desc')
      setSearchParams(next)
    }
  }

  // Example dataloader
  const { data, isLoading } = useQuery({
    queryKey: ['advanced-portfolio', statusParam, sortField, sortOrder],
    queryFn: async () => {
      // Backend does some basic filtering, frontend handles advanced local
      const res = await apiClient.get(/api/estimates?limit=1000)
      return res.data.data.items || []
    }
  })

  const estimates = data || []
  
  const filtered = useMemo(() => {
    return estimates.filter((est: any) => {
      // 1. Ticker Filter
      if (searchTerm && !(est.ticker?.symbol || est.ticker_id || '').toLowerCase().includes(searchTerm.toLowerCase())) return false;
      
      // 2. Status Multi-select
      if (!multiStatus.includes('ALL') && !multiStatus.includes(est.status)) return false;

      // 3. Date Interval
      if (dateFrom || dateTo) {
        const estDate = parseISO(est.created_at)
        if (dateFrom && estDate < new Date(dateFrom)) return false
        if (dateTo && estDate > new Date(dateTo)) return false
      }

      // 4. PnL Range (Mock/Local per test if no realized/current given properly by API)
      if (pnlMin || pnlMax) {
        // Normally computed server side or derived. For this lab, calculate simple simulated % or use API field
        let pnlPct = 0;
        if (est.status.startsWith('CLOSED') && est.realized_pnl) {
           pnlPct = ((parseFloat(est.realized_pnl) - parseFloat(est.start_price)) / parseFloat(est.start_price)) * 100
        } else {
           // just dummy proxy for slider
           pnlPct = calculateLocalPnl(est.start_price, est.current_price || est.start_price, est.direction)
        }
        
        if (pnlMin && pnlPct < parseFloat(pnlMin)) return false;
        if (pnlMax && pnlPct > parseFloat(pnlMax)) return false;
      }
      
      return true;
    }).sort((a: any, b: any) => {
      let valA = a[sortField]
      let valB = b[sortField]
      
      if (sortField === 'pnl') {
         valA = calculateLocalPnl(a.start_price, a.current_price || a.start_price, a.direction)
         valB = calculateLocalPnl(b.start_price, b.current_price || b.start_price, b.direction)
      } else if (sortField === 'ticker') {
         valA = a.ticker?.symbol || a.ticker_id
         valB = b.ticker?.symbol || b.ticker_id
      }
      
      if (valA === valB) return 0;
      const mod = sortOrder === 'desc' ? -1 : 1;
      
      return valA > valB ? 1 * mod : -1 * mod;
    });
  }, [estimates, searchTerm, multiStatus, dateFrom, dateTo, pnlMin, pnlMax, sortField, sortOrder])

  const renderBadge = (status: string, errorMsg?: string) => {
    switch (status) {
      case 'FETCHING':
        return <span style={{ color: theme.colors.warning }} className="flex items-center gap-1 font-bold"><Loader2 className="w-3 h-3 animate-spin" /> FETCHING</span>
      case 'ACTIVE':
      case 'OPEN':
        return <span style={{ color: theme.colors.success }} className="font-bold">ACTIVE</span>
      case 'TARGET HIT':
      case 'CLOSED_WIN':
        return <span style={{ color: theme.colors.info }} className="font-bold">TARGET HIT</span>
      case 'STOP HIT':
      case 'CLOSED_LOSS':
        return <span style={{ color: theme.colors.danger }} className="font-bold">STOP HIT</span>
      case 'EXPIRED':
        return <span style={{ color: theme.colors.expired }} className="font-bold">EXPIRED</span>
      case 'ERROR':
        return (
           <span style={{ color: theme.estimateStatus.ERROR || theme.colors.warning }} title={errorMsg || 'Errore'} className="font-bold cursor-help border-b border-dotted">ERROR</span>
        )
      default:
        return <span className="font-bold text-slate-500">{status}</span>
    }
  }

  const columns: ColumnDef<any>[] = [
    {
      header: (
        <div className="cursor-pointer flex items-center gap-1" onClick={() => toggleSort('ticker')}>
          Ticker {sortField === 'ticker' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3"/> : <ArrowDown className="w-3 h-3"/>)}
        </div>
      ),
      cell: (item) => <div className="font-black">{item.ticker?.symbol || item.ticker_id} <span className="text-xs text-slate-500 ml-1">{item.direction}</span></div>
    },
    {
      header: (
        <div className="cursor-pointer flex items-center gap-1" onClick={() => toggleSort('status')}>
          Stato {sortField === 'status' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3"/> : <ArrowDown className="w-3 h-3"/>)}
        </div>
      ),
      cell: (item) => renderBadge(item.status, item.error_message)
    },
    {
      header: 'Ingresso / Corrente',
      cell: (item) => <div className="flex flex-col text-sm"><span>$ {item.start_price}</span><span className="text-slate-400">$ {item.current_price || item.start_price}</span></div>
    },
    {
      header: 'SL / TP',
      cell: (item) => <div className="flex flex-col text-sm text-slate-500"><span className="text-red-500/80">$ {item.stop_loss_price}</span><span className="text-green-500/80">$ {item.target_price}</span></div>
    },
    {
      header: (
        <div className="cursor-pointer flex items-center gap-1" onClick={() => toggleSort('pnl')}>
          P&L % {sortField === 'pnl' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3"/> : <ArrowDown className="w-3 h-3"/>)}
        </div>
      ),
      cell: (item) => {
         const pnl = calculateLocalPnl(item.start_price, item.current_price || item.start_price, item.direction);
         return <div className={ont-bold }>{pnl.toFixed(2)}%</div>
      }
    },
    {
      header: (
        <div className="cursor-pointer flex items-center gap-1" onClick={() => toggleSort('created_at')}>
          Data {sortField === 'created_at' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3"/> : <ArrowDown className="w-3 h-3"/>)}
        </div>
      ),
      cell: (item) => <span className="text-sm">{format(parseISO(item.created_at), 'dd/MM/yy')}</span>
    }
  ]

  const closeModal = () => setSelectedEstimate(null)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100 mt-2">Portafoglio Avanzato</h2>
      </div>

      <div className="bg-white dark:bg-slate-800 p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col gap-4">
        
        {/* ROW 1: Search & Status */}
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3 top-2.5 text-slate-400 w-4 h-4" />
            <input 
              type="text" 
              placeholder="Filtra per ticker..." 
              className="w-full pl-9 pr-4 py-2 border rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={searchTerm}
              onChange={e => updateParam('ticker', e.target.value)}
            />
          </div>

          <div className="flex items-center gap-2 w-full md:w-auto">
            <Filter className="text-slate-400 w-4 h-4" />
            <select 
              multiple
              value={multiStatus}
              onChange={e => {
                const values = Array.from(e.target.selectedOptions, option => option.value)
                updateParam('status', values.join(','))
              }}
              className="p-2 border rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 h-[42px]"
            >
              <option value="ALL">Tutti gli stati</option>
              <option value="OPEN">ATTIVI</option>
              <option value="FETCHING">FETCHING</option>
              <option value="CLOSED_WIN">TARGET HIT</option>
              <option value="CLOSED_LOSS">STOP HIT</option>
              <option value="EXPIRED">EXPIRED</option>
            </select>
          </div>
        </div>

        {/* ROW 2: Dates and PnL Range */}
        <div className="flex flex-wrap items-center gap-4 text-sm bg-slate-50 dark:bg-slate-900/50 p-3 rounded-lg border border-slate-100 dark:border-slate-700">
           <div className="flex items-center gap-2">
             <span className="text-slate-500 font-medium">Dal:</span>
             <input type="date" value={dateFrom} onChange={e => updateParam('dateFrom', e.target.value)} className="p-1 border rounded dark:bg-slate-800 dark:border-slate-600" />
             <span className="text-slate-500 font-medium ml-2">Al:</span>
             <input type="date" value={dateTo} onChange={e => updateParam('dateTo', e.target.value)} className="p-1 border rounded dark:bg-slate-800 dark:border-slate-600" />
           </div>
           
           <div className="flex items-center gap-2 border-l border-slate-200 dark:border-slate-600 pl-4">
             <span className="text-slate-500 font-medium">P&L Min %:</span>
             <input type="number" value={pnlMin} onChange={e => updateParam('pnlMin', e.target.value)} className="p-1 border rounded dark:bg-slate-800 dark:border-slate-600 w-20" />
             <span className="text-slate-500 font-medium ml-2">Max %:</span>
             <input type="number" value={pnlMax} onChange={e => updateParam('pnlMax', e.target.value)} className="p-1 border rounded dark:bg-slate-800 dark:border-slate-600 w-20" />
           </div>
           
           <button onClick={() => setSearchParams(new URLSearchParams())} className="ml-auto text-xs text-red-500 hover:text-red-700 dark:text-red-400">
             Reset Filtri
           </button>
        </div>

      </div>

      <div className="mt-4">
         <DataTable 
            columns={columns} 
            data={filtered} 
            isLoading={isLoading} 
            emptyMessage="Nessuna stima presente per questi filtri"
            onRowClick={(item) => setSelectedEstimate(item)}
         />
      </div>

      {/* Drawer */}
      <EstimateDetailDrawer 
        estimate={selectedEstimate} 
        onClose={closeModal} 
        renderBadge={renderBadge} 
      />
    </div>
  )
}