import React from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts'
import { usePortfolioMetrics } from '../hooks/usePortfolioMetrics'
import { useTranslation } from 'react-i18next'
import { formatMoney } from '@/shared/finance'

// TODO: replace with /api/portfolio/summary when available

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a28bff', '#ff7373']

export function Dashboard() {
  const { metrics, isLoading, isError, error } = usePortfolioMetrics()
  const { t } = useTranslation('common')

  if (isLoading) {
    return <div className="p-4" aria-live="polite">Loading dashboard...</div>
  }

  if (isError || !metrics) {
    return <div className="p-4 text-red-500" aria-live="polite">Error loading dashboard: {error instanceof Error ? error.message : JSON.stringify(error)}</div>
  }

  const {
    totalInvested,
    totalPnL,
    activeEstimatesCount,
    countsByStatus,
    cumulativePnLData,
    tickerDistribution,
    topPerformers,
    worstPerformers
  } = metrics

  const formatCurrency = (val: number) => {
    try {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
    } catch {
      return val.toString()
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold mb-4">Portfolio Dashboard</h1>

      {/* Top Level Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
          <h2 className="text-sm text-gray-500">Total P&L</h2>
          <p className={`text-2xl font-semibold ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatCurrency(totalPnL)}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
          <h2 className="text-sm text-gray-500">Total Invested (Active)</h2>
          <p className="text-2xl font-semibold">{formatCurrency(totalInvested)}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
          <h2 className="text-sm text-gray-500">Active Estimates</h2>
          <p className="text-2xl font-semibold">{activeEstimatesCount}</p>
        </div>
      </div>

      {/* Breakdown by Status */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 dark:bg-blue-900 border border-blue-200 p-3 rounded">
          <span className="text-sm text-blue-700 dark:text-blue-200 block">Open</span>
          <span className="text-lg font-bold">{countsByStatus.OPEN}</span>
        </div>
        <div className="bg-green-50 dark:bg-green-900 border border-green-200 p-3 rounded">
          <span className="text-sm text-green-700 dark:text-green-200 block">Closed Win</span>
          <span className="text-lg font-bold">{countsByStatus.CLOSED_WIN}</span>
        </div>
        <div className="bg-red-50 dark:bg-red-900 border border-red-200 p-3 rounded">
          <span className="text-sm text-red-700 dark:text-red-200 block">Closed Loss</span>
          <span className="text-lg font-bold">{countsByStatus.CLOSED_LOSS}</span>
        </div>
        <div className="bg-gray-50 dark:bg-gray-700 border border-gray-200 p-3 rounded">
          <span className="text-sm text-gray-700 dark:text-gray-200 block">Closed Neutral</span>
          <span className="text-lg font-bold">{countsByStatus.CLOSED_NEUTRAL}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        {/* Cumulative P&L Chart */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded shadow col-span-1 lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Cumulative P&L</h2>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={cumulativePnLData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorPnL" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" />
                <YAxis />
                <CartesianGrid strokeDasharray="3 3" />
                <Tooltip formatter={(value: any) => formatCurrency(Number(value) || 0)} />
                <Area type="monotone" dataKey="pnl" stroke="#8884d8" fillOpacity={1} fill="url(#colorPnL)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Distribution Pie Chart */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
          <h2 className="text-lg font-semibold mb-4">Ticker Distribution (PnL)</h2>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={tickerDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: any) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="pnl"
                >
                  {tickerDistribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any) => formatCurrency(Number(value) || 0)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top & Worst Performers */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
            <h2 className="text-lg font-semibold mb-4 text-green-600">Top Performers</h2>
            <ul className="space-y-2">
              {topPerformers.length === 0 && <li className="text-sm text-gray-500">No data</li>}
              {topPerformers.map((item: any, idx: number) => (
                <li key={idx} className="flex justify-between border-b pb-1 last:border-0 border-gray-100 dark:border-gray-700">
                  <span className="font-medium">{item.ticker}</span>
                  <span className="text-green-600">{formatCurrency(item.pnl)}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
            <h2 className="text-lg font-semibold mb-4 text-red-600">Worst Performers</h2>
            <ul className="space-y-2">
              {worstPerformers.length === 0 && <li className="text-sm text-gray-500">No data</li>}
              {worstPerformers.map((item: any, idx: number) => (
                <li key={idx} className="flex justify-between border-b pb-1 last:border-0 border-gray-100 dark:border-gray-700">
                  <span className="font-medium">{item.ticker}</span>
                  <span className="text-red-600">{formatCurrency(item.pnl)}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
