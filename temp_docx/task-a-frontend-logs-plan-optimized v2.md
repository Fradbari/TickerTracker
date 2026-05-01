## 🤖 AI EXECUTION PROTOCOL (Gemini 3.1 Pro / Copilot)
1. **NO INVENZIONI:** Se un path non esiste nel manifesto, STOP e chiedi conferma.
2. **OUTPUT STRICT:** Restituisci SOLO:
   - Blocchi di codice completi con path file in header (es. `// FILE: backend/src/models/logs.py`)
   - Comandi shell esatti
   - Niente spiegazioni discorsive, niente "Ecco il codice", niente markdown fuori contesto
3. **CHAIN OF VERIFICATION:** Prima di generare codice, verifica mentalmente:
   - Il file esiste? → Se no, crea struttura minimale
   - Le dipendenze sono installate? → Pydantic v2, React Query v5, SQLAlchemy 2.0+
   - L'autenticazione è gestita? → Usa token localStorage o bypass interno
4. **CONTEXT BOUNDARY:** Usa massimo 120k tokens per codice+diff. Riserva 50k per contesto repo.
5. **ERROR HANDLING:** Ogni `fetch` o `await db.commit()` deve avere `try/catch` esplicito con `console.warn` o logging fallback.

---

# 🎯 Piano Implementazione Task A: System Logs - Integrazione Eventi Frontend
> **Agente Target:** Gemini 3.1 Pro Preview (VS Code Copilot)  
> **Budget Context:** 173k tokens → Usa solo i file elencati. Ignora tutto il resto.  
> **Ambiente:** Backend FastAPI (venv Python), Frontend React 19 (Docker), PostgreSQL, localhost.

---

## 📦 CONTEXT MANIFEST (Da caricare in Copilot prima di eseguire)
> ⚠️ **REGOLA FERREA:** Se un file non è in questo elenco, IGNORALO. Non inventare path. Usa `@file:` syntax di Copilot.

1. `@file:backend/src/main.py` (registrazione router)
2. `@file:backend/src/api/routers/*.py` (struttura esistente)
3. `@file:backend/src/schemas/logs.py`
4. `@file:backend/src/models/logs.py` (o equivalente)
5. `@file:backend/alembic.ini` + `backend/alembic/env.py`
6. `@file:frontend/src/App.tsx` o `Providers.tsx`
7. `@file:frontend/src/features/admin/components/SystemLogs.tsx` (o equivalente)
8. `@file:frontend/.env` (per `VITE_API_BASE_URL`)
9. `@file:docker-compose.yml` (verifica port mapping `8000/3000`)

---

## 🏗️ Architettura di Flusso (Task A)
```text
[Frontend Component] → frontendLogger.ts (queue + flush)
  → POST /api/logs/frontend (FastAPI)
  → Pydantic validation → SQLAlchemy persistence
  → DB table: system_logs (source='frontend')
  → Admin Log Viewer (filter: source)
```

---

## 🔹 Step 1: DB Schema & Alembic
1. Verifica path modello: `@file:backend/src/models/logs.py`
2. Aggiungi colonna:
   ```python
   source = Column(String(20), nullable=False, server_default="backend")
   ```
3. Genera migration ESATTA:
   ```bash
   cd backend
   alembic revision --autogenerate -m "add_source_col_to_system_logs"
   # Modifica upgrade()/downgrade() nel file generato se Alembic non ha rilevato il server_default
   alembic upgrade head
   ```
4. Output richiesto: **solo** il nome del file migration e il blocco `def upgrade()` verificato.

---

## 🔹 Step 2: Backend Router & Schema
1. Crea `@file:backend/src/api/routers/frontend_logs.py`
   ```python
    from backend.src.schemas.logs import FrontendLogIn
    from backend.src.models.logs import LogTable 
   ```
2. Schema: `@file:backend/src/schemas/logs.py`
   ```python
   from datetime import datetime
   from typing import Literal, Optional

   from pydantic import BaseModel, Field

    class FrontendLogIn(BaseModel):
      timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
      level: Literal["info", "warn", "error", "action"]
      component: str = Field(max_length=100)
      message: str = Field(max_length=500)
      metadata: dict = Field(default_factory=dict)
      user_id: Optional[str] = None
   ```
3. Endpoint:
   ```python
   @router.post("/frontend", status_code=202, tags=["internal-logs"])
   async def ingest_frontend_logs(
       payload: list[FrontendLogIn],
       db: AsyncSession = Depends(get_db),
       # Bypass auth se dietro proxy interno, altrimenti usa Depends(get_current_user)
   ):
       if len(payload) > 50:
           raise HTTPException(400, "Batch too large. Max 50.")

       try:
           records = [LogTable(**log.model_dump(), source="frontend") for log in payload]
           db.add_all(records)
           await db.commit()
       except Exception:
           await db.rollback()
           raise

       return {"status": "accepted", "count": len(records)}
   ```
4. Registra il router in `@file:backend/src/main.py` o nel registry router esistente:
   ```python
   app.include_router(frontend_logs.router, prefix="/api/logs")
   ```
5. Se il progetto usa autenticazione obbligatoria, applica una delle due strategie:
   - `Depends(get_current_user)` per endpoint protetto
   - Header interno validato, es. `X-Source: frontend`, se dietro reverse proxy

---

## 🔹 Step 3: Frontend Logger Service
1. Crea: `frontend/src/shared/services/frontendLogger.ts`
2. Implementa queue + periodic flush senza URL hardcoded: usa `VITE_API_BASE_URL`.
3. Requisiti tecnici:
   - `maxBatch = 20`
   - `maxQueue = 100` con drop oldest
   - flush automatico ogni 5s
   - `beforeunload` con `navigator.sendBeacon` se disponibile, fallback async `fetch`
   - mai crash UI: solo `console.warn` in caso di errore

```typescript
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
  private readonly apiBase = import.meta.env.VITE_API_BASE_URL ?? '';

  constructor() {
  this.startAutoFlush();
  window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') this.flush();
  });
  window.addEventListener('beforeunload', () => this.flushOnUnload());
  }

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

      this.queue = this.queue.slice(batch.length);
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
      console.warn('[FrontendLogger] beforeunload flush failed', error);
    }
  }
}

export const logger = new FrontendLogger();

window.addEventListener('beforeunload', () => logger.flushOnUnload());
```

---

## 🔹 Step 4: Admin Viewer (`SystemLogs.tsx`)
⚠️ PREREQUISITO: Verifica che l'endpoint esistente `GET /api/logs` accetti il query param `source`. 
Se non supporta il filtro, usa `params.set('page', '1')` e filtra lato frontend con `data.filter(l => filterSource === 'all' || l.source === filterSource)`.

1. Query con filtro:
   ```tsx
   const { data, isLoading, refetch } = useQuery({
     queryKey: ['logs', filterSource],
     queryFn: async () => {
       const params = new URLSearchParams();
       if (filterSource && filterSource !== 'all') params.set('source', filterSource);

       const response = await fetch(`${API_BASE}/api/logs?${params}`);
       if (!response.ok) {
         console.warn('[SystemLogs] Fetch failed with status', response.status);
         throw new Error('Failed to fetch system logs');
       }

       return response.json();
     },
     refetchInterval: 10000,
   });
   ```
2. UI Filter: Dropdown `<select>` con valori `['all', 'backend', 'frontend', 'system']` che aggiorna `filterSource` state.
3. Render riga frontend:
   ```tsx
   {log.source === 'frontend' && (
     <span title={JSON.stringify(log.metadata)} className="cursor-help text-blue-500">
       🖥️
     </span>
   )}
   ```
4. Integrazione flush globale in `frontend/src/App.tsx` o `Providers.tsx`:

5. Usage example:
   ```tsx
   logger.log('action', 'InsertEstimate', 'Ticker submitted', { ticker: 'AAPL' });
   ```

---

## 🔹 Step 5: Test & Validazione
```bash
# Backend venv
py -m venv .venv && .venv\Scriptsctivate  # Windows
# oppure: source .venv/bin/activate          # macOS/Linux

cd backend
uvicorn src.main:app --reload

# Frontend Docker, se non in dev mode con volume mount
docker compose up --build frontend
```

**Verifica Manuale:**
1. Apri `localhost:3000`, esegui azioni loggate: click, form submit, error console.
2. Testa endpoint da Swagger/OpenAPI: `http://localhost:8000/docs`.
3. Query DB:
   ```sql
   SELECT source, COUNT(*)
   FROM system_logs
   GROUP BY source;
   ```
4. Admin UI: filtra `source=frontend`, verifica timestamp e metadata.

---

## ✅ Acceptance Criteria
- [ ] Endpoint `POST /api/logs/frontend` accetta batch e persiste in DB.
- [ ] `source` column distingue `frontend`, `backend`, `system`.
- [ ] Frontend logger non blocca main thread: queue async + fetch non blocking.
- [ ] Flush automatico ogni 5s o 20 eventi, più `beforeunload`.
- [ ] Degradazione elegante: se backend down, queue non cresce oltre 100 items, drop oldest.
- [ ] Admin viewer filtra per `source` e mostra metadata espandibili.
- [ ] Nessun URL backend hardcoded: usa `VITE_API_BASE_URL` o fallback relativo.
- [ ] `npx tsc --noEmit` verde.
- [ ] `py -m pytest` verde.

---

## ⚠️ Note Critiche per l'Agente AI
1. **Context Management:** Carica SOLO i file nel `CONTEXT MANIFEST`. Ignora tests/docs non correlati, salvo richiesta esplicita.
2. **No Global Changes:** Non toccare auth, routing generale, componenti UI non log-related.
3. **TypeScript Strict:** Usa `interface` dove possibile. Evita `any`; preferisci `Record<string, unknown>`.
4. **Error Handling:** Catch esplicito per fetch errors; fallback a `console.warn`; mai crash UI.
5. **DB Safety:** Ogni `await db.commit()` deve avere rollback in `except`.
6. **Commit Message:**
   ```bash
   git commit -m "feat(logging): implement frontend event ingestion & admin viewer filter"
   ```

---

## ❓ Domande di Verifica (Rispondi prima di procedere)
1. Esiste già una tabella `system_logs` o `audit_events`? Se sì, qual è il path del modello SQLAlchemy?
2. Il frontend gira con volume mount (`-v ./frontend/src:/app/src`) o richiede rebuild Docker a ogni modifica TS?
3. L'endpoint `/api/logs/frontend` deve essere autenticato o pubblico? Si consiglia `internal` o header `X-Source: frontend` se dietro reverse proxy.
4. Il viewer log attuale è in `frontend/src/features/admin/components/SystemLogs.tsx` o altro path?
5. Ci sono vincoli di rate limiting lato backend per questo endpoint? Es. Redis-based `100 req/min` per IP.

📌 *Una volta ricevute le risposte, genererò il diff esatto e i comandi di esecuzione ottimizzati per il tuo ambiente.*

---

## 🔍 Note per l'Uso in Copilot
- Incolla il file intero in una chat di Copilot e aggiungi:
  ```text
  Segui passo-passo. Fermati se un file ha path diverso o se incontri ambiguità. Usa solo il budget context indicato.
  ```
- Se Copilot perde il focus, usa `/clear` e incolla solo la sezione rilevante, es. `## 🔹 Step 2: Backend Router & Schema`.
- I comandi `py` e Docker sono parametrizzati per l'ambiente indicato. Conferma se il venv si chiama diversamente, es. `venv` vs `.venv`.
