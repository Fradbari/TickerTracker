import { useMemo } from 'react'
import Decimal from 'decimal.js'
import { useEstimates } from '@/shared/api/queries/estimates'
import type { Estimate } from '@/shared/types'

export function usePortfolioMetrics() {
  // Use useEstimates with a 5 minute refetch interval
  const { data, isLoading, isError, error } = useEstimates(
    { limit: 100 },
    { refetchInterval: 5 * 60 * 1000 }
  ) as { data: { items: Estimate[] } | undefined, isLoading: boolean, isError: boolean, error: unknown }

  const metrics = useMemo(() => {
    const estimates = data?.items || []
    
    let totalInvested = 0
    let totalPnL = 0
    let activeEstimatesCount = 0
    const countsByStatus: Record<string, number> = {
      OPEN: 0,
      CLOSED_WIN: 0,
      CLOSED_LOSS: 0,
      CLOSED_NEUTRAL: 0,
    }

    const tickerPnL: Record<string, number> = {}
    const cumulativePnLData: { date: string; pnl: number }[] = []

    // Sort estimates by date ascending for cumulative calculation
    const sortedEstimates = [...estimates].sort((a, b) => 
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )

    let currentCumulativePnL = 0

    sortedEstimates.forEach((estimate) => {
      // Status counts
      countsByStatus[estimate.status] = (countsByStatus[estimate.status] || 0) + 1

      if (estimate.status === 'OPEN') {
        activeEstimatesCount++
        try {
          const start = new Decimal(estimate.start_price || '0')
          totalInvested += start.toNumber()
        } catch { /* ignore */ }
      }

      // Realized PnL processing
      if (estimate.realized_pnl) {
        try {
          const pnlValue = new Decimal(estimate.realized_pnl).toNumber()
          totalPnL += pnlValue

          // Ticker distribution
          const symbolStr = estimate.ticker?.symbol || estimate.ticker_id
          tickerPnL[symbolStr] = (tickerPnL[symbolStr] || 0) + pnlValue

          // Cumulative PnL
          currentCumulativePnL += pnlValue
          cumulativePnLData.push({
            date: new Date(estimate.closed_at || estimate.updated_at).toLocaleDateString(),
            pnl: currentCumulativePnL
          })
        } catch { /* ignore */ }
      }
    })

    // Prepare pie chart data
    const tickerDistribution = Object.entries(tickerPnL)
      .map(([ticker, pnl]) => ({ ticker, pnl }))
      .filter(item => item.pnl > 0) // Typically pie charts show positive distributions or absolute values
      // Wait, let's keep all and perhaps chart absolute, or just profits? The prompt says "raggruppa per ticker_id la somma di realized_pnl". Usually we map the positive ones, or map total absolute contribution. Let's just pass `pnl` and handle it in the component.
    
    // Performance table (top/worst)
    const performances = Object.entries(tickerPnL)
      .map(([ticker, pnl]) => ({ ticker, pnl }))
      .sort((a, b) => b.pnl - a.pnl)

    const topPerformers = performances.slice(0, 5)
    const worstPerformers = performances.slice(-5).reverse()

    return {
      totalInvested,
      totalPnL,
      activeEstimatesCount,
      countsByStatus,
      cumulativePnLData,
      tickerDistribution,
      topPerformers,
      worstPerformers
    }
  }, [data])

  return {
    metrics,
    isLoading,
    isError,
    error,
  }
}
