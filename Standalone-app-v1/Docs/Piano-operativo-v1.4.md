# Piano Atomico TickerTracker v3.0
**Guida per LLM (Claude, Code Antigravity, Jules)**

**Versione:** 1.4  
**Data:** 31 Gennaio 2026  
**Autore:** Francesco Di Lecce

---

## CHANGELOG v1.4

**Modifiche rispetto a v1.3:**
- **✅ NUOVO**: Aggiunto **TASK 2.0** - Setup Progetto Python con Poetry
- **🔄 AGGIORNATO**: TASK 2.1 ora dipende da TASK 2.0
- **📄 ORGANIZZAZIONE**: Allineamento completo tra `Piano-operativo-v1.4.md` e `backend/AGENTS.md`
- **🛠️ FILE CREATI**:
  - `backend/pyproject.toml` - Configurazione Poetry con tutte le dipendenze MVP + Fase 2
  - `backend/Makefile` - Comandi standardizzati per sviluppo
  - `backend/.python-version` - Specifica versione Python 3.11
  - `backend/scripts/check_deps.py` - Script verifica dipendenze
  - `backend/requirements.txt` - Dipendenze production (pip fallback)
  - `backend/requirements-dev.txt` - Dipendenze development (pip fallback)
  - `backend/README.md` - Documentazione completa installazione e uso

---

# SEZIONE 1: LINEE GUIDA TRASVERSALI

## TASK 1.1: Setup Struttura Layer Backend

**ID:** TASK 1.1  
**Area:** backend/structure  
**Fase:** MVP  
**Dipendenze:** -

**Descrizione:** Creare la struttura di cartelle e file base per il layering esplicito del backend FastAPI.

**Microstep:**

1. Creare cartella `backend/src/` come root del codice sorgente
2. Creare sottocartelle per ogni bounded context: `estimates/`, `market_data/`, `sync/`, `analytics/`, `shared/`
3. Per ogni bounded context, creare le sottocartelle: `api/`, `schemas/`, `domain/`, `services/`, `repositories/`
4. Creare cartella `backend/src/infra/` con sottocartelle: `yahoo/`, `drive/`, `cache/`, `logging/`, `security/`
5. Creare file `__init__.py` in ogni cartella
6. Creare file `backend/src/README.md` che documenta la convenzione di layering

**Acceptance Criteria:**

- [ ] Struttura cartelle completa e navigabile
- [ ] Ogni cartella ha un `__init__.py`
- [ ] README documenta lo scopo di ogni layer (api, schemas, domain, services, repositories, infra)
- [ ] Nessun file di logica ancora presente (solo struttura)

---

## TASK 1.2: Definizione Modello Risposta API Standard

**ID:** TASK 1.2  
**Area:** backend/shared  
**Fase:** MVP  
**Dipendenze:** TASK 1.1

**Descrizione:** Creare lo schema Pydantic per il modello di risposta API uniforme usato da tutti gli endpoint.

**Microstep:**

1. Creare file `backend/src/shared/schemas/api_response.py`
2. Definire schema `ApiResponse` con campi: `success` (bool), `data` (generic/nullable), `error` (nullable), `trace_id` (UUID string)
3. Definire schema `ApiError` con campi: `code` (string), `message` (string), `details` (optional dict)
4. Creare funzioni helper: `success_response(data, trace_id)`, `error_response(code, message, details, trace_id)`
5. Documentare con docstring l'uso previsto

**Acceptance Criteria:**

- [ ] Schema `ApiResponse` è generico e accetta qualsiasi tipo di `data`
- [ ] Schema `ApiError` è annidabile in `ApiResponse.error`
- [ ] Funzioni helper producono risposte conformi allo schema
- [ ] Tutti i campi hanno type hints corretti
- [ ] Docstring spiega quando usare success vs error response

---

## TASK 1.3: Creazione Value Object Money (Backend)

**ID:** TASK 1.3  
**Area:** backend/shared  
**Fase:** MVP  
**Dipendenze:** TASK 1.1

**Descrizione:** Implementare il value object immutabile `Money` per gestire importi monetari con precisione decimale.

**Microstep:**

1. Creare file `backend/src/shared/domain/value_objects/money.py`
2. Definire dataclass frozen `Money` con campi: `amount` (Decimal), `currency` (str, default "USD")
3. Implementare `__post_init__` per convertire input non-Decimal in Decimal
4. Implementare metodi: `__add__`, `__sub__`, `__mul__` (con Decimal/int), `__neg__`
5. Implementare metodo `round(places: int)` con ROUND_HALF_UP
6. Implementare metodo `to_dict()` che restituisce `{"amount": str, "currency": str}`
7. Implementare metodo class `from_dict(data: dict)`
8. Aggiungere validazione: currency deve essere stringa 3 caratteri uppercase

**Acceptance Criteria:**

- [ ] Classe è immutabile (frozen dataclass)
- [ ] Tutti i calcoli usano Decimal, mai float
- [ ] Somma/sottrazione tra valute diverse solleva ValueError
- [ ] Moltiplicazione accetta solo Decimal o int
- [ ] Serializzazione/deserializzazione round-trip funziona
- [ ] Test unitari coprono tutti i metodi

---

## TASK 1.4: Creazione Value Object Percentage (Backend)

**ID:** TASK 1.4  
**Area:** backend/shared  
**Fase:** MVP  
**Dipendenze:** TASK 1.3

**Descrizione:** Implementare il value object immutabile `Percentage` per gestire valori percentuali.

**Microstep:**

1. Creare file `backend/src/shared/domain/value_objects/percentage.py`
2. Definire dataclass frozen `Percentage` con campo: `value` (Decimal)
3. Implementare `__post_init__` per conversione a Decimal
4. Implementare class method `from_basis_points(bps: int)`
5. Implementare metodo `apply_to(money: Money) -> Money`
6. Implementare metodo `as_multiplier() -> Decimal` (restituisce 1 + value)
7. Implementare metodi `__add__`, `__sub__` tra Percentage
8. Implementare `to_dict()` e `from_dict()`

**Acceptance Criteria:**

- [ ] Classe è immutabile
- [ ] Conversione da basis points corretta (100 bps = 1% = 0.01)
- [ ] `apply_to` restituisce Money con importo corretto
- [ ] `as_multiplier` per 10% restituisce Decimal("1.10")
- [ ] Test unitari coprono tutti i metodi

---

## TASK 1.5: Creazione Value Object PriceTarget (Backend)

**ID:** TASK 1.5  
**Area:** backend/shared  
**Fase:** MVP  
**Dipendenze:** TASK 1.3, TASK 1.4

**Descrizione:** Implementare il value object `PriceTarget` che incapsula target, stop loss e take profit con validazioni.

**Microstep:**

1. Creare file `backend/src/shared/domain/value_objects/price_target.py`
2. Definire dataclass frozen `PriceTarget` con campi: `entry_price` (Money), `stop_loss` (Money), `take_profit` (Money), `direction` (Literal["LONG", "SHORT"])
3. Implementare `__post_init__` con validazioni:
   - Per LONG: stop_loss < entry_price < take_profit
   - Per SHORT: take_profit < entry_price < stop_loss
   - Tutte le currency devono corrispondere
4. Implementare metodo `risk_reward_ratio() -> Decimal`
5. Implementare metodo `is_target_hit(current_price: Money) -> bool`
6. Implementare metodo `is_stop_hit(current_price: Money) -> bool`
7. Implementare `to_dict()` e `from_dict()`

**Acceptance Criteria:**

- [ ] Validazione solleva ValueError per configurazioni invalide
- [ ] Risk/reward ratio calcolato correttamente per entrambe le direzioni
- [ ] Metodi is_target_hit e is_stop_hit funzionano per LONG e SHORT
- [ ] Test unitari coprono scenari validi e invalidi

---

## TASK 1.6: Configurazione Ambienti con Pydantic Settings

**ID:** TASK 1.6  
**Area:** backend/shared  
**Fase:** MVP  
**Dipendenze:** TASK 1.1

**Descrizione:** Implementare sistema di configurazione multi-ambiente con pydantic-settings.

**Microstep:**

1. Creare file `backend/src/shared/infra/config.py`
2. Definire classe `Settings` che eredita da `BaseSettings`
3. Definire campi per ogni ambiente: `ENVIRONMENT` (local/staging/prod), `DEBUG`, `LOG_LEVEL`
4. Definire campi database: `DATABASE_URL` (SecretStr)
5. Definire campi API esterne: `YAHOO_CACHE_TTL`, `GEMINI_API_KEY` (SecretStr), `FINNHUB_API_KEY` (SecretStr, optional)
6. Definire campi Drive: `GOOGLE_SERVICE_ACCOUNT_JSON` (SecretStr), `DRIVE_FOLDER_ID`
7. Definire campi sicurezza: `ENCRYPTION_KEY` (SecretStr), `JWT_SECRET` (SecretStr)
8. Configurare `model_config` con `env_file='.env'`, `case_sensitive=False`
9. Creare funzione `get_settings()` con cache (lru_cache)
10. Creare file `.env.example` con tutti i campi documentati

**Acceptance Criteria:**

- [ ] Settings carica variabili da file .env
- [ ] Tutti i secret usano tipo SecretStr
- [ ] Valori di default sensati per development
- [ ] `.env.example` documenta tutte le variabili richieste
- [ ] `get_settings()` restituisce sempre la stessa istanza (cached)

---

## TASK 1.7: Middleware Sicurezza Base & Healthcheck

**ID:** TASK 1.7  
**Area:** backend/shared  
**Fase:** MVP  
**Dipendenze:** TASK 1.6

**Descrizione:** Aggiungere un middleware di sicurezza base (header, CORS, small rate limit) e endpoint di healthcheck per uso con Docker.

**Microstep:**

1. Creare file `backend/src/shared/infra/security_middleware.py`
2. Implementare un middleware FastAPI che:
   - Aggiunge header di sicurezza minimi (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
   - Configura CORS per l'origin del frontend (es. http://localhost:3000)
   - Implementa un rate limit molto semplice in memoria per IP (es. max 60 richieste/minuto), disattivabile via config
3. Registrare il middleware in `backend/src/main.py` dell'app FastAPI
4. Creare router `backend/src/shared/api/health_routes.py` con:
   - GET /health che ritorna {status: "ok"}
   - GET /health/db che prova una query SELECT 1
5. Documentare nel README come usare /health per verificare che il container backend sia up

**Acceptance Criteria:**

- [ ] Tutte le risposte includono i security header base
- [ ] Il frontend può chiamare il backend senza problemi di CORS
- [ ] /health e /health/db risultano verdi quando il DB è raggiungibile
- [ ] Il rate limit può essere disabilitato via Settings per uso locale se non necessario

---

# SEZIONE 2: BACKEND & DATA

## NOTE NUMERAZIONE

**TASK 2.2**: Originariamente "Setup Docker Compose per PostgreSQL e Redis".  
Spostato in `Docker/AGENTS.md` durante riorganizzazione architetturale.  
La numerazione backend non è stata riallineata per preservare riferimenti storici e dipendenze esistenti.  
Per dettagli su Docker Compose, consultare `Docker/AGENTS.md` → TASK 2.2.

---

## ✨ TASK 2.0: Setup Progetto Python con Poetry [NUOVO]

**ID:** TASK 2.0  
**Area:** backend/infra  
**Fase:** MVP  
**Dipendenze:** -  
**Priorità:** 🔴 CRITICA - Prerequisito per tutti i task backend

**Descrizione:** Inizializzare il progetto Python backend con dependency management moderno (Poetry) e file requirements completo per tutti i task MVP e Fase 2. Questo task è prerequisito fondamentale per tutti gli altri task backend.

**Microstep:**

1. ✅ Creare file `backend/pyproject.toml` con metadati progetto e configurazione Poetry
2. ✅ Configurare dipendenze CORE in `[tool.poetry.dependencies]`:
   - python >= 3.11
   - fastapi, uvicorn[standard], pydantic, pydantic-settings
3. ✅ Aggiungere dipendenze DATABASE & ORM:
   - sqlalchemy[asyncio], asyncpg, alembic
4. ✅ Aggiungere dipendenze CACHE:
   - redis
5. ✅ Aggiungere dipendenze MARKET DATA (TASK 2.18-2.19):
   - yfinance, finnhub-python (optional)
6. ✅ Aggiungere dipendenze GOOGLE DRIVE (TASK 2.20):
   - google-api-python-client, google-auth, google-auth-oauthlib, google-auth-httplib2
7. ✅ Aggiungere dipendenze SICUREZZA (TASK 3.1, 3.4):
   - cryptography, python-jose[cryptography], passlib[bcrypt]
8. ✅ Aggiungere dipendenze SCHEDULING (TASK 2.24):
   - apscheduler
9. ✅ Aggiungere dipendenze OBSERVABILITY - Fase 2 (TASK 3.5, 3.6):
   - structlog, prometheus-client
10. ✅ Aggiungere dipendenze RATE LIMITING - Fase 2 (TASK 3.2):
    - slowapi
11. ✅ Aggiungere dipendenze UTILITY:
    - python-multipart, cachetools, python-dotenv
12. ✅ Configurare dipendenze SVILUPPO in `[tool.poetry.group.dev.dependencies]`:
    - pytest, pytest-asyncio, pytest-cov, httpx, ruff, mypy, black, faker
13. ✅ Configurare sezione `[tool.ruff]` per linting
14. ✅ Configurare sezione `[tool.mypy]` con strict mode
15. ✅ Configurare sezione `[tool.pytest.ini_options]`
16. ✅ Creare file `backend/.python-version` con contenuto: `3.11`
17. ✅ Generare `backend/requirements.txt`
18. ✅ Generare `backend/requirements-dev.txt`
19. ✅ Creare `backend/Makefile` con comandi standardizzati
20. ✅ Creare script `backend/scripts/check_deps.py` per verificare installazione dipendenze
21. ✅ Aggiornare `backend/README.md` con istruzioni installazione

**Acceptance Criteria:**

- [x] `poetry install` completa senza errori
- [x] `pip install -r requirements.txt` funziona come alternativa
- [x] `make check-deps` verifica installazione dipendenze
- [x] `make lint` esegue ruff senza errori su codice base pulito
- [x] `make typecheck` esegue mypy
- [x] `make test` esegue pytest (anche se tests/ è vuoto inizialmente)
- [x] File `pyproject.toml` include TUTTE le dipendenze per MVP + Fase 2
- [x] File `requirements.txt` sincronizzato con `pyproject.toml`
- [x] File `.python-version` presente per gestori versioni (pyenv, asdf)
- [x] Script `check_deps.py` funzionante ed eseguibile
- [x] README.md aggiornato con sezione installazione completa

**Note Importanti:**
- Questo task è **prerequisito fondamentale** per TUTTI i task backend successivi
- `requirements.txt` deve essere rigenerato con `make export-requirements` quando si aggiungono dipendenze
- Per ambienti production, usare `requirements.txt` con versioni pinned esatte
- Il Makefile fornisce comandi standardizzati per tutto il team di sviluppo

**File Creati:**
- ✅ `backend/pyproject.toml`
- ✅ `backend/.python-version`
- ✅ `backend/Makefile`
- ✅ `backend/requirements.txt`
- ✅ `backend/requirements-dev.txt`
- ✅ `backend/scripts/check_deps.py`
- ✅ `backend/README.md`

---

## TASK 2.1: Setup SQLAlchemy e Database Connection Pool

**ID:** TASK 2.1  
**Area:** backend/infra  
**Fase:** MVP  
**Dipendenze:** ⚠️ TASK 2.0 (AGGIORNATO)

**Descrizione:** Configurare SQLAlchemy con connection pooling ottimizzato.

**Microstep:**

1. Creare file `backend/src/infra/database.py`
2. Importare Settings per DATABASE_URL
3. Creare engine con pool_size=10, max_overflow=5, pool_pre_ping=True
4. Configurare sessionmaker con expire_on_commit=False
5. Implementare context manager get_db() per dependency injection
6. Creare Base declarativa per modelli
7. Implementare funzione init_db() per creazione tabelle (dev only)
8. Configurare logging query per debug

**Acceptance Criteria:**

- [ ] Engine SQLAlchemy creato con pool configurato
- [ ] get_db() dependency funzionante
- [ ] Connection pool mantiene connessioni attive
- [ ] Logging query visibile in dev mode
- [ ] Nessun connection leak sotto carico

---

## TASK 2.3 - 2.27: [Altri Task Backend]

*Per brevità, i task 2.3-2.27 rimangono invariati rispetto alla versione 1.3. Consultare `backend/AGENTS.md` per i dettagli completi.*

**Task rimanenti nella Sezione 2:**
- TASK 2.3: Definizione Aggregate Estimate (Domain)
- TASK 2.4-2.9: Modelli SQLAlchemy (Ticker, Estimate, Events, MarketData, User, SyncJob, AiModelRun)
- TASK 2.10: Setup Alembic per Migrazioni
- TASK 2.11: Materialized View EstimateSummaryView (CQRS)
- TASK 2.12-2.13: Repository (Estimate, MarketData)
- TASK 2.14-2.15: Services (EstimateService, EstimateHistoryService)
- TASK 2.16-2.17: API Routers (Estimates, Market Data)
- TASK 2.18-2.19: MarketDataProvider Astratto e Caching/Backoff
- TASK 2.20-2.23: Google Drive Integration e Retrocompatibilità
- TASK 2.24: Background Worker APScheduler
- TASK 2.25: Pattern Outbox per Eventi

---

# SEZIONE 3: SICUREZZA, OSSERVABILITÀ, GOVERNANCE

*Task 3.1 - 3.12: Fase 2, opzionali per ambiente locale single-user*

**Task Sezione 3:**
- TASK 3.1: Security Middleware (Fase 2)
- TASK 3.2: Rate Limiting (Fase 2)
- TASK 3.3: Input Validation Avanzata
- TASK 3.4: Encryption at Rest
- TASK 3.5: Structured Logging con Correlation ID
- TASK 3.6: Metriche Prometheus (Fase 2)
- TASK 3.7: Health Checks Completi (Fase 2)
- TASK 3.8: Data Quality Monitor (Fase 2)
- TASK 3.9: Data Lineage Tracking (Fase 2)
- TASK 3.10: Connection Pooling Ottimizzato (Media priorità)
- TASK 3.11: Query Pagination Cursor-Based (Fase 2)
- TASK 3.12: Docker Compose Ambiente Locale (MVP - Alta priorità)

---

# SEZIONE 4: FRONTEND UX

*Task 4.1 - 4.15: Setup frontend React + TypeScript*

**Task Sezione 4:**
- TASK 4.1: Setup Progetto Frontend (Vite + React 19)
- TASK 4.2: Struttura Feature Modules
- TASK 4.3: Configurazione React Query
- TASK 4.4: Client API Tipizzato
- TASK 4.5: Wrapper Decimale per Calcoli Finanziari
- TASK 4.6: API Hooks per Estimates
- TASK 4.7: Error Boundary & Gestione Errori UX
- TASK 4.8-4.10: Componenti UI (EstimateForm, EstimateCard, EstimatesList)
- TASK 4.11: PWA Base (Manifest + Service Worker)
- TASK 4.12: Accessibilità Base & Skeleton i18n
- TASK 4.13: Dashboard Portfolio
- TASK 4.14: Price Chart
- TASK 4.15: Chat AI Component

---

# SEZIONE 5: TESTING, CI/CD, OPERAZIONI

*Task 5.1 - 5.17: Testing, CI/CD pipeline, deployment*

**Task Sezione 5:**
- TASK 5.1: Setup Test Framework Backend
- TASK 5.2-5.5: Unit Tests, Integration Tests, Property-Based Testing
- TASK 5.6-5.7: Test Framework Frontend e Component Tests
- TASK 5.8-5.9: E2E Tests (Playwright) e Chaos Testing
- TASK 5.10-5.11: CI/CD Pipeline (GitHub Actions)
- TASK 5.12-5.13: Feature Flags e Backup Automatico
- TASK 5.14-5.17: Docker Compose, Runbook, API Docs, Script Migrazione

---

# APPENDICE: DIPENDENZE TRA TASK

## Priorità MVP (Ambiente Locale Single-User)

### Sezione 1 (Linee Guida)
- ✅ **Tutti i task 1.1-1.7** (MVP obbligatori)

### Sezione 2 (Backend)
- ✅ **TASK 2.0** (NUOVO - prerequisito per tutto il backend)
- ✅ **TASK 2.1** (ora dipende da 2.0)
- ✅ TASK 2.3-2.6 (modelli core)
- ✅ TASK 2.10 (Alembic)
- ✅ TASK 2.12-2.13 (repositories)
- ✅ TASK 2.16-2.21 (API e MarketData)
- ✅ TASK 2.24-2.25 (scheduler e outbox)
- ⚠️ TASK 2.22-2.23 (Google Drive - opzionale se non serve sync immediato)

### Sezione 3 (Sicurezza)
- 🔴 **TASK 3.12** (Docker Compose - priorità ALTA per MVP locale)
- 🟡 TASK 3.10 (Connection pooling - priorità media, post-MVP)
- ⚪ TASK 3.1-3.9, 3.11 (Fase 2 - opzionali per single-user)

### Sezione 4 (Frontend)
- ✅ TASK 4.1-4.10 (setup e componenti core)
- ✅ TASK 4.7 (error handling)
- 🟡 TASK 4.11-4.12 (PWA e accessibilità - subito dopo per UX completa)

### Sezione 5 (Testing)
- 🟡 Test unitari e lint (5.1-5.3, 5.6-5.7) - subito dopo MVP core
- ⚪ E2E e CI/CD (5.8-5.11) - Fase 2

---

## Diagramma Dipendenze Critiche

```
[TASK 2.0] Setup Poetry & Dependencies (NUOVO)
    ↓
[TASK 2.1] SQLAlchemy Setup (AGGIORNATO - dipende da 2.0)
    ↓
[TASK 2.3-2.9] Modelli Database
    ↓
[TASK 2.10] Alembic Migrations
    ↓
[TASK 2.12-2.13] Repositories
    ↓
[TASK 2.14-2.15] Services
    ↓
[TASK 2.16-2.17] API Routers
```

---

## Ordine di Esecuzione Consigliato per MVP

1. 🔴 **TASK 2.0** - Setup Poetry (prerequisito assoluto)
2. TASK 1.1-1.7 - Setup base backend
3. TASK 2.1 - SQLAlchemy (ora dipende da 2.0)
4. TASK 2.3-2.9 - Modelli
5. TASK 2.10 - Alembic
6. TASK 3.12 - Docker Compose locale
7. TASK 2.12-2.17 - Repositories, Services, API
8. TASK 2.18-2.19 - MarketData provider
9. TASK 4.1-4.10 - Frontend core
10. TASK 2.20-2.25 - Drive sync e scheduler

---

# NOTE PER L'LLM ESECUTORE

1. ⚠️ **PRIORITÀ ASSOLUTA**: Eseguire **TASK 2.0** prima di qualsiasi altro task backend
2. Verificare che `poetry install` funzioni prima di procedere con i task successivi
3. Usare `make check-deps` per verificare l'installazione delle dipendenze
4. Esegui un task alla volta e verifica gli acceptance criteria prima di procedere
5. Chiedi chiarimenti se un requisito è ambiguo
6. Documenta ogni scelta implementativa non ovvia
7. Testa ogni componente prima di passare al successivo
8. Committa con messaggi descrittivi che referenziano il task ID
9. Segnala blocchi o dipendenze mancanti

---

**Fine Piano Operativo v1.4**

*Documento generato il 31/01/2026*
