import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, useSearchParams } from 'react-router-dom';
import { PortfolioAdvanced } from '../components/PortfolioAdvanced';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

// Modifica il mock per mantenere il modulo originale se necessario, o mockare solo ciò che serve
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useSearchParams: vi.fn(),
  };
});

describe('PortfolioFilters', () => {
  it('updates searchParams on status change', () => {
    const setSearchParams = vi.fn();
    (useSearchParams as any).mockReturnValue([new URLSearchParams(), setSearchParams]);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <PortfolioAdvanced />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'WON' } });

    expect(setSearchParams).toHaveBeenCalled();
  });
});
