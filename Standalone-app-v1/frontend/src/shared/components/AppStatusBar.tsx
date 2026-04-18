import React from 'react'
import { Activity, Database, Cloud, RefreshCw } from 'lucide-react'

// TODO: Nel prossimo task i props proverranno direttamente dal context del backend
export const AppStatusBar: React.FC = () => {
  return (
    <div className="app-status-bar fixed bottom-0 left-0 right-0 h-8 bg-[var(--card)] border-t border-[var(--border)] flex items-center px-4 text-xs font-medium text-slate-500 dark:text-slate-400 justify-between">
      <div className="flex space-x-6 items-center">
        {/* Backend Polling Status */}
        <div className="flex items-center space-x-2 group relative">
          <Activity size={14} className="text-green-500 animate-pulse" />
          <span className="hidden md:inline">API: Healthy</span>
          <div className="absolute bottom-10 left-0 hidden group-hover:block bg-[var(--background)] border border-[var(--border)] p-2 rounded shadow-lg text-[var(--foreground)] whitespace-nowrap">
            Polling Yahoo: Attivo (prox: 14s)
          </div>
        </div>

        {/* Database Status */}
        <div className="flex items-center space-x-2">
          <Database size={14} className="text-green-500" />
          <span className="hidden md:inline">PostgreSQL: Connesso</span>
        </div>
      </div>

      <div className="flex space-x-6 items-center">
        {/* GDrive Sync Status */}
        <div className="flex items-center space-x-2">
          <Cloud size={14} className="text-amber-500" />
          <span className="hidden md:inline">GDrive: Non configurato</span>
        </div>
        <div className="flex items-center space-x-2 cursor-pointer hover:text-green-500 transition-colors">
          <RefreshCw size={12} />
          <span className="hidden md:inline">Sync Now</span>
        </div>
      </div>
    </div>
  )
}
