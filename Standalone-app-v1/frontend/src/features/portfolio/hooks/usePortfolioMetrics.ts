import { useMemo, useEffect } from 'react'
import Decimal from 'decimal.js'
import { useInfiniteEstimates } from '@/shared/api/queries/estimates'
import type { Estimate } from '@/shared/types'

export function usePortfolioMetrics() {
  const { 
    data, 
    isLoading, 
    isError, 
    error,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage
  } = useInfiniteEstimates({}, 100);

  useEffect(() => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  const metrics = useMemo(() => {
    const estimates = data?.pages.flatMap(page => page.items) || [];
    
    let totalInvested = estimates.length * 100; // Simulated  per trade
    let totalPnL = 0;
    
    const active = estimates.filter((e: any) => e.status === 'OPEN').length;
    const wins = estimates.filter((e: any) => e.status === 'CLOSED_WIN').length;
    const losses = estimates.filter((e: any) => e.status === 'CLOSED_LOSS').length;

    let highestPercent: any = null;
    let lowestPercent: any = null;

    const aiStats: Record<string, { pnl: number, count: number }> = {};

    estimates.forEach((estimate: any) => {
      // AI Stats
      const ai = estimate.ai_model || 'Unknown';
      if (!aiStats[ai]) aiStats[ai] = { pnl: 0, count: 0 };
      aiStats[ai].count += 1;

      if (estimate.realized_pnl) {
        try {
          const pnlValue = new Decimal(estimate.realized_pnl).toNumber();
          totalPnL += pnlValue;
          aiStats[ai].pnl += pnlValue;
        } catch { /* ignore */ }
      }

      if (estimate.realized_pnl_percent) {
        try {
          const pnlPercentValue = new Decimal(estimate.realized_pnl_percent).toNumber();
          if (estimate.status !== 'OPEN') {
            if (!highestPercent || pnlPercentValue > highestPercent.percent) {
              highestPercent = { symbol: estimate.ticker?.symbol || estimate.ticker_id, percent: pnlPercentValue };
            }
            if (!lowestPercent || pnlPercentValue < lowestPercent.percent) {
              lowestPercent = { symbol: estimate.ticker?.symbol || estimate.ticker_id, percent: pnlPercentValue };
            }
          }
        } catch { /* ignore */ }
      }
    });

    const highestPercentDisplay = highestPercent ? `${highestPercent.symbol} ${(highestPercent.percent > 0 ? '+' : '')}${highestPercent.percent.toFixed(2)}%` : 'N/D';
    const lowestPercentDisplay = lowestPercent ? `${lowestPercent.symbol} ${(lowestPercent.percent > 0 ? '+' : '')}${lowestPercent.percent.toFixed(2)}%` : 'N/D';

    const roi = totalInvested > 0 ? (totalPnL / totalInvested) * 100 : 0;
    
    // Format charting data
    const aiChartData = Object.keys(aiStats).map(key => ({
      name: key,
      pnl: parseFloat(aiStats[key].pnl.toFixed(2))
    })).sort((a,b) => b.pnl - a.pnl);
    
    const topAi = aiChartData.length > 0 ? aiChartData[0].name : 'N/D';

    return {
      total: estimates.length,
      active,
      wins,
      losses,
      totalPnL,
      roi,
      highestPercentDisplay,
      lowestPercentDisplay,
      topAi,
      aiChartData
    }
  }, [data])

  return {
    metrics,
    isLoading,
    isError,
    error,
  }
}
