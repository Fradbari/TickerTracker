import { useState, useCallback, useEffect } from 'react'

export interface TrackedTask {
  taskId: string
  ticker: string
  direction: 'LONG' | 'SHORT'
  status: 'Pending' | 'Processing' | 'Completed' | 'Failed'
  createdAt: string
  estimateId?: string
}

const STORAGE_KEY = 'Tracker_Tasks'

export function useInsertionTracker() {
  const [tasks, setTasks] = useState<TrackedTask[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) return JSON.parse(stored)
    } catch {
      // ignore
    }
    return []
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks))
  }, [tasks])

  const addTask = useCallback((task: TrackedTask) => {
    setTasks(prev => {
      const newTasks = [task, ...prev].slice(0, 10) // Keep last 10
      return newTasks
    })
  }, [])

  const updateTaskStatus = useCallback((taskId: string, status: TrackedTask['status'], estimateId?: string) => {
    setTasks(prev => prev.map(t => 
      t.taskId === taskId ? { ...t, status, estimateId: estimateId || t.estimateId } : t
    ))
  }, [])

  const removeTask = useCallback((taskId: string) => {
    setTasks(prev => prev.filter(t => t.taskId !== taskId))
  }, [])

  return { tasks, addTask, updateTaskStatus, removeTask }
}
