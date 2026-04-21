import React, { useEffect, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { X, Calendar as CalendarIcon, Briefcase, TrendingUp } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts'
import apiClient from '@/shared/api/client'

interface EstimateDetailDrawerProps {
  estimate: any | null;
  onClose: () => void;
  renderBadge: (status: string, error?: string) => React.ReactNode;
}

export function EstimateDetailDrawer({ estimate, onClose, renderBadge }: EstimateDetailDrawerProps) {
  if (!estimate) return null;

  const symbol = estimate.ticker?.symbol || estimate.ticker_id || ''

  const { data: yahooData, isLoading: isLoadingYahoo, error: yahooError } = useQuery({
    queryKey: ['yahoo-quote-summary', symbol],
    queryFn: async () => {
      // Proxy rule /v10 was added to vite config
      const res = await fetch(`/v10/finance/quoteSummary/?modules=summaryProfile,financialData,recommendationTrend,calendarEvents,earningsTrend,defaultKeyStatistics`)
      if (!res.ok) throw new Error('Yahoo Finance fetch failed')
      const json = await res.json()
      return json.quoteSummary?.result?.[0] || null
    },
    staleTime: 1000 * 60 * 60 * 24, // 24h
    enabled: !!symbol
  })

  // Mocking candles from DB (usually it comes from estimate.candles or via a separate DB fetch)
  // Reusing existing candles from the estimate object if any
  const sparklineData = useMemo(() => {
     if (estimate.candles && Array.isArray(estimate.candles)) {
         return estimate.candles.map((c: any) => ({
           date: new Date(c.timestamp).toLocaleDateString(),
           close: parseFloat(c.close)
         }))
     }
     
     // Dummy if no candles on the estimate for visual testing of the UI
     return [
       { date: 'D-5', close: parseFloat(estimate.start_price) * 0.98 },
       { date: 'D-4', close: parseFloat(estimate.start_price) * 0.99 },
       { date: 'D-3', close: parseFloat(estimate.start_price) * 1.01 },
       { date: 'D-2', close: parseFloat(estimate.start_price) * 1.02 },
       { date: 'D-1', close: parseFloat(estimate.start_price) * 1.05 },
       { date: 'Corrente', close: parseFloat(estimate.current_price || estimate.start_price) }
     ]
  }, [estimate])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/50 backdrop-blur-sm transition-opacity">
      <div className="bg-white dark:bg-slate-800 w-full max-w-xl h-full overflow-y-auto shadow-2xl flex flex-col translate-x-0 transition-transform">
        
        {/* Header */}
        <div className="sticky top-0 bg-white/90 dark:bg-slate-800/90 backdrop-blur-md px-6 py-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center z-10">
          <h3 className="text-lg font-bold flex items-center gap-2">
            <span className="text-2xl font-black text-slate-900 dark:text-white">{symbol}</span>
            <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-100 dark:bg-slate-700">
              {estimate.direction}
            </span>
            <span className="ml-2 text-sm">{renderBadge(estimate.status, estimate.error_message)}</span>
          </h3>
          <button 
            onClick={onClose} 
            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
          >
            <X className="w-6 h-6 text-slate-500" />
          </button>
        </div>
        
        <div className="p-6 space-y-8 flex-1">
          {/* Estimate Basic Details */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700/50">
              <div className="text-xs text-slate-500 mb-1">Prezzo Iniziale</div>
              <div className="font-mono font-bold">$ {estimate.start_price}</div>
            </div>
            <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700/50">
              <div className="text-xs text-slate-500 mb-1">Prezzo Target</div>
              <div className="font-mono font-bold text-green-600">$ {estimate.target_price}</div>
            </div>
            <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700/50">
              <div className="text-xs text-slate-500 mb-1">Stop Loss</div>
              <div className="font-mono font-bold text-red-600">$ {estimate.stop_loss_price}</div>
            </div>
            <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-700/50">
              <div className="text-xs text-slate-500 mb-1">Corrente</div>
              <div className="font-mono font-bold text-slate-600 dark:text-slate-300">$ {estimate.current_price || estimate.start_price}</div>
            </div>
          </div>

          {/* Sparkline from DB */}
          <div>
             <h4 className="text-sm font-bold text-slate-500 mb-3 flex items-center gap-2 uppercase tracking-wide"><TrendingUp className="w-4 h-4"/> Andamento Stimato</h4>
             <div className="h-32 w-full">
               <ResponsiveContainer width="100%" height="100%">
                 <AreaChart data={sparklineData}>
                   <defs>
                     <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                       <stop offset="5%" stopColor={estimate.direction === 'LONG' ? '#22c55e' : '#eab308'} stopOpacity={0.3}/>
                       <stop offset="95%" stopColor={estimate.direction === 'LONG' ? '#22c55e' : '#eab308'} stopOpacity={0}/>
                     </linearGradient>
                   </defs>
                   <RechartsTooltip 
                     contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }}
                     labelStyle={{ color: '#94a3b8' }}
                   />
                   <Area type="monotone" dataKey="close" stroke={estimate.direction === 'LONG' ? '#22c55e' : '#eab308'} fillOpacity={1} fill="url(#colorClose)" />
                 </AreaChart>
               </ResponsiveContainer>
             </div>
          </div>

          {/* Yahoo Details */}
          <div>
            <h4 className="text-lg font-bold text-slate-800 dark:text-slate-200 mb-4 border-b border-slate-200 dark:border-slate-700 pb-2">Yahoo Finance Insights</h4>
            {isLoadingYahoo ? (
              <div className="text-sm text-slate-500 animate-pulse">Recupero dati mercato...</div>
            ) : yahooError ? (
              <div className="text-sm text-red-500 bg-red-50 p-3 rounded">Impossibile ottenere i dati di Yahoo Finance.</div>
            ) : yahooData ? (
              <div className="space-y-6">
                
                {/* OHLC + Volume + Forward */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                   <div className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded border border-slate-100 dark:border-slate-800">
                     <div className="text-slate-500 text-xs uppercase mb-1">Dati OHLC</div>
                     <p>P.Corrente: <span className="font-mono font-bold">$ {yahooData.financialData?.currentPrice?.fmt || '-'}</span></p>
                     <p>Open: <span className="font-mono">$ {yahooData.financialData?.regularMarketOpen?.fmt || '-'}</span></p>
                     <p>High: <span className="font-mono">$ {yahooData.financialData?.regularMarketDayHigh?.fmt || '-'}</span></p>
                     <p>Low:  <span className="font-mono">$ {yahooData.financialData?.regularMarketDayLow?.fmt || '-'}</span></p>
                     <p>Volume: <span className="font-mono">{yahooData.financialData?.volume?.fmt || '-'}</span></p>
                   </div>
                   
                   <div className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded border border-slate-100 dark:border-slate-800">
                     <div className="text-slate-500 text-xs uppercase mb-1">Performance Aziendale</div>
                     <p>EPS Trailing: <span className="font-mono">{yahooData.defaultKeyStatistics?.trailingEps?.fmt || '-'}</span></p>
                     <p>EPS Forward: <span className="font-mono">{yahooData.defaultKeyStatistics?.forwardEps?.fmt || '-'}</span></p>
                     <p>PE Forward: <span className="font-mono">{yahooData.defaultKeyStatistics?.forwardPE?.fmt || '-'}</span></p>
                     <p>Analisti Target: <span className="font-mono font-bold">$ {yahooData.financialData?.targetMeanPrice?.fmt || '-'}</span></p>
                   </div>
                </div>

                {/* Recommendations */}
                {yahooData.recommendationTrend?.trend?.[0] && (
                  <div>
                    <h5 className="text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2"><Briefcase className="w-4 h-4"/> Consensus Analisti (Mese Corrente)</h5>
                    <div className="flex text-xs text-center rounded overflow-hidden">
                       <div className="bg-green-600 text-white flex-1 py-2">Strong Buy: {yahooData.recommendationTrend.trend[0].strongBuy}</div>
                       <div className="bg-green-400 text-white flex-1 py-2">Buy: {yahooData.recommendationTrend.trend[0].buy}</div>
                       <div className="bg-slate-400 text-white flex-1 py-2">Hold: {yahooData.recommendationTrend.trend[0].hold}</div>
                       <div className="bg-red-400 text-white flex-1 py-2">Sell: {yahooData.recommendationTrend.trend[0].sell}</div>
                       <div className="bg-red-600 text-white flex-1 py-2">Strong Sell: {yahooData.recommendationTrend.trend[0].strongSell}</div>
                    </div>
                  </div>
                )}
                
                {/* Event Calendar */}
                {yahooData.calendarEvents?.earnings && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded border border-blue-100 dark:border-blue-900/50">
                    <h5 className="text-sm font-bold text-blue-800 dark:text-blue-300 mb-2 flex items-center gap-2"><CalendarIcon className="w-4 h-4"/> Earnings & Dividends</h5>
                    <div className="text-xs space-y-1 text-slate-700 dark:text-slate-300">
                      <p>Rilascio Utili: {yahooData.calendarEvents.earnings.earningsDate?.[0]?.fmt || 'N/D'}</p>
                      <p>Stima EPS: {yahooData.calendarEvents.earnings.earningsAverage?.fmt || 'N/D'} (Min: {yahooData.calendarEvents.earnings.earningsLow?.fmt} - Max: {yahooData.calendarEvents.earnings.earningsHigh?.fmt})</p>
                      <p>Data Dividendo S-Cedola: {yahooData.calendarEvents.exDividendDate?.fmt || 'N/D'}</p>
                    </div>
                  </div>
                )}

              </div>
            ) : null}
          </div>

          {/* AI Info existing layout from previous modal */}
          <div className="bg-indigo-50 dark:bg-indigo-900/20 p-5 rounded-xl border border-indigo-100 dark:border-indigo-800/30">
            <h4 className="text-sm font-bold text-indigo-900 dark:text-indigo-300 mb-3 uppercase tracking-wider">AI Analysis</h4>
            <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
              <div><span className="text-indigo-600/70 dark:text-indigo-400/70">Model:</span> <span className="font-medium text-slate-800 dark:text-slate-200">{estimate.ai_model || 'N/A'}</span></div>
              <div><span className="text-indigo-600/70 dark:text-indigo-400/70">Version:</span> <span className="font-medium text-slate-800 dark:text-slate-200">{estimate.ai_version || 'N/A'}</span></div>
              <div><span className="text-indigo-600/70 dark:text-indigo-400/70">Confidence:</span> <span className="font-medium text-slate-800 dark:text-slate-200">{estimate.ai_confidence ? `${estimate.ai_confidence}%` : 'N/A'}</span></div>
            </div>
            {estimate.ai_reasoning && (
              <div className="mt-4 pt-4 border-t border-indigo-200/50 dark:border-indigo-800/50">
                <span className="text-xs font-bold text-indigo-500 dark:text-indigo-400 uppercase tracking-widest block mb-2">Reasoning</span>
                <p className="text-sm text-slate-700 dark:text-slate-300 italic whitespace-pre-wrap leading-relaxed">
                  "{estimate.ai_reasoning}"
                </p>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}
