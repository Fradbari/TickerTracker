// frontend/src/shared/services/frontendLogger.ts

interface LogEntry {
    timestamp: string;
    level: 'info' | 'warn' | 'error' | 'action';
    component: string;
    message: string;
    metadata?: Record<string, unknown>;
    user_id?: string;
}

class FrontendLogger {
    private queue: LogEntry[] = [];
    private readonly maxBatch = 20;
    private readonly maxQueue = 100;
    private readonly apiBase =
        (import.meta as { env?: Record<string, string> }).env?.VITE_API_BASE_URL
        ?? 'http://localhost:8000';
    private flushTimer: ReturnType<typeof setInterval> | undefined;

    constructor() {
        this.startAutoFlush();
        window.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') void this.flush();
        });
        window.addEventListener('beforeunload', () => this.flushOnUnload());
    }

    private startAutoFlush() {
        this.flushTimer = setInterval(() => void this.flush(), 5000);
    }

    public destroy() {
        clearInterval(this.flushTimer);
    }

    log(
        level: LogEntry['level'],
        component: string,
        message: string,
        metadata?: Record<string, unknown>
    ) {
        if (this.queue.length >= this.maxQueue) {
            console.warn('[FrontendLogger] Queue full — dropping oldest entry');
            this.queue.shift();
        }
        this.queue.push({
            timestamp: new Date().toISOString(),
            level,
            component,
            message,
            metadata,
        });
    }

    async flush(): Promise<void> {
        if (this.queue.length === 0) return;
        const batch = this.queue.splice(0, this.maxBatch);
        try {
            const res = await fetch(`${this.apiBase}/api/logs/frontend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(batch),
            });
            if (!res.ok) {
                console.warn(`[FrontendLogger] Flush failed: HTTP ${res.status}`);
                this.queue.unshift(...batch); // reinserisce per retry
            }
        } catch (err) {
            console.warn('[FrontendLogger] Flush error:', err);
            this.queue.unshift(...batch);
        }
    }

    private flushOnUnload() {
        if (this.queue.length === 0) return;
        const batch = this.queue.splice(0, this.maxBatch);
        const url = `${this.apiBase}/api/logs/frontend`;
        const data = JSON.stringify(batch);
        if (navigator.sendBeacon) {
            navigator.sendBeacon(url, new Blob([data], { type: 'application/json' }));
        } else {
            void fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: data,
                keepalive: true,
            });
        }
    }
}

export const frontendLogger = new FrontendLogger();