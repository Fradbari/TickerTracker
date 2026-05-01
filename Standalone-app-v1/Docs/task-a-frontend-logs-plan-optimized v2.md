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

> ⚠️ **PREREQUISITO STRUTTURALE (Leggi prima di tutto):**
> Questo piano assume che la repo abbia già una struttura `backend/` (FastAPI)
> e `frontend/` (React 19 + Vite). Se stai operando su un progetto
> HTML standalone o monorepo differente, **FERMATI** e chiedi conferma
> del mapping reale dei path prima di procedere.

---

# 🎯 Piano Implementazione Task A: System Logs - Integrazione Eventi Frontend
> **Agente Target:** Gemini 3.1 Pro Preview (VS Code Copilot)  
> **Budget Context:** 173k tokens → Usa solo i file elencati. Ignora tutto il resto.  
> **Ambiente:** Backend FastAPI (venv Python), Frontend React 19 (Docker), PostgreSQL, localhost.

---

## 📦 CONTEXT MANIFEST (Da caricare in Copilot prima di eseguire)
> ⚠️ **REGOLA FERREA:** Se un file non è in questo elenco, IGNORALO. Non inventare path. Usa `@file:` syntax di Copilot.
> ⚠️ ROOT OPERATIVA: `Standalone-app-v1/`. Tutti i path sono relativi a questa cartella.

1. `@file:Standalone-app-v1/backend/src/main.py` (registrazione router)
2. `@file:Standalone-app-v1/backend/src/shared/api/logs.py` 
3. `@file:Standalone-app-v1/backend/src/shared/router.py` 
4. `@file:Standalone-app-v1/backend/src/shared/infra/database.py` 
5. `@file:Standalone-app-v1/backend/alembic.ini` + `backend/alembic/env.py`
6. `@file:Standalone-app-v1/backend/alembic/versions/` (lista migration esistenti per evitare conflitti)
7. `@file:Standalone-app-v1/frontend/src/App.tsx` o `Providers.tsx`
8. `@file:Standalone-app-v1/frontend/src/features/admin/components/SystemLogs.tsx` (o equivalente)
9. `@file:Standalone-app-v1/frontend/.env` (per `VITE_API_BASE_URL`)
10. `@file:Standalone-app-v1/docker-compose.yml` (verifica port mapping `8000/3000`)
11. `@file:Standalone-app-v1/backend/src/models/logs.py`

---

## 🏗️ Architettura di Flusso (Task A)
```text
[Frontend Component] → frontendLogger.ts (queue + flush)
  → POST /api/logs/frontend (FastAPI)
  → Pydantic validation → SQLAlchemy persistence
  → DB table: system_logs (source='frontend')
  → Admin Log Viewer (filter: source)
```

> ⚠️ PRE-DECISIONE ARCHITETTURALE: I log attuali usano file-based persistence
> (`/app/logs/app.log`). Prima di procedere con Alembic, conferma con l'utente:
> - Opzione A: Persisti i log frontend su DB (richiede nuovo modello ORM + migration)
> - Opzione B: Usa structlog esistente anche per frontend (zero migration, modifica solo schema)
> Il piano procede con Opzione A solo su conferma esplicita.

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
  > Dopo `--autogenerate`, verifica manualmente che `upgrade()` contenga:
  > `op.add_column('system_logs', sa.Column('source', sa.String(20), server_default='backend', nullable=False))`
  > Se Alembic genera solo `nullable=True`, correggi manualmente.
  
4. Output richiesto: **solo** il nome del file migration e il blocco `def upgrade()` verificato.
  > Il file migration avrà naming: `YYYYMMDD_HHMMSS_add_source_col_to_system_logs.py`
  > Verifica che NON ci siano migration pending (`alembic history`) prima di procedere.

---

## 🔹 Step 2: Backend Router & Schema
1. Modifica `@file:backend/src/shared/api/logs.py` (file ESISTENTE):
   - Estendi `FrontendLogPayload` con i nuovi campi oppure crea `FrontendLogIn`
     come schema alternativo nello stesso file
   - NON creare un nuovo router separato (evita conflitti su `/api/logs/frontend`)
2. Schema: `@file:backend/src/schemas/logs.py`
   ```python
   from datetime import datetime, timezone
   from typing import Any, Literal, Optional

   from backend.src.schemas.logs import FrontendLogIn

   from pydantic import BaseModel, Field

    class FrontendLogIn(BaseModel):
      timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
      level: Literal["info", "warn", "error", "action"]
      component: str = Field(max_length=100)
      message: str = Field(max_length=500)
      metadata: dict[str, Any] = Field(default_factory=dict)
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
> Non fare hardcore di localhost:8000 nel codice produzione solo nel .env.example
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
  private readonly apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

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
      this.retryCount = Math.min(this.retryCount + 1, 5);
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
      this.retryCount = Math.min(this.retryCount + 1, 5);
      console.warn('[FrontendLogger] beforeunload flush failed', error);
    }
  }
}

export const logger = new FrontendLogger();

```

---

## 🔹 Step 4: Admin Viewer (`SystemLogs.tsx`)
⚠️ PREREQUISITO: Verifica che l'endpoint esistente `GET /api/logs` accetti il query param `source`. 
Se non supporta il filtro, usa `params.set('page', '1')` e filtra lato frontend con `data.filter(l => filterSource === 'all' || l.source === filterSource)`.

> 🔧 WORKAROUND TEMPORANEO: Il filtro client-side genera trasferimento dati inutile.
> Richiedi all'utente di aggiornare il backend per supportare `?source=` prima di andare in produzione.

1. Query con filtro:
   ```tsx
    const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

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
   ```tsx
    // In App.tsx o Providers.tsx (una sola volta, al mount globale)
    import { logger } from '@/shared/services/frontendLogger';
    // Il logger si auto-inizializza all'import; nessun useEffect necessario.
    // Per destroy al cleanup (opzionale in SPA):
    // useEffect(() => () => logger.destroy(), []);
   ```

5. Usage example:
   ```tsx
   logger.log('action', 'InsertEstimate', 'Ticker submitted', { ticker: 'AAPL' });
   ```

---

## 🔹 Step 5: Test & Validazione
```bash
  # Backend venv
  py -m venv .venv
  .venv\Scripts\activate 

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