import React, { useState, useMemo, useRef, useEffect, useCallback } from 'react';
import { FixedSizeList as List } from 'react-window';
import { useTranslation } from 'react-i18next';
import { useInfiniteEstimates } from '../api/queries';
import { EstimateCard } from './EstimateCard';
import { EstimateListParams, EstimateStatus, Estimate } from '../types';
import Decimal from 'decimal.js';

export function EstimateList() {
  const { t } = useTranslation('common');

  // Filters state
  const [filters, setFilters] = useState<EstimateListParams>({});
  
  // Sort state
  type SortField = 'date' | 'pnl' | 'ticker';
  type SortOrder = 'asc' | 'desc';
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  // Input states
  const [tickerInput, setTickerInput] = useState('');
  const [statusInput, setStatusInput] = useState<EstimateStatus | ''>('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const {
    data,
    isLoading,
    isError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch
  } = useInfiniteEstimates(filters);

  // Combine fetched items
  const allItems = useMemo(() => {
    if (!data) return [];
    return data.pages.flatMap(page => page.items);
  }, [data]);

  // Client-side Sort
  const sortedItems = useMemo(() => {
    const items = [...allItems];
    items.sort((a, b) => {
      let comparison = 0;
      if (sortField === 'date') {
        const dateA = new Date(a.created_at).getTime();
        const dateB = new Date(b.created_at).getTime();
        comparison = dateA - dateB;
      } else if (sortField === 'ticker') {
        comparison = a.ticker_id.localeCompare(b.ticker_id);
      } else if (sortField === 'pnl') {
        // Simple client side parse logic for realized_pnl text sorting
        // Note: For unrealized it doesn't work well without current price, we use realized_pnl if available
        const pnlA = a.realized_pnl ? new Decimal(a.realized_pnl).toNumber() : 0;
        const pnlB = b.realized_pnl ? new Decimal(b.realized_pnl).toNumber() : 0;
        comparison = pnlA - pnlB;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });
    return items;
  }, [allItems, sortField, sortOrder]);

  // Handle filter changes (debounce or explicit apply)
  const applyFilters = () => {
    const newFilters: EstimateListParams = {};
    if (tickerInput) newFilters.ticker_id = tickerInput; // Assuming tickerInput is UUID or handled gracefully
    if (statusInput) newFilters.status = statusInput;
    if (dateFrom) newFilters.created_after = new Date(dateFrom).toISOString();
    if (dateTo) newFilters.created_before = new Date(dateTo).toISOString();
    
    setFilters(newFilters);
  };

  // Virtualization Container Ref
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerHeight, setContainerHeight] = useState(600);

  useEffect(() => {
    if (containerRef.current) {
      setContainerHeight(containerRef.current.getBoundingClientRect().height);
    }
    
    const handleResize = () => {
      if (containerRef.current) {
        setContainerHeight(containerRef.current.getBoundingClientRect().height);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const Row = useCallback(({ index, style }: { index: number, style: React.CSSProperties }) => {
    const estimate = sortedItems[index];
    return (
      <div style={{ ...style, paddingBottom: '16px' }}>
        <EstimateCard estimate={estimate} />
      </div>
    );
  }, [sortedItems]);

  return (
    <div className="flex flex-col h-full gap-4" aria-label={t('listSection', 'Lista Stime')}>
      {/* Filters and Sorting Headers */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold mb-4 text-gray-800">{t('filtersAndSorting', 'Filtri e Ordinamento')}</h2>
        
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="flex-1">
            <label htmlFor="ticker-filter" className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
            {/* TODO: Implement /api/tickers/search autocomplete later */}
            <input 
              id="ticker-filter"
              type="text" 
              placeholder="Cerca ticker..."
              aria-label="Filtra per ticker"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              value={tickerInput}
              onChange={(e) => setTickerInput(e.target.value)}
            />
          </div>

          <div className="flex-1">
            <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">Stato</label>
            <select 
              id="status-filter"
              aria-label="Filtra per stato"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm bg-white"
              value={statusInput}
              onChange={(e) => setStatusInput(e.target.value as EstimateStatus | '')}
            >
              <option value="">Tutti</option>
              <option value="OPEN">Open</option>
              <option value="CLOSED_WIN">Closed (Win)</option>
              <option value="CLOSED_LOSS">Closed (Loss)</option>
              <option value="CLOSED_NEUTRAL">Closed (Neutral)</option>
            </select>
          </div>

          <div className="flex-[2] flex gap-2">
            <div className="flex-1">
              <label htmlFor="date-from-filter" className="block text-sm font-medium text-gray-700 mb-1">Da data</label>
              <input 
                id="date-from-filter"
                type="date" 
                aria-label="Filtra da data inizio"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
              />
            </div>
            <div className="flex-1">
              <label htmlFor="date-to-filter" className="block text-sm font-medium text-gray-700 mb-1">A data</label>
              <input 
                id="date-to-filter"
                type="date" 
                aria-label="Filtra a data fine"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex gap-4 items-center w-full sm:w-auto">
            <label htmlFor="sort-field" className="text-sm font-medium text-gray-700">Ordina per:</label>
            <select 
              id="sort-field"
              aria-label="Seleziona campo di ordinamento"
              className="border border-gray-300 rounded px-3 py-1.5 text-sm bg-white"
              value={sortField}
              onChange={(e) => setSortField(e.target.value as SortField)}
            >
              <option value="date">Data</option>
              <option value="ticker">Ticker</option>
              <option value="pnl">P&amp;L</option>
            </select>
            <button 
              aria-label={sortOrder === 'asc' ? 'Inverti ordine in decrescente' : 'Inverti ordine in crescente'}
              className="px-3 py-1.5 border border-gray-300 rounded text-sm bg-gray-50 hover:bg-gray-100"
              onClick={() => setSortOrder(o => o === 'asc' ? 'desc' : 'asc')}
            >
              {sortOrder === 'asc' ? '↑ Crescente' : '↓ Decrescente'}
            </button>
          </div>
          
          <button 
            aria-label={t('applyFilters', 'Applica filtri')}
            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-medium py-1.5 px-4 rounded transition-colors text-sm"
            onClick={applyFilters}
          >
            {t('applyFilters', 'Applica Filtri')}
          </button>
        </div>
      </div>

      {/* Main List Area */}
      <div 
        ref={containerRef} 
        className="flex-grow flex flex-col relative min-h-[400px]"
      >
        {isLoading && (
          <div className="flex flex-col gap-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse flex p-4 border rounded bg-gray-100 h-32"></div>
            ))}
          </div>
        )}

        {isError && (
          <div className="bg-red-50 text-red-600 p-6 rounded-lg border border-red-100 flex flex-col items-center justify-center text-center">
            <p className="mb-4">Si è verificato un errore durante il caricamento delle stime.</p>
            <button 
              onClick={() => refetch()} 
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
            >
              Riprova
            </button>
          </div>
        )}

        {!isLoading && !isError && sortedItems.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 bg-gray-50 border border-dashed border-gray-300 rounded-lg text-gray-500">
            <svg className="w-12 h-12 mb-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>Nessuna stima trovata con i filtri attuali.</p>
          </div>
        )}

        {!isLoading && !isError && sortedItems.length > 0 && (
          <>
            {sortedItems.length > 100 ? (
              <div className="h-full w-full">
                <List
                  height={containerHeight}
                  itemCount={sortedItems.length}
                  itemSize={160} // Approximate height of the card + gap
                  width="100%"
                >
                  {Row}
                </List>
              </div>
            ) : (
              <div className="flex flex-col gap-4 overflow-y-auto">
                {sortedItems.map(estimate => (
                  <EstimateCard key={estimate.id} estimate={estimate} />
                ))}
              </div>
            )}
            
            {hasNextPage && (
              <div className="flex justify-center mt-4">
                <button
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                  className="px-6 py-2 bg-white border border-gray-300 hover:bg-gray-50 rounded shadow-sm text-gray-700 font-medium text-sm disabled:opacity-50"
                >
                  {isFetchingNextPage ? 'Caricamento in corso...' : 'Carica altri risultati'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
