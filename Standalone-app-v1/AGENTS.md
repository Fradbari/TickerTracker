# Piano Atomico TickerTracker v3.0

## Quick Start per LLM

**Stai per lavorare su TickerTracker v3.0** - un sistema completo per tracking stime di trading con architettura DDD/CQRS/Event Sourcing.

---

## 🛠 Regole Globali di Sviluppo

Queste regole si applicano a tutto il progetto e hanno la precedenza sulle istruzioni locali.

1.  **Precisione Finanziaria**:
    *   **Backend**: Usa SEMPRE `Decimal` per importi, prezzi e percentuali. Mai usare `float`.
    *   **Frontend**: Usa SEMPRE `decimal.js` per ogni calcolo finanziario. Mai usare `number`.
2.  **Comunicazione API**:
    *   Usa SEMPRE il modello `ApiResponse` standard per ogni risposta del backend.
    *   Il frontend deve usare SEMPRE l'API client centralizzato.
3.  **Integrità dei Dati**:
    *   Ogni azione significativa deve produrre un evento di dominio (Event Sourcing).
4.  **Architettura**:
    *   Rispetta rigorosamente i boundary dei moduli. No cross-import diretti tra feature.
5.  **Documentazione**:
    *   Ogni nuovo endpoint deve essere documentato con OpenAPI/Swagger.

---

### Prima di Iniziare
1. **Leggi la sezione appropriata** in base al tuo task:
   - 🐍 **Backend/AGENTS.md** → API, domain logic, database, sync
   - ⚛️ **Frontend/AGENTS.md** → React UI, components, forms, charts
   - 🐳 **Docker/AGENTS.md** → Containerizzazione, compose, deployment
   - 📚 **Docs/AGENTS.md** → Testing, CI/CD, documentazione

2. **Rispetta i boundary**: Non modificare file fuori dalla tua sezione
3. **Segui i microstep**: Ogni task ha step atomici e verificabili
4. **Completa gli Acceptance Criteria**: Prima di marcare un task come fatto

---

## 📊 Progress Tracker

**Legenda**: ✅ Completato | 🚧 In Corso | ⏸️ Bloccato | ⬜ Da Fare

### MVP - Ambiente Locale Single-User (46 task)

### Sezione 1: Setup & Fondamenta (8/8)
- [x] **TASK 1.1** - Setup Struttura Layer Backend
- [x] **TASK 1.2** - Definizione Modello Risposta API Standard
- [x] **TASK 1.3** - Creazione Value Object Money Backend
- [x] **TASK 1.4** - Creazione Value Object Percentage Backend
- [x] **TASK 1.5** - Creazione Value Object PriceTarget Backend
- [x] **TASK 1.6** - Configurazione Ambienti con Pydantic Settings
- [x] **TASK 1.7** - Middleware Sicurezza Base & Healthcheck
- [x] **TASK 1.8** - Setup Wrapper TypeScript per Decimali Frontend

#### Sezione 2: Backend Core & Data (20/20 completati)
- [x] **TASK 2.1** - Setup Progetto Python con Poetry & Dipendenze Complete
- [x] **TASK 2.2** - Setup Docker Compose PostgreSQL/Redis *(in Docker/AGENTS.md)*
- [x] **TASK 2.3** - Setup SQLAlchemy Base + Modello Ticker
- [x] **TASK 2.4** - Definizione Modello SQLAlchemy - Estimate
- [x] **TASK 2.5** - Definizione Modello SQLAlchemy - EstimateEvent
- [x] **TASK 2.6** - Definizione Modello SQLAlchemy - MarketData
- [x] **TASK 2.7** - Definizione Modello SQLAlchemy - User e Role (RBAC Base)
- [x] **TASK 2.10** - Setup Alembic per Migrazioni Database
- [x] **TASK 2.11** - Creazione Materialized View EstimateSummaryView
- [x] **TASK 2.12** - Creazione Repository Estimate
- [x] **TASK 2.13** - Creazione Repository MarketData
- [x] **TASK 2.14** - Creazione Service EstimateService
- [x] **TASK 2.15** - Creazione Service EstimateHistoryService
- [x] **TASK 2.16** - Creazione API Router Estimates
- [x] **TASK 2.17** - Creazione API Router Market Data
- [x] **TASK 2.18** - Definizione MarketDataProvider Astratto
- [x] **TASK 2.19** - Caching & Backoff per MarketDataProvider
- [x] **TASK 2.20** - Implementazione Google Drive Client *(16 tests passing)*
- [x] **TASK 2.21** - Implementazione CSV Parser Legacy *(30 tests passing)*
- [x] **TASK 2.22** - Implementazione Sync Service *(14 tests passing)*
- [x] **TASK 2.23** - Test Retrocompatibilità Backup/History Legacy *(17 tests passing)*
- [ ] **TASK 2.24** - Setup Background Worker APScheduler

#### Sezione 4: Frontend Setup & Features (0/13)
- [ ] **TASK 4.1** - Setup Progetto Frontend (Vite + React 19)
- [ ] **TASK 4.2** - Creazione Struttura Feature Modules
- [ ] **TASK 4.3** - Setup API Client Centralizzato
- [ ] **TASK 4.4** - Definizione Types e API Response Models
- [ ] **TASK 4.5** - Creazione Componenti UI Shared
- [ ] **TASK 4.6** - Implementazione EstimateList Component
- [ ] **TASK 4.7** - Implementazione EstimateDetail Component
- [ ] **TASK 4.8** - Implementazione CreateEstimateForm Component
- [ ] **TASK 4.9** - Implementazione TickerSearch Component
- [ ] **TASK 4.10** - Implementazione CloseEstimateModal Component
- [ ] **TASK 4.11** - Implementazione PortfolioDashboard Component
- [ ] **TASK 4.12** - Implementazione PerformanceChart Component
- [ ] **TASK 4.16** - Setup React Router e Layout

#### Sezione 5: Testing & CI/CD Base (0/5)
- [ ] **TASK 5.1** - Setup Test Framework Backend
- [ ] **TASK 5.2** - Scrivere Unit Test per Value Objects
- [ ] **TASK 5.3** - Scrivere Unit Test per EstimateService
- [ ] **TASK 5.4** - Scrivere Integration Test per API Estimates
- [ ] **TASK 5.6** - Setup Test Framework Frontend

---

### Fase 2 - Produzione Multi-User (19 task)

#### Sezione 2: Auth & Advanced Backend (0/6)
- [ ] **TASK 2.8** - Definizione Modello SQLAlchemy - User e Role RBAC
- [ ] **TASK 2.9** - Definizione Modello SQLAlchemy - SyncJob
- [ ] **TASK 2.25** - Definizione Modello SQLAlchemy - AiModelRun
- [ ] **TASK 2.26** - Implementazione Pattern Outbox per Eventi
- [ ] **TASK 2.27** - Creazione API Router Analytics *(da definire)*
- [ ] **TASK 2.28** - Implementazione AI Prompt Service *(da definire)*

#### Sezione 3: Sicurezza & Observability (0/11)
- [ ] **TASK 3.1** - Implementazione Security Middleware
- [ ] **TASK 3.2** - Implementazione Rate Limiting
- [ ] **TASK 3.3** - Implementazione Input Validation Avanzata
- [ ] **TASK 3.4** - Implementazione Encryption at Rest
- [ ] **TASK 3.5** - Setup Structured Logging con Correlation ID
- [ ] **TASK 3.6** - Implementazione Metriche Prometheus
- [ ] **TASK 3.7** - Implementazione Health Checks Completi
- [ ] **TASK 3.8** - Implementazione Data Quality Monitor
- [ ] **TASK 3.9** - Implementazione Data Lineage Tracking
- [ ] **TASK 3.10** - Setup OpenTelemetry Tracing *(da definire)*
- [ ] **TASK 3.11** - Implementazione Circuit Breaker *(da definire)*
- [ ] **TASK 5.12** - Implementazione Feature Flags *(in backend/AGENTS.md)*
- [ ] **TASK 5.13** - Implementazione Backup Automatico Database *(in backend/AGENTS.md)*

#### Sezione 4: Frontend Advanced (0/3)
- [ ] **TASK 4.13** - Implementazione MarketDataChart Component
- [ ] **TASK 4.14** - Implementazione TickerWatchlist Component
- [ ] **TASK 4.15** - Implementazione ChatAI Component (Gemini)

#### Sezione 5: Testing & CI/CD Completo (0/9)
- [ ] **TASK 5.5** - Implementare Property-Based Testing per P&L
- [ ] **TASK 5.7** - Scrivere Component Test per EstimateForm
- [ ] **TASK 5.8** - Setup E2E Test con Playwright
- [ ] **TASK 5.9** - Implementare Chaos Testing
- [ ] **TASK 5.10** - Configurare CI Pipeline (GitHub Actions)
- [ ] **TASK 5.11** - Configurare CD Pipeline (Deploy)
- [ ] **TASK 5.15** - Creare Runbook Operativo
- [ ] **TASK 5.16** - Documentare API con OpenAPI
- [ ] **TASK 5.17** - Creare Script Migrazione Dati v2.4 → v3.0

#### Docker & Deployment (0/2)
- [ ] **TASK 3.12** - Setup Docker Compose Produzione *(in Docker/AGENTS.md)*
- [ ] **TASK 5.14** - Creare Dockerfile Multi-Stage *(in Docker/AGENTS.md)*

---

### 📈 Statistiche Progresso

| Categoria | Completati | Totali | Percentuale |
|-----------|------------|--------|-------------|
| **MVP** | 20 | 46 | 43% |
| **Fase 2** | 0 | 19 | 0% |
| **TOTALE** | **20** | **65** | 31% |

---

## Struttura Repository

```
Standalone-app-v1/
├── AGENTS.md (questo file)
├── backend/
│   ├── AGENTS.md → 33 task backend (MVP + Fase 2)
│   ├── src/
│   │   ├── estimates/
│   │   ├── market_data/
│   │   ├── sync/
│   │   ├── analytics/
│   │   ├── shared/
│   │   └── infra/
│   └── tests/
│
├── frontend/
│   ├── AGENTS.md → 17 task frontend (MVP + Fase 2)
│   ├── src/
│   │   ├── features/
│   │   ├── shared/
│   │   └── app/
│   └── tests/
│
├── Docker/
│   └── AGENTS.md → 3 task Docker
│
└── Docs/
    └── AGENTS.md → 14 task CI/CD & Docs
```

---

## Priorità Implementazione

### MVP (Ambiente Locale Single-User)
**Obiettivo**: App funzionante localmente per 1 utente, senza autenticazione.

**Backend MVP**:
- ✅ TASK 1.1-1.7: Setup base, value objects, config
- ✅ TASK 2.1, 2.3-2.6: Database, modelli dominio (Ticker, Estimate, Event, MarketData)
- ✅ TASK 2.10-2.16: API endpoints estimates (CRUD)
- ✅ TASK 2.17-2.19: Market data & cache
- ✅ TASK 2.20-2.24: Sync Google Drive & scheduler

**Frontend MVP**:
- ✅ TASK 1.8: Setup decimal.js wrapper
- ✅ TASK 4.1-4.10: Setup + feature estimates completa
- ✅ TASK 4.11-4.12: Dashboard portfolio
- ✅ TASK 4.16: Router & layout

**Docker MVP**:
- ✅ Compose locale con PostgreSQL, backend, frontend
- ✅ Healthchecks base

**Docs MVP**:
- ✅ Test unitari backend/frontend
- ✅ Linting configurato
- ✅ README usage base

---

### Fase 2 (Produzione Multi-User)
**Obiettivo**: Deploy produzione con auth, osservabilità, sicurezza.

**Backend Fase 2**:
- TASK 2.8-2.9, 2.25: User management, JWT auth, RBAC
- TASK 2.26-2.28: Outbox pattern, analytics API, AI service
- TASK 3.1-3.11: Sicurezza avanzata, metrics, backup

**Frontend Fase 2**:
- TASK 4.13-4.14: Market data charts, watchlist
- TASK 4.15: Chat AI (Gemini)

**Docker Fase 2**:
- Compose produzione con Nginx, Redis, Prometheus, Grafana
- SSL/TLS, secrets management

**Docs Fase 2**:
- Test E2E completi
- CI/CD pipeline (GitHub Actions)
- Documentazione API completa

---

## Link Diretti alle Sezioni

### 🐍 [Backend/AGENTS.md](./backend/AGENTS.md)
**Scope**: Python/FastAPI, Domain Logic, Database, API, Sync Drive
- Sezione 1: Linee guida trasversali (7 task)
- Sezione 2: Backend & Data (26 task)
- Sezione 3: Sicurezza & Observability (13 task - Fase 2)

**Regole Backend**:
- Usa Decimal per money, mai float
- Segui layering: api → services → repositories → domain
- Eventi domain per azioni significative
- CQRS: write tramite commands, read tramite query projections

---

### ⚛️ [Frontend/AGENTS.md](./frontend/AGENTS.md)
**Scope**: React 19, TypeScript, TailwindCSS, React Query
- Sezione 1: Setup (1 task)
- Sezione 4: Frontend & UX (16 task)

**Regole Frontend**:
- Usa decimal.js per calcoli finanziari
- API client centralizzato (no fetch diretto)
- Feature modules isolati (no cross-import)
- Componenti shared in `shared/components/`

---

### 🐳 [Docker/AGENTS.md](./Docker/AGENTS.md)
**Scope**: Containerizzazione, Compose, Deployment
- Setup containers backend/frontend/postgres
- Healthchecks e restart policies
- Volume persistence
- Networking isolato

---

### 📚 [Docs/AGENTS.md](./Docs/AGENTS.md)
**Scope**: Testing, CI/CD, Documentazione
- Test unitari (pytest, vitest)
- Test integrazione
- Test E2E (Playwright)
- CI/CD pipeline (GitHub Actions)
- Documentazione API (OpenAPI)

---

## Dipendenze tra Sezioni

```
Backend Setup (1.1-1.7)
  ↓
Backend Core (2.1-2.7) + Frontend Setup (4.1-4.5)
  ↓
Backend API (2.10-2.16) ↔ Frontend Features (4.6-4.12)
  ↓
Docker Compose MVP
  ↓
Tests & Docs
  ↓
[Fase 2] Sicurezza + Observability + Auth
```

---

## Grafo Dipendenze Completo

### Priorità MVP (ambiente locale single‑user):

**Sezione 1**: tutti i task 1.1-1.8 (fondamenta)

**Sezione 2**: 
- Core: 2.1-2.7, 2.10
- API Estimates: 2.11-2.16
- Market Data: 2.17-2.19
- Sync Drive: 2.20-2.24

**Sezione 4**:
- Setup: 4.1-4.5
- Estimates: 4.6-4.10
- Portfolio: 4.11-4.12
- Router: 4.16

**Docker**: Compose locale base

**Docs**: Test unitari + lint base

---

### Fase 2 (produzione multi-user):

**Sezione 2**:
- Auth: 2.8-2.9, 2.25
- Advanced: 2.26-2.28

**Sezione 3**: Tutti i task 3.1-3.11 (sicurezza, metrics, backup)

**Sezione 4**:
- Market Data: 4.13-4.14
- Chat AI: 4.15

**Docker**: Compose produzione con Nginx, Redis, Prometheus

**Docs**: E2E tests + CI/CD completo

---

## Dettaglio Dipendenze

```
Sezione 1 (Setup base):
1.1 → 1.2, 1.3, 1.6, 1.8
1.3 → 1.4 → 1.5
1.6 → 1.7

Sezione 2 (Backend MVP):
2.1 → 2.2 → 2.3 → 2.5 → 2.6
2.3 → 2.7 → 2.10
2.5 + 2.7 → 2.11 → 2.16
2.5 + 2.10 → 2.12 → 2.14 → 2.16
2.6 + 2.12 → 2.15
2.7 + 2.10 → 2.13
2.6 → 2.17 → 2.18 → 2.19
2.1 → 2.20 → 2.21 → 2.22 → 2.23
2.11 + 2.22 → 2.24 → 2.26
2.12 → 2.27 → 2.28

Sezione 2 (Auth - Fase 2):
2.3 → 2.8 → 2.9, 2.25

Sezione 3 (Sicurezza - Fase 2):
Tutti paralleli dopo 2.20

Sezione 4 (Frontend):
4.1 → 4.2 → 4.3 → 4.4 → 4.5
4.5 → 4.6 → 4.7, 4.10, 4.11
4.5 → 4.8 → 4.9
4.6 → 4.13
4.11 → 4.12
4.5 → 4.15
4.6 + 4.11 → 4.16
```

---

## NOTE PER L'LLM ESECUTORE

### Workflow Ideale
1. **Leggi il task completo** prima di iniziare
2. **Verifica le dipendenze** sono soddisfatte
3. **Segui i microstep in ordine** senza saltare
4. **Testa dopo ogni step significativo**
5. **Verifica acceptance criteria** prima di marcare done
6. **Committa con messaggio descrittivo** referenziando task ID
7. **Aggiorna Progress Tracker** marcando task completato

### Se Incontri Blocchi
- **Chiedi chiarimenti** se requisito ambiguo
- **Documenta** scelte implementative non ovvie
- **Segnala** dipendenze mancanti o conflitti
- **NON riscrivere** codice esistente senza conferma

### Convenzioni Commit
```
feat(TASK-X.Y): breve descrizione

- Microstep 1 completato
- Microstep 2 completato
- Test aggiunti per scenario X

Closes #issue-number
```

---

## Risorse Utili

### Backend
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)

### Frontend
- [React 19 Docs](https://react.dev/)
- [TailwindCSS Docs](https://tailwindcss.com/)
- [React Query Docs](https://tanstack.com/query/latest)
- [Recharts Docs](https://recharts.org/)

### Tools
- [Docker Docs](https://docs.docker.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)

---

## Support & Questions

Per domande o chiarimenti:
1. Verifica prima la sezione specifica (Backend/Frontend/Docker/Docs)
2. Controlla acceptance criteria del task
3. Rivedi dipendenze nel grafo
4. Se ancora bloccato: documenta il problema e chiedi help

---

**Buon lavoro! 🚀**