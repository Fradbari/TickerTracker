import React from 'react'
import { usePortfolioMetrics } from '../hooks/usePortfolioMetrics'
import { KpiCard } from '@/shared/components/KpiCard'
import { AiPerformanceChart } from './AiPerformanceChart'
import { 
  Activity, 
  TrendingUp, 
  Target, 
  ThumbsUp, 
  ThumbsDown, 
  Award 
} from 'lucide-react'

export function Dashboard() {
  const { metrics, isLoading, isError } = usePortfolioMetrics()

  if (isError) {
    return <div className="p-4 flex h-full items-center justify-center text-[var(--danger)]">Errore durante il caricamento</div>
  }

  const skSkeletons = Array.from({ length: 6 }).map((_, i) => (
    <KpiCard key={i} title="Caricamento..." value="-" isLoading={true} />
  ))

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold tracking-tight text-[var(--foreground)]">Overview Performance</h2>

      {/* KPI STATS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {isLoading || !metrics ? skSkeletons : (
          <>
            <KpiCard
              title="Attive"
              value={metrics.active}
              icon={<Activity />}
            />
            <KpiCard
              title="P&L Totale"
              value={`${metrics.totalPnL > 0 ? '+' : ''}${metrics.totalPnL.toFixed(2)}€`}
              trend={{ isPositive: metrics.totalPnL >= 0, value: 'Totale' }}
              icon={<TrendingUp />}
            />
            <KpiCard
              title="ROI"
              value={`${metrics.roi > 0 ? '+' : ''}${metrics.roi.toFixed(1)}%`}
              trend={{ isPositive: metrics.roi >= 0, value: 'Media' }}
              icon={<Target />}
            />
            <KpiCard
              title="In Profitto"
              value={metrics.wins}
              icon={<ThumbsUp className="text-[var(--success)]" />}
            />
            <KpiCard
              title="In Perdita"
              value={metrics.losses}
              icon={<ThumbsDown className="text-[var(--danger)]" />}
            />
            <KpiCard
              title="Top AI"
              value={metrics.topAi}
              icon={<Award className="text-purple-500" />}
            />
          </>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6">
        <AiPerformanceChart 
          data={isLoading ? [] : (metrics?.aiChartData || [])} 
          isLoading={isLoading} 
        />
      </div>
    </div>
  )
}
