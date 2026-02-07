# TickerTracker Backend

## Descrizione

Backend Python/FastAPI per TickerTracker v3.0 - Sistema di tracking stime trading con architettura DDD/CQRS/Event Sourcing.

## Requisiti

- Python 3.11+
- PostgreSQL 16+ (per ambiente di sviluppo: Docker Compose)
- Redis 7+ (per ambiente di sviluppo: Docker Compose)

## Installazione

### Opzione 1: pip (Scelta Veloce su Windows)

```bash
cd backend

# Attiva virtual environment (se non presente: python -m venv venv)
# Su Windows:
venv\Scripts\activate
# Su Linux/macOS:
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verifica installazione
python scripts/check_deps.py
```

### Opzione 2: Poetry (Raccomandato)

Poetry è il gestore di dipendenze raccomandato per questo progetto.

```bash
# Installa Poetry se non presente
# Windows (PowerShell):
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
# Linux/macOS:
curl -sSL https://install.python-poetry.org | python3 -

# Installa dipendenze
cd backend
poetry install

# Verifica installazione
python scripts/check_deps.py
```

### Opzione 3: PowerShell Script (Windows)

Su Windows puoi usare il build script:

```powershell
cd backend

# Mostra comandi disponibili
.\build.ps1 help

# Installa dipendenze
.\build.ps1 install-pip

# Oppure con Poetry
.\build.ps1 install
```

### Verifica Installazione

Dopo l'installazione, verifica che tutte le dipendenze siano installate correttamente:

```bash
# Opzione 1: Script check_deps.py
python scripts/check_deps.py

# Opzione 2: Make command (su Linux/macOS o con make su Windows)
make check-deps

# Opzione 3: PowerShell (su Windows)
.\build.ps1 check-deps
```

Output atteso:
```
╔═══════════════════════════════════════════════════════════╗
║   VERIFICA DIPENDENZE TICKERTRACKER BACKEND             ║
╚═══════════════════════════════════════════════════════════╝

[Python] ✓ Python 3.11.0

[DIPENDENZE CRITICHE] (Obbligatorie)
  ✓ FastAPI - Web Framework
  ✓ Uvicorn - ASGI Server
  ✓ Pydantic - Data Validation
  ✓ SQLAlchemy - ORM/Database
  ✓ AsyncPG - PostgreSQL Driver
  ✓ Redis - Cache Client
  ✓ YFinance - Market Data
  ✓ Google API Client
  ✓ APScheduler - Job Scheduling

[DIPENDENZE OPZIONALI] (Fase 2)
  ✓ Cryptography - Security
  ✓ Google Auth - Authentication
  ✓ Prometheus - Metrics
  ✓ Structlog - Structured Logging
  ✓ SlowAPI - Rate Limiting

[DIPENDENZE SVILUPPO] (Dev/Testing)
  ✓ Pytest - Testing Framework
  ✓ Pytest AsyncIO - Async Testing
  ✓ Pytest Coverage - Coverage Reports
  ✓ Mypy - Type Checker
  ✓ Ruff - Code Linter/Formatter
  ✓ HTTPX - HTTP Client

==================================================
✓ Tutte le 20 dipendenze sono installate correttamente!
✓ Sistema pronto per lo sviluppo
```

## Configurazione

1. Copia il file di configurazione esempio:
```bash
cp .env.example .env
```

2. Modifica `.env` con i tuoi valori:
```env
# Database
DATABASE_URL=postgresql+asyncpg://ticker:password@localhost:5432/tickertracker

# Cache
REDIS_URL=redis://localhost:6379/0

# Security (genera con: python -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=your-encryption-key-here
JWT_SECRET=your-jwt-secret-here

# Google Drive (opzionale per sync)
GOOGLE_SERVICE_ACCOUNT_JSON={...}
DRIVE_FOLDER_ID=your-folder-id

# API Keys (opzionali)
FINNHUB_API_KEY=your-finnhub-key  # Fase 2
```

## Avvio Database (Sviluppo)

Utilizza Docker Compose per avviare PostgreSQL e Redis:

```bash
# Dalla root del progetto
docker compose up -d db redis
```

Oppure consulta `../Docker/AGENTS.md` per dettagli sul setup Docker completo.

## Health Check & Monitoring

L'applicazione espone endpoint di health check per monitoraggio e Docker health probes:

### Endpoint Disponibili

```bash
# Basic health check (always 200 OK if app is running)
curl http://localhost:8000/health

# Readiness check (dependency checks)
curl http://localhost:8000/health/ready

# Response format
{
  "success": true,
  "data": {
    "status": "ok"  # or "ready"
  },
  "trace_id": "uuid-string",
  "error": null
}
```

### Docker Health Probe

Per aggiungere un HEALTHCHECK nel Dockerfile:

```dockerfile
FROM python:3.13-slim

# ... setup ...

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)"
```

### Kubernetes Health Probes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tickertracker-backend
spec:
  containers:
  - name: backend
    image: tickertracker-backend:latest
    ports:
    - containerPort: 8000
    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 30
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 10
```

## Security Features

L'applicazione include security middleware di base:

### Security Headers

Tutte le risposte HTTP includono header di sicurezza standard:
- `X-Content-Type-Options: nosniff` - Previene MIME sniffing
- `X-Frame-Options: DENY` - Previene clickjacking
- `X-XSS-Protection: 1; mode=block` - Protezione XSS
- `Strict-Transport-Security` - Enforce HTTPS in produzione

### CORS Configuration

Frontend può effettuare richieste da:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)

Per aggiungere altri origin:

```env
CORS_ORIGINS=https://example.com,https://other-domain.com
```

### Rate Limiting

Rate limit semplice in memoria: **60 richieste/minuto per IP**

Per disabilitare in sviluppo locale:

```env
ENABLE_RATE_LIMIT=false
```

---

## Comandi Utili

### Build Script (Windows)

Usa `build.ps1` per eseguire i comandi (alternativa a Make):

```powershell
.\build.ps1 help        # Mostra tutti i comandi
.\build.ps1 check-deps  # Verifica dipendenze
.\build.ps1 lint        # Linting con Ruff
.\build.ps1 format      # Formattazione codice
.\build.ps1 typecheck   # Type checking con Mypy
.\build.ps1 test        # Esegui test
.\build.ps1 test-cov    # Test con coverage report
.\build.ps1 run         # Avvia server dev
.\build.ps1 clean       # Pulisci cache
.\build.ps1 all         # Esegui tutti i controlli
```

### Makefile Commands (Linux/macOS)

Su sistemi Unix, usa Make:

```bash
make help         # Mostra tutti i comandi
make check-deps   # Verifica dipendenze critiche
make lint         # Linting con ruff
make format       # Formattazione codice con ruff
make typecheck    # Type checking con mypy
make test         # Esegui tutti i test
make test-unit    # Solo unit tests
make test-integration  # Solo integration tests
make test-cov     # Test con coverage report
make run          # Avvia server di sviluppo (http://localhost:8000)
make clean        # Rimuovi file temporanei e cache
make export-requirements  # Rigenera requirements.txt da pyproject.toml
make all          # Esegui tutti i controlli (lint, type, test)
```

### Manual Commands

Se preferisci eseguire comandi direttamente:

```bash
# Attiva virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Linting
ruff check src/ tests/

# Code formatting
ruff format src/ tests/
ruff check src/ tests/ --fix

# Type checking
mypy src/

# Testing
pytest tests/                              # Tutti i test
pytest -m unit tests/                      # Solo unit tests
pytest -m integration tests/               # Solo integration tests
pytest --cov=src --cov-report=html tests/  # Con coverage

# Dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Clean up
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type d -name .pytest_cache -exec rm -rf {} +
```

## Struttura Progetto

```
backend/
├── src/                  # Codice sorgente
│   ├── estimates/        # Bounded Context: Stime
│   ├── market_data/      # Bounded Context: Dati di mercato
│   ├── sync/             # Bounded Context: Sincronizzazione Drive
│   ├── analytics/        # Bounded Context: Analytics e AI
│   ├── shared/           # Codice condiviso (value objects, utils)
│   │   ├── domain/       # Valore objects immutabili
│   │   │   └── value_objects/
│   │   │       ├── money.py            # ✅ [1.3] Value Object Money (36 tests)
│   │   │       ├── percentage.py       # ✅ [1.4] Value Object Percentage (39 tests)
│   │   │       └── price_target.py     # ✅ [1.5] Value Object PriceTarget (41 tests)
│   │   ├── infra/        # Infrastruttura layer
│   │   │   ├── config.py              # ✅ [1.6] Configuration Management (27 tests)
│   │   │   ├── security_middleware.py # ✅ [1.7] Security Middleware + Rate Limit (16 tests)
│   │   │   ├── cache/
│   │   │   ├── drive/
│   │   │   ├── logging/
│   │   │   ├── security/
│   │   │   └── yahoo/
│   │   ├── api/          # API layer
│   │   │   └── health_routes.py       # ✅ [1.7] Health Check Endpoints
│   │   ├── schemas/      # Modelli Pydantic condivisi
│   │   │   └── api_response.py     # ✅ [1.2] Risposta API standardizzata
│   │   └── services/     # Servizi condivisi
│   └── main.py           # ✅ [1.7] Entry point FastAPI
├── tests/                # Test
│   ├── unit/             # Unit tests
│   │   └── shared/
│   │       ├── domain/
│   │       │   ├── test_money.py           # ✅ 36 tests ✓
│   │       │   ├── test_percentage.py      # ✅ 39 tests ✓
│   │       │   └── test_price_target.py    # ✅ 41 tests ✓
│   │       ├── test_config.py              # ✅ 27 tests ✓
│   │       └── test_middleware.py          # ✅ 16 tests ✓
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── alembic/              # Migrazioni database
├── scripts/              # Script di utilità
├── .env.example          # ✅ [1.6] Configuration template
├── .gitignore            # ✅ [1.6] Git ignore configuration
├── pyproject.toml        # Configurazione Poetry e tools
├── requirements.txt      # Dipendenze production (pip)
├── requirements-dev.txt  # Dipendenze development (pip)
└── Makefile              # Comandi standardizzati
```

## Implementation Progress

### Phase 1: Foundation & API Structure (7/8 task - 87.5% ✨)

| Task | Descrizione | Status | Tests | Implementation |
|------|-----------|--------|-------|-----------------|
| 1.1 | Setup Struttura Layer Backend | ✅ COMPLETATO | - | Directory structure |
| 1.2 | Modello Risposta API Standard | ✅ COMPLETATO | - | `ApiResponse` schema |
| 1.3 | Value Object Money | ✅ COMPLETATO | 36 ✓ | Decimal-safe operations |
| 1.4 | Value Object Percentage | ✅ COMPLETATO | 39 ✓ | Basis points support |
| 1.5 | Value Object PriceTarget | ✅ COMPLETATO | 41 ✓ | LONG/SHORT validation |
| 1.6 | Config Multi-Ambiente | ✅ COMPLETATO | 27 ✓ | Pydantic Settings + Secrets |
| 1.7 | **Middleware Sicurezza** | ✅ **COMPLETATO** | **16 ✓** | **Headers + CORS + Rate Limit + Healthcheck** |

**Total Tests**: 159 passing ✅

## Documentazione API

Una volta avviato il server, la documentazione interattiva è disponibile su:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architettura

Il backend segue i principi di:

- **Domain-Driven Design (DDD)**: Organizzazione in bounded contexts
- **CQRS**: Separazione command/query
- **Event Sourcing**: Tracciamento completo delle modifiche alle stime
- **Clean Architecture**: Dipendenze verso l'interno, domain al centro

### Layering

Ogni bounded context segue una struttura layered:

- **api/**: Router FastAPI e dependency injection
- **schemas/**: Schema Pydantic per request/response
- **domain/**: Entità, value objects, aggregates
- **services/**: Business logic e orchestrazione
- **repositories/**: Accesso dati e persistenza

## Contribuire

Prima di committare:

```bash
make format      # Formatta codice
make lint        # Verifica linting
make typecheck   # Verifica tipi
make test        # Esegui test
```

## Note per Sviluppatori

### Aggiungere Dipendenze

Con Poetry:
```bash
poetry add nome-pacchetto
make export-requirements  # Aggiorna requirements.txt
```

Con pip:
```bash
pip install nome-pacchetto
pip freeze > requirements.txt  # Aggiorna manualmente
```

### Gestione Migrazioni

Dopo aver modificato i modelli SQLAlchemy:

```bash
make migrate-new  # Crea migrazione
# Rivedi il file generato in alembic/versions/
make migrate      # Applica migrazione
```

### Rigenerare requirements.txt

Se modifichi `pyproject.toml`, rigenera i file requirements:

```bash
make export-requirements
```

## Link Utili

- [AGENTS.md](./AGENTS.md) - Piano atomico task backend
- [../Docs/Piano-operativo-v1.4.md](../Docs/Piano-operativo-v1.4.md) - Piano operativo completo
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Licenza

Proprietario - © 2026 Francesco Di Lecce

---

## Modelli Principali

### SyncJob

Il modello `SyncJob` è utilizzato per tracciare i job di sincronizzazione con Google Drive. Include i seguenti campi principali:

- **id**: Identificativo univoco del job (UUID).
- **job_type**: Tipo di job (enum `SyncJobType` con valori: `INITIAL_IMPORT`, `DAILY_HISTORY_UPDATE`, `ON_ESTIMATE_SAVE`, `MANUAL_SYNC`).
- **status**: Stato del job (enum `SyncJobStatus` con valori: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `PARTIAL`).
- **started_at**: Timestamp di inizio job.
- **finished_at**: Timestamp di fine job (opzionale).
- **error_message**: Messaggio di errore (opzionale).
- **filename**: Nome del file associato al job.
- **checksum_before**: Checksum del file prima del job (opzionale).
- **checksum_after**: Checksum del file dopo il job (opzionale).
- **records_processed**: Numero di record processati.
- **records_failed**: Numero di record falliti.

Il modello include un indice sul campo `started_at` per ottimizzare le query cronologiche.

### AiModelRun

Il modello `AiModelRun` è utilizzato per tracciare le esecuzioni dei modelli AI. Include i seguenti campi principali:

- **id**: Identificativo univoco dell'esecuzione (UUID).
- **estimate_id**: ID della stima associata (FK, opzionale).
- **model_name**: Nome del modello AI.
- **model_version**: Versione del modello AI.
- **prompt_hash**: Hash del prompt per deduplicazione.
- **prompt_tokens**: Numero di token utilizzati nel prompt.
- **completion_tokens**: Numero di token generati nella risposta.
- **latency_ms**: Latenza dell'esecuzione in millisecondi.
- **output_summary**: Riassunto dell'output generato (opzionale).
- **raw_response**: Risposta grezza in formato JSONB (opzionale).
- **created_at**: Timestamp di creazione dell'esecuzione.

Il modello include un indice sui campi `model_name` e `created_at` per ottimizzare le query cronologiche e per modello.
