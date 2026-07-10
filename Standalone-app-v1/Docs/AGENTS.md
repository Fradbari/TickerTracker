# AGENTS — Docs (Testing, CI/CD, Documentazione, Runbook)

> **Agente:** docs-dev
>
> ↗ Invarianti architetturali e workflow atomico: vedi [`../CLAUDE.md`](../CLAUDE.md) · Progress Tracker globale e grafo dipendenze: vedi [`../AGENTS.md`](../AGENTS.md)

## Scope

Questa sezione contiene i task per il **track docs**: testing, CI/CD, documentazione e runbook operativi.

- **Testing backend**: pytest (marker `unit`/`integration`/`e2e`/`slow`/`chaos`/`properties` in `backend/pyproject.toml`)
- **Testing frontend**: Vitest + Testing Library
- **E2E**: Playwright (suite alla **root del repo**: `playwright.config.ts` — NON sotto `frontend/`)
- **CI/CD**: GitHub Actions (`.github/workflows/`)
- **Documentazione tecnica**: deep-dive in [`../backend/docs/`](../backend/docs/) (audience dev), runbook in [`runbook/`](runbook/) (audience ops)
- **Runbook operativi**: procedure di produzione in [`runbook/`](runbook/)

**Non modificare (fuori scope — track diversi):**
- Codice backend → [`../backend/AGENTS.md`](../backend/AGENTS.md)
- Codice frontend → [`../frontend/AGENTS.md`](../frontend/AGENTS.md)
- Docker/compose → [`../Docker/AGENTS.md`](../Docker/AGENTS.md)
- TASK 5.12 (Feature Flags) e 5.13 (Backup DB) → vivono in `backend/AGENTS.md`
- TASK 5.14 (Dockerfile multi-stage) → vive in `docker/AGENTS.md`

---

## Mappa della cartella `Docs/`

| File/Cartella | Scopo | Stato |
|---|---|---|
| `runbook/` | 7 procedure operative di produzione (startup, recovery, outage, monitoring, scaling, drive-sync, contacts) | ✅ Attivo (TASK 5.15) |
| `superpowers/plans/` | Analisi gap repository (storiche) | Storico |
| `piano-di-lavoro-v2.md` | Documento unico di governo della fase di sviluppo (snapshot, roadmap, regole di sessione, evidenze) | ✅ Attivo |
| `archive/Piano-operativo-v1.7-estratto.md` | Estratto testuale del piano operativo storico (docx rimosso, in git history) | Storico, non normativo |

> ⚠️ La numerazione task in `archive/` è STALE: mai usarla come fonte di ID — il ledger canonico è root `AGENTS.md`. I file storici `Piano-di-lavoro.md`, `Stato-avanzamento-pdl.md` e `Piano-operativo-v1.7.docx` sono stati rimossi il 2026-07-10 (recuperabili da git history, HEAD di riferimento `feef0f4`).

---

## Regole Generali (docs track)

- **Decimal precision** (rinvio): `Decimal` backend / `decimal.js` frontend, mai `float`/`number`. Dettagli in `CLAUDE.md` → Critical Architectural Invariants.
- **API client centralizzato** (rinvio): tutto HTTP via `frontend/src/shared/api/client.ts`. Dettagli in `CLAUDE.md`.
- **Runbook vs deep-dive**: `runbook/*.md` = procedure operative *come-consumare* (ops); `backend/docs/*.md` = come è *implementato* (dev). Ogni runbook cross-linka il deep-dive corrispondente e viceversa.
- **Una sola fonte di verità**: il Progress Tracker ufficiale è in root [`../AGENTS.md`](../AGENTS.md). Non duplicarlo qui o nei `README.md`.
- **OpenAPI**: ogni nuovo endpoint backend deve essere documentato (FastAPI genera `/docs` automaticamente; TASK 5.16 = export/versioning formale).

---

## Convenzioni formato task

Ogni task segue il blocco standard (allineato agli altri `AGENTS.md`):

```
ID: TASK X.Y
Area: docs/<sottoarea>
Fase: MVP | Fase 2
Dipendenze: TASK a.b[, TASK c.d] | -

## TASK X.Y: <titolo>
**Descrizione:** ...
**Microstep:** 1. ... 2. ...
**Acceptance Criteria:** - [ ] ...
```

**Legenda stato**: ✅ Completato | 🚧 In Corso | ⏸️ Bloccato | ⬜ Da Fare

---

## TASK 5.x (Testing & CI/CD)

> Lo stato ufficiale vive nel Progress Tracker di [`../AGENTS.md`](../AGENTS.md). Qui i task canonici con dettaglio.

ID: TASK 5.1
Area: docs/testing-backend
Fase: MVP
Dipendenze: TASK 2.1

### TASK 5.1: Setup Test Framework Backend
**Stato:** ⬜ Da fare
**Descrizione:** Configurare pytest con marker, fixture e coverage nel `backend/pyproject.toml`.
**Acceptance Criteria:**
- [ ] Marker definiti (`unit`, `integration`, `e2e`, `slow`, `chaos`, `properties`)
- [ ] Coverage reporting configurato
- [ ] Fixture shared in `conftest.py`

---

ID: TASK 5.2
Area: docs/testing-backend
Fase: MVP
Dipendenze: TASK 1.3, TASK 1.4, TASK 1.5

### TASK 5.2: Scrivere Unit Test per Value Objects
**Stato:** ✅ Completato (36+ test)
**Descrizione:** Unit test per `Money`, `Percentage`, `PriceTarget` (currency-match, basis-points, configurazioni LONG/SHORT invalide).

---

ID: TASK 5.3
Area: docs/testing-backend
Fase: MVP
Dipendenze: TASK 2.14

### TASK 5.3: Scrivere Unit Test per EstimateService
**Stato:** ✅ Completato
**Descrizione:** Test del service layer: creazione, aggiornamento, chiusura stime, generazione eventi.

---

ID: TASK 5.4
Area: docs/testing-backend
Fase: MVP
Dipendenze: TASK 2.16

### TASK 5.4: Scrivere Integration Test per API Estimates
**Stato:** ✅ Completato
**Descrizione:** Test end-to-end dei router Estimates (CRUD, paginazione cursor-based, `ApiResponse` standard).

---

ID: TASK 5.5
Area: docs/testing-backend
Fase: Fase 2
Dipendenze: TASK 5.2, TASK 2.14

### TASK 5.5: Implementare Property-Based Testing per P&L
**Stato:** ⬜ Da fare
**Descrizione:** Usare Hypothesis per test proprietà P&L (commutatività, invarianti Decimal precision).

---

ID: TASK 5.6
Area: docs/testing-frontend
Fase: MVP
Dipendenze: TASK 4.1

### TASK 5.6: Setup Test Framework Frontend
**Stato:** ✅ Completato
**Descrizione:** Vitest + Testing Library + jsdom. Nota: `npm run test` entra in watch — usare `npm run test:coverage` o `--run` in CI (vedi `CLAUDE.md` → Non-obvious Quirks).

---

ID: TASK 5.7
Area: docs/testing-frontend
Fase: Fase 2
Dipendenze: TASK 4.8

### TASK 5.7: Scrivere Component Test per EstimateForm
**Stato:** ✅ Completato
**Descrizione:** Component test per form stime (validazione Zod, submit, errori).

---

ID: TASK 5.8
Area: docs/testing-e2e
Fase: Fase 2
Dipendenze: TASK 4.16

### TASK 5.8: Setup E2E Test con Playwright
**Stato:** ✅ Completato
**Descrizione:** Suite Playwright alla **root del repo** (`playwright.config.ts`). Non esiste `test:e2e` in `frontend/package.json`; il `test` della root `package.json` è uno stub.

---

ID: TASK 5.9
Area: docs/testing-e2e
Fase: Fase 2
Dipendenze: TASK 5.8

### TASK 5.9: Implementare Chaos Testing
**Stato:** ✅ Completato
**Descrizione:** Test di resilienza: outbox retry, dead-letter, fallback cache market data, outage provider.

---

ID: TASK 5.10
Area: docs/cicd
Fase: Fase 2
Dipendenze: TASK 5.2

### TASK 5.10: Configurare CI Pipeline (GitHub Actions)
**Stato:** ✅ Completato
**Descrizione:** `.github/workflows/ci.yml`: backend-lint, backend-test, frontend-test (con postgres/redis services), backend-security (Trivy), e2e-test (Playwright).

---

ID: TASK 5.11
Area: docs/cicd
Fase: Fase 2
Dipendenze: TASK 5.10

### TASK 5.11: Configurare CD Pipeline (Deploy)
**Stato:** ✅ Completato
**Descrizione:** Pipeline di deploy continuo su merge del branch principale.

---

ID: TASK 5.15
Area: docs/runbook
Fase: Fase 2
Dipendenze: TASK 3.7

### TASK 5.15: Creare Runbook Operativo
**Stato:** ✅ Completato
**Descrizione:** 7 procedure in [`runbook/`](runbook/) + policy RTO/RPO. Vedi [`runbook/README.md`](runbook/README.md).

---

ID: TASK 5.16
Area: docs/api
Fase: Fase 2
Dipendenze: TASK 2.16, TASK 2.17

### TASK 5.16: Documentare API con OpenAPI
**Stato:** ⬜ Da fare
**Descrizione:** Formalizzare export/versioning dello schema OpenAPI. Riferimento implementativo: [`../backend/docs/API-REFERENCE.md`](../backend/docs/API-REFERENCE.md). FastAPI espone già `/docs` a runtime.

---

ID: TASK 5.17
Area: docs/migration
Fase: Fase 2
Dipendenze: TASK 2.23

### TASK 5.17: Creare Script Migrazione Dati v2.4 → v3.0
**Stato:** ✅ Completato
**Descrizione:** Script di migrazione dei dati legacy (formato v2.4 CSV/JSON) verso lo schema v3.0.

---

## Link Diretti

- ↗ Entry point: [`../CLAUDE.md`](../CLAUDE.md)
- ↗ Task ledger globale + Progress Tracker: [`../AGENTS.md`](../AGENTS.md)
- ⚙️ Deep-dive tecnici backend (dev): [`../backend/docs/`](../backend/docs/)
- 🚑 Runbook operativi (ops): [`runbook/`](runbook/)
- 🐳 Docker track: [`../Docker/AGENTS.md`](../Docker/AGENTS.md)
- 🐍 Backend track: [`../backend/AGENTS.md`](../backend/AGENTS.md)
- ⚛️ Frontend track: [`../frontend/AGENTS.md`](../frontend/AGENTS.md)
