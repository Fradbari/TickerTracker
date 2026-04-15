
import apiClient from './client'

export interface LogPayload {
  level: 'info' | 'warning' | 'error' | 'debug'
  message: string
  trace_id?: string
  meta?: Record<string, any>
}

let batch: LogPayload[] = []
let timeoutId: any = null

function sendBatch() {
  if (batch.length === 0) return
  const logsToSend = [...batch]
  batch = []
  
  // We send them individually or we could send them as a batch if endpoint supports it
  // But backend endpoint accepts a single log object right now.
  logsToSend.forEach((log) => {
    // Send fire and forget
    apiClient.post('/api/logs/frontend', log).catch(() => {})
  })
}

export function logToBackend(payload: LogPayload) {
  batch.push(payload)
  if (!timeoutId) {
    timeoutId = setTimeout(() => {
      sendBatch()
      timeoutId = null
    }, 1000)
  }
}

