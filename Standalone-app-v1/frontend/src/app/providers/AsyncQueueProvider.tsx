import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { v4 as uuidv4 } from 'uuid'

export type QueueStatus = 'PENDING' | 'SUCCESS' | 'ERROR'

export interface QueueItem {
  id: string
  ticker: string
  direction: 'LONG' | 'SHORT'
  status: QueueStatus
  message?: string
  progress?: number // 0 to 100
  timestamp: number
  estimateId?: string
}

interface AsyncQueueContextType {
  queue: QueueItem[]
  addItem: (item: Omit<QueueItem, 'id' | 'timestamp' | 'status' | 'progress'>) => string
  updateItem: (id: string, updates: Partial<QueueItem>) => void
  removeItem: (id: string) => void
  clearQueue: () => void
}

const AsyncQueueContext = createContext<AsyncQueueContextType | undefined>(undefined)

export const useAsyncQueue = () => {
  const context = useContext(AsyncQueueContext)
  if (!context) {
    throw new Error('useAsyncQueue must be used within an AsyncQueueProvider')
  }
  return context
}

export const AsyncQueueProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [queue, setQueue] = useState<QueueItem[]>([])

  const addItem = useCallback((item: Omit<QueueItem, 'id' | 'timestamp' | 'status' | 'progress'>) => {
    const newItem: QueueItem = {
      ...item,
      id: uuidv4(),
      timestamp: Date.now(),
      status: 'PENDING',
      progress: 10
    }
    
    setQueue(prev => {
      const newQueue = [newItem, ...prev]
      // Keep only last 10 elements to prevent uncontrolled growth
      return newQueue.slice(0, 10)
    })
    
    return newItem.id
  }, [])

  const updateItem = useCallback((id: string, updates: Partial<QueueItem>) => {
    setQueue(prev => prev.map(item => item.id === id ? { ...item, ...updates } : item))
  }, [])

  const removeItem = useCallback((id: string) => {
    setQueue(prev => prev.filter(item => item.id !== id))
  }, [])

  const clearQueue = useCallback(() => {
    setQueue([])
  }, [])

  return (
    <AsyncQueueContext.Provider value={{ queue, addItem, updateItem, removeItem, clearQueue }}>
      {children}
    </AsyncQueueContext.Provider>
  )
}
