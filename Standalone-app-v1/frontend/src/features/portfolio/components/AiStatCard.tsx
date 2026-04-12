import React from 'react'
import { HoverTooltipBox } from '@/shared/components/HoverTooltipBox'

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
        <HoverTooltipBox description="Nome specifico dell'Intelligenza Artificiale o del Modello Quantitativo." className="flex-1 w-full overflow-hidden mr-2 cursor-default" tooltipClassName="-top-2 -translate-y-full mb-1">
          <h4 className="font-bold text-[var(--foreground)] truncate">{aiName}</h4>
        </HoverTooltipBox>
        <HoverTooltipBox description="Numero totale combinato di stime elaborate che sono attualmente Attive sulla timeline o Chiuse storicamente (sia in profitto che in perdita)." className="shrink-0 cursor-default" tooltipClassName="-top-2 -translate-y-full mb-1">
          <span className="text-xs font-medium text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-md">
            {stats.total} Totali
          </span>
        </HoverTooltipBox>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm mb-3">
        <HoverTooltipBox description="Stime di mercato in corso previste e calcolate da questa IA." className="cursor-default" tooltipClassName="-bottom-2 translate-y-full mt-1">
          <div>
            <span className="text-slate-500 text-xs block">Attive</span>
            <span className="font-semibold text-[var(--foreground)]">{stats.active}</span>
          </div>
        </HoverTooltipBox>
        
        <HoverTooltipBox description="Rapporto matematico di precisione predittiva di questa Intelligenza Artificiale diviso sul totale delle stime decifrate." className="cursor-default" tooltipClassName="-bottom-2 translate-y-full mt-1">
          <div>
            <span className="text-slate-500 text-xs block">Win Rate</span>
            <span className="font-semibold text-[var(--foreground)]">{stats.winRate.toFixed(1)}%</span>
          </div>
        </HoverTooltipBox>
        
        <HoverTooltipBox description="Esprime un contatore netto delle singole stime concluse con esito positivo (incasso del Target Profit) e con esito negativo (incasso dello Stop Loss)." className="cursor-default" tooltipClassName="-bottom-2 translate-y-full mt-1">
          <div>
            <span className="text-slate-500 text-xs block">Profitto / Perdita</span>
            <div className="flex items-center gap-1 font-semibold">
              <span className="text-[var(--success)]">{stats.wins}</span>
              <span className="text-slate-400">/</span>
              <span className="text-[var(--danger)]">{stats.losses}</span>
            </div>
          </div>
        </HoverTooltipBox>
        
        <HoverTooltipBox description="Valore reale aggregato tra le operazioni positive e negative in valuta fiat incassate storicamente." className="cursor-default" tooltipClassName="-bottom-2 translate-y-full mt-1">
          <div>
            <span className="text-slate-500 text-xs block">P&L Totale</span>
            <span className={`font-bold ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'} truncate max-w-full block`}>
              {isPositive ? '+' : ''}{stats.totalPnL.toFixed(2)}€
            </span>
          </div>
        </HoverTooltipBox>
      </div>
    </div>
  )
}
