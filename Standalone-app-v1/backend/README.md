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

## Connection Pooling (Task 3.10)

Il database engine usa `AsyncAdaptedQueuePool` (wrapper asincrono di SQLAlchemy `QueuePool`) con parametri configurabili via variabili d'ambiente:

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `DB_POOL_SIZE` | 5 | Connessioni persistenti nel pool (5=dev, 10=prod) |
| `DB_MAX_OVERFLOW` | 10 | Connessioni extra oltre pool_size (10=dev, 20=prod) |
| `DB_POOL_TIMEOUT` | 30 | Secondi di attesa per una connessione dal pool |
| `DB_POOL_RECYCLE` | 1800 | Secondi dopo i quali una connessione viene riciclata (30 min) |
| `DB_POOL_PRE_PING` | True | Esegui SELECT 1 prima di usare una connessione |

### Diagnostica Pool

```bash
# Endpoint dedicato pool status
curl http://localhost:8000/health/pool
# {"pool_size": 5, "checked_in": 5, "checked_out": 0, "overflow": 0, "invalid": 0}

# Pool status incluso anche in /health
curl http://localhost:8000/health | jq .connection_pool

# Metriche Prometheus (aggiornate ad ogni scrape)
curl http://localhost:8000/metrics | grep db_pool
# db_pool_checked_out 0.0
# db_pool_checked_in 5.0
# db_pool_overflow 0.0
# db_pool_size 5.0
```

### Tuning per ambiente

```env
# Development (default)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Production (esempio)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=15
DB_POOL_RECYCLE=900
```

## Cursor-Based Pagination (Task 3.11)

Il sistema supporta la paginazione cursor-based per la history di mercato, con costo O(1) per pagina indipendente dalla dimensione del dataset.

### Endpoint

```
GET /api/market/history/{ticker}/paginated
```

## Strumenti CI/CD (GitHub Actions)

Il progetto utilizza **GitHub Actions** per la Continuous Integration e il Deploy automatico (vedi file `.github/workflows/ci.yml` e `.github/workflows/cd.yml`).

### Workflow `ci.yml`
- I job vengono avviati per *push* e *pull request* sui rami `main` e `develop`.
- **backend-lint**: Linting (`Ruff`) e Type Checking (`MyPy`).
- **backend-test**: Test suite con `pytest` asincrono, simulando i container PostgreSQL e Redis come services effimeri.
- **backend-security**: Scansione vulnerabilità (`aquasecurity/trivy-action`).
- **frontend-test & e2e-test**: Suite speculari su React e test end-to-end integrali con *Playwright*.

### Workflow `cd.yml`
Pipeline di Continuous Deployment con trigger separato.
- Crea *Build* delle nuove immagini Docker (backend e frontend).
- Push sul *GitHub Container Registry* (GHCR).
- Applica i tag corti tramite metadati (es. `sha-<commit>`). 
- Avvia Webhooks remoti verso Staging (da `develop`) e verso Production (da `main` - **Richiede Approval**). Include possibilità passiva di Rollback lanciando lo stesso yml con un Tag personalizzato.
- **Codecov**: È supportata la reportistica coverage tramite `codecov-action` caricando `coverage.xml`.  Richiede la variabile segreta repository `CODECOV_TOKEN`.

Per simulare questo task in locale (es. backend tests):
```bash
# Eseguire test
pytest --cov=src --cov-report=xml tests/

# Analisi statica e code convention
ruff check .
mypy src/
```

### Query Parameters

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| `cursor` | — | Cursore opaco dalla risposta precedente |
| `direction` | `next` | `next` (avanti) o `prev` (indietro) |
| `limit` | `50` | Items per pagina (1–500) |
| `start_date` | — | Filtro data minima (YYYY-MM-DD, opzionale) |
| `end_date` | — | Filtro data massima (YYYY-MM-DD, opzionale) |

### Navigazione

```bash
# Prima pagina (senza cursor)
curl "http://localhost:8000/api/market/history/AAPL/paginated?limit=10"

# Pagina successiva (usa next_cursor dalla risposta)
curl "http://localhost:8000/api/market/history/AAPL/paginated?limit=10&cursor=<next_cursor>"

# Con filtro date
curl "http://localhost:8000/api/market/history/AAPL/paginated?start_date=2024-01-01&end_date=2024-12-31&limit=20"
```

### Formato Risposta

```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "items": [...],
    "next_cursor": "eyJkYXRlIjogIjIwMjQtMDEtMTUifQ",
    "prev_cursor": null,
    "has_more": true,
    "total_in_page": 50,
    "limit": 50
  }
}
```

### Note

- Il cursore è **opaco** (base64url, no padding): i client non devono interpretarne il contenuto.
- I filtri `start_date`/`end_date` delimitano la finestra dati e rimangono fissi durante tutta la navigazione.
- La navigazione è **sequenziale**: non è possibile saltare a pagine arbitrarie.
- Modulo: `src/shared/repositories/pagination.py` — esportato via `src/shared/repositories/__init__.py`.

## Security Features

L'applicazione include un sistema di security middleware multi-livello:

### Security Headers ✅ [1.7] + [3.1]

Tutte le risposte HTTP includono header di sicurezza standard:
- `X-Content-Type-Options: nosniff` - Previene MIME sniffing
- `X-Frame-Options: DENY` - Previene clickjacking
- `X-XSS-Protection: 1; mode=block` - Protezione XSS
- `Strict-Transport-Security` - Enforce HTTPS (solo su connessioni HTTPS)
- `Content-Security-Policy` - Configurable CSP policy

### API Key Authentication ✅ [3.1]

Autenticazione via API Key opzionale (disabilitata in sviluppo locale).  
Quando abilitata, ogni richiesta deve includere l'header `X-API-Key`.

```env
ENABLE_API_KEY_AUTH=true
API_KEY=your-secret-api-key-here

# Percorsi esenti da autenticazione (separati da virgola)
API_KEY_EXEMPT_PATHS=/health,/health/ready,/health/db,/docs,/openapi.json,/redoc
```

La validazione usa `secrets.compare_digest` per resistere a timing attacks.

### Content Security Policy ✅ [3.1]

CSP policy configurabile tramite variabile d'ambiente:

```env
CSP_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
```

Impostare `CSP_POLICY=` (vuoto) per disabilitare l'header.

### Structured Request Logging ✅ [3.1]

Ogni richiesta viene loggata via `structlog` con campi strutturati:
- `method`, `path`, `status_code`, `duration_ms`
- `client_ip` (con supporto `X-Forwarded-For` per proxy multipli)
- `request_id` (per tracciamento distribuito)

```env
REQUEST_LOG_ENABLED=true   # Disabilitare in test per ridurre noise
```

### CORS Configuration

Frontend può effettuare richieste da:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)

Per aggiungere altri origin:

```env
CORS_ORIGINS=https://example.com,https://other-domain.com
```

### Rate Limiting (Task 3.2)

Rate limiting Redis-backed tramite **slowapi**, con limiti per-endpoint e IP whitelist.

| Endpoint | Limite di default |
|---|---|
| Tutti gli endpoint | `100/minute` |
| `POST /api/estimates` | `30/minute` |
| `GET /api/market/price/{ticker}` | `60/minute` |
| `POST /api/chat` | `10/minute` |

**Configurazione chiave `.env`:**

```env
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_SLOWAPI_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_WHITELIST_IPS=["127.0.0.1","::1"]
```

In assenza di Redis raggiungibile il sistema effettua il fallback automatico a storage in-memory senza interrompere il servizio.

Le risposte 429 includono gli header `Retry-After` e `X-RateLimit-Limit` e un body JSON nel formato API standard.

**Nota per i route handler:** endpoint decorati con `@limiter.limit()` **devono** avere sia `request: Request` che `response: Response` come parametri (richiesto da slowapi per l'iniezione degli header).

### Middleware Execution Order

I middleware vengono eseguiti nel seguente ordine (dal più esterno al più interno):

```
Request → _RequestContextMiddleware [3.2] → SlowAPIMiddleware [3.2] → SecurityMiddleware [3.1] → RateLimitMiddleware [1.7] → CORSMiddleware → SecurityHeadersMiddleware → Routes
```

`_RequestContextMiddleware` popola la ContextVar con il request corrente (necessaria per la whitelist IP zero-arg); `SlowAPIMiddleware` applica i rate limit; `SecurityMiddleware` valida l'API Key.

---

## API Endpoints

### Estimates API

API per gestione stime di trading con tracking completo e audit trail.

#### Standard di Risposta

Tutte le risposte seguono lo standard `ApiResponse[T]`:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "trace_id": "uuid-string"
}
```

In caso di errore:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  },
  "trace_id": "uuid-string"
}
```

#### Endpoints Disponibili

##### 1. Crea Estimate

```http
POST /api/estimates
Content-Type: application/json

{
  "ticker_id": "uuid",
  "direction": "LONG",
  "target_profit_percent": "15.0",
  "stop_loss_percent": "5.0",
  "ai_model": "gpt-4",
  "ai_confidence": "75.0",
  "ai_reasoning": "Strong bullish indicators"
}
```

Risposta (201):
```json
{
  "success": true,
  "data": {
    "estimate": {
      "id": "uuid",
      "ticker_id": "uuid",
      "direction": "LONG",
      "status": "OPEN",
      "start_price": "100.00",
      "target_price": "115.00",
      "stop_loss_price": "95.00",
      ...
    },
    "message": "Estimate created successfully"
  },
  "trace_id": "uuid"
}
```

##### 2. Lista Estimates (con filtri)

```http
GET /api/estimates?ticker_id=uuid&status=OPEN&limit=20
```

Query Parameters:
- `ticker_id` (UUID): Filtra per ticker
- `user_id` (UUID): Filtra per utente
- `status` (string): OPEN, CLOSED_WIN, CLOSED_LOSS, CLOSED_MANUAL, EXPIRED
- `direction` (string): LONG, SHORT
- `include_deleted` (bool): Includi cancellati logicamente
- `limit` (int): Items per pagina (1-100)
- `cursor` (string): Cursore paginazione

Risposta (200):
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 42,
    "page_info": {
      "has_next_page": true,
      "has_previous_page": false,
      "next_cursor": "eyJpZCI6IjEyMyJ9",
      "previous_cursor": null
    }
  },
  "trace_id": "uuid"
}
```

##### 3. Get Estimate Dettaglio

```http
GET /api/estimates/{estimate_id}
```

Risposta (200):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "ticker_id": "uuid",
    "status": "OPEN",
    "direction": "LONG",
    "start_price": "100.00",
    "target_price": "115.00",
    "stop_loss_price": "95.00",
    "exit_price": null,
    "realized_pnl": null,
    "created_at": "2024-01-15T10:00:00Z",
    ...
  },
  "trace_id": "uuid"
}
```

##### 4. Aggiorna Estimate

```http
PATCH /api/estimates/{estimate_id}
Content-Type: application/json

{
  "target_profit_percent": "20.0",
  "stop_loss_percent": "7.5",
  "ai_model": "gpt-4-turbo"
}
```

Risposta (200):
```json
{
  "success": true,
  "data": {
    "estimate": { ... },
    "message": "Estimate updated successfully"
  },
  "trace_id": "uuid"
}
```

##### 5. Chiudi Estimate

```http
DELETE /api/estimates/{estimate_id}
Content-Type: application/json

{
  "exit_price": "115.00",
  "final_status": "CLOSED_WIN"
}
```

Risposta (200):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "CLOSED_WIN",
    "message": "Estimate closed successfully with status CLOSED_WIN"
  },
  "trace_id": "uuid"
}
```

##### 6. Get Audit Trail

```http
GET /api/estimates/{estimate_id}/history
```

Risposta (200):
```json
{
  "success": true,
  "data": {
    "estimate_id": "uuid",
    "audit_trail": [
      {
        "event_id": "uuid",
        "event_type": "CREATED",
        "timestamp": "2024-01-15T10:00:00Z",
        "user_id": "uuid",
        "description": "Estimate created: LONG at $100.00",
        "changes": [...]
      },
      ...
    ],
    "summary": {
      "total_events": 5,
      "first_event_at": "2024-01-15T10:00:00Z",
      "last_event_at": "2024-01-20T15:30:00Z",
      "event_type_counts": {
        "CREATED": 1,
        "UPDATED": 2,
        "CLOSED": 1
      }
    }
  },
  "trace_id": "uuid"
}
```

#### Codici di Errore

| Codice | Descrizione |
|--------|-------------|
| `TICKER_NOT_FOUND` | Ticker ID non esiste |
| `ESTIMATE_NOT_FOUND` | Estimate ID non trovato |
| `ESTIMATE_ALREADY_CLOSED` | Tentato update/close su estimate già chiuso |
| `INVALID_PRICE` | Prezzi calcolati non validi |
| `INVALID_ESTIMATE_STATE` | Stato estimate non valido per operazione |
| `MARKET_DATA_UNAVAILABLE` | Dati di mercato non disponibili |
| `INTERNAL_ERROR` | Errore interno server |

#### Testing API

Per testare gli endpoint:

1. **Swagger UI**: Avvia il server e apri http://localhost:8000/docs
2. **ReDoc**: Documentazione alternativa su http://localhost:8000/redoc
3. **cURL/Postman**: Usa i sample sopra
4. **Script Python**: Vedi `tests/test_estimate_routes.py`

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
pytest tests/e2e/test_legacy_compatibility.py -v  # Test backward compatibility sync
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
│   │   │   │   └── config.py         # ✅ [3.5] configure_logging (JSON structlog), CorrelationIDMiddleware (18 tests)
│   │   │   ├── metrics/
│   │   │   │   ├── metrics.py        # ✅ [3.6] Counter/Gauge/Histogram business+technical, @track_duration (24 tests)
│   │   │   │   └── routes.py         # ✅ [3.6] GET /metrics Prometheus scrape endpoint
│   │   │   ├── security/
│   │   │   │   ├── middleware.py      # ✅ [3.1] SecurityMiddleware (API key, CSP, request logging, 29 tests)
│   │   │   │   ├── rate_limit.py     # ✅ [3.2] Rate Limiting slowapi+Redis (33 tests)
│   │   │   │   └── encryption.py     # ✅ [3.4] EncryptedString TypeDecorator (Fernet AES-128), rotate_key (35 tests)
│   │   │   └── yahoo/
│   │   ├── api/          # API layer
│   │   │   └── health_routes.py       # ✅ [1.7] Health Check Endpoints
│   │   ├── schemas/      # Modelli Pydantic condivisi
│   │   │   ├── api_response.py     # ✅ [1.2] Risposta API standardizzata
│   │   │   ├── pagination.py
│   │   │   └── validators.py       # ✅ [3.3] Input validators (ticker, text, price, percentage, date range)
│   │   └── services/     # Servizi condivisi
│   └── main.py           # ✅ [1.7] Entry point FastAPI
├── tests/                # Test
│   │   ├── unit/             # Unit tests
│   │   ├── infra/
│   │   │   ├── test_security_middleware.py # ✅ 29 tests ✓ [3.1]
│   │   │   ├── test_rate_limit.py          # ✅ 33 tests ✓ [3.2]
│   │   │   ├── test_encryption.py          # ✅ 35 tests ✓ [3.4]
│   │   │   ├── test_logging.py             # ✅ 18 tests ✓ [3.5]
│   │   │   └── test_metrics.py             # ✅ 24 tests ✓ [3.6]
│   │   └── shared/
│   │       ├── domain/
│   │       │   ├── test_money.py           # ✅ 36 tests ✓
│   │       │   ├── test_percentage.py      # ✅ 39 tests ✓
│   │       │   └── test_price_target.py    # ✅ 41 tests ✓
│   │       ├── test_config.py              # ✅ 27 tests ✓
│   │       ├── test_middleware.py          # ✅ 16 tests ✓
│   │       └── test_validators.py          # ✅ 63 tests ✓ [3.3]
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

### Phase 1: Foundation & Infrastructure (10/10 tasks - 100% ✨)

| Task | Descrizione | Status | Tests | Implementation |
|------|-----------|--------|-------|-----------------|
| 1.1 | Setup Struttura Layer Backend | ✅ COMPLETATO | - | Directory structure |
| 1.2 | Modello Risposta API Standard | ✅ COMPLETATO | - | `ApiResponse` schema |
| 1.3 | Value Object Money | ✅ COMPLETATO | 36 ✓ | Decimal-safe operations |
| 1.4 | Value Object Percentage | ✅ COMPLETATO | 39 ✓ | Basis points support |
| 1.5 | Value Object PriceTarget | ✅ COMPLETATO | 41 ✓ | LONG/SHORT validation |
| 1.6 | Config Multi-Ambiente | ✅ COMPLETATO | 27 ✓ | Pydantic Settings + Secrets |
| 1.7 | Middleware Sicurezza | ✅ COMPLETATO | 16 ✓ | Headers + CORS + Rate Limit |
| 1.8 | Healthcheck Endpoints | ✅ COMPLETATO | ✓ | `/health` and `/health/db` |
| 2.1 | **Setup Python & Poetry** | ✅ **COMPLETATO** | **✓** | **Dipendenze complete (MVP + Phase 2)** |
| 2.2 | **Docker Compose Base** | ✅ **COMPLETATO** | **✓** | **PostgreSQL 16 + Redis 7 + Healthchecks** |

**Total Tests**: 241 passing ✅
- **Sync Module**: 60 tests (16 Drive Client + 30 CSV Parser + 14 Sync Service)
- **E2E Legacy Compatibility**: 17 tests (JSON/CSV backward compatibility)
- **Core Domain**: 164 tests (Value Objects, Services, Repositories)

### Phase 2: Core Domain & Persistence (14/14 tasks - 100% ✨)

| Task | Descrizione | Status | Tests | Implementation |
|------|-----------|--------|-------|----------------|
| 2.3 | Modello Ticker | ✅ COMPLETATO | ✓ | SQLAlchemy model + indices |
| 2.4 | Modello Estimate | ✅ COMPLETATO | ✓ | Entity con DECIMAL e Enums |
| 2.5 | Event Sourcing - EstimateEvent | ✅ COMPLETATO | - | JSONB audit log storage |
| 2.6 | Market Data - MarketData OHLCV | ✅ COMPLETATO | - | Prezzi storici con precisione Decimal |
| 2.7 | Modello User & Role (RBAC) | ✅ COMPLETATO | ✓ | Gestione ruoli e permessi base |
| 2.10 | Setup Alembic | ✅ COMPLETATO | ✓ | Database migrations (10 tabelle) |
| 2.11 | **EstimateSummaryView CQRS** | ✅ **COMPLETATO** | **✓** | **Materialized View pre-calcolata** |
| 2.12 | Repository Estimate | ✅ COMPLETATO | ✓ | CRUD + cursor pagination |
| 2.13 | Repository MarketData | ✅ COMPLETATO | ✓ | Upsert batch + aggregation |
| 2.14 | Service EstimateService | ✅ COMPLETATO | 8 ✓ | Business logic orchestration |
| 2.15 | Service EstimateHistoryService | ✅ COMPLETATO | 5 ✓ | Event sourcing + audit trail |
| 2.16 | API Router Estimates | ✅ COMPLETATO | ✓ | 6 REST endpoints + OpenAPI |
| 2.18 | Market Data Providers | ✅ COMPLETATO | 5 ✓ | Yahoo/Fake Providers + Interface |
| 2.19 | **Caching & Resiliency** | ✅ **COMPLETATO** | **✓** | **LRU Cache + Exponential Backoff** |

### Phase 3: Security & Observability (8/11 tasks - 73%)

| Task | Descrizione | Status | Tests | Implementation |
|------|-----------|--------|-------|----------------|
| 3.1 | **Security Middleware Avanzato** | ✅ **COMPLETATO** | **29 ✓** | **API Key auth, CSP, HSTS condizionale, request logging structlog** |
| 3.2 | **Rate Limiting** | ✅ **COMPLETATO** | **33 ✓** | **slowapi + Redis, per-endpoint limits, IP whitelist, Retry-After headers** |
| 3.3 | **Input Validation Avanzata** | ✅ **COMPLETATO** | **63 ✓** | **sanitize_ticker, sanitize_text, validate_price, validate_percentage, validate_date_range** |
| 3.4 | **Encryption at Rest** | ✅ **COMPLETATO** | **35 ✓** | **EncryptedString TypeDecorator (Fernet AES-128), rotate_key, EncryptionConfigError, DecryptionError** |
| 3.5 | **Structured Logging + Correlation ID** | ✅ **COMPLETATO** | **18 ✓** | **configure_logging (JSON structlog), CorrelationIDMiddleware, ContextVar, add_correlation_id processor** |
| 3.6 | **Metriche Prometheus** | ✅ **COMPLETATO** | **24 ✓** | **GET /metrics, Counter/Gauge/Histogram business+technical metrics, @track_duration decorator, /metrics in API_KEY_EXEMPT_PATHS** |
| 3.7 | **Health Checks Completi** | ✅ **COMPLETATO** | **13 ✓** | **HealthService (DB/Redis/Yahoo/Drive), GET /health + /health/ready + /health/live, JSONResponse, 503 on UNHEALTHY** |
| 3.8 | **Data Quality Monitor** | ✅ **COMPLETATO** | **26 ✓** | **DataQualityMonitor (positive_prices/no_large_gaps/daily_change_lt50/positive_volume), run_checks/run_all_checks, daily job 06:00 UTC, structlog alert su critical** |
| 3.9 | **Data Lineage Tracking** | ✅ **COMPLETATO** | **20 ✓** | **DataSource enum, LineageTracked mixin, ingested_at→ingestion_timestamp rename, source_timestamp column, MarketDataLineageSchema, ?include_lineage API param, Alembic migration a3b5c7d9e1f0** |
| 3.10 | **Connection Pooling Ottimizzato** | ✅ **COMPLETATO** | **20 ✓** | **AsyncAdaptedQueuePool via Settings (5 campi), get_pool_status(), 4 Gauge Prometheus, update_pool_metrics(), GET /health/pool, connection_pool in /health** |
| 3.11 | **Query Pagination Cursor-Based** | ✅ **COMPLETATO** | **42 ✓** | **CursorPagination, PaginatedResult[T], encode/decode_cursor (base64url), apply_cursor_pagination, get_history_paginated(), GET /api/market/history/{ticker}/paginated** |

**Total Tests**: 605 passing ✅ (aggiornato con Task 3.11)



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

### Market Data Provider Pattern

Il sistema utilizza un **pattern Provider astratto** per disaccoppiare la logica di business dalle fonti di dati di mercato:

```python
# Interfaccia astratta
class MarketDataProvider(ABC):
    async def get_current_price(symbol: str) -> PriceData
    async def get_historical_prices(symbol, start, end) -> List[PriceData]
    async def get_fundamentals(symbol: str) -> FundamentalsData
```

**Provider Implementati:**
- ✅ **YahooMarketDataProvider**: Yahoo Finance (delayed data, free)
- ✅ **FakeMarketDataProvider**: Testing senza chiamate esterne
- ⏸️ **FinnhubMarketDataProvider**: Stub (real-time, 60 API calls/min free)
- ⏸️ **AlphaVantageMarketDataProvider**: Stub (5 API calls/min free)
- ⏸️ **PolygonMarketDataProvider**: Stub (delayed free tier)

**Vantaggi:**
- **Testabilità**: FakeProvider per unit test deterministici
- **Flessibilità**: Cambio provider senza modificare business logic
- **Future-proof**: Facile aggiungere provider premium
- **Dependency Injection**: Provider configurabile via FastAPI `Depends()`

**Esempio uso:**
```python
# Nel service
class MarketDataService:
    def __init__(self, provider: MarketDataProvider):
        self._provider = provider  # Iniettato
    
    async def get_price(self, ticker_id: UUID) -> Decimal:
        ticker = await self._get_ticker(ticker_id)
        price_data = await self._provider.get_current_price(ticker.symbol)
        return price_data.close

# Dependency injection in FastAPI
async def get_market_data_service() -> MarketDataService:
    provider = YahooMarketDataProvider(timeout=30)
    return MarketDataService(provider, ...)
```

**Contratti Dati:**
- `PriceData`: OHLCV + volume + source + timestamp + is_stale flag
- `FundamentalsData`: Market cap, P/E, EPS, sector, industry + is_stale flag

Per dettagli: [src/market_data/domain/providers.py](src/market_data/domain/providers.py)

#### Caching & Retry Logic

Il sistema implementa un **decorator pattern** per aggiungere caching in-memory e retry automatico a qualsiasi provider:

```python
from src.market_data.infrastructure import CachedMarketDataProvider, CacheConfig
from src.market_data.api import get_market_data_provider

# Configurazione via Settings
config = CacheConfig(
    current_price_ttl=60,        # 60s per prezzi correnti
    historical_price_ttl=3600,    # 1h per dati storici
    fundamentals_ttl=86400,       # 24h per fundamentals
    max_retries=3,                # Retry fino a 3 volte
    initial_backoff=0.5,          # Backoff 0.5s, 1s, 2s, 4s...
)

# Wrappa provider con cache
base_provider = YahooMarketDataProvider()
cached_provider = CachedMarketDataProvider(base_provider, config)

# Uso trasparente
price1 = await cached_provider.get_current_price("AAPL")  # API call
price2 = await cached_provider.get_current_price("AAPL")  # Cache hit (no API call)
```

**Caratteristiche:**
- ✅ **TTL Differenziati**: 60s per prezzi, 1h per storico, 24h per fundamentals
- ✅ **Exponential Backoff**: Retry su timeout/rate-limit/5xx errors
- ✅ **Stale Fallback**: Restituisce dati scaduti (is_stale=True) se API fails
- ✅ **Cache Statistics**: Tracking hits/misses/hit_rate
- ✅ **Thread-Safe**: RLock per operazioni concorrenti
- ✅ **Configurabile**: Tutti i parametri configurabili via Settings

**Configurazione Settings:**
```python
# In .env o config.py
CACHE_CURRENT_PRICE_TTL=60       # 1 minuto
CACHE_HISTORICAL_PRICE_TTL=3600  # 1 ora
CACHE_FUNDAMENTALS_TTL=86400     # 24 ore
CACHE_MAX_SIZE=1000              # Max 1000 items in cache

RETRY_MAX_ATTEMPTS=3             # Max 3 retry
RETRY_INITIAL_BACKOFF=0.5        # Backoff iniziale 0.5s
RETRY_MAX_BACKOFF=8.0            # Backoff massimo 8s
RETRY_BACKOFF_MULTIPLIER=2.0     # Moltiplicatore esponenziale
```

**Dependency Injection:**
```python
from src.market_data.api import get_market_data_provider

@router.get("/price/{symbol}")
async def get_price(
    symbol: str,
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    # Provider è già cached e configurato
    price = await provider.get_current_price(symbol)
    return {"price": price.close, "is_stale": price.is_stale}
```

Per dettagli: [src/market_data/infrastructure/cached_provider.py](src/market_data/infrastructure/cached_provider.py)
Per cache implementation: [src/infra/cache/memory_cache.py](src/infra/cache/memory_cache.py)

## Background Worker & Job Scheduling (APScheduler)

TickerTracker utilizza [APScheduler](https://apscheduler.readthedocs.io/) per gestire job schedulati di sync, refresh e controllo target.

### Scheduler Principale
- **Tipo:** AsyncIOScheduler (timezone UTC)
- **Avvio:** Automatico su startup FastAPI
- **Shutdown:** Graceful su shutdown FastAPI
- **Logging:** Inizio/fine job, errori, durata, successo/fallimento

### Job Schedulati
- **process_outbox_events**: ogni 30 secondi (processamento eventi Outbox per sync Drive)
- **handle_dead_letters**: ogni giorno alle 02:00 UTC (gestione eventi falliti)
- **refresh_market_data**: ogni 5 minuti (lun-ven, 14:00-21:55 UTC, orari di mercato)
- **daily_history_sync**: ogni giorno alle 23:00 UTC
- **refresh_materialized_views**: ogni 5 minuti
- **check_targets**: ogni minuto

Tutti i job sono implementati in `src/infra/scheduler/jobs.py` e registrati in `src/infra/scheduler/scheduler.py` con wrapper per logging e metriche.

### Pattern Outbox per Eventi Drive

TickerTracker implementa il **Pattern Outbox** per garantire delivery affidabile degli eventi verso Google Drive:

#### Funzionamento
1. **Salvataggio Atomico**: Eventi salvati nella stessa transazione degli estimates (`EstimateEvent` table)
2. **Polling Asincrono**: Job `process_outbox_events` processa eventi ogni 30s
3. **Transaction Isolation**: Ogni evento processato in transazione separata
4. **Retry Logic**: Fino a 5 tentativi automatici per eventi falliti
5. **Dead Letter Queue**: Eventi con 5 retry falliti → log error + alert placeholder

#### Implementazione
- **OutboxProcessor**: `src/infra/outbox/outbox_processor.py`
- **Metodi Helper**: `EstimateEvent.mark_processed()`, `mark_failed()`, `can_retry()`, `is_dead_letter()`
- **Query Eventi**: `EstimateEvent.get_unprocessed()`, `get_dead_letters()`

#### Eventi Sincronizzabili
- `CREATED`: Nuova estimate creata
- `UPDATED`: Metadata estimate aggiornato
- `CLOSED`: Estimate chiusa

Altri tipi di evento (`PRICE_UPDATED`, `TARGET_HIT`, `STOP_HIT`, `REOPENED`) sono marcati come processati senza sync Drive.

#### Graceful Degradation
Se `SyncService` non è disponibile o `sync_estimate_to_drive()` manca:
- Log warning (no crash)
- Eventi marcati come processati
- Continuazione processing altri eventi

#### Monitoraggio
- **Logging Strutturato**: `event_id`, `estimate_id`, `retry_count`, `error` in tutti i log
- **Dead Letter Alerts**: Log `ERROR` con dettagli completi + placeholder per Slack/Email webhook
- **Metriche Job**: `{"processed": X, "failed": Y, "skipped": Z}` in log job

#### Testing
- **Unit Tests**: `tests/unit/outbox/test_outbox_processor.py` (95%+ coverage)
- **E2E Tests**: `tests/e2e/test_outbox_e2e.py` (flow completo create → process → Drive)

---

### Integrazione FastAPI
- Hook `@app.on_event("startup")`: avvia lo scheduler
- Hook `@app.on_event("shutdown")`: shutdown graceful
- Errori nei job non bloccano l'applicazione

### Esempio Avvio Manuale (dev)

```bash
# Attiva venv
.\Standalone-app-v1\backend\.venv\Scripts\activate
# Avvia server
py -m uvicorn src.main:app --reload
```

### Dipendenze
- `apscheduler` (in requirements.txt)

### Stato Job e Metriche
- Logging automatico inizio/fine job
- Durata e successo/fallimento visibili nei log
- Possibile estendere con Prometheus/metrics

---

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

#### Database Schema

Il database include le seguenti tabelle principali:

**Core Tables:**
- `tickers` - Informazioni ticker (AAPL, TSLA, etc.)
- `market_data` - Dati storici OHLCV
- `estimates` - Stime di trading con target/stop-loss
- `estimates` include soft delete (`is_deleted`, `deleted_at`)
- `estimate_events` - Event sourcing per stime
- `ai_model_runs` - Tracciamento esecuzioni AI
- `sync_jobs` - Tracciamento sincronizzazione Drive
- `users` - Utenti sistema
- `roles` - Ruoli RBAC
- `user_roles` - Tabella di associazione user-role

**Materialized Views:**
- `estimate_summary_view` - View CQRS per dashboard queries (< 5ms)

Per dettagli completi sulle migrazioni: [ALEMBIC_SETUP_COMPLETED.md](./ALEMBIC_SETUP_COMPLETED.md)

### CQRS Pattern - Estimate Summary View

Per ottimizzare le query del dashboard, è stata implementata una **materialized view** che pre-calcola metriche e join:

```bash
# Refresh manuale (con lock)
docker exec tickertracker-db psql -U tickertracker -d tickertracker_dev -c "REFRESH MATERIALIZED VIEW estimate_summary_view;"

# Refresh concorrente (senza lock, raccomandato)
python scripts/refresh_estimate_summary_view.py

# Con statistiche
python scripts/refresh_estimate_summary_view.py --stats
```

**Metriche pre-calcolate:**
- `current_price` - Ultimo prezzo di mercato disponibile
- `current_pnl` - PnL non realizzato (LONG/SHORT aware)
- `current_pnl_percent` - PnL in percentuale
- `days_open` - Giorni dalla creazione della stima
- `risk_level` - Classificazione rischio (LOW/MEDIUM/HIGH)

**Performance:**
- Query time: < 5ms (target < 50ms) ✅
- Concurrent refresh: ~12ms
- Zero downtime con `REFRESH MATERIALIZED VIEW CONCURRENTLY`

Per dettagli completi: [docs/ESTIMATE_SUMMARY_VIEW.md](./docs/ESTIMATE_SUMMARY_VIEW.md)

### Repository & Paginazione (Task 2.12)

Il repository `EstimateRepository` centralizza le operazioni CRUD su `Estimate` e
fornisce paginazione cursor-based con filtri dedicati:

- Repository: `backend/src/estimates/repositories/estimate_repository.py`
- Schemi Pydantic: `backend/src/estimates/schemas/filters.py`

Esempio d'uso (cursor-based):

```python
filters = EstimateFilters(status=EstimateStatus.OPEN)
pagination = Pagination(limit=20)

result = await repository.get_all(filters=filters, pagination=pagination)
next_cursor = result.next_cursor
```

### MarketData Repository (Task 2.13)

`MarketDataRepository` fornisce accesso efficiente ai dati di mercato storici e attuali:

- Repository: `backend/src/market_data/repositories/market_data_repository.py`
- Schemi Pydantic: `backend/src/market_data/schemas/filters.py`

**Metodi principali:**
- `upsert_daily()` - Upsert atomico OHLCV con ON CONFLICT PostgreSQL
- `get_history()` - Query storica per range di date
- `get_latest_price()` - Ultimo prezzo per ticker
- `get_latest_prices_batch()` - Batch query di ultimi prezzi (no N+1)
- `get_aggregated()` - Aggregazione 1D/1W/1M con helper methods

Esempio di uso batch per evitare N+1:

```python
ticker_ids = [uuid1, uuid2, uuid3]
latest_prices = await repository.get_latest_prices_batch(ticker_ids)
# Restituisce Dict[UUID, MarketData] con un'unica query
```

Esempio di aggregazione:

```python
aggregated = await repository.get_aggregated(
    ticker_id=uuid,
    interval="1W",  # Weekly
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)
# Restituisce List[AggregatedData] con OHLCV aggregato per settimana
```

### EstimateService (Task 2.14)

`EstimateService` orchestra la business logic per la creazione e gestione delle stime di trading:

- Service: `backend/src/estimates/services/estimate_service.py`
- Comandi: `backend/src/estimates/schemas/commands.py`
- Eccezioni: `backend/src/estimates/services/exceptions.py`

**Metodi principali:**
- `create_estimate()` - Crea stima con calcolo automatico prezzi target/stop da percentuali
- `update_estimate()` - Aggiorna stima esistente con ricalcolo prezzi
- `close_estimate()` - Chiude stima manualmente con calcolo PnL
- `check_and_update_targets()` - Verifica e chiude automaticamente su target/stop hit

**Caratteristiche:**
- Validazione completa input tramite comandi Pydantic
- Recupero prezzo corrente da MarketDataRepository
- Calcolo automatico di target_price e stop_loss_price da percentuali
- Supporto completo per LONG e SHORT con logica appropriata
- Pubblicazione eventi atomica (EstimateEvent) nella stessa transazione
- Eccezioni business tipizzate per errori domain-specific
- Calcolo automatico di PnL realized al momento della chiusura

Esempio di creazione stima LONG:

```python
from src.estimates.schemas.commands import CreateEstimateCommand
from decimal import Decimal

# Il prezzo corrente è recuperato automaticamente dal repository
command = CreateEstimateCommand(
    ticker_id=ticker_uuid,
    direction="LONG",
    target_profit_percent=Decimal("15.0"),  # +15% sopra prezzo corrente
    stop_loss_percent=Decimal("5.0"),       # -5% sotto prezzo corrente
    ai_model="gpt-4",
    ai_confidence=Decimal("75.0"),
)

estimate = await service.create_estimate(command)
# estimate.start_price = prezzo corrente (es. 100.00)
# estimate.target_price = 115.00 (automaticamente calcolato)
# estimate.stop_loss_price = 95.00 (automaticamente calcolato)
```

Esempio di chiusura automatica su target:

```python
# Chiamato periodicamente da background worker
closed_estimate = await service.check_and_update_targets(
    estimate_id=uuid,
    current_price=Decimal("116.50")  # Opzionale, altrimenti fetched
)

if closed_estimate:
    print(f"Estimate closed: {closed_estimate.status}")
    print(f"PnL: ${closed_estimate.realized_pnl}")
```

### EstimateHistoryService (Task 2.15)

`EstimateHistoryService` implementa Event Sourcing per ricostruire lo stato storico delle stime:

- Service: `backend/src/estimates/services/estimate_history_service.py`
- Repository: `backend/src/estimates/repositories/estimate_event_repository.py`
- Schemi: `backend/src/estimates/schemas/history.py`

**Metodi principali:**
- `get_state_at()` - Ricostruisce stato estimate ad un timestamp specifico
- `get_audit_trail()` - Genera audit trail completo human-readable
- `get_changes_between()` - Identifica cambiamenti tra due timestamp
- `get_history_summary()` - Statistiche complete dello storico

**Caratteristiche:**
- Replay completo eventi per state reconstruction
- Supporto totale per tipi evento: CREATED, UPDATED, PRICE_UPDATED, TARGET_HIT, STOP_HIT, CLOSED, REOPENED
- Descrizioni human-readable generate automaticamente
- Change tracking field-level con old/new values
- Performance ottimizzata con query ordinate cronologicamente

Esempio di state reconstruction:

```python
from datetime import datetime, timezone, timedelta

# Ricostruisci stato 7 giorni fa
week_ago = datetime.now(timezone.utc) - timedelta(days=7)
snapshot = await history_service.get_state_at(estimate_id, week_ago)

print(f"Status era: {snapshot.status}")
print(f"Target price era: ${snapshot.target_price}")
print(f"Eventi fino a quel momento: {snapshot.event_count}")
```

Esempio di audit trail:

```python
# Ottieni audit trail completo
audit_trail = await history_service.get_audit_trail(estimate_id)

for entry in audit_trail:
    timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    actor = "System" if entry.is_system_event else f"User {entry.user_id}"
    print(f"[{timestamp}] {actor}: {entry.description}")
    
    if entry.changed_fields:
        for field in entry.changed_fields:
            old = entry.old_values.get(field)
            new = entry.new_values.get(field)
            print(f"  - {field}: {old} -> {new}")
```

Esempio di change detection:

```python
# Cambiamenti negli ultimi 30 giorni
thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
changes = await history_service.get_changes_between(
    estimate_id,
    thirty_days_ago,
    datetime.now(timezone.utc)
)

for change in changes:
    print(f"{change.field_name}: {change.old_value} -> {change.new_value}")
    print(f"  Changed at: {change.changed_at} by event {change.event_type.value}")
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

## Chaos Testing

Il sistema implementa test di resilienza per verificare la tenuta sotto carico o in condizioni di API esterne fallite. Per eseguire i test di Chaos:

````bash
pytest -m chaos tests/chaos/
```
Scenari validati:
- Timeout e failure provider esterni (es: Google Drive / Yahoo).
- Fallback a memoria in cache con dati markati come stale.
- Retries esponenziali ed intermittenza di rete.
- Load testing e isolamento a livello di asyncpg pool con Graceful Degradation (503 Service Unavailable).
- Transazioni atomiche per non corrompere dati preesistenti durante sincronizzazioni parziali.

## Migrazione Dati Legacy (v2.4 -> v3.0)  
  
Per importare i file storici da Google Drive al nuovo database locale PostgreSQL in modo idempotente:  
```bash  
# Testa la lettura con --dry-run  
py scripts/migrate_from_legacy.py --dry-run --source-folder-id "YOUR_DRIVE_FOLDER_ID"  
  
# Esegui importazione (richiede GOOGLE_SERVICE_ACCOUNT_CREDENTIALS in .env)  
py scripts/migrate_from_legacy.py --source-folder-id "YOUR_DRIVE_FOLDER_ID"  
``` 
