import React, { useState } from 'react'
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { usePriceHistory } from '../hooks'
import { formatMoney } from '@/shared/finance'

export interface PriceChartProps {
  ticker: string
  dateRange: { from: string; to: string }
  chartType?: 'line' | 'candlestick'
  entryPrice?: string
  targetPrice?: string
  stopLossPrice?: string
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 shadow-md rounded text-sm">
        <p className="font-semibold text-gray-700 dark:text-gray-300 mb-1">{label}</p>
        <div className="flex flex-col gap-1">
          <p><span className="font-medium">Open:</span> {data.open}</p>
          <p><span className="font-medium">High:</span> {data.high}</p>
          <p><span className="font-medium">Low:</span> {data.low}</p>
          <p><span className="font-medium">Close:</span> {data.close}</p>
          <p><span className="font-medium">Volume:</span> {data.volume}</p>
        </div>
      </div>
    )
  }
  return null
}

export function PriceChart({
  ticker,
  dateRange,
  chartType = 'line',
  entryPrice,
  targetPrice,
  stopLossPrice,
}: PriceChartProps) {
  const [aggregation, setAggregation] = useState<'1d' | '1w' | '1m'>('1d')

  const { data: response, isLoading, isError } = usePriceHistory(ticker, dateRange, aggregation)
  const data = response?.data || []

  // Ensure chartType='candlestick' is handled gracefully (simulated or fallback)
  const renderChart = () => {
    if (chartType === 'candlestick') {
      // TODO: implement properly via custom Bar or stick to Line for now. 
      // Falling back to line chart with close prices as per instructions.
    }

    return (
      <Line
        type="monotone"
        dataKey="close"
        stroke="#3b82f6"
        dot={false}
        strokeWidth={2}
      />
    )
  }

  if (isLoading) {
    return (
      <div className="w-full h-80 bg-gray-100 dark:bg-gray-800 animate-pulse rounded-md flex items-center justify-center">
        <span className="text-gray-400">Loading chart data...</span>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="w-full h-80 flex items-center justify-center bg-red-50 dark:bg-red-900 rounded-md">
        <p className="text-red-500 dark:text-red-200">Error loading price history for {ticker}</p>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="w-full h-80 flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-md">
        <p className="text-gray-500">No data available for the selected range.</p>
      </div>
    )
  }

  return (
    <div className="w-full flex flex-col gap-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-lg">{ticker} Price Chart</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setAggregation('1d')}
            className={`px-3 py-1 text-sm rounded ${aggregation === '1d' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
          >
            1D
          </button>
          <button
            onClick={() => setAggregation('1w')}
            className={`px-3 py-1 text-sm rounded ${aggregation === '1w' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
          >
            1W
          </button>
          <button
            onClick={() => setAggregation('1m')}
            className={`px-3 py-1 text-sm rounded ${aggregation === '1m' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
          >
            1M
          </button>
        </div>
      </div>

      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            
            {renderChart()}

            {entryPrice && (
              <ReferenceLine y={Number(entryPrice)} stroke="#a855f7" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Entry' }} />
            )}
            {targetPrice && (
              <ReferenceLine y={Number(targetPrice)} stroke="#22c55e" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Target' }} />
            )}
            {stopLossPrice && (
              <ReferenceLine y={Number(stopLossPrice)} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Stop Loss' }} />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
