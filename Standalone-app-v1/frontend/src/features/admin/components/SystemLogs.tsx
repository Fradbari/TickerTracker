// FILE: frontend/src/features/admin/components/SystemLogs.tsx

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import apiClient from '../../../shared/api/client'

type LogLevel = 'info' | 'warn' | 'warning' | 'error' | 'action' | 'unknown'
type LogSource = 'all' | 'frontend' | 'backend' | 'system'

interface LogEntry {
  level: LogLevel
  message?: string
  event?: string
  source?: string
  component?: string
  timestamp?: string
  user_id?: string
  error?: string
  [key: string]: unknown
}

const LEVEL_COLORS: Record<string, string> = {
  error:   'text-red-400 border-red-500',
  warn:    'text-yellow-400 border-yellow-500',
  warning: 'text-yellow-400 border-yellow-500',
  info:    'text-green-300 border-green-600',
  action:  'text-blue-300 border-blue-500',
  unknown: 'text-gray-400 border-gray-600',
}

export function SystemLogs() {
  const [sourceFilter, setSourceFilter] = useState<LogSource>('all')
  const [search, setSearch] = useState('')
  const [tail, setTail] = useState(200)

  const { data: logs = [], isFetching, refetch } = useQuery<LogEntry[]>({
    queryKey: ['logs'],
    queryFn: async () => {
      const res = await apiClient.get(`/api/logs?tail=${tail}`)
      return (res.data?.data ?? []) as LogEntry[]
    },
    refetchInterval: 10_000,
  })

  // Filtro client-side: non causa refetch al cambio dropdown
  const filteredLogs = logs.filter((log) => {
    if (sourceFilter !== 'all' && log.source !== sourceFilter) return false
    if (search) {
      const text = JSON.stringify(log).toLowerCase()
      if (!text.includes(search.toLowerCase())) return false
    }
    return true
  })

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(filteredLogs, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `logs-${sourceFilter}-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white rounded-lg overflow-hidden">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3 p-4 border-b border-gray-700 bg-gray-800">
        <h2 className="text-lg font-bold font-mono mr-auto">System Logs</h2>

        {/* Source filter */}
        <select
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value as LogSource)}
          className="bg-gray-700 text-sm text-white px-3 py-1.5 rounded border border-gray-600 focus:outline-none"
        >
          <option value="all">All sources</option>
          <option value="frontend">Frontend</option>
          <option value="backend">Backend</option>
          <option value="system">System</option>
        </select>

        {/* Text search */}
        <input
          type="text"
          placeholder="Search…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-gray-700 text-sm text-white px-3 py-1.5 rounded border border-gray-600 focus:outline-none w-48"
        />

        {/* Tail selector */}
        <select
          value={tail}
          onChange={(e) => { setTail(Number(e.target.value)); void refetch() }}
          className="bg-gray-700 text-sm text-white px-3 py-1.5 rounded border border-gray-600 focus:outline-none"
        >
          <option value={50}>Last 50</option>
          <option value={200}>Last 200</option>
          <option value={500}>Last 500</option>
        </select>

        <button
          onClick={handleDownload}
          className="text-gray-300 hover:text-white px-2 py-1.5 rounded hover:bg-gray-700 text-sm"
          title="Download JSON"
        >
          📥
        </button>

        <button
          onClick={() => void refetch()}
          disabled={isFetching}
          className="text-gray-300 hover:text-white px-2 py-1.5 rounded hover:bg-gray-700 text-sm disabled:opacity-50"
          title="Refresh"
        >
          {isFetching ? '⏳' : '🔄'}
        </button>

        <span className="text-xs text-gray-400 font-mono">
          {filteredLogs.length} / {logs.length}
        </span>
      </div>

      {/* Log list */}
      <div className="flex-1 overflow-auto p-4 font-mono text-sm space-y-2">
        {filteredLogs.map((log, idx) => {
          const colorClass = LEVEL_COLORS[log.level] ?? LEVEL_COLORS.unknown
          const text = log.event ?? log.message ?? '(no message)'
          return (
            <div
              key={idx}
              className={`bg-gray-800 p-3 rounded border-l-4 ${colorClass}`}
            >
              <div className="flex flex-wrap items-center gap-2 mb-1 text-xs text-gray-400">
                <span className="uppercase font-bold">[{log.level}]</span>
                {log.timestamp && (
                  <span>{new Date(log.timestamp).toLocaleString()}</span>
                )}
                <span className="bg-gray-700 px-1 rounded">
                  {log.source ?? 'backend'}
                </span>
                {log.component && (
                  <span className="bg-blue-900 px-1 rounded text-blue-300">
                    {log.component}
                  </span>
                )}
              </div>
              <div className="whitespace-pre-wrap">{text}</div>
              {log.error && (
                <div className="text-red-500 mt-1 whitespace-pre-wrap text-xs">
                  {log.error}
                </div>
              )}
            </div>
          )
        })}
        {filteredLogs.length === 0 && (
          <div className="text-gray-500 text-center mt-10">
            {logs.length === 0 ? 'No logs available.' : `No logs matching "${sourceFilter}" source.`}
          </div>
        )}
      </div>
    </div>
  )
}