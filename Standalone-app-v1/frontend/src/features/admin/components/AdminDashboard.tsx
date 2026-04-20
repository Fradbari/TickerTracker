import React from 'react'
import { useBackendStats } from '@/shared/api/queries/backendStats'
import { KpiCard } from '@/shared/components/KpiCard'
import { Database, Settings, RefreshCw, Power } from 'lucide-react'
import { AdminSettings, FinnhubSettings } from './AdminSettings'
import { SystemStatusCards } from './SystemStatusCards'

export function AdminDashboard() {
  const { data: backendStats, isLoading, isError } = useBackendStats()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Admin Console</h2>
      </div>

      <div className="bg-[var(--card)] rounded-2xl p-6 shadow-sm border border-[var(--border)]">
        <h3 className="text-sm font-semibold mb-4 uppercase tracking-wide flex items-center gap-2 text-indigo-500">
          <Settings size={16} /> Backend System Status
        </h3>
        
        {isError || (!isLoading && !backendStats) ? (
          <div className="text-red-500 p-4 bg-red-100 dark:bg-red-900/20 rounded-md">
            Errore di connessione o controlli temporaneamente disabilitati.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard
              title="Open Estimates"
              value={backendStats?.open_estimates ?? 0}
              icon={<Database />}
              isLoading={isLoading}
              description="Mostra il numero di stime attualmente monitorate dal sistema ed attive nel db in tempo reale."
            />
            <KpiCard
              title="Auto-Closed Engine"
              value={backendStats?.auto_closed_estimates ?? 0}
              icon={<RefreshCw />}
              isLoading={isLoading}
              description="Indica quante stime sono state chiuse o controllate automaticamente dall'elaboratore dei prezzi (motore di resolving)."
            />
            <KpiCard
              title="Market Sync"
              value={backendStats?.synced_market_rows ?? 0}
              icon={<Database />}
              isLoading={isLoading}
              description="Quantità di dati di mercato grezzi scaricati e inseriti nello storage di sistema."
            />
            <KpiCard
              title="Cron System"
              value={backendStats?.backend_jobs_active ? "ACTIVE" : "HALTED"}
              icon={<Power />}
              isLoading={isLoading}
              description="Status del cron job in esecuzione. ACTIVE = C'è sincronizzazione e automazione oraria, in tempo reale."
            />
          </div>
        )}
      </div>
      
      <SystemStatusCards />

      <AdminSettings />
      <FinnhubSettings />
      <FinnhubSettings />
    </div>
  )
}
