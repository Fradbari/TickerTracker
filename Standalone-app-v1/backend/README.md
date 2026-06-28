# TickerTracker Backend

> ↗ Entry point di progetto e invarianti architetturali: vedi [`../CLAUDE.md`](../CLAUDE.md) · Task ledger backend e completed-task history: vedi [`AGENTS.md`](AGENTS.md)

## Descrizione

Backend Python/FastAPI per TickerTracker v3.0 — sistema di tracking stime di trading con architettura **DDD/CQRS/Event Sourcing**. Stack: FastAPI, SQLAlchemy 2.0 (async) + Alembic, PostgreSQL 16, Redis 7, APScheduler.

## Requisiti

- **Python 3.11+**
- **PostgreSQL 16+** (sviluppo: Docker Compose)
- **Redis 7+** (sviluppo: Docker Compose)
- **Poetry** (gestore dipendenze raccomandato)

## Installazione

### Opzione 1: Poetry (Raccomandato)

```bash
cd backend
# Installa Poetry se assente:
#   Windows (PowerShell): (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
#   Linux/macOS:          curl -sSL https://install.pythonpoetry.org | python3 -
poetry install
python scripts/check_deps.py   # verifica le 20 dipendenze critiche/opzionali/dev
```

### Opzione 2: pip

```bash
cd backend
# Windows: venv\Scripts\activate   |   Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python scripts/check_deps.py
```

### Opzione 3: PowerShell Script (Windows)

```powershell
cd backend
.\build.ps1 help          # elenco comandi
.\build.ps1 check-deps    # verifica dipendenze
```

## Configurazione

```bash
cp .env.example .env
```

Variabili chiave (vedi `.env.example` per la lista completa):

```env
DATABASE_URL=postgresql+asyncpg://ticker:password@localhost:5432/tickertracker
REDIS_URL=redis://localhost:6379/0
ENCRYPTION_KEY=<genera con: python -c "import secrets; print(secrets.token_urlsafe(32))">
JWT_SECRET=<genera come sopra>
GOOGLE_SERVICE_ACCOUNT_JSON={...}   # opzionale, per Drive sync
DRIVE_FOLDER_ID=<folder-id>          # opzionale
FINNHUB_API_KEY=<key>                # opzionale, Fase 2
```

## Avvio Database (Sviluppo)

```bash
# Dalla root del progetto
docker compose up -d db redis
```

Per il setup Docker completo (backend + frontend + db + redis) vedi [`../README.md`](../README.md) e [`../docker/AGENTS.md`](../docker/AGENTS.md).

## Avvio Backend (Sviluppo Locale)

```bash
cd backend
poetry shell                       # o attiva il venv
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API disponibili: `http://localhost:8000` · Swagger UI: `http://localhost:8000/docs`

## Struttura Progetto

```
backend/
├── src/
│   ├── estimates/        # Bounded Context: Stime (DDD: api/domain/services/repositories)
│   ├── market_data/      # Bounded Context: Dati di mercato + provider
│   ├── sync/             # Bounded Context: sincronizzazione Google Drive (csv/json parsers, sync_job)
│   ├── analytics/        # Bounded Context: Analytics e AI
│   ├── shared/           # Codice condiviso
│   │   ├── domain/value_objects/   # Money, Percentage, PriceTarget (Decimal)
│   │   ├── infra/                  # config, security, cache, drive, logging, metrics, yahoo
│   │   ├── api/                    # health_routes
│   │   ├── schemas/                # api_response, pagination, validators
│   │   ├── repositories/
│   │   ├── services/
│   │   └── core/
│   ├── infra/            # outbox, scheduler (background worker)
│   └── main.py           # entry point FastAPI
├── tests/                # unit / infra / shared / e2e (marker: unit, integration, e2e, slow, chaos, properties)
├── alembic/              # migrazioni DB
├── docs/                 # deep-dive tecnici (audience: dev) — vedi sezione sotto
└── scripts/              # check_deps, refresh_estimate_summary_view, migrazione legacy, ecc.
```

> Dettagli task per modulo e completed-task history: [`AGENTS.md`](AGENTS.md).

## Comandi Utili

### Makefile (Linux/macOS)

```bash
make help              # elenco comandi
make check-deps        # verifica dipendenze critiche
make lint              # ruff
make format            # ruff format
make typecheck         # mypy
make test              # tutti i test
make test-unit         # solo unit (marker)
make test-integration  # solo integration
make test-cov          # test + coverage
make run               # server dev (http://localhost:8000)
make clean
make all               # lint + type + test
```

### Build Script (Windows)

```powershell
.\build.ps1 help        # elenco
.\build.ps1 lint
.\build.ps1 typecheck
.\build.ps1 test
.\build.ps1 test-cov
.\build.ps1 run
.\build.ps1 all
```

### Comandi Manuali

```bash
# Linting / formattazione / type-check
ruff check src/ tests/
ruff format src/ tests/
mypy src/

# Testing (marker in pyproject.toml [tool.pytest.ini_options])
pytest tests/                              # tutti
pytest -m unit tests/                      # solo unit
pytest -m integration tests/               # solo integration
pytest tests/e2e/test_legacy_compatibility.py -v
pytest --cov=src --cov-report=html tests/  # coverage

# Dipendenze
poetry add <pkg>              # poi: make export-requirements
```

## Documentazione Tecnica (deep-dive)

I dettagli implementativi di ogni sottosistema vivono in [`docs/`](docs/). Questo README non li duplica.

| Argomento | Documento |
|---|---|
| Connection pooling + diagnostica `/health/pool` | [`docs/CONNECTION-POOL.md`](docs/CONNECTION-POOL.md) |
| Cursor-based pagination | [`docs/PAGINATION.md`](docs/PAGINATION.md) |
| Security headers, API Key, CSP, rate limit, ordine middleware | [`docs/SECURITY.md`](docs/SECURITY.md) |
| Structured logging + correlation ID | [`docs/LOGGING.md`](docs/LOGGING.md) |
| Metriche Prometheus (`/metrics`, `@track_duration`) | [`docs/METRICS.md`](docs/METRICS.md) |
| Encryption at rest (Fernet, `EncryptedString`, key rotation) | [`docs/ENCRYPTION.md`](docs/ENCRYPTION.md) |
| Input validation (ticker, price, percentage, date range) | [`docs/VALIDATION.md`](docs/VALIDATION.md) |
| Workflow Alembic + migrazioni correnti | [`docs/ALEMBIC.md`](docs/ALEMBIC.md) |
| Data lineage (ingestion/source timestamps, provider) | [`docs/LINEAGE.md`](docs/LINEAGE.md) |
| Health checks (`/health`, `/health/ready`, `/health/pool`, 503) | [`docs/HEALTH.md`](docs/HEALTH.md) |
| Data quality monitor (cron 06:00 UTC) | [`docs/DATA-QUALITY.md`](docs/DATA-QUALITY.md) |
| APScheduler jobs + pattern Outbox (retry, dead-letter, idempotenza) | [`docs/SCHEDULER.md`](docs/SCHEDULER.md) |
| API Reference (endpoints Estimates & Market Data, error codes) | [`docs/API-REFERENCE.md`](docs/API-REFERENCE.md) |
| Market Data Provider pattern + caching/retry | [`docs/MARKET_DATA_PROVIDER.md`](docs/MARKET_DATA_PROVIDER.md) |
| CQRS materialized view `estimate_summary_view` | [`docs/ESTIMATE_SUMMARY_VIEW.md`](docs/ESTIMATE_SUMMARY_VIEW.md) |

### Sezioni speciali (riferimento)

- **Database schema** (tabelle core + materialized views): vedi `CLAUDE.md` → Critical Architectural Invariants e [`docs/ESTIMATE_SUMMARY_VIEW.md`](docs/ESTIMATE_SUMMARY_VIEW.md).
- **Market Data Provider / Caching & Retry**: [`docs/MARKET_DATA_PROVIDER.md`](docs/MARKET_DATA_PROVIDER.md).
- **SyncJob / AiModelRun** (entity di dominio): docstring nei modelli SQLAlchemy; per il pattern outbox vedi [`docs/SCHEDULER.md`](docs/SCHEDULER.md).
- **Chaos Testing / Migrazione Legacy v2.4 → v3.0**: tracciati in [`AGENTS.md`](AGENTS.md) (TASK 5.9, 5.17); script in `backend/scripts/`.

## Contribuire

### Prima di Committare

```bash
make all                 # lint + type + test (o: .\build.ps1 all su Windows)
```

### Standard

- **Decimal precision**: `Decimal` SEMPRE per importi/prezzi/percentuali, mai `float`. Colonne DB `DECIMAL(10,4)`/`DECIMAL(8,4)`. Dettagli: `CLAUDE.md` → Critical Architectural Invariants.
- **Layering**: `api → services → repositories → domain`. Nessun cross-import tra bounded context (comunicazione solo via `shared/`).
- **Event Sourcing**: ogni azione significativa emette un evento di dominio (`EstimateEvent`).
- **Convenzioni commit**: `feat(TASK-X.Y): descrizione` (vedi [`../AGENTS.md`](../AGENTS.md)).
- **Validatore dipendenze** (dalla root): `python scripts/validate_dependencies.py`.

### Gestione Migrazioni (Alembic)

```bash
cd backend
alembic revision --autogenerate -m "descrizione"
# rivedi il file generato in alembic/versions/
alembic upgrade head
```

> Gotcha: `alembic revision --autogenerate` richiede i modelli importati in `env.py` (`target_metadata = Base.metadata`). Dettagli: [`docs/ALEMBIC.md`](docs/ALEMBIC.md).

## Link Utili

- ↗ Entry point progetto: [`../CLAUDE.md`](../CLAUDE.md)
- Task ledger + completed-task history: [`AGENTS.md`](AGENTS.md)
- Setup Docker / Quick Start globale: [`../README.md`](../README.md)
- Docker track: [`../docker/AGENTS.md`](../docker/AGENTS.md)
- Runbook operativi (produzione): [`../docs/runbook/`](../docs/runbook/)

## Licenza

Progetto rilasciato come sorgente aperto per uso educativo/personale. Nessun file `LICENSE` incluso; ogni dipendenza mantiene la propria licenza dichiarata in `.venv/` e nei rispettivi `dist-info`.
