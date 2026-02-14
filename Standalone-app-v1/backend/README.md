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

**Total Tests**: 164 passing ✅

### Phase 2: Estimates & Market Data (7/7 tasks - 100% ✨)

| Task | Descrizione | Status | Tests | Implementation |
|------|-----------|--------|-------|----------------|
| 2.5 | Modello SQLAlchemy - Estimate | ✅ COMPLETATO | - | Entity con DECIMAL, Enums, indici |
| 2.6 | Modello SQLAlchemy - EstimateEvent/MarketData | ✅ COMPLETATO | - | Event Sourcing e Market Data OHLCV |
| 2.12 | Repository Estimate | ✅ COMPLETATO | ✓ | CRUD + cursor pagination |
| 2.13 | Repository MarketData | ✅ COMPLETATO | ✓ | Upsert batch + aggregation |
| 2.14 | Service EstimateService | ✅ COMPLETATO | 8 ✓ | Business logic orchestration |
| 2.15 | Service EstimateHistoryService | ✅ COMPLETATO | 5 ✓ | Event sourcing + audit trail |
| 2.16 | API Router Estimates | ✅ COMPLETATO | ✓ | 6 REST endpoints + OpenAPI |
| 2.18 | **Market Data Provider Abstraction** | ✅ **COMPLETATO** | **5 ✓** | **Interface + Yahoo/Fake Providers** |

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
- `PriceData`: OHLCV + volume + source + timestamp
- `FundamentalsData`: Market cap, P/E, EPS, sector, industry

Per dettagli: [src/market_data/domain/providers.py](src/market_data/domain/providers.py)

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
