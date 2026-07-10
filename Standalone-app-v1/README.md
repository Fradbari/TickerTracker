# TickerTracker v3.0 🚀

**TickerTracker v3.0** è un sistema avanzato e professionale per il tracciamento delle stime di trading, progettato con un'architettura robusta basata su **DDD (Domain-Driven Design)**, **CQRS** e **Event Sourcing**.

L'applicazione permette di gestire stime di acquisto/vendita (Long/Short), monitorare i target di prezzo in tempo reale, sincronizzare i dati con Google Drive e interagire con un assistente AI per l'analisi del portfolio.

---

## 🏗️ Architettura & Tech Stack

L'applicazione segue i principi del Clean Architecture e separazione dei ruoli (Separation of Concerns).

### Backend
- **Framework**: Python 3.11+ con **FastAPI**.
- **Database**: **PostgreSQL 16** (SQLAlchemy + Alembic per le migrazioni).
- **Cache**: **Redis** per rate limiting e caching dei dati di mercato.
- **Patterns**: Event Sourcing per l'audit trail delle stime, CQRS con Materialized Views per query prestazionali.
- **Provider Dati**: Integrazione con Yahoo Finance (via yfinance).
- **Auth / RBAC**: Modelli base `User` e `Role` aggiunti in `backend/src/shared/domain` (TASK 2.7).

### Frontend
- **Framework**: **React 18** + **TypeScript**.
- **Build Tool**: **Vite**.
- **Styling**: **TailwindCSS**.
- **Data Fetching**: **React Query** (TanStack Query).
- **Calcoli Finanziari**: **decimal.js** per massima precisione decimale.

### Infrastruttura
- **Containerizzazione**: Docker e Docker Compose.
- **Sync**: Motore di sincronizzazione bidirezionale con **Google Drive API**.

---

## 📂 Struttura del Progetto

```bash
Standalone-app-v1/
├── CLAUDE.md           # Entry point sessione + invarianti architetturali
├── AGENTS.md           # Task ledger + Progress Tracker (fonte di verità)
├── backend/            # Python/FastAPI (src/, alembic/, tests/, docs/)
│   └── docs/           # Deep-dive tecnici (dev): API, SECURITY, PAGINATION, ...
├── frontend/           # React 18/TypeScript (src/features|shared|app)
├── docker/             # Compose/Dockerfile + Docker/AGENTS.md
├── Docs/               # Runbook (ops), Docs/AGENTS.md, Piano operativo (docx)
├── e2e/                # Suite Playwright (playwright.config.ts alla root)
├── scripts/            # Tool di sviluppo (validate_dependencies.py, ...)
└── docker-compose*.yml # base / dev / prod
```

---

## 🚀 Avvio Rapido (Ambiente Docker)

### ⚡ One-Command Start (TASK 3.12)

Avvia **tutti i servizi** (DB, Redis, Backend, Frontend) con un solo comando:

```bash
# 1. Copia le variabili d'ambiente
cp .env.example .env

# 2. Avvia tutto
docker compose up --build
```

L'applicazione sarà disponibile su:

| Servizio | URL |
|----------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **Swagger UI** | http://localhost:8000/docs |
| **PostgreSQL** | localhost:5432 |
| **Redis** | localhost:6379 |

> Il frontend comunica con il backend tramite la rete Docker interna (`http://backend:8000`), configurata automaticamente via `VITE_API_TARGET`.

---

### Avvio Manuale (Servizi Separati)

Per avviare solo DB + Redis (utile durante lo sviluppo locale del backend):

```bash
# Solo infrastruttura
docker compose -f docker-compose.base.yml up -d
```

---

### 1. Prerequisiti
- **Docker** e **Docker Compose** installati sul sistema
- Un account Google Cloud con API Drive abilitate (opzionale, per la sincronizzazione)
- Python 3.11+ (per test script di connettività)

### 2. Configurazione Ambiente
Copia il file di esempio per le variabili d'ambiente:

```bash
cp backend/.env.example backend/.env
# Inserisci le tue chiavi API (Google, Yahoo, Gemini) nel file .env
```

### 3. Avvio Servizi Infrastrutturali (PostgreSQL + Redis)

#### Opzione A: Script di Gestione (Raccomandato)

**Windows (PowerShell)**:
```powershell
.\docker-manage.ps1 up          # Avvia PostgreSQL e Redis
.\docker-manage.ps1 health       # Verifica stato healthcheck
.\docker-manage.ps1 logs         # Mostra log in real-time
.\docker-manage.ps1 down         # Arresta servizi
```

**Linux/macOS (Bash)**:
```bash
chmod +x docker-manage.sh
./docker-manage.sh up            # Avvia PostgreSQL e Redis
./docker-manage.sh health        # Verifica stato healthcheck
./docker-manage.sh logs          # Mostra log in real-time
./docker-manage.sh down          # Arresta servizi
```

#### Opzione B: Docker Compose Diretto

```bash
# Avvia solo database e cache (servizi base)
docker compose -f docker-compose.base.yml up -d

# Verifica lo stato
docker compose -f docker-compose.base.yml ps

# Visualizza log
docker compose -f docker-compose.base.yml logs -f

# Arresta servizi
docker compose -f docker-compose.base.yml down
```

### 4. Avvio Ambiente Completo (Backend + Frontend)

Una volta che PostgreSQL e Redis sono in esecuzione:

```bash
# Avvia backend, frontend, database e cache
docker compose \
  -f docker-compose.base.yml \
  -f docker-compose.dev.yml \
  up --build
```

L'applicazione sarà disponibile ai seguenti indirizzi:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **PostgreSQL**: `localhost:5432` (user: `tickertracker`, password: `devpassword`)
- **Redis**: `localhost:6379` (password: `devpassword`)

### 5. Test di Connettività

Dopo aver avviato i servizi, verifica la connettività:

```bash
# Attiva venv nella root
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Testa connessioni
python scripts/test_docker_services.py
```

Expected output:
```
✓ PostgreSQL OK - PostgreSQL 16.x
✓ Redis OK - vX.X.X - Memory: XXM
✓ PostgreSQL Advanced OK - INSERT/SELECT/DELETE funzionante
```

### 6. Pulizia (Rimozione Dati)

⚠️ **ATTENZIONE**: Questo comando rimuove TUTTI i dati persistenti!

```bash
# Windows
.\docker-manage.ps1 clean

# Linux/macOS
./docker-manage.sh clean

# Oppure direttamente
docker compose -f docker-compose.base.yml down -v
```

---

## � CI/CD e Pipeline Actions

Il progetto include pipeline CI configurate con GitHub Actions (vedi `.github/workflows/ci.yml`).

- **backend-lint**: Type checking/linting
- **backend-test** / **frontend-test**: Test suite con postgres/redis e reportistica Codecov
- **backend-security**: File system vulnerality scanner (`aquasecurity/trivy-action`)
- **e2e-test**: Playwright actions in sandboxed OS containers

---

## �📋 Struttura Docker Compose

- **`docker-compose.yml`** (TASK 3.12) ← **Entry point principale**
  - Tutti i servizi: PostgreSQL 16, Redis 7, Backend FastAPI, Frontend React
  - Avvio one-command: `docker compose up --build`
  - Volume mount per hot-reload (src/ sincronizzata con il container)
  - `VITE_API_TARGET=http://backend:8000` per routing interno Docker
  - Legge variabili da `.env` (root del progetto)

- **`docker-compose.base.yml`** (TASK 2.2)
  - Servizi infrastrutturali standalone: PostgreSQL 16, Redis 7
  - Utile per avviare solo DB + Redis durante sviluppo locale del backend
  - Network condivisa: `ticker-network`
  - Volumi persistenti: `postgres-data`, `redis-data`

- **`docker-compose.prod.yml`** (TASK 5.14 — pianificato)
  - Configurazione produzione (no hot-reload, resource limits, Nginx)

---

## 🛠️ Linee Guida per lo Sviluppo

Il progetto adotta un approccio **Atomic Development**. Ogni modifica deve essere tracciata tramite i file `AGENTS.md` presenti in ogni sezione.

### Workflow di Sviluppo

1. **Consulta `AGENTS.md`**: Leggi la roadmap dei task e le dipendenze prima di iniziare basandoti sugli ID (es. TASK 1.1).
   - [AGENTS.md principale](./AGENTS.md) - Progress tracker globale
   - [backend/AGENTS.md](./backend/AGENTS.md) - Task backend
   - [frontend/AGENTS.md](./frontend/AGENTS.md) - Task frontend
   - [Docker/AGENTS.md](./Docker/AGENTS.md) - Task Docker
   - [AGENTS.md — §Sprint UX](./AGENTS.md) - Sprint UX (TASK C/D/B/A); per il workflow task-driven usare root `AGENTS.md`

2. **Standard di Codifica**:
    - **Backend**: Usa sempre `Decimal` per valori monetari. Segui il layering api → services → repositories → domain.
    - **Frontend**: Usa `decimal.js` per i calcoli. Utilizza i componenti della cartella `shared/`.

3. **Test prima di procedere**: Assicurati che ogni nuovo microstep passi i test unitari.

---

## 🔧 Strumenti di Sviluppo

### Validazione Dipendenze Task

Prima di iniziare l'implementazione, verifica la coerenza del grafo dipendenze:

```bash
# Da root del progetto
python scripts/validate_dependencies.py
```

**Output:**
- ✅ Task totali e distribuzione per sezione
- ✅ Rilevamento dipendenze circolari
- ✅ Verifica task referenziati esistenti
- ⚠️ Warning su gap numerazione
- 🚀 Entry points (task senza dipendenze)

**Quando eseguirlo:**
- Prima di iniziare un nuovo task
- Dopo modifiche agli AGENTS.md
- Prima di un merge su branch principale

### Setup Ambiente Locale (Poetry)

Per sviluppo con IDE e hot-reload rapido:

```bash
# Backend
cd backend/
poetry install
poetry shell

# Avvia solo infrastruttura Docker
docker compose -f docker-compose.base.yml up -d

# Avvia backend locale
uvicorn src.main:app --reload

# Frontend (in altra shell)
cd frontend/
npm install
npm run dev
```

### Linting & Type Checking

```bash
# Backend
cd backend/
ruff check .           # Linting
mypy src/              # Type checking
pytest tests/          # Run tests
pytest --cov=src       # Con coverage

# Frontend
cd frontend/
npm run lint           # ESLint
npm run type-check     # TypeScript
npm run test           # Vitest
```

---

## 📚 Documentazione

### Mappa della documentazione

- **[CLAUDE.md](./CLAUDE.md)** — entry point di sessione + invarianti architetturali
- **[AGENTS.md](./AGENTS.md)** — task ledger + Progress Tracker (fonte di verità sullo stato)
- **Track docs (Testing/CI-CD/Runbook)** — [`Docs/AGENTS.md`](./Docs/AGENTS.md)
- **Backend deep-dive (dev)** — [`backend/docs/`](./backend/docs/) (API, SECURITY, PAGINATION, ALEMBIC, ...)
- **Runbook operativi (ops)** — [`Docs/runbook/`](./Docs/runbook/) (startup, recovery, outage, monitoring)
- **Backend API Docs** — http://localhost:8000/docs (quando l'app è running)
- **[Piano di lavoro v2](./Docs/piano-di-lavoro-v2.md)** — documento unico di governo della fase di sviluppo (roadmap MVP residuo + Fase 2); piano operativo storico in [`Docs/archive/`](./Docs/archive/Piano-operativo-v1.7-estratto.md)

### Guide Rapide

- **Architecture / Best Practices**: [CLAUDE.md](./CLAUDE.md) → Critical Architectural Invariants
- **Task Dependencies**: "Grafo Dipendenze Completo" in [AGENTS.md](./AGENTS.md)
- **Database Schema**: [CLAUDE.md](./CLAUDE.md) + [`backend/docs/ESTIMATE_SUMMARY_VIEW.md`](./backend/docs/ESTIMATE_SUMMARY_VIEW.md)

---

## 📊 Roadmap & Stato del Progetto

> **Fonte di verità unica**: il Progress Tracker ufficiale (MVP + Fase 2, statistiche, dipendenze) vive in [AGENTS.md](./AGENTS.md). Le tabelle di avanzamento qui sono state rimosse per evitare duplicazioni e dati incoerenti.

**Fasi ad alto livello:**
- **MVP — Ambiente Locale Single-User**: app funzionante localmente per 1 utente, senza autenticazione (backend core + dati, API estimates, market data & cache, sync Drive & scheduler, frontend estimates/portfolio, compose locale). Dettaglio task: [`AGENTS.md`](./AGENTS.md).
- **Fase 2 — Produzione Multi-User**: deploy produzione con auth, osservabilità, sicurezza (RBAC, pattern outbox, security middleware, metrics, runbook, E2E + CI/CD). Dettaglio task: [`AGENTS.md`](./AGENTS.md).

### 🗄️ Database Schema

PostgreSQL 16. Tabelle core: `tickers`, `market_data`, `estimates`, `estimate_events`, `ai_model_runs`, `sync_jobs`, `users`, `roles`, `user_roles`. Materialized view CQRS `estimate_summary_view` (refresh concorrente, query < 5ms).

- Workflow migrazioni Alembic + migrazioni correnti: [`backend/docs/ALEMBIC.md`](./backend/docs/ALEMBIC.md)
- Dettagli materialized view (CQRS): [`backend/docs/ESTIMATE_SUMMARY_VIEW.md`](./backend/docs/ESTIMATE_SUMMARY_VIEW.md)
- Invarianti architetturali (Decimal, CQRS, outbox): [`CLAUDE.md`](./CLAUDE.md)

---

## 🤝 Contribuire

### Workflow Git

1. **Branch naming**: `feature/TASK-X.Y-description`
2. **Commit convention**: 
   ```
   feat(TASK-X.Y): breve descrizione
   
   - Microstep 1 completato
   - Microstep 2 completato
   ```
3. **Pull Request**: Includi task ID e checklist acceptance criteria
4. **Code Review**: Almeno 1 approval richiesto
5. **CI Green**: Tutti i test devono passare

### Prima di Committare

```bash
# Valida dipendenze
python scripts/validate_dependencies.py

# Run tests
cd backend && pytest
cd frontend && npm run test

# Lint check
cd backend && ruff check .
cd frontend && npm run lint
```

---

## 🔒 Sicurezza

### Reporting Vulnerabilities

Per segnalare vulnerabilità di sicurezza, contattare privatamente il maintainer.

### Security Checklist

- ✅ Dependabot alerts enabled
- ✅ Security scanning in CI (Trivy)
- ✅ No secrets in code (use .env)
- ✅ HTTPS enforcement
- ✅ Input validation (Pydantic)

---

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/Fradbari/TickerTracker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Fradbari/TickerTracker/discussions)
- **Documentation**: Consulta i file AGENTS.md e Piano Operativo

---

## 📜 Licenza

Questo progetto è rilasciato come sorgente aperto per uso educativo/personale. Nessun file `LICENSE` è incluso nel repository; ogni dipendenza mantiene la propria licenza dichiarata in `node_modules/`, `.venv/` e nei rispettivi `dist-info`.

---

**Versione:** 3.0  
**Status:** In Sviluppo (MVP)  
**Ultimo aggiornamento:** 7 Febbraio 2026
