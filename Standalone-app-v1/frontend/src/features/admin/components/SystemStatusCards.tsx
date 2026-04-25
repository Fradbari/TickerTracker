import React from 'react'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/shared/api/client'
import { Activity, Clock, Globe } from 'lucide-react'
import { useEstimateDefaults } from './AdminSettings'

interface HealthComponent {
  name: string
  status: string
  latency_ms: number
  message: string
}

interface HealthResponse {
  status: string
  version: string
  uptime_seconds: number
  ready: boolean
  components: HealthComponent[]
}

const fetchHealth = async (): Promise<HealthResponse> => {
  const res = await apiClient.get('/api/health')
  return res.data
}

export const SystemStatusCards: React.FC = () => {
  const defaults = useEstimateDefaults()
  const { data: health, isLoading, isError } = useQuery({
    queryKey: ['system-health'],
    queryFn: fetchHealth,
    refetchInterval: (defaults.refreshInterval || 30) * 1000,
  })

  if (isLoading) {
    return <div className="text-slate-500 animate-pulse text-sm">Caricamento stato di sistema...</div>
  }

  if (isError || !health) {
    return <div className="text-red-500 text-sm">Errore nel recupero dello stato di sistema.</div>
  }

  const components = health.components || []
  const dbStatus = components.find(c => c.name === 'database')
  const redisStatus = components.find(c => c.name === 'redis')
  const yahooStatus = components.find(c => c.name === 'yahoo_finance')
  const gdriveStatus = components.find(c => c.name === 'google_drive')

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'HEALTHY': return 'text-green-500 bg-green-100 dark:bg-green-900/30'
      case 'DEGRADED': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30'
      case 'UNHEALTHY': return 'text-red-500 bg-red-100 dark:bg-red-900/30'
      default: return 'text-slate-500 bg-slate-100 dark:bg-slate-800'
    }
  }

  const renderStatusBadge = (status?: string) => {
    if (!status) return <span className="text-xs px-2 py-1 rounded bg-slate-100 text-slate-500">SCONOSCIUTO</span>
    return (
      <span className={`text-xs font-bold px-2 py-1 rounded ${getStatusColor(status)}`}>
        {status}
      </span>
    )
  }

  return (
    <div className="bg-[var(--card)] rounded-2xl p-6 shadow-sm border border-[var(--border)] mt-6">
      <h3 className="text-sm font-semibold mb-4 uppercase tracking-wide flex items-center gap-2 text-indigo-500">
        <Activity size={16} /> System Health & Connections
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Backend / Cron */}
        <div className="flex flex-col p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50" title="Il sistema in background verifica i Target/Stop loss ogni minuto e sincronizza lo storico (60gg) alle 23:00 UTC.">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 font-medium">
              <Clock size={18} className="text-blue-500" />
              Core & Cron System
            </div>
            {renderStatusBadge(health.status)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-2">
            Dettagli: DB {dbStatus?.status || 'N/A'}, Redis {redisStatus?.status || 'N/A'}<br/>
            Uptime: {Math.floor(health.uptime_seconds / 3600)}h {Math.floor((health.uptime_seconds % 3600) / 60)}m
          </div>
        </div>

        {/* Yahoo Finance */}
        <div className="flex flex-col p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50" title="Verifica la raggiungibilit� degli endpoint Yahoo. Fornisce prezzi correnti (ritardo 15m) e dati storici.">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 font-medium">
              <Globe size={18} className="text-purple-500" />
              Yahoo Finance API
            </div>
            {renderStatusBadge(yahooStatus?.status)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-2">
            Ping Latency: {yahooStatus?.latency_ms ? `${yahooStatus.latency_ms}ms` : 'N/A'}<br/>
            State: {yahooStatus?.status === 'HEALTHY' ? 'Connesso' : 'Disconnesso / Lento'}
          </div>
        </div>

        {/* Google Drive */}
        <div className="flex flex-col p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50" title="Verifica accesso al folder di backup configurato via variabile ambiente.">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 font-medium">
              <Globe size={18} className="text-emerald-500" />
              Google Drive
            </div>
            {renderStatusBadge(gdriveStatus?.status)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-2">
            Ping Latency: {gdriveStatus?.latency_ms ? `${gdriveStatus.latency_ms}ms` : 'N/A'}<br/>
            State: {gdriveStatus?.status === 'HEALTHY' ? 'Configurato' : 'Non configurato / Degradato'}
          </div>
        </div>
        
      </div>
    </div>
  )
}
