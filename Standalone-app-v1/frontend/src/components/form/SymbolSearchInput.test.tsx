
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SymbolSearchInput } from './SymbolSearchInput';
import { useSymbolSearch } from '@/features/market-data/hooks/useSymbolSearch';
import { vi } from 'vitest';

vi.mock('@/features/market-data/hooks/useSymbolSearch')

const mockUseSymbolSearch = useSymbolSearch as ReturnType<typeof vi.fn>

describe('SymbolSearchInput', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('renderizza input con il placeholder corretto', () => {
    mockUseSymbolSearch.mockReturnValue({ data: undefined, isLoading: false, isError: false })
    render(<SymbolSearchInput value=\
\ onChange={vi.fn()} />)
    expect(screen.getByPlaceholderText(/Cerca simbolo o azienda/i)).toBeInTheDocument()
  })

  test('mostra spinner durante il caricamento', () => {
    mockUseSymbolSearch.mockReturnValue({ data: undefined, isLoading: true, isError: false })
    const { container } = render(<SymbolSearchInput value=\A\ onChange={vi.fn()} />)
    const input = screen.getByPlaceholderText(/Cerca/i)
    fireEvent.focus(input)
    fireEvent.change(input, { target: { value: 'AA' } })
    // In this basic dom testing we check class or element.
    expect(container.querySelector('.animate-spin')).toBeInTheDocument()
  })

  test('mostra risultati della ricerca', async () => {
    mockUseSymbolSearch.mockReturnValue({
      data: [{ symbol: 'AAPL', description: 'Apple Inc.', type: 'Common Stock', current_price: 150.0 }],
      isLoading: false,
      isError: false
    })
    
    render(<SymbolSearchInput value=\A\ onChange={vi.fn()} />)
    const input = screen.getByPlaceholderText(/Cerca/i)
    
    fireEvent.focus(input)
    fireEvent.change(input, { target: { value: 'AA' } })
    
    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument()
      expect(screen.getByText('Apple Inc.')).toBeInTheDocument()
    })
  })

  test('chiama onChange quando si seleziona un risultato', async () => {
    mockUseSymbolSearch.mockReturnValue({
      data: [{ symbol: 'AAPL', description: 'Apple Inc.', type: 'Common Stock', current_price: 150.0 }],
      isLoading: false,
      isError: false
    })
    const onChangeMock = vi.fn()
    
    render(<SymbolSearchInput value=\\ onChange={onChangeMock} />)
    const input = screen.getByPlaceholderText(/Cerca/i)
    
    fireEvent.focus(input)
    fireEvent.change(input, { target: { value: 'AA' } })
    
    await waitFor(() => {
      const option = screen.getByText('AAPL')
      fireEvent.click(option)
    })
    
    expect(onChangeMock).toHaveBeenCalledWith('AAPL', true)
  })

  test('mostra messaggio nessun risultato', async () => {
    mockUseSymbolSearch.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false
    })
    
    render(<SymbolSearchInput value=\\ onChange={vi.fn()} />)
    const input = screen.getByPlaceholderText(/Cerca/i)
    
    fireEvent.focus(input)
    fireEvent.change(input, { target: { value: 'INVALID123' } })
    
    await waitFor(() => {
      expect(screen.getByText(/Nessun risultato/i)).toBeInTheDocument()
    })
  })
})

