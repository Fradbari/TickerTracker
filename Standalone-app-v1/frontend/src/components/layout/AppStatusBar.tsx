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

export const AppStatusBar: React.FC = () => {
    const [status, setStatus] = useState<TaskStatus | null>(null);
    const [offline, setOffline] = useState(false);

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

    const renderLoopStatus = () => {
        if (offline) return <span style={{ color: theme.colors.textMuted }}>● OFFLINE</span>;
        if (!status) return <span style={{ color: theme.colors.warning }}>● LOADING</span>;
        return status.running 
            ? <span style={{ color: theme.colors.success }}>● RUNNING</span>
            : <span style={{ color: theme.colors.warning }}>● PAUSED</span>;
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
                    {status.last_yahoo_call && (
                        <div>
                            Yahoo: {status.last_yahoo_call.success 
                                ? <span style={{ color: theme.colors.success }}>OK</span> 
                                : <span style={{ color: theme.colors.danger }}>FAIL</span>}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};