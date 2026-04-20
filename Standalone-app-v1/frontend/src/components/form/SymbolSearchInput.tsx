import React, { useState, useEffect, useRef } from 'react'
import { useSymbolSearch, type SymbolSearchResult } from '@/features/market-data/hooks/useSymbolSearch'
import { Search, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'

// Simple useDebounce hook inside the file
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}

export interface SymbolSearchInputProps {
  value: string
  onChange: (value: string, isValid: boolean) => void
  error?: string
  disabled?: boolean
  autoFocus?: boolean
  className?: string
  placeholder?: string
}

export const SymbolSearchInput: React.FC<SymbolSearchInputProps> = ({
  value,
  onChange,
  error,
  disabled,
  autoFocus,
  className = '',
  placeholder = 'Cerca simbolo o azienda...',
}) => {
  const [inputValue, setInputValue] = useState(value)
  const [isOpen, setIsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const containerRef = useRef<HTMLDivElement>(null)

  const debouncedQuery = useDebounce(inputValue, 300)
  
  const { data: results, isLoading, isError } = useSymbolSearch(debouncedQuery)

  // Update local input if remote value changes
  useEffect(() => {
    if (value !== inputValue) {
      setInputValue(value)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value])

  useEffect(() => {
    // Close dropdown on click outside
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (result: SymbolSearchResult) => {
    setInputValue(result.symbol)
    setIsOpen(false)
    onChange(result.symbol, true)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value.toUpperCase()
    setInputValue(val)
    setIsOpen(true)
    setActiveIndex(-1)
    onChange(val, false) // Note: manually typing invalidates the validation
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || !results || results.length === 0) return

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActiveIndex((prev) => (prev < results.length - 1 ? prev + 1 : prev))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActiveIndex((prev) => (prev > 0 ? prev - 1 : -1))
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (activeIndex >= 0 && activeIndex < results.length) {
        handleSelect(results[activeIndex])
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false)
    }
  }

  const wrapperClass = `relative w-full ${className}`
  const inputBaseClass = `w-full pl-10 pr-4 py-2 bg-slate-900 border text-slate-100 rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors ${
    error ? 'border-red-500 pr-10' : 'border-slate-700'
  } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`

  return (
    <div className={wrapperClass} ref={containerRef}>
      <div className="relative flex items-center">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsOpen(true)}
          disabled={disabled}
          autoFocus={autoFocus}
          placeholder={placeholder}
          className={inputBaseClass}
          autoComplete="off"
          spellCheck={false}
        />
        
        {/* Loading Spinner */}
        {isLoading && debouncedQuery && isOpen && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 animate-spin" />
        )}
        
        {/* Valid Icon */}
        {!isLoading && value === inputValue && results?.some(r => r.symbol === value) && !error && (
          <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-green-500" />
        )}

        {/* Error icon */}
        {error && (
           <AlertCircle className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-red-500" />
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && debouncedQuery.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-slate-800 border border-slate-700 rounded-md shadow-lg max-h-60 overflow-y-auto">
          {isLoading && (
            <div className="p-3 pl-10 text-sm text-slate-400">
              Ricerca in corso...
            </div>
          )}
          
          {isError && (
            <div className="p-3 text-sm text-red-400">
              Errore durante la ricerca.
            </div>
          )}
          
          {!isLoading && !isError && results?.length === 0 && (
            <div className="p-3 text-sm text-slate-400">
              Nessun risultato trovato per "{debouncedQuery}"
            </div>
          )}
          
          {!isLoading && results && results.length > 0 && (
            <ul>
              {results.map((result, index) => (
                <li
                  key={result.symbol}
                  onClick={() => handleSelect(result)}
                  className={`px-3 py-2 cursor-pointer flex justify-between items-center text-sm ${
                    index === activeIndex ? 'bg-slate-700' : 'hover:bg-slate-700'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-semibold text-slate-100">{result.symbol}</span>
                    <span className="text-xs text-slate-400 truncate max-w-[200px]">
                      {result.description}
                    </span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-xs text-slate-500 uppercase">{result.type}</span>
                    {result.current_price !== null && (
                       <span className="text-xs text-green-400">${result.current_price.toFixed(2)}</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      
      {/* Validation Message */}
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  )
}