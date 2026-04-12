import React from 'react'
import { TrackerBoxItem } from './TrackerBoxItem'
import { Activity } from 'lucide-react'
import { useInsertionTracker } from '../hooks/useInsertionTracker'

export function InsertionTrackerBox() {
  const { tasks, updateTaskStatus, removeTask } = useInsertionTracker()

  if (tasks.length === 0) {
    return null
  }

  return (
    <div className="bg-[#12141c] border border-white/10 rounded-xl overflow-hidden shadow-2xl mt-8">
      <div className="bg-white/5 px-4 py-3 border-b border-white/10 flex items-center justify-between">
        <h3 className="font-semibold text-gray-100 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-400" />
          Tracker Inserimenti (ultimi 10)
        </h3>
        <span className="bg-white/10 text-gray-300 px-2 py-0.5 rounded-full text-xs">
          {tasks.length} Task
        </span>
      </div>
      <div className="flex flex-col max-h-[400px] overflow-y-auto">
        {tasks.map(task => (
          <TrackerBoxItem 
            key={task.taskId} 
            task={task} 
            onStatusUpdate={updateTaskStatus}
            onRemove={removeTask}
          />
        ))}
      </div>
    </div>
  )
}
