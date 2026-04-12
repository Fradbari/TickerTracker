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
    
    const totalInvested = estimates.length * 100; // Simulated € per trade
    let totalPnL = 0;
    
    const active = estimates.filter((e: any) => e.status === 'OPEN').length;
    const wins = estimates.filter((e: any) => e.realized_pnl_percent && new Decimal(e.realized_pnl_percent).toNumber() > 0).length;
    const losses = estimates.filter((e: any) => e.realized_pnl_percent && new Decimal(e.realized_pnl_percent).toNumber() < 0).length;

    let highestPercent: any = null;
    let lowestPercent: any = null;

    const aiStats: Record<string, { pnl: number, count: number }> = {};
    const aiDetailedStats: Record<string, { 
      total: number; 
      active: number; 
      wins: number; 
      losses: number; 
      totalPnL: number; 
      winRate: number; 
      rawEstimates: any[];
    }> = {};

    estimates.forEach((estimate: any) => {
      const ai = estimate.ai_model || 'Unknown';
      if (!aiStats[ai]) aiStats[ai] = { pnl: 0, count: 0 };
      if (!aiDetailedStats[ai]) aiDetailedStats[ai] = { total: 0, active: 0, wins: 0, losses: 0, totalPnL: 0, winRate: 0, rawEstimates: [] };
      
      aiStats[ai].count += 1;
      aiDetailedStats[ai].total += 1;
      aiDetailedStats[ai].rawEstimates.push(estimate);

      if (estimate.status === 'OPEN') {
        aiDetailedStats[ai].active += 1;
      } else if (estimate.realized_pnl_percent && new Decimal(estimate.realized_pnl_percent).toNumber() > 0) {
        aiDetailedStats[ai].wins += 1;
      } else if (estimate.realized_pnl_percent && new Decimal(estimate.realized_pnl_percent).toNumber() < 0) {
        aiDetailedStats[ai].losses += 1;
      }

      if (estimate.realized_pnl) {
        try {
          const pnlValue = new Decimal(estimate.realized_pnl).toNumber();
          totalPnL += pnlValue;
          aiStats[ai].pnl += pnlValue;
          aiDetailedStats[ai].totalPnL += pnlValue;
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

    Object.keys(aiDetailedStats).forEach(key => {
      const stats = aiDetailedStats[key];
      const finished = stats.wins + stats.losses;
      stats.winRate = finished > 0 ? (stats.wins / finished) * 100 : 0;
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
      aiChartData,
      aiDetailedStats
    }
  }, [data])

  return {
    metrics,
    isLoading,
    isError,
    error,
  }
}
