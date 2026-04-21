import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PortfolioAdvanced } from '../components/PortfolioAdvanced';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: vi.fn(),
  };
});

describe('PortfolioBadges', () => {
  it('renders correct badges for different statuses', () => {
    (useQuery as any).mockReturnValue({
      data: [
        { id: 1, ticker: { symbol: 'AAPL' }, status: 'FETCHING', direction: 'LONG' },
        { id: 2, ticker: { symbol: 'MSFT' }, status: 'WON', direction: 'SHORT' },
        { id: 3, ticker: { symbol: 'TSLA' }, status: 'ERROR', error_message: 'Bad Data', direction: 'LONG' }
      ],
      isLoading: false,
    });
    
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <PortfolioAdvanced />
        </MemoryRouter>
      </QueryClientProvider>
    );

    // fetching uses Loader2 so we look for "FETCHING" text
    expect(screen.getByText('FETCHING')).toBeInTheDocument();
    
    // WON should be styled by badge logic (and text WON)
    expect(screen.getByText('WON')).toBeInTheDocument();
    
    // Check error message tooltip logic - "ERROR" text
    expect(screen.getByText('ERROR')).toBeInTheDocument();
    expect(screen.getByTitle('Bad Data')).toBeInTheDocument();
  });
});
