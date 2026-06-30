# HANDOFF.md — TickerTracker v3.0

> Documento autocontenuto. Aggiornato: **2026-06-29**.
> Zero contesto esterno necessario. Sessione precedente non richiesta.

---

## 1. Stato Repository

**Branch attivo:** `vibe-claude`
**Commit HEAD:** `b843f54` — `feat: initialize backend project roadmap and configure Claude settings`
**Git status:** clean (nessuna modifica staged o unstaged)
**Repo root:** `Standalone-app-v1/`

### Gerarchia fonti di verità

| File | Ruolo | Stato |
|---|---|---|
| `CLAUDE.md` | Invarianti architetturali, sub-agent roster, workflow atomico | OK |
| `AGENTS.md` (root) | Task ledger, Progress Tracker, grafo dipendenze | 1 bug (vedi §3) |
| `backend/AGENTS.md` | Task Python/FastAPI, back-link a CLAUDE.md e root AGENTS.md | OK |
| `frontend/AGENTS.md` | Task React/TS, back-link a CLAUDE.md e root AGENTS.md | 1 bug (vedi §3) |
| `docker/AGENTS.md` | Task container/compose, back-link a CLAUDE.md e root AGENTS.md | OK |
| `docs/AGENTS.md` | Task testing/CI-CD/runbook, back-link a CLAUDE.md e root AGENTS.md | 1 bug (vedi §3) |

### Documentazione tecnica

| Percorso | Contenuto | Stato |
|---|---|---|
| `backend/docs/` | 13 deep-dive tecnici (API-REFERENCE, SECURITY, SCHEDULER, ALEMBIC, …) | OK |
| `backend/docs/history/orig/` | 6 `TASK_*.md` archiviati (completion logs storici) | OK |
| `docs/runbook/` | 7 runbook operativi | OK |
| `docs/agents-sprint-fix.md` | Piano sprint UX — 4 task (C→D→B→A) | Attivo, non iniziato |
| `docs/PROJECT-STATUS.md` | Snapshot storico 2026-06-13 + Delta log | Storico |
| `docs/Piano-operativo-v1.7.docx` | Business plan (binario) | Riferimento |
| `backend/SETUP_GUIDE.md` | Guida setup locale | Path stale (vedi §3) |

---

## 2. Progresso Task MVP

**Fonte autoritativa:** root `AGENTS.md` Progress Tracker.

| Sezione | Stato |
|---|---|
| Sezione 1 — Setup & Fondamenta | 8/8 completati |
| Sezione 2 — Backend Core & Data | 21/21 completati |
| Sezione 3 — Sicurezza & Observability | 9/11 (aperti: TASK 3.10, 3.11) |
| Sezione 4 — Frontend MVP | 9/15 (aperti: TASK 4.5b, 4.10, 4.11, 4.12, 4.16) |
| Sezione 5 — Testing & CI-CD | parziale (vedi `docs/AGENTS.md` per dettaglio) |
| Fase 2 | 0/19 |

Totale MVP: ~56% completato.

---

## 3. Bug Documentali da Correggere

Tempo stimato: <10 minuti totali. Correggere prima di qualsiasi altro lavoro.

### BUG-1 — Progress Tracker inconsistente (AGENTS.md)

**Problema:** La sezione "Frontend MVP" (righe ~217–219) elenca TASK 4.10, 4.11, 4.12, 4.16 come completati (`✅`), ma il Progress Tracker (righe ~99–101) li ha come aperti (`[ ]`).

**Azione:** Verificare esistenza reale dei componenti, poi allineare la sezione "Frontend MVP" al Progress Tracker.

```bash
# Verifica componenti frontend
ls frontend/src/features/estimates/components/
ls frontend/src/features/portfolio/components/
ls frontend/src/app/router/ 2>/dev/null || ls frontend/src/app/
```

### BUG-2 — Backtick non chiuso (docs/AGENTS.md:30)

**Problema:** `` `HANDOFF.md | `` — backtick di chiusura mancante, rompe rendering tabella.

**Fix:** sostituire `` `HANDOFF.md | `` con `` `HANDOFF.md` | ``

### BUG-3 — Path relativo sbagliato (frontend/AGENTS.md:22)

**Problema:** path usa `../src/shared/...` ma il file è in `frontend/`, corretto è `./src/shared/...`.

**Fix:** sostituire `../src/` con `./src/` righe 22–23.

### BUG-4 — backend/SETUP_GUIDE.md path stale

**Problema:** `AI Studio\Standalone-app-v1` non corrisponde alla root reale.

**Fix:** aggiornare path riga 12, o rimuovere il file se coperto da `backend/README.md`.

---

## 4. Work Package Documentali Incompleti (WP5–WP7)

WP1–WP4 completati nella sessione 2026-06-28. Rimangono:

### WP5 — Rimuovere sezioni ridondanti da root AGENTS.md

Le sezioni seguenti duplicano `CLAUDE.md` e vanno eliminate per mantenere root `AGENTS.md` come task ledger puro:

- §"Regole Globali di Sviluppo" (righe ~14–31): già in `CLAUDE.md §Critical Architectural Invariants`
- §"Risorse Utili" (righe ~434–452): link esterni, zero valore per agenti
- §"Support & Questions" (righe ~453–461): filler

### WP6 — Back-link backend/docs → runbook (direzione inversa mancante)

5 runbook linkano già `backend/docs/*.md`. Il contrario è assente.

Aggiungere sezione `## Vedere anche` in:

| File | Link da aggiungere |
|---|---|
| `backend/docs/HEALTH.md` | `[Runbook monitoring](../../docs/runbook/monitoring.md)` |
| `backend/docs/METRICS.md` | `[Runbook monitoring](../../docs/runbook/monitoring.md)` |
| `backend/docs/LOGGING.md` | `[Runbook monitoring](../../docs/runbook/monitoring.md)` |
| `backend/docs/SCHEDULER.md` | `[Runbook yahoo-outage](../../docs/runbook/yahoo-outage.md)` |

### WP7 — Allineare versione React nei docs

`CLAUDE.md` r.1 dice "React 18/Vite". Il codice usa React 19.

**Fix:** aggiornare `CLAUDE.md` r.1 da "React 18" a "React 19".

---

## 5. Sprint UX Attivo

Spec completa: `docs/agents-sprint-fix.md`

> ATTENZIONE: Questo sprint richiede branch `test`, non `vibe-claude`.

```bash
git checkout test
# Se non esiste:
git checkout -b test
```

### Ordine esecuzione (vincolante — non invertire)

**TASK C — Barra inferiore**
- Rimuovere pulsante `Sync Now` con tutte le dipendenze UI nella barra
- Rimuovere badge `GDrive: Non configurato` dalla barra globale
- Aggiungere indicatore Yahoo elapsed time: `Yahoo: aggiornato Xs fa`
- Soglie: <5m normale | 5–30m warning | >30m o fallito danger
- Timer locale frontend; no polling extra

**TASK D — Nuova Stima / Finnhub**
- Esporre `finnhub_key_configured: boolean` dall'endpoint config/admin
- Banner inline quando Finnhub non configurata (no blocco form)
- Al blur del campo simbolo: validazione Yahoo come fallback
- No API key esposta mai

**TASK B — Admin operativa**
- Campo Google Drive folder ID: input + caricamento valore attuale + salvataggio backend
- Sezione Finnhub: verifica esplicita + salvataggio solo a verifica riuscita
- `PRICE_UPDATE_INTERVAL_MINUTES`: visibile, modificabile, persistito backend
- Configurazioni di sistema: backend, non localStorage

**TASK A — System Logs**
- Endpoint `POST /api/logs/frontend` (o equivalente già esistente)
- Servizio `frontendLogger` con buffer + flush fire-and-forget + fallback silenzioso
- Viewer: filtro `source: frontend | backend`
- Log obbligatori: navigazione pagina, errori API, errori boundary, click su azioni critiche

### Verifica dopo ogni task

```bash
cd frontend && npx tsc --noEmit && cd ..
# + test manuali UI descritti in docs/agents-sprint-fix.md §Acceptance criteria
```

### Pre-analisi obbligatoria (leggere prima di scrivere codice)

```
frontend/src/components/layout/AppStatusBar.tsx
frontend/src/features/admin/components/AdminDashboard.tsx
frontend/src/features/admin/components/AdminSettings.tsx
frontend/src/features/admin/components/SystemStatusCards.tsx
frontend/src/features/estimates/components/InsertEstimate.tsx
frontend/src/features/estimates/components/EstimateForm.tsx
```

### STOP — Fermarsi e chiedere se

- Componente barra inferiore reale diverso da `AppStatusBar.tsx`
- Endpoint status non espone timestamp Yahoo
- Backend non supporta `finnhub_key_configured`
- Rimozione `Sync Now` richiede touch a logica usata altrove

### Formato commit per ogni task

```
fix(frontend): <descrizione> — Task C
fix(estimate-form): <descrizione> — Task D
fix(admin): <descrizione> — Task B
fix(logging): <descrizione> — Task A
```

---

## 6. Invarianti Architetturali

Non violare mai. Non ridefinire. Non bypassare.

| Regola | Dettaglio |
|---|---|
| Decimal precision backend | `Decimal` sempre, mai `float`. DB: `DECIMAL(10,4)` / `DECIMAL(8,4)` |
| Decimal precision frontend | `decimal.js` sempre, mai `number` per calcoli finanziari |
| API client frontend | Tutto HTTP via `frontend/src/shared/api/client.ts`. No `fetch()` diretti in componenti |
| Feature isolation | No cross-import tra feature. Solo via `shared/` |
| Outbox location | `backend/src/infra/outbox/` — NON in `backend/src/sync/` (sync/ = Drive) |
| CQRS view | `estimate_summary_view` — refresh ogni 5 min. Script manuale: `backend/scripts/refresh_estimate_summary_view.py` |
| Zod v4 | `.refine()` per numeric coercion — NON `z.coerce.number()` |
| Error handling frontend | `useNotify()` da `@/shared/ui`; `AppErrorBoundary` in `src/app/components/` |
| Non esiste | `docs/Piano-operativo-v1.7.md` (solo `.docx`), `LICENSE` file root |
| Playwright | Suite in repo root (`playwright.config.ts`), NON sotto `frontend/` |
| Vitest | `npm run test:coverage` o `--run` in CI; `npm run test` entra in watch |
| Alembic | Models importati in `env.py`; `target_metadata = Base.metadata`; partial indexes con `text("...")` |

---

## 7. Sub-agent Roster

| Agente | Quando usare | Scope |
|---|---|---|
| `task-planner` | Piano sessione, task non bloccati, dependency graph | Read-only AGENTS.md |
| `backend-dev` | Qualsiasi edit `backend/**`, FastAPI/SQLAlchemy/Alembic/Pytest | `backend/` |
| `frontend-dev` | Qualsiasi edit `frontend/**`, React/TS/Vite/Vitest | `frontend/` |
| `docker-dev` | `docker/**`, compose files, helper scripts | `docker/` |
| `docs-dev` | `docs/**`, markdown, runbook, PDF/docx | `docs/` |
| `code-reviewer` | Prima di ogni commit o PR | Diff only |
| `Explore` | Ricerca read-only across the tree | None |

Boundary: NON modificare file fuori dal proprio scope senza task esplicito in `AGENTS.md`.

---

## 8. Comandi Pronti all'Uso

```bash
# Validazione dipendenze task
cd Standalone-app-v1
python scripts/validate_dependencies.py
```

```powershell
# Docker locale (PowerShell)
.\docker-manage.ps1 up       # avvia db + redis + backend
.\docker-manage.ps1 health   # verifica healthcheck
.\docker-manage.ps1 logs     # log realtime
.\docker-manage.ps1 down     # spegni
```

```bash
# Backend
cd backend
make dev           # uvicorn hot-reload
make test          # tutti i test
make lint          # ruff + mypy
make type-check    # solo mypy
alembic upgrade head
alembic revision --autogenerate -m "nome"
alembic current
```

```bash
# Frontend
cd frontend
npm run dev             # vite dev server
npm run type-check      # tsc --noEmit
npm run test:coverage   # vitest (NON npm run test)
npm run lint
npm run build
```

---

## 9. Storico Sessioni

| Data | Branch | Attività |
|---|---|---|
| 2026-06-22 | vibe-nemotron | Refactor docs: CLAUDE.md riscritto, 12 deep-dive `backend/docs/` creati, stale link corretti. Bloccato NIM (Opus 4.8) — Bash/Agent spawn disabilitati. |
| 2026-06-28 | vibe-claude | Task A–D HANDOFF eseguiti: `TASK_*.md` archiviati, `backend/README.md` 1482→227 righe, WP1–WP4 armonizzazione docs completati. |
| 2026-06-29 | vibe-claude | Review doc state: WP5–WP7 PARZIALE/MANCANTE, 4 bug documentali identificati. Questo HANDOFF riscritto. |

---

## 10. Checklist Avvio Prossima Sessione

```
[ ] git status → deve essere clean
[ ] echo ping → Bash funzionante
[ ] Leggere questo HANDOFF.md
[ ] Fix BUG-1: Progress Tracker AGENTS.md (~5 min)
[ ] Fix BUG-2: docs/AGENTS.md:30 backtick (~30 sec)
[ ] Fix BUG-3: frontend/AGENTS.md:22 path (~30 sec)
[ ] Fix BUG-4: backend/SETUP_GUIDE.md path (~2 min)
[ ] WP5: rimuovere sezioni ridondanti da root AGENTS.md
[ ] WP6: aggiungere "Vedere anche" in 4 file backend/docs/
[ ] WP7: CLAUDE.md r.1 React 18 → React 19
[ ] git checkout test → eseguire Sprint UX (TASK C→D→B→A)
[ ] python scripts/validate_dependencies.py prima di ogni commit
[ ] Aggiornare questo HANDOFF.md prima di chiudere la sessione
```

---

**Fine HANDOFF.md. Aggiornare prima di chiudere ogni sessione.**
