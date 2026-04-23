import React, { useEffect, useState } from 'react';
import { theme } from '../../styles/theme';
import axios from 'axios';

interface TaskStatus {
    running: boolean;
    next_run_iso: string;
    last_run_iso: string;
    estimates_monitored: number;
    interval_seconds: number;
    last_yahoo_call: { timestamp: string; success: boolean } | null;
    last_gdrive_sync: { timestamp: string; success: boolean } | null;
}

const formatElapsed = (timestampIso: string, nowMs: number): string | null => {
    const parsedTimestamp = Date.parse(timestampIso);
    if (Number.isNaN(parsedTimestamp)) {
        return null;
    }

    const elapsedSeconds = Math.max(0, Math.floor((nowMs - parsedTimestamp) / 1000));

    if (elapsedSeconds < 60) {
        return `${elapsedSeconds}s`;
    }

    const elapsedMinutes = Math.floor(elapsedSeconds / 60);
    if (elapsedMinutes < 60) {
        return `${elapsedMinutes}m`;
    }

    const elapsedHours = Math.floor(elapsedMinutes / 60);
    const remainingMinutes = elapsedMinutes % 60;
    if (remainingMinutes === 0) {
        return `${elapsedHours}h`;
    }

    return `${elapsedHours}h ${remainingMinutes}m`;
};

export const AppStatusBar: React.FC = () => {
    const [status, setStatus] = useState<TaskStatus | null>(null);
    const [offline, setOffline] = useState(false);
    const [elapsedNowMs, setElapsedNowMs] = useState(() => Date.now());

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await axios.get('/api/tasks/status');
                setStatus(res.data);
                setOffline(false);
            } catch (err) {
                setOffline(true);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        const elapsedTimer = setInterval(() => {
            setElapsedNowMs(Date.now());
        }, 5000);

        return () => clearInterval(elapsedTimer);
    }, []);

    const renderLoopStatus = () => {
        if (offline) return <span style={{ color: theme.colors.textMuted }}>● OFFLINE</span>;
        if (!status) return <span style={{ color: theme.colors.warning }}>● LOADING</span>;
        return status.running 
            ? <span style={{ color: theme.colors.success }}>● RUNNING</span>
            : <span style={{ color: theme.colors.warning }}>● PAUSED</span>;
    };

    const renderYahooStatus = () => {
        if (!status?.last_yahoo_call) {
            return <span style={{ color: theme.colors.textMuted }}>Yahoo: nessun aggiornamento registrato</span>;
        }

        const elapsed = formatElapsed(status.last_yahoo_call.timestamp, elapsedNowMs);
        if (!elapsed) {
            return <span style={{ color: theme.colors.textMuted }}>Yahoo: nessun aggiornamento registrato</span>;
        }

        if (status.last_yahoo_call.success) {
            return <span style={{ color: theme.colors.success }}>Yahoo: aggiornato {elapsed} fa</span>;
        }

        return <span style={{ color: theme.colors.danger }}>Yahoo: ultimo tentativo fallito {elapsed} fa</span>;
    };

    return (
        <div style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            height: '32px',
            backgroundColor: theme.colors.surface,
            borderTop: `1px solid ${theme.colors.border}`,
            display: 'flex',
            alignItems: 'center',
            padding: '0 16px',
            fontSize: '12px',
            fontFamily: theme.font.mono,
            color: theme.colors.textMuted,
            zIndex: 9000,
            gap: '24px'
        }}>
            <div>Prices Loop: {renderLoopStatus()}</div>
            {status && !offline && (
                <>
                    <div>Stime attive: <span style={{ color: theme.colors.text }}>{status.estimates_monitored}</span></div>
                    <div>{renderYahooStatus()}</div>
                </>
            )}
        </div>
    );
};