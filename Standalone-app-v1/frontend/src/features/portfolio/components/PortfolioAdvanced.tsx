import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import apiClient from '@/shared/api/client'
import { Filter, Search, ArrowUp, ArrowDown, Loader2 } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import { DataTable, type ColumnDef } from '@/shared/components/DataTable'
import { theme } from '@/styles/theme'
import { EstimateDetailDrawer } from './EstimateDetailDrawer'
import { format, parseISO } from 'date-fns'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Calcola il P&L % locale (usato come proxy lato frontend). */
const calculateLocalPnl = (entry: string, current: string, direction: string): number => {
  const e = parseFloat(entry || '0')
  const c = parseFloat(current || '0')
  if (e === 0) return 0
  const pct = ((c - e) / e) * 100
  return direction === 'LONG' ? pct : -pct
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

// TODO: replace `any` with typed Estimate domain model when available
export const PortfolioAdvanced: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const queryClient = useQueryClient()

  // — URL params ————————————————————————————————————————————————————————————
  const searchTerm  = searchParams.get('ticker') || ''
  const statusParam = searchParams.get('status')
  const multiStatus = statusParam ? statusParam.split(',') : ['ALL']
  const sortField   = searchParams.get('sort') || 'created_at'
  const sortOrder   = searchParams.get('dir')  || 'desc'
  const dateFrom    = searchParams.get('dateFrom') || ''
  const dateTo      = searchParams.get('dateTo')   || ''
  const pnlMin      = searchParams.get('pnlMin')   || ''
  const pnlMax      = searchParams.get('pnlMax')   || ''

  const [selectedEstimate, setSelectedEstimate] = useState<any | null>(null) // TODO: type

  // — Param helpers ——————————————————————————————————————————————————————————
  const updateParam = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    setSearchParams(next)
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

  // — Data fetching ——————————————————————————————————————————————————————————
  const { data, isLoading } = useQuery({
    queryKey: ['advanced-portfolio', statusParam, sortField, sortOrder],
    queryFn: async () => {
      const res = await apiClient.get('/api/estimates?limit=1000')
      return (res.data.data.items || []) as any[] // TODO: typed array
    },
  })

  const estimates = data || []

  // — Delete mutation ————————————————————————————————————————————————————————
  const { mutate: deleteEstimate } = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/estimates/${id}`)
    },
    onSuccess: () => {
      toast.success('Stima eliminata')
      void queryClient.invalidateQueries({ queryKey: ['advanced-portfolio'] })
    },
    onError: (err: Error) => {
      toast.error(`Eliminazione fallita: ${err.message}. Riprova.`)
    },
  })

  // — Client-side filtering & sorting ———————————————————————————————————————
  const filtered = useMemo(() => {
    return estimates
      .filter((est: any) => {
        if (searchTerm && !(est.ticker?.symbol || est.ticker_id || '').toLowerCase().includes(searchTerm.toLowerCase())) return false
        if (!multiStatus.includes('ALL') && !multiStatus.includes(est.status)) return false
        if (dateFrom || dateTo) {
          const estDate = parseISO(est.created_at)
          if (dateFrom && estDate < new Date(dateFrom)) return false
          if (dateTo   && estDate > new Date(dateTo))   return false
        }
        if (pnlMin || pnlMax) {
          let pnlPct = 0
          if (est.status.startsWith('CLOSED') && est.realized_pnl) {
            pnlPct = ((parseFloat(est.realized_pnl) - parseFloat(est.start_price)) / parseFloat(est.start_price)) * 100
          } else {
            pnlPct = calculateLocalPnl(est.start_price, est.current_price || est.start_price, est.direction)
          }
          if (pnlMin && pnlPct < parseFloat(pnlMin)) return false
          if (pnlMax && pnlPct > parseFloat(pnlMax)) return false
        }
        return true
      })
      .sort((a: any, b: any) => {
        let valA = a[sortField]
        let valB = b[sortField]
        if (sortField === 'pnl') {
          valA = calculateLocalPnl(a.start_price, a.current_price || a.start_price, a.direction)
          valB = calculateLocalPnl(b.start_price, b.current_price || b.start_price, b.direction)
        } else if (sortField === 'ticker') {
          valA = a.ticker?.symbol || a.ticker_id
          valB = b.ticker?.symbol || b.ticker_id
        }
        if (valA === valB) return 0
        const mod = sortOrder === 'desc' ? -1 : 1
        return valA > valB ? 1 * mod : -1 * mod
      })
  }, [estimates, searchTerm, multiStatus, dateFrom, dateTo, pnlMin, pnlMax, sortField, sortOrder])

  // — Status badge ———————————————————————————————————————————————————————————
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
          <span
            style={{ color: theme.estimateStatus?.ERROR ?? theme.colors.warning }}
            title={errorMsg || 'Errore'}
            className="font-bold cursor-help border-b border-dotted"
          >
            ERROR
          </span>
        )
      default:
        return <span className="font-bold text-slate-500">{status}</span>
    }
  }

  // — Table columns ——————————————————————————————————————————————————————————
  const columns: ColumnDef<any>[] = [ // TODO: typed ColumnDef<Estimate>
    {
      header: (
        <div className="cursor-pointer flex items-center gap-1" onClick={() => toggleSort('ticker')}>
          Ticker {sortField === 'ticker' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
        </div>
      ),
      cell: (item) => (
        <div className="font-black">
          {item.ticker?.symbol || item.ticker_id}{' '}
          <span className="text-xs text-slate-500 ml-1">{item.direction}</span>
        </div>
      ),
    },
    {
      header: (
        <div className="cursor-pointer flex items-center gap-1" onClick={() => toggleSort('status')}>
          Stato {sortField === 'status' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
        </div>
      ),
      cell: (item) => renderBadge(item.status, item.error_message),
    },
    {
      header: 'Ingresso / Corrente',
      cell: (item) => (
        <div className="flex flex-col text-sm">
          <span>$ {item.start_price}</span>
          <span className="text-slate-400">$ {item.current_price || item.start_price}</span>
        </div>
      ),
    },
    {
      header: 'SL / TP',
      cell: (item) => (
        <div className="flex flex-col text-sm text-slate-500">
          <span className="text-red-500/80">$ {item.stop_loss_price}</span>
          <span className="text-green-500/80">$ {item.target_price}</span>
        </div>
      ),
    },
    {
      header: (
        <div className="cursor-pointer flex items-center gap-1" onClick={() => toggleSort('pnl')}>
          P&L % {sortField === 'pnl' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
        </div>
      ),
      cell: (item) => {
        const pnl = calculateLocalPnl(item.start_price, item.current_price || item.start_price, item.direction)
        return (
          <div className={`font-bold ${pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {pnl.toFixed(2)}%
          </div>
        )
      },
    },
    {
      header: (
        <div className="cursor-pointer flex items-center gap-1" onClick={() => toggleSort('created_at')}>
          Data {sortField === 'created_at' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
        </div>
      ),
      cell: (item) => <span className="text-sm">{format(parseISO(item.created_at), 'dd/MM/yy')}</span>,
    },
    {
      header: '',
      cell: (item) => (
        <button
          onClick={(e) => {
            e.stopPropagation()
            deleteEstimate(item.id as string)
          }}
          className="text-xs text-red-400 hover:text-red-300 px-2 py-1 rounded border border-red-800/40 hover:border-red-600/60 transition-colors"
        >
          Elimina
        </button>
      ),
    },
  ]

  // — JSX ————————————————————————————————————————————————————————————————————
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100 mt-2">
          Portafoglio Avanzato
        </h2>
      </div>

      <div className="bg-white dark:bg-slate-800 p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col gap-4">

        {/* ROW 1: Ricerca & Stato */}
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
                const values = Array.from(e.target.selectedOptions, o => o.value)
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

        {/* ROW 2: Date e P&L Range */}
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

          <button
            onClick={() => setSearchParams(new URLSearchParams())}
            className="ml-auto text-xs text-red-500 hover:text-red-700 dark:text-red-400"
          >
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

      {/* Drawer dettaglio */}
      <EstimateDetailDrawer
        estimate={selectedEstimate}
        onClose={() => setSelectedEstimate(null)}
        renderBadge={renderBadge}
      />
    </div>
  )
}