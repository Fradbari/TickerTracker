import React, { useEffect } from 'react'
import { useEstimateTaskStatus } from '../api/queries'
import { CheckCircle, Clock, AlertCircle, XCircle } from 'lucide-react'
import type { TrackedTask } from '../hooks/useInsertionTracker'
import { useQueryClient } from '@tanstack/react-query'
import { estimateKeys } from '../api'

interface TrackerBoxItemProps {
  task: TrackedTask
  onStatusUpdate: (taskId: string, status: TrackedTask['status'], estimateId?: string) => void
  onRemove: (taskId: string) => void
}

export function TrackerBoxItem({ task, onStatusUpdate, onRemove }: TrackerBoxItemProps) {
  const { data: statusData, isLoading, isError } = useEstimateTaskStatus(task.taskId)
  const qc = useQueryClient()

  // Track status changes and forward them to the parent Array state.
  useEffect(() => {
    if (statusData && statusData.status !== task.status) {
      onStatusUpdate(task.taskId, statusData.status, statusData.estimate?.id)
      if (statusData.status === 'Completed') {
        qc.invalidateQueries({ queryKey: estimateKeys.all })
      }
    }
  }, [statusData, task.status, task.taskId, onStatusUpdate, qc])

  // Icon computation
  const getIcon = () => {
    if (isLoading || task.status === 'Pending' || task.status === 'Processing') return <Clock className="w-5 h-5 text-blue-400 animate-spin" />
    if (isError || task.status === 'Failed') return <AlertCircle className="w-5 h-5 text-red-500" />
    
    switch (task.status) {
      case 'Completed': return <CheckCircle className="w-5 h-5 text-green-500" />
      default: return <Clock className="w-5 h-5 text-blue-400 animate-spin" />
    }
  }

  return (
    <div className="flex items-center justify-between p-3 border-b border-white/10 last:border-0 hover:bg-white/5 transition-colors">
      <div className="flex items-center gap-3">
        {getIcon()}
        <div className="flex flex-col text-sm">
          <div className="flex items-center gap-2">
            <span className="font-bold text-gray-100">{task.ticker}</span>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${task.direction === 'LONG' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
              {task.direction}
            </span>
          </div>
          <span className="text-gray-400 text-xs">
             {new Date(task.createdAt).toLocaleTimeString()}
          </span>
        </div>
      </div>
      
      <div className="flex items-center gap-3 text-sm">
        {task.status === 'Completed' && (
          <span className="px-2 py-1 rounded-full border border-green-500/30 text-green-400 bg-green-500/10">Completata</span>
        )}
        {task.status === 'Failed' && (
          <span className="px-2 py-1 rounded-full border border-red-500/30 text-red-400 bg-red-500/10">Fallita</span>
        )}
        {(task.status === 'Pending' || task.status === 'Processing') && (
          <span className="px-2 py-1 rounded-full border border-blue-500/30 text-blue-400 bg-blue-500/10">
            {task.status === 'Pending' ? 'In Coda' : 'Elab...'}
          </span>
        )}
        
        <button className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-red-400 transition" onClick={() => onRemove(task.taskId)} title="Rimuovi">
          <XCircle className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
