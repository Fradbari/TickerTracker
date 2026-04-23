import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AppStatusBar } from '../AppStatusBar';
import axios from 'axios';

vi.mock('axios');

interface MockTaskStatus {
    running: boolean;
    next_run_iso: string;
    last_run_iso: string;
    estimates_monitored: number;
    interval_seconds: number;
    last_yahoo_call: { timestamp: string; success: boolean } | null;
    last_gdrive_sync: { timestamp: string; success: boolean } | null;
}

const buildStatus = (overrides: Partial<MockTaskStatus> = {}): MockTaskStatus => ({
    running: true,
    next_run_iso: '2026-04-23T10:00:00Z',
    last_run_iso: '2026-04-23T09:59:00Z',
    estimates_monitored: 5,
    interval_seconds: 60,
    last_yahoo_call: null,
    last_gdrive_sync: null,
    ...overrides,
});

describe('AppStatusBar component', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders initial loading state', () => {
        (axios.get as any).mockReturnValue(new Promise(() => {}));
        render(<AppStatusBar />);
        expect(screen.getByText('Prices Loop:')).toBeTruthy();
    });

    it('renders offline state when api fails', async () => {
        (axios.get as any).mockRejectedValueOnce(new Error('Network Error'));
        render(<AppStatusBar />);
        
        await waitFor(() => {
            expect(screen.getByText('● OFFLINE')).toBeTruthy();
        });
    });

    it('renders no-update copy when Yahoo data is missing', async () => {
        (axios.get as any).mockResolvedValueOnce({
            data: buildStatus({
                last_yahoo_call: null,
            })
        });
        
        render(<AppStatusBar />);
        
        await waitFor(() => {
            expect(screen.getByText('● RUNNING')).toBeTruthy();
            expect(screen.getByText('5')).toBeTruthy();
            expect(screen.getByText('Yahoo: nessun aggiornamento registrato')).toBeTruthy();
        });
    });

    it('renders elapsed success copy when Yahoo last call succeeded', async () => {
        const recentTimestamp = new Date(Date.now() - 12000).toISOString();

        (axios.get as any).mockResolvedValueOnce({
            data: buildStatus({
                last_yahoo_call: { timestamp: recentTimestamp, success: true }
            })
        });

        render(<AppStatusBar />);

        await waitFor(() => {
            expect(screen.getByText(/Yahoo: aggiornato \d+s fa/)).toBeTruthy();
        });
    });

    it('renders elapsed failure copy when Yahoo last call failed', async () => {
        const recentTimestamp = new Date(Date.now() - 18000).toISOString();

        (axios.get as any).mockResolvedValueOnce({
            data: buildStatus({
                last_yahoo_call: { timestamp: recentTimestamp, success: false }
            })
        });

        render(<AppStatusBar />);

        await waitFor(() => {
            expect(screen.getByText(/Yahoo: ultimo tentativo fallito \d+s fa/)).toBeTruthy();
        });
    });
});