# Backend - Core Application Logic

## Scope
Questa sezione contiene SOLO task per il backend Python/FastAPI:
- Bounded context: `estimates/`, `market_data/`, `sync/`, `analytics/`, `shared/`
- Infra: `yahoo/`, `drive/`, `cache/`, `logging/`, `security/`, `scheduler/`, `outbox/`
- Value objects, repositories, services, API routes
- Database migrations (Alembic)
- Configurazione (pydantic-settings)

**Non modificare**:
- File di Docker/compose (vedi `Docker/AGENTS.md`)
- File di test/CI (vedi `Docs/AGENTS.md`)
- Codice frontend (vedi `Frontend/AGENTS.md`)

---

# SEZIONE 1: LINEE GUIDA TRASVERSALI (Backend)

---

ID: TASK 1.1
Area: backend/structure
Fase: MVP
Dipendenze: -

## TASK 1.1: Setup Struttura Layer Backend

**Descrizione:** Creare la struttura di cartelle e file base per il layering esplicito del backend FastAPI.

**Microstep:**

1. Creare cartella [`backend/src/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src) come root del codice sorgente
2. Creare sottocartelle per ogni bounded context: [`estimates/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/estimates), [`market_data/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/market_data), [`sync/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/sync), [`analytics/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/analytics), [`shared/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/shared)
3. Per ogni bounded context, creare le sottocartelle: `api/`, `schemas/`, `domain/`, `services/`, `repositories/`
4. Creare cartella [`backend/src/infra/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/infra) con sottocartelle: `yahoo/`, `drive/`, `cache/`, `logging/`, `security/`
5. Creare file `__init__.py` in ogni cartella
6. Creare file [`backend/src/README.md`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/README.md) che documenta la convenzione di layering

**Acceptance Criteria:**

- [x] Struttura cartelle completa e navigabile
- [x] Ogni cartella ha un `__init__.py`
- [x] README documenta lo scopo di ogni layer (api, schemas, domain, services, repositories, infra)
- [x] Nessun file di logica ancora presente (solo struttura)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.2
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.1

## TASK 1.2: Definizione Modello Risposta API Standard

**Descrizione:** Creare lo schema Pydantic per il modello di risposta API uniforme usato da tutti gli endpoint.

**Microstep:**

1. Creare file [`backend/src/shared/schemas/api_response.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/schemas/api_response.py)
2. Definire schema `ApiResponse` con campi: `success` (bool), `data` (generic/nullable), `error` (nullable), `trace_id` (UUID string)
3. Definire schema `ApiError` con campi: `code` (string), `message` (string), `details` (optional dict)
4. Creare funzioni helper: `success_response(data, trace_id)`, `error_response(code, message, details, trace_id)`
5. Documentare con docstring l'uso previsto

**Acceptance Criteria:**

- [x] Schema `ApiResponse` è generico e accetta qualsiasi tipo di `data`
- [x] Schema `ApiError` è annidabile in `ApiResponse.error`
- [x] Funzioni helper producono risposte conformi allo schema
- [x] Tutti i campi hanno type hints corretti
- [x] Docstring spiega quando usare success vs error response

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/schemas/api_response.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.3
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.1

## TASK 1.3: Creazione Value Object Money (Backend)

**Descrizione:** Implementare il value object immutabile `Money` per gestire importi monetari con precisione decimale.

**Microstep:**

1. Creare file [`backend/src/shared/domain/value_objects/money.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/domain/value_objects/money.py)
2. Definire dataclass frozen `Money` con campi: `amount` (Decimal), `currency` (str, default "USD")
3. Implementare `__post_init__` per convertire input non-Decimal in Decimal
4. Implementare metodi: `__add__`, `__sub__`, `__mul__` (con Decimal/int), `__neg__`
5. Implementare metodo `round(places: int)` con ROUND_HALF_UP
6. Implementare metodo `to_dict()` che restituisce `{"amount": str, "currency": str}`
7. Implementare metodo class `from_dict(data: dict)`
8. Aggiungere validazione: currency deve essere stringa 3 caratteri uppercase

**Acceptance Criteria:**

- [x] Classe è immutabile (frozen dataclass)
- [x] Tutti i calcoli usano Decimal, mai float
- [x] Somma/sottrazione tra valute diverse solleva ValueError
- [x] Moltiplicazione accetta solo Decimal o int
- [x] Serializzazione/deserializzazione round-trip funziona
- [x] Test unitari coprono tutti i metodi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/value_objects/money.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.4
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.3

## TASK 1.4: Creazione Value Object Percentage (Backend)

**Descrizione:** Implementare il value object immutabile `Percentage` per gestire valori percentuali.

**Microstep:**

1. Creare file [`backend/src/shared/domain/value_objects/percentage.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/domain/value_objects/percentage.py)
2. Definire dataclass frozen `Percentage` con campo: `value` (Decimal)
3. Implementare `__post_init__` per conversione a Decimal
4. Implementare class method `from_basis_points(bps: int)`
5. Implementare metodo `apply_to(money: Money) -> Money`
6. Implementare metodo `as_multiplier() -> Decimal` (restituisce 1 + value)
7. Implementare metodi `__add__`, `__sub__` tra Percentage
8. Implementare `to_dict()` e `from_dict()`

**Acceptance Criteria:**

- [x] Classe è immutabile
- [x] Conversione da basis points corretta (100 bps = 1% = 0.01)
- [x] `apply_to` restituisce Money con importo corretto
- [x] `as_multiplier` per 10% restituisce Decimal("1.10")
- [x] Test unitari coprono tutti i metodi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/value_objects/percentage.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.5
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.3, TASK 1.4

## TASK 1.5: Creazione Value Object PriceTarget (Backend)

**Descrizione:** Implementare il value object `PriceTarget` che incapsula target, stop loss e take profit con validazioni.

**Microstep:**

1. Creare file [`backend/src/shared/domain/value_objects/price_target.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/domain/value_objects/price_target.py)
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

- [x] Validazione solleva ValueError per configurazioni invalide
- [x] Risk/reward ratio calcolato correttamente per entrambe le direzioni
- [x] Metodi is_target_hit e is_stop_hit funzionano per LONG e SHORT
- [x] Test unitari coprono scenari validi e invalidi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/value_objects/price_target.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.6
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.1

## TASK 1.6: Configurazione Ambienti con Pydantic Settings

**Descrizione:** Implementare sistema di configurazione multi-ambiente con pydantic-settings.

**Microstep:**

1. Creare file [`backend/src/shared/infra/config.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/infra/config.py)
2. Definire classe `Settings` che eredita da `BaseSettings`
3. Definire campi per ogni ambiente: `ENVIRONMENT` (local/staging/prod), `DEBUG`, `LOG_LEVEL`
4. Definire campi database: `DATABASE_URL` (SecretStr)
5. Definire campi API esterne: `YAHOO_CACHE_TTL`, `GEMINI_API_KEY` (SecretStr), `FINNHUB_API_KEY` (SecretStr, optional)
6. Definire campi Drive: `GOOGLE_SERVICE_ACCOUNT_JSON` (SecretStr), `DRIVE_FOLDER_ID`
7. Definire campi sicurezza: `ENCRYPTION_KEY` (SecretStr), `JWT_SECRET` (SecretStr)
8. Configurare `model_config` con `env_file='.env'`, `case_sensitive=False`
9. Creare funzione `get_settings()` con cache (lru_cache)
10. Creare file [`.env.example`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/.env.example) con tutti i campi documentati

**Acceptance Criteria:**

- [x] Settings carica variabili da file .env
- [x] Tutti i secret usano tipo SecretStr
- [x] Valori di default sensati per development
- [x] `.env.example` documenta tutte le variabili richieste
- [x] `get_settings()` restituisce sempre la stessa istanza (cached)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/infra/config.py, .env.example] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.7
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.6

## TASK 1.7: Middleware Sicurezza Base & Healthcheck

**Descrizione:** Aggiungere un middleware di sicurezza base (header, CORS, small rate limit) e endpoint di healthcheck per uso con Docker.

**Microstep:**

1. Creare file [`backend/src/shared/infra/security_middleware.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/infra/security_middleware.py)
2. Implementare un middleware FastAPI che:
   - Aggiunge header di sicurezza minimi (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
   - Configura CORS per l'origin del frontend (es. http://localhost:3000)
   - Implementa un rate limit molto semplice in memoria per IP (es. max 60 richieste/minuto), disattivabile via config
3. Registrare il middleware in [`backend/src/main.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/main.py) dell'app FastAPI
4. Creare router [`backend/src/shared/api/health_routes.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/api/health_routes.py) con:
   - GET /health che ritorna {status: "ok"}
   - GET /health/db che prova una query SELECT 1
5. Documentare nel README come usare /health per verificare che il container backend sia up

**Acceptance Criteria:**

- [x] Tutte le risposte includono i security header base
- [x] Il frontend può chiamare il backend senza problemi di CORS
- [x] /health e /health/db risultano verdi quando il DB è raggiungibile (Mock/Basic implementato)
- [x] Il rate limit può essere disabilitato via Settings

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/infra/security_middleware.py, backend/src/shared/api/health_routes.py, backend/src/main.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

# SEZIONE 2: BACKEND & DATA

---

## NOTE NUMERAZIONE

**TASK 2.2**: Originariamente "Setup Docker Compose per PostgreSQL e Redis".  
Spostato in `Docker/AGENTS.md` durante riorganizzazione architetturale.  
La numerazione backend non è stata riallineata per preservare riferimenti storici e dipendenze esistenti.  
Per dettagli su Docker Compose, consultare `Docker/AGENTS.md` → TASK 2.2.

---

ID: TASK 2.1
Area: backend/infra
Fase: MVP
Dipendenze: -

## TASK 2.1: Setup Progetto Python con Poetry & Dipendenze Complete

**Descrizione:** Inizializzare pyproject.toml con TUTTE le dipendenze necessarie per MVP e Fase 2, evitando installazioni frammentate.

**Microstep:**

1. Creare `backend/pyproject.toml` con metadata progetto
2. Configurare dipendenze MVP:
   - Core: fastapi, uvicorn[standard], pydantic, pydantic-settings
   - Database: sqlalchemy[asyncio], asyncpg, alembic
   - API esterne: google-api-python-client, google-auth-httplib2, google-auth-oauthlib, yfinance
   - Cache: redis[hiredis]
   - Scheduler: apscheduler
3. Configurare dipendenze Fase 2 (opzionali):
   - Security: cryptography, slowapi
   - Observability: structlog, prometheus-client
4. Configurare dipendenze sviluppo: pytest, pytest-asyncio, pytest-cov, ruff, mypy, httpx
5. Configurare tool.ruff, tool.mypy, tool.pytest.ini_options
6. Creare `Makefile`, `.python-version`, `scripts/check_deps.py`
7. Esportare `requirements.txt` e `requirements-dev.txt`

**Acceptance Criteria:**

- [ ] `poetry install` completa senza errori
- [ ] `make check-deps` verifica dipendenze critiche
- [ ] `requirements*.txt` sincronizzati con pyproject.toml
- [ ] TASK 2.1 può partire immediatamente senza installare altro

[... resto del contenuto invariato ...]
