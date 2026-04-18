import { useNavigate } from 'react-router-dom';
import { differenceInDays, parseISO, format } from 'date-fns';
import { Estimate } from '../types';
import { 
  calculatePnL, 
  formatMoney, 
  formatPercentage,
  parseMoneyFromString,
  fromDecimalAmount,
  DecimalInstance
} from '@/shared/finance/decimalMoney';
import Decimal from 'decimal.js';

interface EstimateCardProps {
  estimate: Estimate;
  currentPrice?: string; // Optional real-time or latest daily price to show unrealised P&L
  onClose?: (id: string, e: React.MouseEvent) => void;
  onDelete?: (id: string, e: React.MouseEvent) => void;
  onEdit?: (id: string, e: React.MouseEvent) => void;
  onClick?: (id: string, e: React.MouseEvent) => void;
}

export function EstimateCard({ estimate, currentPrice, onClose, onDelete, onEdit, onClick }: EstimateCardProps) {
  const navigate = useNavigate();

  const isClosed = estimate.status.startsWith('CLOSED');
  
  // Dates
  const startDate = parseISO(estimate.created_at);
  const formattedStart = format(startDate, 'dd/MM/yyyy');
  let durationText = '';
  
  if (isClosed && estimate.closed_at) {
    const closedDate = parseISO(estimate.closed_at);
    const formattedClose = format(closedDate, 'dd/MM/yyyy');
    const days = differenceInDays(closedDate, startDate);
    durationText = `Chiusa il ${formattedClose} (${days} giorni)`;
  } else {
    // Open
    const days = differenceInDays(new Date(), startDate);
    durationText = `Aperta da ${days} giorni`;
  }

  // P&L calculation
  let pnlToDisplay: DecimalInstance | null = null;
  let pnlPercentageDisplay: DecimalInstance | null = null;
  let pnlText = '-';
  
  // We assume base currency USD for everything internally in EstimateCard for formatting
  const CURRENCY = 'USD';
  
  if (isClosed && estimate.realized_pnl) {
    const realisedMoney = parseMoneyFromString(estimate.realized_pnl, CURRENCY);
    const entryMoney = parseMoneyFromString(estimate.start_price, CURRENCY);
    pnlToDisplay = realisedMoney.amount;
    pnlPercentageDisplay = realisedMoney.amount.dividedBy(entryMoney.amount).times(100);
    pnlText = formatMoney(realisedMoney);
  } else if (!isClosed && currentPrice) {
    const entry = parseMoneyFromString(estimate.start_price, CURRENCY);
    const curr = parseMoneyFromString(currentPrice, CURRENCY);
    const qty = new Decimal(1);
    
    const pnlResult = calculatePnL(entry, curr, qty);
    
    // adjust for short
    const pnlAbsolute = false
      ? pnlResult.absolute.times(-1)
      : pnlResult.absolute;
    const pnlPercentage = false
      ? pnlResult.percentage.times(-1)
      : pnlResult.percentage;
    
    pnlToDisplay = pnlAbsolute;
    pnlPercentageDisplay = pnlPercentage;
    pnlText = formatMoney(fromDecimalAmount(pnlAbsolute, CURRENCY));
  }

  const pnlColorClass = pnlToDisplay 
    ? (pnlToDisplay.greaterThan(0) ? 'text-green-500' : pnlToDisplay.lessThan(0) ? 'text-red-500' : 'text-gray-500')
    : 'text-gray-500';

  // Badges
  const directionBadgeColor = estimate.direction === 'LONG' 
    ? 'bg-blue-100 text-blue-800' 
    : 'bg-purple-100 text-purple-800';

  const statusBadgeColor = {
    'OPEN': 'bg-yellow-100 text-yellow-800',
    'CLOSED_WIN': 'bg-green-100 text-green-800',
    'CLOSED_LOSS': 'bg-red-100 text-red-800',
    'CLOSED_NEUTRAL': 'bg-gray-100 text-gray-800',
  }[estimate.status] || 'bg-gray-100 text-gray-800';

  return (
    <div 
      className="bg-white border rounded shadow-sm hover:shadow-md transition-shadow p-4 flex flex-col sm:flex-row sm:items-center justify-between cursor-pointer gap-4 relative"
      onClick={(e) => onClick ? onClick(estimate.id, e) : navigate(`/estimates/${estimate.id}`)}
      data-testid="estimate-card"
    >
      {/* Left section: Ticker, Direction, Status, Dates */}
      <div className="flex flex-col gap-2 flex-grow">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-bold text-gray-900">{estimate.ticker_id}</h3>
          
          <span className={`px-2 py-0.5 rounded text-xs font-semibold ${statusBadgeColor}`}>
            {estimate.status.replace('_', ' ')}
          </span>
          
          {estimate.ai_model && (
            <span className="px-2 py-0.5 rounded text-xs bg-indigo-50 border border-indigo-200 text-indigo-700">
              AI: {estimate.ai_model} {estimate.ai_confidence ? `(${estimate.ai_confidence})` : ''}
            </span>
          )}
        </div>
        
        <div className="text-sm text-gray-500">
          Iniziata: {formattedStart} • {durationText}
        </div>
      </div>

      {/* Middle section: Prices */}
      <div className="flex flex-row justify-between sm:flex-col gap-2 sm:gap-1 text-sm text-gray-700 w-full sm:w-auto">
        <div className="flex justify-between sm:justify-end gap-2">
          <span className="text-gray-500">Entry:</span>
          <span className="font-medium">${formatMoney(parseMoneyFromString(estimate.start_price, CURRENCY))}</span>
        </div>
        <div className="flex justify-between sm:justify-end gap-2">
          <span className="text-gray-500">Target:</span>
          <span className="font-medium text-green-600">${formatMoney(parseMoneyFromString(estimate.target_price, CURRENCY))}</span>
        </div>
        <div className="flex justify-between sm:justify-end gap-2">
          <span className="text-gray-500">Stop:</span>
          <span className="font-medium text-red-600">${formatMoney(parseMoneyFromString(estimate.stop_loss_price, CURRENCY))}</span>
        </div>
        {isClosed && estimate.exit_price && (
          <div className="flex justify-between sm:justify-end gap-2">
            <span className="text-gray-500">Exit:</span>
            <span className="font-medium">${formatMoney(parseMoneyFromString(estimate.exit_price, CURRENCY))}</span>
          </div>
        )}
      </div>

      {/* Right section: P&L and Actions */}
      <div className="flex items-center justify-between sm:flex-col sm:items-end sm:justify-center gap-4 w-full sm:w-auto mt-2 sm:mt-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-gray-100">
        <div className="flex flex-col items-start sm:items-end">
          <span className="text-xs text-gray-500 uppercase">{isClosed ? 'PnL' : 'PnL Stimato'}</span>
          <span className={`text-lg font-bold ${pnlColorClass}`} data-testid="pnl-amount">
            {pnlToDisplay?.greaterThan(0) ? '+' : ''}
            {pnlToDisplay ? '$' + pnlText : pnlText}
          </span>
          {pnlPercentageDisplay && (
            <span className={`text-sm font-medium ${pnlColorClass}`} data-testid="pnl-percent">
              {pnlPercentageDisplay.greaterThan(0) ? '+' : ''}
              {formatPercentage(pnlPercentageDisplay)}
            </span>
          )}
        </div>

        {/* Desktop actions (Dropdown or buttons) */}
        <div 
          className="flex space-x-2"
          onClick={(e) => e.stopPropagation()} 
        >
          {onClose && !isClosed && (
            <button
              onClick={(e) => onClose(estimate.id, e)}
              className="text-sm px-3 py-1 bg-gray-50 hover:bg-gray-100 text-gray-700 border border-gray-200 rounded transition-colors"
            >
              Chiudi
            </button>
          )}
          {onEdit && (
            <button
              onClick={(e) => onEdit(estimate.id, e)}
              className="text-sm px-3 py-1 bg-blue-50 hover:bg-blue-100 text-blue-600 border border-blue-200 rounded transition-colors"
            >
              Modifica
            </button>
          )}
          {onDelete && (
            <button
              onClick={(e) => onDelete(estimate.id, e)}
              className="text-sm px-3 py-1 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded transition-colors"
            >
              Elimina
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

