import React, { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { useQuery } from '@tanstack/react-query'
import apiClient from '../api/client'

export const LogViewerContext = React.createContext<{
  openWithTraceId: (traceId: string) => void
}>({ openWithTraceId: () => {} })

export const SystemLogViewer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [traceIdFilter, setTraceIdFilter] = useState('')

  const { data: logs = [], refetch } = useQuery({
    queryKey: ['systemLogs', traceIdFilter],
    queryFn: async () => {
      const res = await apiClient.get('/api/logs?tail=200')
      let items = res.data.data || []
      if (traceIdFilter) {
        items = items.filter((log: any) => log.trace_id === traceIdFilter || log.correlation_id === traceIdFilter)
      }
      return items
    },
    enabled: isOpen,
    refetchInterval: isOpen ? 3000 : false
  })

  // Expose function to open viewer specifically filtering by trace_id
  const openWithTraceId = (traceId: string) => {
    setTraceIdFilter(traceId)
    setIsOpen(true)
  }

  return (
    <LogViewerContext.Provider value={{ openWithTraceId }}>
      {children}
      {/* FAB - Floating Action Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 bg-gray-800 text-white rounded-full p-3 shadow-lg z-50 hover:bg-gray-700 transition"
        title="Open System Log Console"
      >
        <svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
        </svg>
      </button>

      {isOpen && createPortal(
        <div className="fixed inset-y-0 right-0 w-1/2 bg-gray-900 shadow-2xl z-[100] flex flex-col border-l border-gray-700">
          {/* Header */}
          <div className="flex justify-between items-center p-4 border-b border-gray-700 bg-gray-800">
            <div>
              <h2 className="text-white text-xl font-bold font-mono">System Logs</h2>
            </div>
            <div className="flex items-center space-x-3">
              <input 
                type="text" 
                placeholder="Filter by Trace ID" 
                value={traceIdFilter}
                onChange={e => setTraceIdFilter(e.target.value)}
                className="bg-gray-700 text-sm text-white px-3 py-1 rounded w-64 border border-gray-600 focus:outline-none"
              />
              <button 
                onClick={() => {
                  const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `system-logs-${new Date().toISOString().replace(/:/g, '-')}.json`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className="text-gray-300 hover:text-white px-2"
                title="Download JSON"
              >
                📥
              </button>
              <button 
                onClick={() => { setTraceIdFilter(''); refetch(); }}
                className="text-gray-300 hover:text-white px-2"
                title="Refresh"
              >
                🔄
              </button>
              <button 
                onClick={() => setIsOpen(false)}
                className="text-gray-300 hover:text-white rounded-full hover:bg-gray-700 p-1"
              >
                <svg fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          {/* List */}
          <div className="flex-1 overflow-auto p-4 font-mono text-sm space-y-2">
            {logs.map((log: any, idx: number) => {
              const isFrontend = log.source === 'frontend'
              const colorClass = log.level === 'error' ? 'text-red-400' 
                               : log.level === 'warning' ? 'text-yellow-400'
                               : isFrontend ? 'text-blue-300' : 'text-green-300'
              
              return (
                <div key={idx} className={`bg-gray-800 p-3 rounded ${colorClass} border-l-4 border-current`}>
                  <div className="flex flex-wrap items-center gap-2 mb-1 text-xs text-gray-400">
                    <span className="uppercase font-bold">[{log.level}]</span>
                    {log.timestamp && <span>{new Date(log.timestamp).toLocaleString()}</span>}
                    <span className="bg-gray-700 px-1 rounded">{log.source || 'backend'}</span>
                    {(log.trace_id || log.correlation_id) && (
                      <span title="Trace / Correlation ID">🏷️ {(log.trace_id || log.correlation_id).substring(0, 8)}...</span>
                    )}
                  </div>
                  <div className="whitespace-pre-wrap">{log.event || log.message}</div>
                  {log.error && <div className="text-red-500 mt-1 whitespace-pre-wrap text-xs">{log.error}</div>}
                </div>
              )
            })}
            {logs.length === 0 && <div className="text-gray-500 text-center mt-10">No logs found.</div>}
          </div>
        </div>,
        document.body
      )}
    </LogViewerContext.Provider>
  )
}
