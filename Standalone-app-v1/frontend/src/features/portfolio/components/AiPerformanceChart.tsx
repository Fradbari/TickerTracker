import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts'
import { Skeleton } from '@/shared/components/Skeleton'

interface AiPerformanceChartProps {
  data: Array<{ name: string; pnl: number }>;
  isLoading?: boolean;
}

export function AiPerformanceChart({ data, isLoading }: AiPerformanceChartProps) {
  if (isLoading) {
    return (
      <div className="bg-[var(--card)] rounded-2xl p-6 shadow-sm border border-[var(--border)]">
        <h3 className="text-lg font-bold mb-4 text-[var(--foreground)]">Performance per AI</h3>
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="bg-[var(--card)] rounded-2xl p-6 shadow-sm border border-[var(--border)]">
      <h3 className="text-lg font-bold mb-4 text-[var(--foreground)]">Performance per AI</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
            <XAxis dataKey="name" stroke="var(--foreground)" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip 
              cursor={{ fill: 'var(--border)', opacity: 0.4 }} 
              contentStyle={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px' }} 
              itemStyle={{ color: 'var(--foreground)' }}
              labelStyle={{ color: 'var(--foreground)', fontWeight: 'bold', marginBottom: '0.5rem' }}
            />
            <Bar dataKey="pnl" name="€" radius={[4, 4, 4, 4]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.pnl >= 0 ? 'var(--success)' : 'var(--danger)'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
