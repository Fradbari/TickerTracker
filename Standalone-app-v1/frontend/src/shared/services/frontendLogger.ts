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
  private readonly apiBase = (import.meta as any).env?.VITE_API_BASE_URL ?? 'http://localhost:8000';

  private readonly retryDelay = [1000, 2000, 4000, 8000, 16000];

  constructor() {
  this.startAutoFlush();
  window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') this.flush();
  });
  window.addEventListener('beforeunload', () => this.flushOnUnload());
  }

  private flushTimer: ReturnType<typeof setInterval> | undefined;
  private startAutoFlush() {
    this.flushTimer = setInterval(() => void this.flush(), 5000);
  }

  public destroy() {
    clearInterval(this.flushTimer);
  }

  log(level: LogEntry['level'], component: string, message: string, metadata?: Record<string, unknown>) {
    this.queue.push({
      timestamp: new Date().toISOString(),
      level,
      component,
      message,
      metadata,
    });

    if (this.queue.length > this.maxQueue) {
      this.queue = this.queue.slice(-this.maxQueue);
    }

    if (this.queue.length >= this.maxBatch) {
      void this.flush();
    }
  }

  async flush(): Promise<void> {
    if (this.queue.length === 0) return;

    const batch = [...this.queue];

    try {
      const response = await fetch(`${this.apiBase}/api/logs/frontend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(batch),
      });

      if (!response.ok) {
        console.warn('[FrontendLogger] Flush failed with status', response.status);
        return;
      }

      this.queue.splice(0, batch.length);
    } catch (error) {
      console.warn('[FrontendLogger] Flush failed, retrying later...', error);
    }
  }

  flushOnUnload(): void {
    if (this.queue.length === 0) return;

    const batch = [...this.queue];
    const body = JSON.stringify(batch);
    const url = `${this.apiBase}/api/logs/frontend`;

    try {
      if (navigator.sendBeacon) {
        const blob = new Blob([body], { type: 'application/json' });
        navigator.sendBeacon(url, blob);
        this.queue = [];
        return;
      }

      void fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        keepalive: true,
      });
      this.queue = [];
    } catch (error) {
      const delay = this.retryDelay.shift() ?? 1000;
      console.warn('[FrontendLogger] beforeunload flush failed', error);
    }
  }
}

export const logger = new FrontendLogger();
export const frontendLogger = logger;