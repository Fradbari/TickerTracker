import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts'
import { usePortfolioMetrics } from '../hooks/usePortfolioMetrics'
import { useBackendStats } from '@/shared/api/queries/backendStats'

export function Dashboard() {
  const { metrics, isLoading, isError } = usePortfolioMetrics()
  const { 
    data: backendStats, 
    isLoading: isLoadingStats, 
    isError: isErrorStats 
  } = useBackendStats()

  if (isLoading) {
    return <div className="p-4 flex h-full items-center justify-center text-gray-400">Caricamento statistiche...</div>
  }

  if (isError || !metrics) {
    return <div className="p-4 flex h-full items-center justify-center text-red-500">Errore durante il caricamento</div>
  }

  const {
    total, active, wins, losses, totalPnL, roi,
    highestPercentDisplay, lowestPercentDisplay, topAi, aiChartData
  } = metrics

  const pnlColorClass = totalPnL >= 0 ? 'text-green-500' : 'text-red-500'
  const roiColorClass = roi >= 0 ? 'text-green-500' : 'text-red-500'

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      
      {/* 6 HEADER STATS */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 text-center">
        
        <div className="bg-gray-800 rounded-2xl p-4 shadow-lg text-white">
          <div className="text-xs text-gray-400 uppercase tracking-wide">Attive</div>
          <div className="text-2xl font-bold text-blue-400">{active}</div>
          <div className="text-sm text-gray-500">Totale {total}</div>
        </div>

        <div className="bg-gray-800 rounded-2xl p-4 shadow-lg text-white">
          <div className="text-xs text-gray-400 uppercase tracking-wide">P&L Totale</div>
          <div className={`text-2xl font-bold ${pnlColorClass}`}>
            {totalPnL > 0 ? '+' : ''}{totalPnL.toFixed(2)}
          </div>
        </div>

        <div className="bg-gray-800 rounded-2xl p-4 shadow-lg hover:scale-105 transition-transform text-white">
          <div className="text-xs text-gray-400 uppercase tracking-wide">ROI</div>
          <div className={`text-2xl font-bold ${roiColorClass}`}>
            {roi > 0 ? '+' : ''}{roi.toFixed(1)}%
          </div>
        </div>

        <div className="bg-gray-800 rounded-2xl p-4 shadow-lg text-white">
          <div className="text-xs text-gray-400 uppercase tracking-wide">In Profitto</div>
          <div className="text-2xl font-bold text-green-500">{wins}</div>
        </div>

        <div className="bg-gray-800 rounded-2xl p-4 shadow-lg text-white">
          <div className="text-xs text-gray-400 uppercase tracking-wide">In Perdita</div>
          <div className="text-2xl font-bold text-red-500">{losses}</div>
        </div>

        <div className="bg-gray-800 rounded-2xl p-4 shadow-lg text-white">
          <div className="text-xs text-gray-400 uppercase tracking-wide">Top AI</div>
          <div className="text-xl font-bold text-purple-400 truncate mt-1">{topAi}</div>
        </div>

      </div>

      {/* ADMIN / BACKEND STATS (TEMPORARY) */}
      <div className="bg-gray-800 rounded-2xl p-4 shadow-lg border border-indigo-500/30">
        <h3 className="text-sm text-indigo-400 font-semibold mb-3 uppercase tracking-wide">Admin: Dati Backend (Jobs)</h3>
        {isLoadingStats ? (
          <div className="text-sm text-gray-400">Loading backend check...</div>
        ) : isErrorStats || !backendStats ? (
          <div className="text-sm text-red-400">Errore check background</div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="bg-gray-900 rounded p-3">
              <div className="text-xs text-gray-400">Open Estimates (DB)</div>
              <div className="text-lg font-bold text-blue-300">{backendStats.open_estimates}</div>
            </div>
            <div className="bg-gray-900 rounded p-3">
              <div className="text-xs text-gray-400">Auto-Closed by Engine</div>
              <div className="text-lg font-bold text-purple-300">{backendStats.auto_closed_estimates}</div>
            </div>
            <div className="bg-gray-900 rounded p-3">
              <div className="text-xs text-gray-400">Synced Market Rows</div>
              <div className="text-lg font-bold text-teal-300">{backendStats.synced_market_rows}</div>
            </div>
            <div className="bg-gray-900 rounded p-3">
              <div className="text-xs text-gray-400">Cron Status</div>
              <div className="text-lg font-bold text-green-400">
                {backendStats.backend_jobs_active ? "OK" : "NOT RUNNING"}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6">
        
        {/* BarChart per performance AI */}
        <div className="bg-gray-800 rounded-2xl p-6 shadow-lg text-white">
          <h3 className="text-lg font-bold mb-4 text-gray-300">Performance per AI</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={aiChartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                <XAxis dataKey="name" stroke="#9CA3AF" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{fill: '#374151'}} 
                  contentStyle={{backgroundColor: '#1F2937', border: '1px solid #4B5563', borderRadius: '8px'}} 
                  itemStyle={{ color: '#F3F4F6' }}
                  labelStyle={{ color: '#F3F4F6', fontWeight: 'bold', marginBottom: '0.5rem' }}
                />
                <Bar dataKey="pnl" name="€" radius={[4, 4, 4, 4]}>
                  {aiChartData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.pnl >= 0 ? '#10B981' : '#EF4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  )
}
