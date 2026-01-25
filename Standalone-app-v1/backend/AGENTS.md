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

1. Creare cartella `backend/src/` come root del codice sorgente
2. Creare sottocartelle per ogni bounded context: `estimates/`, `market_data/`, `sync/`, `analytics/`, `shared/`
3. Per ogni bounded context, creare le sottocartelle: `api/`, `schemas/`, `domain/`, `services/`, `repositories/`
4. Creare cartella `backend/src/infra/` con sottocartelle: `yahoo/`, `drive/`, `cache/`, `logging/`, `security/`
5. Creare file `__init__.py` in ogni cartella
6. Creare file `README.md` in `backend/src/` che documenta la convenzione di layering

**Acceptance Criteria:**

- [ ] Struttura cartelle completa e navigabile
- [ ] Ogni cartella ha un `__init__.py`
- [ ] README documenta lo scopo di ogni layer (api, schemas, domain, services, repositories, infra)
- [ ] Nessun file di logica ancora presente (solo struttura)

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

1. Creare file `backend/src/shared/infra/security_middleware.py`
2. Implementare un middleware FastAPI che:
   - Aggiunge header di sicurezza minimi (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
   - Configura CORS per l'origin del frontend (es. http://localhost:3000)
   - Implementa un rate limit molto semplice in memoria per IP (es. max 60 richieste/minuto), disattivabile via config
3. Registrare il middleware in main.py dell'app FastAPI
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

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/infra/security_middleware.py, backend/src/shared/api/health_routes.py, backend/src/main.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

# SEZIONE 2: BACKEND & DATA

---

ID: TASK 2.1
Area: backend/infra
Fase: MVP
Dipendenze: TASK 1.6

## TASK 2.1: Setup SQLAlchemy e Database Connection Pool

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

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/database.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.3
Area: backend/estimates
Fase: MVP
Dipendenze: TASK 2.1

## TASK 2.3: Definizione Aggregate Estimate (Domain)

**Descrizione:** Creare aggregate root Estimate con logica domain.

**Microstep:**

1. Creare file `backend/src/estimates/domain/estimate.py`
2. Definire dataclass `Estimate` con campi: id, ticker, direction, entry_price, stop_loss, take_profit, created_at, closed_at (optional), status
3. Implementare metodo `calculate_pnl(exit_price: Money) -> Money`
4. Implementare metodo `calculate_pnl_percentage(exit_price: Money) -> Percentage`
5. Implementare metodo `close(exit_price: Money) -> EstimateClosedEvent`
6. Implementare metodo `check_targets(current_price: Money) -> Optional[TargetHitEvent]`
7. Validazioni: non permettere close se già chiuso, non calcolare PnL se non chiuso
8. Immutabilità: usare metodi che restituiscono nuovi oggetti

**Acceptance Criteria:**

- [ ] Estimate è un aggregate root valido
- [ ] Logica PnL corretta per LONG e SHORT
- [ ] Eventi domain emessi per azioni significative
- [ ] Validazioni impediscono stati inconsistenti
- [ ] Test unitari coprono tutti i metodi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/domain/estimate.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.4
Area: backend/estimates
Fase: MVP
Dipendenze: TASK 2.3

## TASK 2.4: Implementazione Repository Estimates (CQRS Write)

**Descrizione:** Implementare repository per persistenza aggregate Estimate (lato write).

**Microstep:**

1. Creare file `backend/src/estimates/repositories/estimate_repository.py`
2. Definire interfaccia `EstimateRepository` (ABC) con metodi: save, get_by_id, delete
3. Implementare `SqlAlchemyEstimateRepository`
4. Implementare metodo save: insert se nuovo, update se esistente
5. Implementare metodo get_by_id: carica da DB e ricostruisce domain object
6. Implementare metodo delete: soft delete (imposta deleted_at)
7. Gestire transazioni: commit/rollback automatico
8. Implementare conversione ORM <-> Domain model

**Acceptance Criteria:**

- [ ] Repository segue pattern CQRS write
- [ ] Save è idempotente
- [ ] Errori database gestiti (UniqueViolation, NotFound)
- [ ] Conversione domain <-> DB funziona
- [ ] Test integrazione con DB

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/repositories/estimate_repository.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.5
Area: backend/market_data
Fase: MVP
Dipendenze: TASK 2.1

## TASK 2.5: Implementazione YahooFinanceProvider

**Descrizione:** Creare provider per recupero dati da Yahoo Finance con caching.

**Microstep:**

1. Creare file `backend/src/infra/yahoo/yahoo_provider.py`
2. Installare dipendenza yfinance
3. Implementare metodo get_current_price(ticker: str) -> Money
4. Implementare metodo get_historical_prices(ticker, start, end) -> List[OHLCV]
5. Implementare metodo validate_ticker(ticker: str) -> bool
6. Gestire errori: ticker non trovato, API timeout, rate limit
7. Implementare retry logic con backoff esponenziale
8. Implementare caching in-memory (TTL 5 minuti per current price)

**Acceptance Criteria:**

- [ ] get_current_price restituisce Money valido
- [ ] Errori gestiti con eccezioni custom (TickerNotFound, ApiError)
- [ ] Retry funziona su errori transitori
- [ ] Cache riduce chiamate ripetute
- [ ] Test con mock API

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/yahoo/yahoo_provider.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.6
Area: backend/infra
Fase: MVP
Dipendenze: TASK 2.1

## TASK 2.6: Implementazione Event Store

**Descrizione:** Creare event store per Event Sourcing.

**Microstep:**

1. Creare file `backend/src/infra/event_store.py`
2. Definire tabella events: id, aggregate_id, aggregate_type, event_type, event_data (JSONB), timestamp, version
3. Implementare metodo append_event(aggregate_id, event)
4. Implementare metodo get_events(aggregate_id) -> List[Event]
5. Implementare ottimistic locking con version check
6. Implementare snapshot mechanism (ogni N eventi)
7. Implementare metodo replay_events per ricostruire stato
8. Gestire concurrent append con retry

**Acceptance Criteria:**

- [ ] Eventi append in ordine con versioning
- [ ] Conflitti concorrenti gestiti (ConcurrentModificationError)
- [ ] Replay ricostruisce stato corretto
- [ ] Snapshot riduce eventi da leggere
- [ ] Test concorrenza con thread multipli

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/event_store.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.7
Area: backend/shared
Fase: Fase 2
Dipendenze: TASK 2.1

## TASK 2.7: Creazione Modello User

**Descrizione:** Definire modello User per gestione autenticazione.

**Microstep:**

1. Creare file `backend/src/shared/domain/user/user.py`
2. Definire dataclass User: id, email, hashed_password, full_name, is_active, created_at
3. Implementare metodo verify_password(plain_password) -> bool
4. Implementare class method hash_password(plain_password) -> str (bcrypt)
5. Creare file `backend/src/shared/repositories/user_repository.py`
6. Implementare get_by_email, create, update
7. Implementare validazione email con regex
8. Implementare soft delete

**Acceptance Criteria:**

- [ ] Password hashate con bcrypt
- [ ] Validazione email funzionante
- [ ] Repository segue pattern standard
- [ ] Test unitari per hashing/verificazione password

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/user/user.py, backend/src/shared/repositories/user_repository.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.8
Area: backend/shared
Fase: Fase 2
Dipendenze: TASK 2.7

## TASK 2.8: Implementazione JWT Authentication

**Descrizione:** Sistema autenticazione basato su JWT tokens.

**Microstep:**

1. Installare python-jose[cryptography], passlib
2. Creare file `backend/src/shared/infra/security/jwt.py`
3. Implementare create_access_token(data: dict, expires_delta: timedelta)
4. Implementare verify_token(token: str) -> dict (solleva JWTError se invalido)
5. Implementare get_current_user dependency per FastAPI
6. Configurare SECRET_KEY e ALGORITHM da Settings
7. Creare endpoint POST /auth/login: verifica credenziali, restituisce token
8. Creare endpoint POST /auth/refresh: refresh token

**Acceptance Criteria:**

- [ ] Token JWT validi generati
- [ ] Token scaduti rifiutati
- [ ] get_current_user dependency funziona
- [ ] Login endpoint restituisce token
- [ ] Test con token validi/invalidi/scaduti

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/infra/security/jwt.py, backend/src/shared/api/auth_routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.9
Area: backend/shared
Fase: Fase 2
Dipendenze: TASK 2.7

## TASK 2.9: Implementazione Role-Based Access Control

**Descrizione:** Sistema RBAC per autorizzazioni granulari.

**Microstep:**

1. Creare file `backend/src/shared/domain/user/role.py`
2. Definire enum Role: USER, ADMIN, ANALYST
3. Creare file `backend/src/shared/infra/security/rbac.py`
4. Implementare decorator require_role(role: Role) per endpoint
5. Modificare User per includere campo roles: List[Role]
6. Implementare check_permission(user, resource, action) -> bool
7. Creare middleware che verifica ruolo prima di route
8. Gestire errori con HTTPException 403 Forbidden

**Acceptance Criteria:**

- [ ] Decorator require_role blocca utenti non autorizzati
- [ ] ADMIN ha accesso completo
- [ ] USER ha accesso limitato
- [ ] Test con utenti di ruoli diversi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/user/role.py, backend/src/shared/infra/security/rbac.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.10
Area: backend/infra
Fase: MVP
Dipendenze: TASK 2.1

## TASK 2.10: Configurazione Alembic per Migrations

**Descrizione:** Setup sistema migrations database con Alembic.

**Microstep:**

1. Installare alembic
2. Inizializzare Alembic: `alembic init alembic`
3. Configurare `alembic.ini` con DATABASE_URL da Settings
4. Configurare `env.py` per importare Base da SQLAlchemy
5. Creare prima migration: tabella estimates
6. Creare migration: tabella events
7. Creare migration: tabella market_data
8. Implementare script upgrade/downgrade
9. Documentare workflow migrations nel README

**Acceptance Criteria:**

- [ ] `alembic upgrade head` applica tutte le migrations
- [ ] `alembic downgrade -1` fa rollback
- [ ] Migrations compatibili con PostgreSQL
- [ ] README documenta comandi comuni

---

### Istruzioni per LLM
- Non modificare file fuori da [alembic/, alembic.ini, backend/README.md] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.11
Area: backend/estimates
Fase: MVP
Dipendenze: TASK 2.4, TASK 2.6

## TASK 2.11: Implementazione Command Handler CreateEstimate

**Descrizione:** Implementare command handler per creazione stime (CQRS pattern).

**Microstep:**

1. Creare file `backend/src/estimates/services/command_handlers.py`
2. Definire dataclass `CreateEstimateCommand`: ticker, direction, stop_loss_pct, take_profit_pct
3. Implementare handler `handle_create_estimate(cmd) -> Estimate`
4. Nel handler:
   - Recupera prezzo corrente da YahooProvider
   - Calcola stop_loss e take_profit da percentuali
   - Crea aggregate Estimate
   - Salva via EstimateRepository
   - Pubblica EstimateCreatedEvent su EventStore
5. Gestire errori: ticker invalido, prezzi non disponibili
6. Implementare validazioni: percentuali in range sensato

**Acceptance Criteria:**

- [ ] Command pattern implementato correttamente
- [ ] Eventi pubblicati su event store
- [ ] Errori gestiti con eccezioni domain
- [ ] Test unitari con mock repository

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/services/command_handlers.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.12
Area: backend/estimates
Fase: MVP
Dipendenze: TASK 2.4, TASK 2.10

## TASK 2.12: Implementazione Query Projection Estimates

**Descrizione:** Creare materialized view per query efficienti (CQRS read).

**Microstep:**

1. Creare file `backend/src/estimates/repositories/estimate_query_repository.py`
2. Definire tabella read-optimized `estimates_read_model`: dati denormalizzati
3. Implementare query: list_all, filter_by_status, filter_by_ticker, search
4. Implementare paginazione cursor-based
5. Implementare ordinamento (created_at, pnl, ticker)
6. Creare projection handler che aggiorna read model da eventi
7. Implementare eventual consistency: handler eventi -> aggiorna projection

**Acceptance Criteria:**

- [ ] Query veloci su dati denormalizzati
- [ ] Projection aggiornata da eventi
- [ ] Paginazione funzionante
- [ ] Test con dataset grande (1000+ record)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/repositories/estimate_query_repository.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.13
Area: backend/estimates
Fase: MVP
Dipendenze: TASK 2.6, TASK 2.10

## TASK 2.13: Implementazione Event Subscribers

**Descrizione:** Creare subscribers per eventi domain.

**Microstep:**

1. Creare file `backend/src/estimates/services/event_subscribers.py`
2. Implementare `EstimateCreatedSubscriber`: logga evento, aggiorna analytics
3. Implementare `EstimateClosedSubscriber`: calcola PnL, invia notifica
4. Implementare `TargetHitSubscriber`: logga alert
5. Registrare subscribers in event dispatcher
6. Implementare pattern publish-subscribe
7. Gestire errori in subscriber senza bloccare publisher
8. Implementare retry su failure

**Acceptance Criteria:**

- [ ] Subscribers ricevono eventi
- [ ] Failure in subscriber non blocca flow
- [ ] Eventi processati in ordine
- [ ] Test con mock subscribers

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/services/event_subscribers.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.14
Area: backend/estimates
Fase: MVP
Dipendenze: TASK 2.12

## TASK 2.14: Implementazione API Endpoint List Estimates

**Descrizione:** Endpoint GET per listare stime con filtri.

**Microstep:**

1. Creare file `backend/src/estimates/api/estimate_routes.py`
2. Implementare GET /api/estimates
3. Parametri query: status, ticker, page, per_page, sort_by, order
4. Usare QueryRepository per dati
5. Restituire ApiResponse con lista paginata
6. Implementare validazione parametri (Pydantic)
7. Gestire errori con HTTPException
8. Documentare con docstring OpenAPI

**Acceptance Criteria:**

- [ ] Endpoint restituisce lista paginata
- [ ] Filtri funzionanti
- [ ] Validazione parametri
- [ ] Documentazione OpenAPI completa
- [ ] Test API con client HTTP

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/api/estimate_routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.15
Area: backend/estimates
Fase: MVP
Dipendenze: TASK 2.5, TASK 2.12

## TASK 2.15: Implementazione API Endpoint Get Estimate

**Descrizione:** Endpoint GET per singola stima.

**Microstep:**

1. Implementare GET /api/estimates/{estimate_id}
2. Recupera da QueryRepository
3. Arricchisce con prezzo corrente (Yahoo)
4. Calcola PnL non realizzato se aperta
5. Restituisce schema EstimateDetailResponse
6. Gestire 404 se non trovata
7. Implementare cache HTTP (ETag)

**Acceptance Criteria:**

- [ ] Endpoint restituisce dettaglio completo
- [ ] PnL aggiornato con prezzo live
- [ ] 404 su ID non valido
- [ ] Cache HTTP funzionante
- [ ] Test con estimate aperta/chiusa

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/api/estimate_routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.16
Area: backend/estimates
Fase: MVP
Dipendenze: TASK 2.14

## TASK 2.16: Implementazione API Endpoint Create Estimate

**Descrizione:** Endpoint POST per creare nuova stima.

**Microstep:**

1. Implementare POST /api/estimates
2. Definire schema CreateEstimateRequest (Pydantic)
3. Validare input: ticker formato, percentuali range
4. Chiamare CommandHandler create_estimate
5. Restituire 201 Created con location header
6. Gestire errori: ticker non valido (400), API error (503)
7. Implementare idempotency key

**Acceptance Criteria:**

- [ ] Endpoint crea stima valida
- [ ] Validazione input funzionante
- [ ] 201 con location header
- [ ] Idempotency evita duplicati
- [ ] Test con input validi/invalidi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/api/estimate_routes.py, backend/src/estimates/schemas/estimate_schemas.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.17
Area: backend/market_data
Fase: MVP
Dipendenze: TASK 2.5

## TASK 2.17: Implementazione MarketDataRepository

**Descrizione:** Repository per storico dati di mercato.

**Microstep:**

1. Creare file `backend/src/market_data/repositories/market_data_repository.py`
2. Definire tabella market_data: ticker, date, open, high, low, close, volume
3. Implementare save_bulk(data: List[OHLCV])
4. Implementare get_historical(ticker, start, end)
5. Implementare get_latest_price(ticker)
6. Creare indici: (ticker, date) unique, (ticker) btree
7. Implementare upsert per evitare duplicati
8. Implementare query ottimizzate con window functions

**Acceptance Criteria:**

- [ ] Bulk insert performante (1000+ record)
- [ ] Query veloci su range temporali
- [ ] Indici ottimizzati
- [ ] Upsert evita duplicati
- [ ] Test con dati storici reali

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/repositories/market_data_repository.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.18
Area: backend/market_data
Fase: MVP
Dipendenze: TASK 2.17

## TASK 2.18: Implementazione API MarketData Endpoints

**Descrizione:** Endpoint per recupero dati storici.

**Microstep:**

1. Creare file `backend/src/market_data/api/market_data_routes.py`
2. Implementare GET /api/market-data/{ticker}/historical
3. Parametri: start_date, end_date, interval (daily/weekly/monthly)
4. Fetch da repository, fallback a Yahoo se mancante
5. Restituire OHLCV array
6. Implementare cache HTTP (ETag basato su last date)
7. Implementare compressione gzip

**Acceptance Criteria:**

- [ ] Endpoint restituisce dati storici
- [ ] Fallback a Yahoo funziona
- [ ] Cache HTTP riduce query DB
- [ ] Compressione riduce payload
- [ ] Test con range temporali vari

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/api/market_data_routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.19
Area: backend/market_data
Fase: MVP
Dipendenze: TASK 2.18

## TASK 2.19: Implementazione In-Memory Cache

**Descrizione:** Cache in-memory per prezzi correnti.

**Microstep:**

1. Creare file `backend/src/infra/cache/memory_cache.py`
2. Implementare classe Cache con TTL
3. Usare dict con timestamp per ogni entry
4. Implementare get, set, delete, clear
5. Implementare background task per pulizia expired
6. Integrare in YahooProvider
7. Configurare TTL via Settings

**Acceptance Criteria:**

- [ ] Cache riduce chiamate Yahoo
- [ ] Expired entries rimossi automaticamente
- [ ] Thread-safe per accesso concorrente
- [ ] Test con TTL vari

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/cache/memory_cache.py, backend/src/infra/yahoo/yahoo_provider.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.20
Area: backend/sync
Fase: MVP
Dipendenze: TASK 2.1

## TASK 2.20: Implementazione GoogleDriveClient

**Descrizione:** Client per interazione con Google Drive API.

**Microstep:**

1. Creare file `backend/src/infra/drive/google_drive_client.py`
2. Installare google-api-python-client
3. Implementare autenticazione con service account
4. Implementare list_files(folder_id) -> List[DriveFile]
5. Implementare download_file(file_id) -> bytes
6. Implementare upload_file(file_name, content, folder_id)
7. Gestire errori: auth failure, quota exceeded, file not found
8. Implementare retry con backoff

**Acceptance Criteria:**

- [ ] Autenticazione service account funzionante
- [ ] List/download/upload operazioni complete
- [ ] Errori gestiti con eccezioni custom
- [ ] Retry su errori transitori
- [ ] Test con mock Google API

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/drive/google_drive_client.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.21
Area: backend/sync
Fase: MVP
Dipendenze: TASK 2.20

## TASK 2.21: Implementazione CSV Parser Legacy

**Descrizione:** Parser per CSV legacy (History_*.csv).

**Microstep:**

1. Creare file `backend/src/sync/infra/csv_parser.py`
2. Implementare parse_history_csv(content: str) -> List[EstimateLegacy]
3. Gestire colonne: Date, Ticker, Action, Price, Quantity, Fee
4. Implementare validazione: date format, numeric values
5. Gestire encoding (UTF-8, Latin-1)
6. Implementare error recovery: riga invalida -> skip con warning
7. Creare dataclass EstimateLegacy per dati raw

**Acceptance Criteria:**

- [ ] Parser legge CSV legacy
- [ ] Validazione robusta
- [ ] Errori non bloccano parsing
- [ ] Test con CSV reali

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/sync/infra/csv_parser.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.22
Area: backend/sync
Fase: MVP
Dipendenze: TASK 2.21

## TASK 2.22: Implementazione Sync Engine

**Descrizione:** Motore sincronizzazione Drive -> DB.

**Microstep:**

1. Creare file `backend/src/sync/services/sync_engine.py`
2. Implementare sync_from_drive():
   - Lista files da Drive
   - Filtra History_*.csv
   - Download files
   - Parse CSV
   - Converte in Estimate v3
   - Salva in DB
3. Implementare conflict resolution: se estimate esiste, merge
4. Implementare sync incrementale: track last_sync_timestamp
5. Implementare rollback su failure
6. Logga operazioni (created, updated, skipped)

**Acceptance Criteria:**

- [ ] Sync importa CSV legacy
- [ ] Conflict resolution funzionante
- [ ] Sync incrementale riduce lavoro
- [ ] Rollback su errore
- [ ] Test end-to-end con Drive mock

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/sync/services/sync_engine.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.23
Area: backend/sync
Fase: MVP
Dipendenze: TASK 2.22

## TASK 2.23: Test Retro-Compatibilità con Dati Legacy

**Descrizione:** Validare che app v3 legge correttamente dati v1/v2.

**Microstep:**

1. Creare cartella `tests/fixtures/legacy/`
2. Aggiungere backup reale: portfolio.json v1
3. Aggiungere CSV reali: History_2023.csv, History_2024.csv
4. Creare test `test_legacy_import.py`
5. Testare import JSON -> DB v3
6. Testare import CSV -> DB v3
7. Validare: tutti i campi mappati correttamente
8. Validare: PnL ricalcolato corrisponde a legacy

**Acceptance Criteria:**

- [ ] Import JSON funziona
- [ ] Import CSV funziona
- [ ] Dati mappati correttamente
- [ ] PnL consistente
- [ ] Test passano con dati reali

---

### Istruzioni per LLM
- Non modificare file fuori da [tests/fixtures/legacy/, tests/e2e/test_legacy_import.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.24
Area: backend/sync
Fase: MVP
Dipendenze: TASK 2.11, TASK 2.22

## TASK 2.24: Implementazione Scheduled Task Sync

**Descrizione:** Task schedulato per sync automatico.

**Microstep:**

1. Installare APScheduler
2. Creare file `backend/src/infra/scheduler/scheduler.py`
3. Configurare job sync_drive_data ogni 1 ora
4. Implementare startup: esegui sync iniziale
5. Implementare graceful shutdown
6. Logga risultati sync (success, failure, skipped)
7. Implementare health endpoint /scheduler/status

**Acceptance Criteria:**

- [ ] Scheduler esegue job periodico
- [ ] Sync automatico funziona
- [ ] Shutdown graceful
- [ ] Health status visibile
- [ ] Test con mock scheduler

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/scheduler/scheduler.py, backend/src/main.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.25
Area: backend/sync
Fase: Fase 2
Dipendenze: TASK 2.24

## TASK 2.25: Implementazione Outbox Pattern

**Descrizione:** Pattern outbox per eventi atomici.

**Microstep:**

1. Creare file `backend/src/infra/outbox/outbox_processor.py`
2. Definire tabella outbox_events: id, aggregate_id, event_type, payload, processed_at
3. Implementare save_to_outbox(event) in transazione DB
4. Implementare OutboxProcessor: polling outbox table
5. Pubblicare eventi non processati
6. Marcare come processed
7. Implementare retry su failure
8. Configurare polling interval

**Acceptance Criteria:**

- [ ] Eventi salvati atomicamente con aggregate
- [ ] Processor pubblica eventi in ordine
- [ ] Retry su fallimento
- [ ] Nessun evento perso
- [ ] Test con failure simulato

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/outbox/outbox_processor.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.26
Area: backend/analytics
Fase: Fase 2
Dipendenze: TASK 2.12

## TASK 2.26: Implementazione Analytics Aggregates

**Descrizione:** Aggregazioni per dashboard analytics.

**Microstep:**

1. Creare file `backend/src/analytics/services/aggregation_service.py`
2. Implementare calculate_portfolio_stats():
   - Total PnL realized
   - Total PnL unrealized
   - Win rate
   - Average RR ratio
3. Implementare calculate_ticker_performance(ticker)
4. Implementare calculate_time_series_pnl(period)
5. Usare QueryRepository + SQL window functions
6. Cache risultati (TTL 5 minuti)

**Acceptance Criteria:**

- [ ] Stats calcolati correttamente
- [ ] Performance ottimizzata (query aggregate)
- [ ] Cache riduce carico
- [ ] Test con dati variati

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/analytics/services/aggregation_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.27
Area: backend/analytics
Fase: Fase 2
Dipendenze: TASK 2.26

## TASK 2.27: Implementazione API Analytics Endpoints

**Descrizione:** Endpoint per statistiche portfolio.

**Microstep:**

1. Creare file `backend/src/analytics/api/analytics_routes.py`
2. Implementare GET /api/analytics/portfolio
3. Implementare GET /api/analytics/ticker/{ticker}
4. Implementare GET /api/analytics/pnl-history
5. Parametri: time_range (7d, 30d, 1y, all)
6. Cache HTTP (ETag)
7. Documentare con OpenAPI

**Acceptance Criteria:**

- [ ] Endpoint restituiscono statistiche
- [ ] Cache funzionante
- [ ] Documentazione completa
- [ ] Test con vari time range

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/analytics/api/analytics_routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

# SEZIONE 3: SICUREZZA & OBSERVABILITY (Backend only)

---

ID: TASK 3.1
Area: backend/security
Fase: Fase 2
Dipendenze: TASK 2.8

## TASK 3.1: Implementazione Rate Limiting Avanzato

**Descrizione:** Rate limiting granulare per endpoint.

**Microstep:**

1. Installare slowapi
2. Creare file `backend/src/infra/security/rate_limiter.py`
3. Configurare limit: 100 req/min per IP
4. Configurare limit: 1000 req/min per utente autenticato
5. Implementare whitelist IP admin
6. Implementare storage Redis per limiti distribuiti
7. Restituire 429 Too Many Requests con Retry-After header

**Acceptance Criteria:**

- [ ] Limit per IP funzionante
- [ ] Limit per user funzionante
- [ ] Redis storage per multi-instance
- [ ] Header Retry-After presente
- [ ] Test con burst requests

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/security/rate_limiter.py, backend/src/main.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.2
Area: backend/security
Fase: Fase 2
Dipendenze: TASK 3.1

## TASK 3.2: Implementazione Request ID & Correlation Tracing

**Descrizione:** Tracciamento richieste end-to-end.

**Microstep:**

1. Creare middleware `backend/src/infra/logging/correlation_middleware.py`
2. Generare UUID per ogni richiesta (X-Request-ID)
3. Propagare ID in tutti i log
4. Aggiungere ID a response headers
5. Integrare con logger structlog
6. Implementare context var per accesso ID ovunque
7. Logga request/response per audit

**Acceptance Criteria:**

- [ ] Ogni richiesta ha ID unico
- [ ] ID presente in tutti i log
- [ ] ID in response header
- [ ] Audit trail completo
- [ ] Test verifica ID propagazione

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/logging/correlation_middleware.py, backend/src/main.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.3
Area: backend/security
Fase: Fase 2
Dipendenze: TASK 2.6

## TASK 3.3: Implementazione Audit Log

**Descrizione:** Log eventi critici per audit.

**Microstep:**

1. Creare tabella audit_log: id, user_id, action, resource, timestamp, ip, metadata
2. Creare file `backend/src/infra/logging/audit_logger.py`
3. Implementare log_action(user, action, resource, metadata)
4. Integrare in: login, create estimate, close estimate, admin actions
5. Implementare query audit: filter by user, action, date range
6. Configurare retention 1 anno
7. Implementare export CSV per compliance

**Acceptance Criteria:**

- [ ] Eventi critici loggati
- [ ] Query audit funzionanti
- [ ] Retention configurata
- [ ] Export CSV funzionante
- [ ] Test con vari scenari

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/logging/audit_logger.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.4
Area: backend/infra
Fase: Fase 2
Dipendenze: TASK 2.1

## TASK 3.4: Configurazione Structured Logging

**Descrizione:** Logging strutturato con structlog.

**Microstep:**

1. Installare structlog
2. Configurare processors: add timestamp, add log level, JSON renderer
3. Configurare logger in `backend/src/infra/logging/config.py`
4. Integrare con uvicorn
5. Logga structured data: request_id, user_id, duration
6. Configurare log rotation
7. Configurare livelli per ambiente (DEBUG dev, INFO prod)

**Acceptance Criteria:**

- [ ] Log in formato JSON
- [ ] Context data propagato
- [ ] Rotation funzionante
- [ ] Livelli corretti per ambiente
- [ ] Test log parsing

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/logging/config.py, backend/src/main.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.5
Area: backend/infra
Fase: Fase 2
Dipendenze: TASK 3.4

## TASK 3.5: Implementazione Metrics Collection

**Descrizione:** Metriche applicative con Prometheus.

**Microstep:**

1. Installare prometheus-fastapi-instrumentator
2. Configurare instrumentator in main.py
3. Esporre /metrics endpoint
4. Aggiungere custom metrics:
   - Counter: estimates_created, estimates_closed
   - Histogram: estimate_processing_duration
   - Gauge: active_estimates
5. Integrare con middleware per auto-instrumentation
6. Configurare Prometheus scraper

**Acceptance Criteria:**

- [ ] /metrics espone metriche Prometheus
- [ ] Custom metrics funzionanti
- [ ] Auto-instrumentation attiva
- [ ] Scraper configurato
- [ ] Test metrics collection

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/logging/metrics.py, backend/src/main.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.6
Area: backend/infra
Fase: Fase 2
Dipendenze: TASK 3.5

## TASK 3.6: Setup Prometheus & Grafana

Priorità: Fase 2 (opzionale per ambiente locale single-user).

**Descrizione:** Stack osservabilità con Prometheus e Grafana.

**Microstep:**

1. Aggiungere servizio prometheus a docker-compose.prod.yml
2. Configurare prometheus.yml: scrape backend /metrics ogni 15s
3. Aggiungere servizio grafana
4. Configurare datasource Prometheus
5. Creare dashboard TickerTracker:
   - Request rate
   - Error rate
   - Latency percentiles
   - Custom metrics (estimates created/closed)
6. Configurare alerting rules basic

**Acceptance Criteria:**

- [ ] Prometheus scrape metrics
- [ ] Grafana visualizza dashboard
- [ ] Alert rules funzionanti
- [ ] Dashboard salvata

---

### Istruzioni per LLM
- Non modificare file fuori da [docker/docker-compose.prod.yml, docker/prometheus.yml, docker/grafana-dashboard.json] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.7
Area: backend/infra
Fase: Fase 2
Dipendenze: TASK 3.4

## TASK 3.7: Integrazione Sentry per Error Tracking

Priorità: Fase 2 (necessario solo in produzione per monitoraggio errori real-time).

**Descrizione:** Tracking errori automatico con Sentry.

**Microstep:**

1. Installare sentry-sdk[fastapi]
2. Configurare Sentry in main.py
3. Configurare DSN da Settings (SENTRY_DSN)
4. Configurare sample_rate per performance
5. Aggiungere context: user_id, request_id
6. Configurare release tracking
7. Testare error capture

**Acceptance Criteria:**

- [ ] Errori inviati a Sentry
- [ ] Context propagato
- [ ] Performance tracking attivo
- [ ] Release taggato
- [ ] Test con errore simulato

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/main.py, backend/src/shared/infra/config.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.8
Area: backend/security
Fase: Fase 2
Dipendenze: TASK 2.1

## TASK 3.8: Implementazione Backup Automatico Database

Priorità: Fase 2 (critico per produzione, opzionale in locale).

**Descrizione:** Script backup automatico PostgreSQL.

**Microstep:**

1. Creare script `backend/scripts/backup_db.sh`
2. Usare pg_dump con compressione
3. Upload backup a Google Drive
4. Configurare cron job (daily 2 AM)
5. Implementare retention: 7 daily, 4 weekly
6. Notificare su failure (email/webhook)
7. Testare restore da backup

**Acceptance Criteria:**

- [ ] Backup automatico funziona
- [ ] Upload Drive completo
- [ ] Retention policy applicata
- [ ] Notifica failure funzionante
- [ ] Restore testato

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/scripts/backup_db.sh] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.9
Area: backend/security
Fase: Fase 2
Dipendenze: TASK 2.7

## TASK 3.9: Implementazione Feature Flags

Priorità: Fase 2 (utile per rollout graduali di nuove feature; non necessario per MVP).

**Descrizione:** Sistema feature flags per rilasci graduali.

**Microstep:**

1. Creare file `backend/src/infra/feature_flags/flags.py`
2. Definire enum FeatureFlag: SYNC_DRIVE, CHAT_AI, GEMINI_INTEGRATION
3. Implementare storage flags in DB (tabella feature_flags)
4. Implementare is_enabled(flag, user_id) -> bool
5. Integrare check in endpoint
6. Creare admin endpoint per toggle flags
7. Implementare percentage rollout (es. 10% utenti)

**Acceptance Criteria:**

- [ ] Flags configurabili
- [ ] Check funzionante in endpoint
- [ ] Percentage rollout funziona
- [ ] Admin toggle funzionante
- [ ] Test con flag on/off

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/feature_flags/flags.py, backend/src/shared/api/admin_routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.10
Area: backend/security
Fase: Fase 2
Dipendenze: TASK 2.1

## TASK 3.10: Implementazione Data Encryption at Rest

Priorità: Media (post-MVP, importante per dati sensibili in produzione).

**Descrizione:** Encryption campi sensibili nel database.

**Microstep:**

1. Installare cryptography
2. Creare file `backend/src/infra/security/encryption.py`
3. Implementare encrypt(data: str) -> str usando Fernet
4. Implementare decrypt(encrypted: str) -> str
5. Configurare ENCRYPTION_KEY da Settings (32-byte key)
6. Applicare encryption a: API keys, passwords, PII
7. Creare migration per encrypt dati esistenti
8. Implementare key rotation mechanism

**Acceptance Criteria:**

- [ ] Dati sensibili encrypted in DB
- [ ] Decrypt trasparente in app
- [ ] Key rotation supportata
- [ ] Migration encrypt dati esistenti
- [ ] Test encrypt/decrypt cycle

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/security/encryption.py, alembic/versions/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.11
Area: backend/infra
Fase: Fase 2
Dipendenze: TASK 2.12

## TASK 3.11: Implementazione Query Pagination Cursor-Based

Priorità: Fase 2 (necessario solo con dataset molto grandi; non blocca l'MVP locale).

**Descrizione:** Implementare paginazione efficiente basata su cursore per grandi dataset.

**Microstep:**

1. Creare file `backend/src/shared/repositories/pagination.py`
2. Definire dataclass `CursorPagination`: cursor (optional), limit, direction (NEXT/PREV)
3. Definire dataclass `PaginatedResult[T]`: items, next_cursor, prev_cursor, has_more
4. Implementare funzione `encode_cursor(values: dict) -> str` (base64 encode)
5. Implementare funzione `decode_cursor(cursor: str) -> dict`
6. Implementare helper `apply_cursor_pagination(query, cursor, sort_columns)` per SQLAlchemy
7. Modificare repository MarketData per usare cursor pagination
8. Documentare formato cursore e limitazioni

**Acceptance Criteria:**

- [ ] Cursore opaco (non manipolabile dall'utente)
- [ ] Performance O(1) indipendente dalla pagina
- [ ] Navigazione avanti e indietro funzionante
- [ ] Gestione edge case: prima pagina, ultima pagina, dataset vuoto

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/repositories/pagination.py, backend/src/market_data/repositories/market_data_repository.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.
