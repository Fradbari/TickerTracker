import React, { useMemo } from 'react'
import { X } from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis
} from 'recharts'
import { HoverTooltipBox } from '@/shared/components/HoverTooltipBox'

interface AiDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  aiName: string;
  stats: any;
}

export function AiDetailsModal({ isOpen, onClose, aiName, stats }: AiDetailsModalProps) {
  if (!isOpen) return null;

  const historyData = useMemo(() => {
    if (!stats?.rawEstimates) return [];
    
    const closed = stats.rawEstimates.filter((e: any) => e.status !== 'OPEN' && e.closed_at)
      .sort((a: any, b: any) => new Date(a.closed_at).getTime() - new Date(b.closed_at).getTime());
      
    let cum = 0;
    return closed.map((e: any) => {
      const pnl = parseFloat(e.realized_pnl || '0');
      cum += pnl;
      return {
        date: new Date(e.closed_at).toLocaleDateString(),
        pnl: pnl.toFixed(2),
        cumulative: parseFloat(cum.toFixed(2))
      };
    });
  }, [stats]);

  const scatterData = useMemo(() => {
    if (!stats?.rawEstimates) return [];
    
    return stats.rawEstimates
      .filter((e: any) => e.status !== 'OPEN' && e.target_profit_percent && e.realized_pnl_percent)
      .map((e: any) => {
        const expected = Math.abs(parseFloat(e.target_profit_percent));
        const realized = parseFloat(e.realized_pnl_percent);
        return {
          symbol: e.ticker?.symbol || e.ticker_id,
          expected,
          realized,
          isWin: realized > 0
        };
      }).filter((d: any) => d.expected > 0);
  }, [stats]);

  const CustomTooltipArea = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[var(--card)] border border-[var(--border)] p-3 rounded-lg shadow-lg text-sm">
          <p className="font-semibold text-slate-500 mb-1">{label}</p>
          <p className="text-[var(--foreground)]">
            <span className="font-semibold text-purple-500">P&L Cumulato: </span> 
            {payload[0].value}€
          </p>
        </div>
      );
    }
    return null;
  };

  const CustomTooltipScatter = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[var(--card)] border border-[var(--border)] p-3 rounded-lg shadow-lg text-sm">
          <p className="font-bold text-[var(--foreground)] mb-1">{data.symbol}</p>
          <p className="text-slate-400">Target Atteso (Volatilità): <span className="text-[var(--foreground)] font-semibold">{data.expected.toFixed(2)}%</span></p>
          <p className="text-slate-400">P&L Realizzato: <span className={`font-semibold ${data.realized >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{data.realized.toFixed(2)}%</span></p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div 
        className="bg-[var(--background)] w-full max-w-5xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col border border-[var(--border)] overflow-hidden"
      >
        <div className="flex justify-between items-center p-6 border-b border-[var(--border)] shrink-0">
          <div>
            <h2 className="text-2xl font-bold text-[var(--foreground)] truncate max-w-lg" title={aiName}>{aiName}</h2>
            <p className="text-sm text-slate-500">Statistiche Avanzate & Dettagli Operativi</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-full hover:bg-[var(--hover)] transition-colors text-slate-500 hover:text-[var(--foreground)]"
          >
            <X size={24} />
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto flex-1">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <HoverTooltipBox description="Rappresenta la percentuale matematica di stime chiuse nativamente in target-profit, divisa per il totale delle stime giunte a scadenza/chiusura elaborate da questa Intelligenza Artificiale." className="h-full group cursor-default" tooltipClassName="-bottom-2 translate-y-full">
              <div className="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] h-full transition-transform group-hover:-translate-y-1">
                <div className="text-sm text-slate-500 mb-1">Win Rate Globale</div>
                <div className="text-2xl font-bold text-[var(--foreground)]">{stats?.winRate?.toFixed(1)}%</div>
              </div>
            </HoverTooltipBox>
            <HoverTooltipBox description="Il profitto (verde) o perdita (rosso) totale capitalizzato storicamente dall'intelligenza artificiale, misurato in valuta fiat." className="h-full group cursor-default" tooltipClassName="-bottom-2 translate-y-full">
              <div className="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] h-full transition-transform group-hover:-translate-y-1">
                <div className="text-sm text-slate-500 mb-1">P&L Netto</div>
                <div className={`text-2xl font-bold ${stats?.totalPnL >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                  {stats?.totalPnL >= 0 ? '+' : ''}{stats?.totalPnL?.toFixed(2)}€
                </div>
              </div>
            </HoverTooltipBox>
            <HoverTooltipBox description="Asset e segnali temporali completamente decorsi o che hanno raggiunto lo Stop Loss / Take Target price definitivo nel tempo." className="h-full group cursor-default" tooltipClassName="-bottom-2 translate-y-full">
              <div className="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] h-full transition-transform group-hover:-translate-y-1">
                <div className="text-sm text-slate-500 mb-1">Stime Chiuse</div>
                <div className="text-2xl font-bold text-[var(--foreground)]">{stats?.wins + stats?.losses}</div>
              </div>
            </HoverTooltipBox>
            <HoverTooltipBox description="Volume di stime ed elaborazioni fornite da questa IA attualmente attive e aperte sul mercato." className="h-full group cursor-default" tooltipClassName="-bottom-2 translate-y-full">
              <div className="bg-[var(--card)] p-4 rounded-xl border border-[var(--border)] h-full transition-transform group-hover:-translate-y-1">
                <div className="text-sm text-slate-500 mb-1">Stime Attive</div>
                <div className="text-2xl font-bold text-[var(--foreground)]">{stats?.active}</div>
              </div>
            </HoverTooltipBox>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Area Chart: Andamento P&L */}
            <HoverTooltipBox 
              className="h-full w-full"
              tooltipClassName="bottom-full mb-2"
              description={`Mostra la crescita o la contrazione cumulativa del capitale nel tempo per questa AI.\n\nEsempio pratico: Se l'IA genera +10€ nel primo trade e -5€ nel secondo, il grafico salirà a +10€ e poi scenderà a +5€, tracciando visivamente la reale resilienza ed efficienza storica del modello artificiale.`}
            >
              <div className="bg-[var(--card)] rounded-xl border border-[var(--border)] p-4 w-full h-[360px] flex flex-col">
                <div className="mb-4">
                  <h3 className="font-semibold text-[var(--foreground)]">Andamento P&L Cumulato</h3>
                  <p className="text-xs text-slate-500">Crescita del capitale basata sui trade chiusi</p>
                </div>
                <div className="flex-1 w-full overflow-hidden">
                  {historyData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={historyData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <defs>
                          <linearGradient id="colorCum" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.5}/>
                            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" opacity={0.5} />
                        <XAxis 
                          dataKey="date" 
                          stroke="var(--foreground)" 
                          tick={{ fill: "var(--foreground)", fontSize: 12, fontWeight: 500 }}
                          tickLine={false} 
                          axisLine={false} 
                          minTickGap={20}
                        />
                        <YAxis 
                          stroke="var(--foreground)" 
                          tick={{ fill: "var(--foreground)", fontSize: 12, fontWeight: 500 }}
                          tickLine={false} 
                          axisLine={false}
                          tickFormatter={(v) => `${v}€`}
                        />
                        <RechartsTooltip content={<CustomTooltipArea />} />
                        <Area 
                          type="monotone" 
                          dataKey="cumulative" 
                          stroke="#8b5cf6" 
                          strokeWidth={3}
                          fillOpacity={1} 
                          fill="url(#colorCum)" 
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                      Dati insufficienti per il grafico Andamento P&L.
                    </div>
                  )}
                </div>
              </div>
            </HoverTooltipBox>

            {/* Scatter Chart: Target (Volatilità) vs P&L */}
            <HoverTooltipBox 
              className="h-full w-full"
              tooltipClassName="bottom-full mb-2"
              description={`Mappa la resa attesa dall'IA a confronto con il rendimento reale generato, permettendo di valutare intuitivamente se l'Intelligenza Artificiale riesce a supportare nel tempo i target stimati.\n\nEsempio pratico: Se una stima prevede un Target del +5% (Asse X) ma termina al rialzo a +4% reali (Asse Y, pallino verde), il punto sarà tracciato alle coordinate (5, 4). Se termina colpendo lo stop a -2%, sarà un pallino rosso incrociato su (5, -2). L'ideale è visualizzare una massiccia scia verde verso l'alto a destra!`}
            >
              <div className="bg-[var(--card)] rounded-xl border border-[var(--border)] p-4 w-full h-[360px] flex flex-col">
                <div className="mb-4">
                  <h3 className="font-semibold text-[var(--foreground)]">Correlazione Reale vs Attesa (Resa)</h3>
                  <p className="text-xs text-slate-500">Distribuzione percentuale (Target vs Realizzato)</p>
                </div>
                <div className="flex-1 w-full overflow-hidden">
                  {scatterData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.5} />
                        <XAxis 
                          type="number" 
                          dataKey="expected" 
                          name="Target" 
                          unit="%" 
                          stroke="var(--foreground)" 
                          tick={{ fill: "var(--foreground)", fontSize: 12, fontWeight: 500 }}
                          tickLine={false} 
                          axisLine={false}
                        />
                        <YAxis 
                          type="number" 
                          dataKey="realized" 
                          name="Realizzato" 
                          unit="%" 
                          stroke="var(--foreground)" 
                          tick={{ fill: "var(--foreground)", fontSize: 12, fontWeight: 500 }}
                          tickLine={false} 
                          axisLine={false}
                        />
                        <ZAxis type="category" dataKey="symbol" name="Simbolo" />
                        <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltipScatter />} />
                        <Scatter 
                          name="Profitto" 
                          data={scatterData.filter((d: any) => d.isWin)} 
                          fill="var(--success)" 
                          shape="circle" 
                        />
                        <Scatter 
                          name="Perdita" 
                          data={scatterData.filter((d: any) => !d.isWin)} 
                          fill="var(--danger)" 
                          shape="circle" 
                        />
                      </ScatterChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                      Dati insufficienti per il grafico di Correlazione.
                    </div>
                  )}
                </div>
              </div>
            </HoverTooltipBox>

          </div>
        </div>
      </div>
    </div>
  )
}
