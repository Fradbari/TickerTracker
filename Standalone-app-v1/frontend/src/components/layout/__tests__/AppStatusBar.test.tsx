import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AppStatusBar } from '../AppStatusBar';
import axios from 'axios';

vi.mock('axios');

describe('AppStatusBar component', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders initial loading state', () => {
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

    it('renders running status with data', async () => {
        (axios.get as any).mockResolvedValueOnce({
            data: {
                running: true,
                estimates_monitored: 5,
                last_yahoo_call: { success: true }
            }
        });
        
        render(<AppStatusBar />);
        
        await waitFor(() => {
            expect(screen.getByText('● RUNNING')).toBeTruthy();
            expect(screen.getByText('5')).toBeTruthy();
            expect(screen.getByText('OK')).toBeTruthy();
        });
    });
});