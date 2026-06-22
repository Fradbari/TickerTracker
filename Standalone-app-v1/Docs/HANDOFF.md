# HANDOFF.md — Documentation Refactor Session

**Data creazione:** 2026-06-22
**Branch lavoro:** `vibe-nemotron`
**Stato HEAD (expected):** `c756154` o successivo
**Modello usato:** Opus 4.8 (1M context) — consistentemente bloccato su Bash classifier NIM

---

## ✅ COMPLETATO — Non toccare più

### 1. CLAUDE.md riscritto
- **File:** `Standalone-app-v1/CLAUDE.md`
- Da ~250 righe a ~128 righe
- Sezioni: Sub-agent Roster, Atomic-dev Workflow (5 steps), Critical Architectural Invariants, Real Layouts, Non-obvious Quirks, Things That Were Wrong Before, Quick References, Doc Ownership Map
- **Attenzione:** contiene 2 errori conosciuti: `docs/AGENTS.md` non esiste (noto, in Things That Were Wrong Before) e `Piano-operativo-v1.7.md` non esiste (solo .docx)

### 2. PROJECT-STATUS.md creato + PROJECT_ANALYSIS.md eliminato
- **File eliminato:** `Standalone-app-v1/PROJECT_ANALYSIS.md`
- **File creato:** `Standalone-app-v1/docs/PROJECT-STATUS.md`
- Banner spiega che è snapshot storico 2026-06-13
- Contenuto originale + Delta log con claim smentiti

### 3. Stale link patches applicati
- `Standalone-app-v1/README.md` (5 edit): MIT license → sorgente aperto senza LICENSE; `docs/AGENTS.md` → `docs/agents-sprint-fix.md`; `.md` → `.docx` nel tree diagram; link corretto Piano Operativo
- `backend/README.md` linea 1409: link `Piano-operativo-v1.4.md` → `../../docs/Piano-operativo-v1.7.docx`
- `frontend/src/features/estimates/api/mutations.ts` linea 106: commento Piano-operativo versione `.docx`

### 4. Verifiche stale-link completate
- Grep confermato zero match per pattern `.md` stale rimanenti (esclusi Delta log e Things That Were Wrong Before)

### 5. Nuovi file docs backend creati (12 file + indice)

Tutti in `Standalone-app-v1/backend/docs/`:

| File | Righe | Contenuto estratto |
|---|---|---|
| `CONNECTION-POOL.md` | ~70 | Task 3.10 — variables, tuning, /health/pool |
| `PAGINATION.md` | ~80 | Task 3.11 — cursor-based, base64url opaque cursors |
| `SECURITY.md` | ~115 | Task 1.7+3.1+3.2 — headers, API Key, CSP, slowapi rate limit, middleware order |
| `LOGGING.md` | ~75 | Task 3.5 — structlog, JSON, correlation ID, X-Request-ID |
| `METRICS.md` | ~65 | Task 3.6 — Prometheus, @track_duration, Counter/Gauge/Histogram |
| `ALEMBIC.md` | ~85 | Task 2.10 — upgrade/downgrade, autogenerate gotcha, current migrations |
| `API-REFERENCE.md` | ~170 | Task 2.16+2.17 — endpoints estimates & market data, error codes, cache TTL |
| `SCHEDULER.md` | ~130 | APScheduler jobs + Outbox pattern, max 5 retry, dead letter, idempotenza |
| `ENCRYPTION.md` | ~70 | Task 3.4 — EncryptedString TypeDecorator, Fernet, key rotation |
| `VALIDATION.md` | ~40 | Task 3.3 — sanitize_ticker, validate_price/percentage/date range |
| `LINEAGE.md` | ~50 | Task 3.9 — ingestion_timestamp, source_timestamp, source_provider |
| `HEALTH.md` | ~40 | Task 3.7 — /health, /health/ready, /health/pool, 503 on UNHEALTHY |
| `DATA-QUALITY.md` | ~50 | Task 3.8 — DataQualityMonitor checks, cron 06:00 UTC |

### 6. TASK-COMPLETION-LOGS indice creato
- **File:** `Standalone-app-v1/backend/docs/history/TASK-COMPLETION-LOGS.md`
- Tabella indice 5 entry (TASK 2.11, 2.12, 2.13, 2.13 post-fix, 2.17)
- Sommari brevi per task
- Linee guida future per archival

### 7. `orig/` directory e README
- **File:** `Standalone-app-v1/backend/docs/history/orig/README.md`
- Tabella placeholder con i 5 file da archiviare (ancora non mossi — vedi ❌)

---

## ❌ DA FARE — Primo avvio prossima sessione

### ⚠️ Blocker #1: Agent spawn / Bash NIM classifier bloccati

**Sintomo:** Tutti i tool Bash, PowerShell, e Agent spawn bloccati da:
```
claude-opus-4-8[1m] is temporarily unavailable
```

**Workarounds provati:** Inefficaci. Read/Write/Edit funzionano normalmente.

**Raccomandazione per nuova sessione:** Aprire nuovo thread clean con `/model sonnet` o `/model haiku` prima di tentare Bash. Se anche così Bash è bloccato, usare `!` prefix dal prompt utente (`! bash command`).

### Task #A: Sposta i 5 file TASK_*.md in history/orig/

| File originale | Destinazione |
|---|---|
| `backend/TASK_2_11_DOCUMENTATION_COMPLETE.md` | `backend/docs/history/orig/` |
| `backend/TASK_2.12_VERIFICATION.md` | `backend/docs/history/orig/` |
| `backend/TASK_2.13_VERIFICATION.md` | `backend/docs/history/orig/` |
| `backend/TASK_2.13_FIX_SUMMARY.md` | `backend/docs/history/orig/` |
| `backend/src/market_data/TASK_2.17_REPORT.md` | `backend/docs/history/orig/` |

Uso preferito: `git mv ...` per preservare history. Ma `mv` seguito da `git add` è accettabile.

### Task #B: Slim `backend/README.md` da 1482 a ~220 righe

**File:** `Standalone-app-v1/backend/README.md` (1482 linee, letto interamente in questa sessione)

**Sezioni da CONSERVARE (~50 righe):**
1. Title + descrizione (1-3)
2. Prerequisiti (Python 3.11+, PostgreSQL, Redis)
3. Quick Start (Docker + Local)
4. Struttura directory `backend/` (tree conciso)
5. Link a tutti i nuovi docs (12 file)
6. Contribuire (format + lint + type-check, prima di committare)

**Sezioni già estratte — ELIMINARE dal README, linkare ai nuovi file:**
- Connection Pooling → `docs/CONNECTION-POOL.md`
- Cursor-Based Pagination → `docs/PAGINATION.md`
- Security / CORS / Rate Limit → `docs/SECURITY.md`
- Structured Logging → `docs/LOGGING.md`
- Metrics Prometheus → `docs/METRICS.md`
- Encryption at Rest → `docs/ENCRYPTION.md`
- Input Validation → `docs/VALIDATION.md`
- Alembic workflow → `docs/ALEMBIC.md`
- Data Lineage → `docs/LINEAGE.md`
- Health checks → `docs/HEALTH.md`
- Data Quality → `docs/DATA-QUALITY.md`
- APScheduler + Outbox → `docs/SCHEDULER.md`
- API Endpoints (Estimates, Market Data) → `docs/API-REFERENCE.md`
- Implementation Progress (DUPLICATO di AGENTS.md) — eliminare

**Sezioni speciali da trattare:**
- `Market Data Provider Pattern` / `Caching & Retry Logic` → verificare `backend/docs/MARKET_DATA_PROVIDER.md`, comprimere a 1 frase + link
- `Database Schema` listing → mantenere solo nomi tabelle core + link `docs/ESTIMATE_SUMMARY_VIEW.md`
- `Chaos Testing`, `Migrazione Dati Legacy` → 1 riga ciascuno + link a nuovi file se creati
- `SyncJob`, `AiModelRun` descriptions → eliminare (entities domain, meglio in docstring)

### Task #C: Slim / verify `frontend/README.md`

**File:** `Standalone-app-v1/frontend/README.md` (248 linee)

Verificato 248 linee. Probabilmente già abbastanza slim (template Vite standard), ma controllare se ha sezioni da comprimere o link da aggiornare.

### Task #D: Commit finale

```bash
git add -A
git commit -m "docs: slim READMEs, archive TASK_ logs, extract deep dives

- Archive 5 TASK_2.1*.md completion logs in backend/docs/history/orig/
- Add 12 focused docs under backend/docs/ (API, SECURITY, PAGINATION, ...)
- Slim backend/README.md from 1482 to ~220 lines (deep-dive links)
- Slim frontend/README.md from 248 to ~XX lines
- Update stale doc links (Piano-operativo .md -> .docx, AGENTS.md)"
```

---

## 🗂️ Checklist per nuova sessione

- [ ] Verifica `git status` dalla root (staged? unpushed?)
- [ ] Verifica Bash funzionante (`echo ping`)
- [ ] Se Bash bloccato: provare `/model sonnet` o `/model haiku` nuovo thread
- [ ] #A: Sposta 5 TASK_ files con `git mv`
- [ ] #B: Slim `backend/README.md` (~220 righe)
- [ ] #C: Slim/verify `frontend/README.md`
- [ ] #D: Commit + con messaggio chiaro
- [ ] Verifica link tutti validi in README.md
- [ ] `python scripts/validate_dependencies.py` dalla root

---

## 🚨 Note critiche / errori da NON ripetere

1. **No LICENSE file alla root.** Il progetto è "sorgente aperto per uso educativo/personale" — non MIT.
2. **`docs/AGENTS.md` NON ESISTE.** Link corretto a `docs/agents-sprint-fix.md`
3. **`Piano-operativo-v1.7.md` esiste solo come `.docx`** in `docs/Piano-operativo-v1.7.docx`. NON creare `.md`.
4. **No `fetch()` diretti frontend.** Tutto HTTP via `frontend/src/shared/api/client.ts`.
5. **Outbox è in `backend/src/infra/outbox/`, NOT `backend/src/sync/`** (sync/ = Drive sync)
6. **`backend/docs/` = deep-dive tecnici.** Non confondere con `docs/` alla root (Piano operativo, runbook, ecc.)
7. **Non toccare `backend/AGENTS.md`** a meno che non sia un task tracciato.
8. **Decimal precision invariant:** `Decimal` mai `float`. DB `DECIMAL(10,4)`/`DECIMAL(8,4)`.
9. **`backend/docs/history` directory era precedentemente vuota** (creata in sessione precedente). Questa sessione ha popolato l'indice ma NON ha spostato i file (blocco NIM).

---

## 📁 File creati in questa sessione (da committare)

| Livello | File creati |
|---|---|
| `docs/` | `PROJECT-STATUS.md` |
| `backend/docs/` | `CONNECTION-POOL.md`, `PAGINATION.md`, `SECURITY.md`, `LOGGING.md`, `METRICS.md`, `ALEMBIC.md`, `API-REFERENCE.md`, `SCHEDULER.md`, `ENCRYPTION.md`, `VALIDATION.md`, `LINEAGE.md`, `HEALTH.md`, `DATA-QUALITY.md` |
| `backend/docs/history/` | `TASK-COMPLETION-LOGS.md` |
| `backend/docs/history/orig/` | `README.md` |

---

## 🔍 Debug NIM / Bash block

Se nuovo thread non riesce a fare Bash:

1. `! bash -c "echo test"` direttamente dal prompt utente
2. Se funziona: problem è solo del tool `Bash` nella sessione
3. Se non funziona: è un problema di sistema/host, non di model
4. Come ultima spiaggia operare shell manualmente e poi riassumere con Read sui file

**Fine handoff.**
