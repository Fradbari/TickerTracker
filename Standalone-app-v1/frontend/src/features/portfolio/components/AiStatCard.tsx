import React from 'react'

interface AiStatCardProps {
  aiName: string;
  stats: {
    total: number;
    active: number;
    wins: number;
    losses: number;
    totalPnL: number;
    winRate: number;
  };
  onClick: (aiName: string) => void;
}

export function AiStatCard({ aiName, stats, onClick }: AiStatCardProps) {
  const isPositive = stats.totalPnL >= 0;
  return (
    <div 
      onClick={() => onClick(aiName)}
      className="p-4 rounded-xl bg-[var(--card)] border border-[var(--border)] shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 cursor-pointer group"
    >
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-bold text-[var(--foreground)] truncate">{aiName}</h4>
        <span className="text-xs font-medium text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-md">
          {stats.total} Totali
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm mb-3">
        <div>
          <span className="text-slate-500 text-xs block">Attive</span>
          <span className="font-semibold text-[var(--foreground)]">{stats.active}</span>
        </div>
        <div>
          <span className="text-slate-500 text-xs block">Win Rate</span>
          <span className="font-semibold text-[var(--foreground)]">{stats.winRate.toFixed(1)}%</span>
        </div>
        <div>
          <span className="text-slate-500 text-xs block">Profitto / Perdita</span>
          <div className="flex items-center gap-1 font-semibold">
            <span className="text-[var(--success)]">{stats.wins}</span>
            <span className="text-slate-400">/</span>
            <span className="text-[var(--danger)]">{stats.losses}</span>
          </div>
        </div>
        <div>
          <span className="text-slate-500 text-xs block">P&L Totale</span>
          <span className={`font-bold ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
            {isPositive ? '+' : ''}{stats.totalPnL.toFixed(2)}€
          </span>
        </div>
      </div>
    </div>
  )
}
