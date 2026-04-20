import { useQuery } from '@tanstack/react-query'
import apiClient from '@/shared/api/client'
import { unwrapResponse, type ApiResponse } from '@/shared/types'

export interface SymbolSearchResult {
  symbol: string
  description: string
  type: string
  mic_code: string | null
  current_price: number | null
}

const BASE = '/api/market'

export async function searchSymbols(query: string): Promise<SymbolSearchResult[]> {
  if (!query || query.length < 1) return []
  const { data } = await apiClient.get<ApiResponse<SymbolSearchResult[]>>(
    `${BASE}/symbol-search`,
    { params: { q: query } },
  )
  return unwrapResponse(data)
}

export const SYMBOL_SEARCH_KEYS = {
  all: ['symbol-search'] as const,
  query: (q: string) => [...SYMBOL_SEARCH_KEYS.all, q] as const,
} as const

export function useSymbolSearch(query: string) {
  return useQuery({
    queryKey: SYMBOL_SEARCH_KEYS.query(query),
    queryFn: () => searchSymbols(query),
    enabled: query.length >= 1,
    staleTime: 5 * 60 * 1000, // 5 minuti
  })
}