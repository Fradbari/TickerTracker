# ARCHIVIO STORICO — Piano Operativo v1.7 (estratto testuale integrale)

> **NON NORMATIVO.** Estratto testuale completo di `Docs/Piano-operativo-v1.7.docx`
> (binario, rimosso dal repo il 2026-07-10; recuperabile da git history:
> `rtk proxy git show feef0f4 -- "Standalone-app-v1/Docs/Piano-operativo-v1.7.docx"`).
> Conservato per garanzia di zero perdita informativa.
>
> ⚠️ **La numerazione task di questo documento NON corrisponde al ledger attuale**
> (root `AGENTS.md` = fonte canonica). Esempi di divergenza: qui TASK 2.25 = Outbox
> (ledger: 2.26); qui TASK 4.10 = EstimatesList (ledger: 4.6); qui TASK 4.11 = PWA e
> TASK 4.12 = Accessibilità/i18n (assenti dal ledger attuale); qui TASK 3.10/3.11 =
> Connection Pooling / Pagination (ledger: OpenTelemetry / Circuit Breaker).
> Dettagli e implicazioni: `Docs/piano-di-lavoro-v2.md` §7.
> La formattazione originale delle tabelle Word è persa nell'estrazione (testo lineare).

---

# Piano Operativo TickerTracker v3.0 — Merge v1.3 + v1.5
Data: 31/01/2026Base: v1.3Integrazioni: v1.5 Integrato (Executive Summary, Changelog, Standard di Qualità, Percorso Docker, Ordine MVP, Decisioni &amp; Bonifica, Matrice Impatto × Priorità, Appendice).
# Piano Atomico TickerTracker v3.0
## Guida per LLM (Claude Code / Antigravity / Jules)
---
# SEZIONE 1: LINEE GUIDA TRASVERSALI
# Standard di Qualità (Globali)
• **GitOps/Documentazione**: tutti i file di processo e guida usano percorsi relativi.
• **Tooling**: Poetry come standard; export `requirements*.txt` per ambienti che non usano Poetry.
• **Calcoli Finanziari**: vietato l’uso di float JS; in FE usare `decimal.js` e wrapper condivisi.
• **Security by default**: header minimi, CORS, rate limit base disattivabile in locale; secret in `pydantic-settings` (SecretStr).
• **Testing**: acceptance criteria verificabili per ogni task; coverage minimo 80% per VO e servizi core.
---
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
## TASK 1.4: Creazione Value Object Percentage (Backend)
**Descrizione:** Implementare il value object immutabile `Percentage` per gestire valori percentuali.
**Microstep:**
1. Creare file `backend/src/shared/domain/value_objects/percentage.py`
2. Definire dataclass frozen `Percentage` con campo: `value` (Decimal)
3. Implementare `__post_init__` per conversione a Decimal
4. Implementare class method `from_basis_points(bps: int)`
5. Implementare metodo `apply_to(money: Money) -&gt; Money`
6. Implementare metodo `as_multiplier() -&gt; Decimal` (restituisce 1 + value)
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
**Descrizione:** Implementare il value object `PriceTarget` che incapsula target, stop loss e take profit con validazioni.
**Microstep:**
1. Creare file `backend/src/shared/domain/value_objects/price_target.py`
2. Definire dataclass frozen `PriceTarget` con campi: `entry_price` (Money), `stop_loss` (Money), `take_profit` (Money), `direction` (Literal["LONG", "SHORT"])
3. Implementare `__post_init__` con validazioni:
- Per LONG: stop_loss &lt; entry_price &lt; take_profit
- Per SHORT: take_profit &lt; entry_price &lt; stop_loss
- Tutte le currency devono corrispondere
4. Implementare metodo `risk_reward_ratio() -&gt; Decimal`
5. Implementare metodo `is_target_hit(current_price: Money) -&gt; bool`
6. Implementare metodo `is_stop_hit(current_price: Money) -&gt; bool`
7. Implementare `to_dict()` e `from_dict()`
**Acceptance Criteria:**
- [ ] Validazione solleva ValueError per configurazioni invalide
- [ ] Risk/reward ratio calcolato correttamente per entrambe le direzioni
- [ ] Metodi is_target_hit e is_stop_hit funzionano per LONG e SHORT
- [ ] Test unitari coprono scenari validi e invalidi
---
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
11. **Creare/aggiornare `backend/.gitignore` per escludere `.env`, `__pycache__/`, `.venv/`, `.pytest_cache/`, `.coverage`, `.mypy_cache/`**
12. Creare test in `tests/unit/shared/test_config.py` per verificare caricamento, singleton, e protezione SecretStr
**Acceptance Criteria:**
- [ ] Settings carica variabili da file .env
- [ ] Tutti i secret usano tipo SecretStr
- [ ] Valori di default sensati per development
- [ ] `.env.example` documenta tutte le variabili richieste
- [ ] `get_settings()` restituisce sempre la stessa istanza (cached)
- [ ] `.env` è in `.gitignore` e NON può essere committato
- [ ] Test unitari passano e coprono casi principali
---
## TASK 1.7: Middleware Sicurezza Base &amp; Healthcheck
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
TASK 1.8: Setup Wrapper TypeScript per Decimali (Frontend)
Descrizione: Creare wrapper TypeScript per gestione decimale precisa nel frontend usando decimal.js, garantendo coerenza con i Value Objects backend (Money, Percentage) e prevenendo bug di arrotondamento IEEE 754 (es. 0.1 + 0.2 ≠ 0.3 in JavaScript nativo).
Microstep:
Installare dipendenze decimal.js
Eseguire: npm install decimal.js
Eseguire: npm install --save-dev @types/decimal.js
Verificare che decimal.js sia in dependencies e @types/decimal.js in devDependencies del package.json
Creare file frontend/src/shared/utils/decimal.ts
Definire interface MoneyValue con campi: amount: Decimal, currency: string
Implementare funzione createMoney(amount: string | number | Decimal, currency?: string): MoneyValue
Default currency = "USD"
Validare che currency sia esattamente 3 caratteri uppercase (ISO 4217), altrimenti lanciare errore
Convertire amount in Decimal usando costruttore new Decimal(amount)
Implementare funzione addMoney(a: MoneyValue, b: MoneyValue): MoneyValue
Verificare che a.currency === b.currency, altrimenti lanciare errore con messaggio "Cannot add {currency1} to {currency2}. Convert currencies first!"
Ritornare nuovo MoneyValue con amount sommato usando a.amount.plus(b.amount)
Implementare analogamente: subtractMoney, multiplyMoney, divideMoney
multiplyMoney e divideMoney accettano secondo parametro factor: string | number | Decimal
divideMoney deve verificare che divisor non sia zero
Implementare funzione roundMoney(money: MoneyValue, decimalPlaces: number = 2): MoneyValue
Usare money.amount.toDecimalPlaces(decimalPlaces, Decimal.ROUND_HALF_UP) per arrotondamento bancario
Implementare funzione formatMoney(money: MoneyValue, locale?: string): string
Usare Intl.NumberFormat con style: "currency", currency: money.currency
Default locale = navigator.language || "en-US"
Implementare funzioni serializzazione: moneyToJSON(money: MoneyValue) → {amount: string, currency: string} e moneyFromJSON(data) → MoneyValue
amount deve essere salvato come stringa per evitare perdita precisione
Implementare funzioni comparazione: compareMoney, isPositiveMoney, isNegativeMoney, isZeroMoney
Creare file frontend/src/shared/utils/percentage.ts
Definire interface PercentageValue con campo: value: Decimal (in formato decimale: 0.10 = 10%)
Implementare funzione createPercentage(percent: string | number | Decimal): PercentageValue
Dividere input per 100: new Decimal(percent).dividedBy(100)
Implementare funzione createPercentageFromBasisPoints(bps: number): PercentageValue
Dividere per 10000: 100 bps = 1% = 0.01
Implementare funzione createPercentageFromDecimal(value: string | number | Decimal): PercentageValue
Per input già in formato decimale (0.10)
Implementare funzione applyPercentage(percentage: PercentageValue, money: MoneyValue): MoneyValue
Usare multiplyMoney(money, percentage.value) da decimal.ts
Implementare funzione asMultiplier(percentage: PercentageValue): Decimal
Ritornare new Decimal(1).plus(percentage.value) per calcoli tipo "prezzo + 10%"
Implementare funzioni: addPercentage, subtractPercentage, formatPercentage(percentage, decimalPlaces = 2)
Implementare serializzazione: percentageToJSON e percentageFromJSON
Creare barrel export frontend/src/shared/utils/financial.ts
Re-esportare tutti i tipi e funzioni da decimal.ts e percentage.ts
Aggiungere commento JSDoc che specifica questo come unico entry point per import nei componenti
Configurare path alias in tsconfig.json
Aggiungere in compilerOptions.paths: "@/*": ["src/*"], "@/shared/*": ["src/shared/*"]
Verificare che import tipo import { createMoney } from '@/shared/utils/financial' funzioni
Creare test unitari frontend/src/shared/utils/__tests__/decimal.test.ts
Test per createMoney: verifica creazione corretta, errore su currency invalida
Test per addMoney: verifica somma corretta, errore su valute diverse
Test critico JavaScript bug: addMoney(createMoney("0.1"), createMoney("0.2")) deve dare esattamente "0.3"
Test per formatMoney: verifica locale "en-US" produce "$1,234.56" e "it-IT" produce "1.234,56 €"
Test per roundMoney: verifica arrotondamento con ROUND_HALF_UP (es. 123.456 → 123.46)
Test per operazioni su valute diverse: verificare che lancino errori espliciti
Creare test unitari frontend/src/shared/utils/__tests__/percentage.test.ts
Test per createPercentage(10) produce value: 0.1
Test per createPercentageFromBasisPoints(100) produce value: 0.01
Test per applyPercentage: 10% di $100 = $10
Test per asMultiplier: 10% diventa moltiplicatore 1.10
Test per formatPercentage: 10.5678% formattato con 2 decimali = "10.57%"
Configurare test runner in package.json
Aggiungere script: "test": "vitest", "test:coverage": "vitest --coverage"
Aggiungere devDependencies: vitest, @vitest/ui, @vitest/coverage-v8
Verificare che npm run test esegua tutti i test senza errori
Verificare coverage ≥ 80% con npm run test:coverage
Documentare nel frontend/README.md
Aggiungere sezione "💰 Calcoli Finanziari (OBBLIGATORIO)"
Includere esempio corretto (✅): uso di createMoney con stringhe
Includere esempio vietato (❌): calcoli con number nativo
Includere tabella mapping Backend Python ⟷ Frontend TypeScript per coerenza API
Acceptance Criteria:
decimal.js installato e presente in package.json
File decimal.ts creato con tutti i tipi e funzioni richiesti
File percentage.ts creato con tutti i tipi e funzioni richiesti
File financial.ts barrel export creato
Validazione currency verifica 3 caratteri uppercase (ISO 4217)
Operazioni tra valute diverse lanciano errore esplicito con messaggio chiaro
Arrotondamento usa Decimal.ROUND_HALF_UP (coerente con backend Python money.py)
Formattazione formatMoney rispetta locale (separatori migliaia, simbolo valuta)
Serializzazione JSON produce {amount: string, currency: string} (coerente con backend Money.to_dict())
Path alias @/shared/utils/financial configurato e funzionante
Test unitari coprono tutti i metodi principali
Test verifica precisione: 0.1 + 0.2 = 0.3 esatto (non 0.30000000000000004)
Test verifica errori su valute diverse e divisione per zero
Coverage test ≥ 80%
npm run build completa senza errori TypeScript
README aggiornato con sezione calcoli finanziari
Nessun uso di number nativo per calcoli monetari nel codice prodotto
Istruzioni per LLM
Non modificare file fuori da [frontend/src/shared/utils/decimal.ts, frontend/src/shared/utils/percentage.ts, frontend/src/shared/utils/financial.ts, frontend/src/shared/utils/__tests__/, frontend/package.json, frontend/tsconfig.json, frontend/README.md] se non strettamente necessario.
Segui i microstep in ordine sequenziale e non introdurre pattern/tecnologie non menzionati (es. non usare librerie diverse da decimal.js).
Validazione currency deve essere identica al backend: verifica che sia esattamente 3 caratteri uppercase, lancia errore con messaggio esplicito se non rispetta formato ISO 4217.
Arrotondamento deve usare Decimal.ROUND_HALF_UP per garantire coerenza con backend Python che usa ROUND_HALF_UP in money.py.
Serializzazione JSON deve produrre oggetto con amount come stringa (non number) per evitare perdita precisione durante trasporto HTTP.
Operazioni tra valute diverse devono sempre lanciare errore con messaggio tipo "Cannot {operation} {currency1} {with/from/to} {currency2}. Convert currencies first!" - mai eseguire calcoli su valute diverse silenziosamente.
Preferire stringhe per input: documentare che passare stringhe tipo "123.45" è preferibile a numeri 123.45 per evitare corruzione float prima della conversione in Decimal.
Coerenza API backend: studiare i file backend/src/shared/domain/value_objects/money.py e backend/src/shared/domain/value_objects/percentage.py per garantire comportamento identico (stessi metodi, stesse validazioni, stesso output).
Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
Alla fine, produci un elenco puntato con file modificati e test eseguiti, includendo risultati coverage test.
---
# SEZIONE 2: BACKEND &amp; DATA
---
## TASK 2.1: Setup Progetto Python con Poetry &amp; Dipendenze Complete
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
---
## TASK 2.2: Setup Docker Compose per PostgreSQL e Redis
**Descrizione:** Configurare docker-compose.base.yml per i servizi infrastrutturali comuni (Database e Cache), separando la configurazione base da quelle di sviluppo e produzione.
**Microstep:**
Creare file docker-compose.base.yml nella root del progetto Standalone-app-v1/
Definire servizio db con immagine postgres:16
Configurare variabili ambiente: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
Configurare volume persistente postgres-data per dati PostgreSQL
Configurare healthcheck per PostgreSQL: test: ["CMD-SHELL", "pg_isready -U tickertracker"] interval: 10s timeout: 5s retries: 5
Definire servizio redis con immagine redis:7-alpine
Configurare volume persistente redis-data per Redis
Configurare healthcheck per Redis: test: ["CMD", "redis-cli", "ping"] interval: 10s timeout: 3s retries: 5
Definire network condivisa ticker-network con driver bridge
Esporre porte: PostgreSQL 5432:5432, Redis 6379:6379
**Acceptance Criteria:**
docker compose -f docker-compose.base.yml up -d avvia entrambi i servizi
PostgreSQL accessibile su localhost:5432
Redis accessibile su localhost:6379
Healthcheck passa per entrambi i servizi (docker compose -f docker-compose.base.yml ps mostra healthy)
Dati persistono dopo restart container (docker compose -f docker-compose.base.yml restart)
Network ticker-network creata correttamente
**Note:**
⚠️ NON creare docker-compose.override.yml - questo progetto usa strategia multi-file esplicita
✅ Coerente con TASK 3.12 (docker-compose.dev.yml) e TASK 5.14 (docker-compose.prod.yml)
✅ Comandi usano flag -f esplicito per chiarezza
---
## TASK 2.3: Definizione Modello SQLAlchemy - Ticker
**Descrizione:** Configurare SQLAlchemy async base e creare primo modello Ticker.
### PARTE 1: Setup SQLAlchemy Base
1. Creare file `backend/src/shared/infra/database.py`
2. Importare `declarative_base` da SQLAlchemy
3. Creare `Base = declarative_base()`
4. Configurare async engine con `create_async_engine()`:
- Pool size: 5 (dev), 20 (prod)
- Echo: True (dev), False (prod)
- DATABASE_URL da Settings
5. Creare `AsyncSessionLocal` con `async_sessionmaker`
6. Creare dependency `get_db()` per FastAPI injection
7. Esportare `Base`, `engine`, `AsyncSessionLocal`, `get_db` da `__init__.py`
### PARTE 2: Modello Ticker
8. Creare file `backend/src/market_data/domain/entities.py`
9. Importare `Base` da `shared.infra.database`
10. Definire classe `Ticker(Base)`:
- `__tablename__ = "tickers"`
- `id`: UUID primary key con `default=uuid.uuid4`
- `symbol`: String(10), unique, not null, index
- `name`: String(255), not null
- `exchange`: String(50)
- `currency`: String(3), default='USD'
- `asset_type`: String(20), check constraint ('stock','etf','crypto')
11. Aggiungere colonne audit:
- `created_at`: DateTime, `default=func.now()`
- `updated_at`: DateTime, `default=func.now()`, `onupdate=func.now()`
12. Definire `__repr__` per debug
13. Aggiungere `Index('ix_ticker_symbol', 'symbol')`
**Acceptance Criteria:**
- ✅ `Base` importabile da `shared.infra.database`
- ✅ Async engine si connette a PostgreSQL Docker
- ✅ `get_db()` dependency funziona con FastAPI
- ✅ Modello `Ticker` ha tutti i campi richiesti
- ✅ UUID generato automaticamente
- ✅ Timestamps gestiti automaticamente
- ✅ Constraint unique su `symbol`
- ✅ Indice su `symbol` definito
---
## TASK 2.4: Definizione Modello SQLAlchemy - Estimate
**Descrizione:** Creare il modello SQLAlchemy per l'entità Estimate (stime/previsioni).
**Microstep:**
1. Creare file `backend/src/estimates/domain/entities.py`
2. Definire classe `Estimate` che eredita da Base
3. Definire colonne identificative: `id` (UUID, PK), `ticker_id` (FK to Ticker), `user_id` (FK to User, nullable per ora)
4. Definire colonne prezzo: `start_price` (DECIMAL 10,4), `target_price` (DECIMAL 10,4), `stop_loss_price` (DECIMAL 10,4)
5. Definire colonne target: `target_profit_percent` (DECIMAL 8,4), `stop_loss_percent` (DECIMAL 8,4)
6. Definire colonne stato: `status` (Enum: OPEN, CLOSED_WIN, CLOSED_LOSS, CLOSED_MANUAL, EXPIRED), `direction` (Enum: LONG, SHORT)
7. Definire colonne AI: `ai_model` (String), `ai_confidence` (DECIMAL 5,2), `ai_reasoning` (Text)
8. Definire colonne date: `created_at`, `updated_at`, `closed_at` (nullable)
9. Definire colonne esito: `exit_price` (DECIMAL 10,4, nullable), `realized_pnl` (DECIMAL 12,4, nullable)
10. Definire relazione con Ticker
11. Definire indici: su `ticker_id`, su `status`, su `created_at`, indice parziale su status='OPEN'
**Acceptance Criteria:**
- [ ] Tutti i campi prezzo usano DECIMAL, non FLOAT
- [ ] Enums definiti come tipi Python Enum
- [ ] Foreign key a Ticker definita correttamente
- [ ] Indici ottimizzati per query frequenti
- [ ] Campi nullable marcati esplicitamente
---
## TASK 2.5: Definizione Modello SQLAlchemy - EstimateEvent (Event Sourcing)
**Descrizione:** Creare il modello per Event Sourcing delle stime.
**Microstep:**
1. Creare file `backend/src/estimates/domain/events.py`
2. Definire Enum `EstimateEventType`: CREATED, UPDATED, PRICE_UPDATED, TARGET_HIT, STOP_HIT, CLOSED, REOPENED
3. Definire classe `EstimateEvent` che eredita da Base
4. Definire colonne: `id` (UUID, PK), `estimate_id` (FK to Estimate), `event_type` (Enum), `event_data` (JSONB), `user_id` (UUID, nullable), `timestamp` (DateTime with timezone)
5. Definire indice composto su `(estimate_id, timestamp)`
6. Definire constraint: timestamp deve avere timezone
**Acceptance Criteria:**
- [ ] Eventi sono immutabili (no update)
- [ ] JSONB usato per flessibilità dati evento
- [ ] Indice permette query efficienti per timeline
- [ ] Ogni tipo evento documentato nel Enum
---
## TASK 2.6: Definizione Modello SQLAlchemy - MarketData
**Descrizione:** Creare il modello per dati storici di mercato (OHLCV).
**Microstep:**
1. Creare file `backend/src/market_data/domain/market_data.py`
2. Definire classe `MarketData` che eredita da Base
3. Definire colonne: `ticker_id` (FK), `date` (Date), `open` (DECIMAL 10,4), `high` (DECIMAL 10,4), `low` (DECIMAL 10,4), `close` (DECIMAL 10,4), `volume` (BigInteger)
4. Definire PK composta: `(ticker_id, date)`
5. Definire colonne lineage: `data_source` (String), `ingested_at` (DateTime), `quality_score` (DECIMAL 3,2)
6. Definire indici: su `date`, su `(ticker_id, date)` unique
**Acceptance Criteria:**
- [ ] PK composta impedisce duplicati per ticker+data
- [ ] Tutti i prezzi usano DECIMAL
- [ ] Volume usa BigInteger per supportare valori grandi
- [ ] Metadati lineage presenti per audit
---
## TASK 2.7: Definizione Modello SQLAlchemy - User e Role (RBAC Base)
**Descrizione:** Creare modelli per utenti e ruoli, preparando per multi-utente futuro.
**Microstep:**
1. Creare file `backend/src/shared/domain/user.py`
2. Definire Enum `RoleType`: ADMIN, USER, READONLY
3. Definire classe `User`: `id` (UUID), `email` (String, unique), `hashed_password` (String, nullable), `is_active` (Boolean), `created_at`, `updated_at`
4. Definire classe `Role`: `id` (UUID), `name` (RoleType), `description` (String)
5. Definire tabella associativa `user_roles` per relazione many-to-many
6. Definire relazioni bidirezionali User &lt;-&gt; Role
**Acceptance Criteria:**
- [ ] Password mai salvata in chiaro (campo per hash)
- [ ] Relazione many-to-many funzionante
- [ ] Ruoli base definiti
- [ ] Utente può avere multipli ruoli
---
## TASK 2.8: Definizione Modello SQLAlchemy - SyncJob
**Descrizione:** Creare modello per tracciare i job di sincronizzazione con Google Drive.
**Microstep:**
1. Creare file `backend/src/sync/domain/entities.py`
2. Definire Enum `SyncJobType`: INITIAL_IMPORT, DAILY_HISTORY_UPDATE, ON_ESTIMATE_SAVE, MANUAL_SYNC
3. Definire Enum `SyncJobStatus`: PENDING, RUNNING, COMPLETED, FAILED, PARTIAL
4. Definire classe `SyncJob`: `id` (UUID), `job_type` (Enum), `status` (Enum), `started_at`, `finished_at` (nullable), `error_message` (Text, nullable), `filename` (String), `checksum_before` (String), `checksum_after` (String), `records_processed` (Integer), `records_failed` (Integer)
5. Definire indice su `started_at` per ordinamento cronologico
**Acceptance Criteria:**
- [ ] Tutti i tipi di job rappresentati
- [ ] Stati permettono tracking completo del ciclo di vita
- [ ] Checksum permette verifica integrità
- [ ] Contatori permettono monitoraggio successo/fallimento
---
## TASK 2.9: Definizione Modello SQLAlchemy - AiModelRun
**Descrizione:** Creare modello per tracciare esecuzioni dei modelli AI.
**Microstep:**
1. Creare file `backend/src/analytics/domain/entities.py`
2. Definire classe `AiModelRun`: `id` (UUID), `estimate_id` (FK, nullable), `model_name` (String), `model_version` (String), `prompt_hash` (String), `prompt_tokens` (Integer), `completion_tokens` (Integer), `latency_ms` (Integer), `output_summary` (Text), `raw_response` (JSONB), `created_at`
3. Definire indice su `model_name` e `created_at`
**Acceptance Criteria:**
- [ ] Traccia consumo token per monitoraggio costi
- [ ] Hash del prompt per deduplicazione
- [ ] Latenza per performance monitoring
- [ ] JSONB per risposta raw flessibile
---
## TASK 2.10: Setup Alembic per Migrazioni Database
**Descrizione:** Configurare Alembic per gestione migrazioni schema database.
**Microstep:**
1. Installare alembic come dipendenza
2. Eseguire `alembic init backend/alembic`
3. Configurare `alembic.ini` con path corretto
4. Modificare `alembic/env.py` per usare async engine e importare tutti i modelli
5. Configurare `alembic/env.py` per leggere DATABASE_URL da Settings
6. Creare prima migrazione: `alembic revision --autogenerate -m "initial_schema"`
7. Verificare migrazione generata
8. Documentare comandi nel Makefile: `make migrate`, `make migrate-down`, `make migrate-new`
**Acceptance Criteria:**
- [ ] `alembic upgrade head` esegue senza errori
- [ ] `alembic downgrade -1` esegue senza errori
- [ ] Migrazione riflette tutti i modelli definiti
- [ ] Async engine configurato correttamente
---
## TASK 2.11: Creazione Materialized View EstimateSummaryView (CQRS)
**Descrizione:** Creare materialized view per query dashboard ottimizzate.
**Microstep:**
1. Creare migrazione Alembic per materialized view
2. Definire view `estimate_summary_view` con colonne: tutti i campi Estimate + `current_price` (da ultima MarketData), `current_pnl`, `current_pnl_percent`, `days_open`, `risk_level` (calcolato)
3. Creare indici sulla materialized view: su `status`, su `ticker_id`
4. Creare funzione/comando per refresh: `REFRESH MATERIALIZED VIEW CONCURRENTLY`
5. Documentare che la view richiede indice unique per refresh concurrente
**Acceptance Criteria:**
- [ ] View creata con successo
- [ ] Query su view restituisce dati corretti
- [ ] Refresh concurrente funziona senza lock
- [ ] Performance query &lt; 50ms per lista stime
---
## TASK 2.12: Creazione Repository Estimate
**Descrizione:** Implementare repository per accesso dati Estimate.
**Microstep:**
1. Creare file `backend/src/estimates/repositories/estimate_repository.py`
2. Definire classe `EstimateRepository`
3. Iniettare async session factory
4. Implementare metodo `create(estimate: Estimate) -&gt; Estimate`
5. Implementare metodo `get_by_id(id: UUID) -&gt; Optional[Estimate]`
6. Implementare metodo `get_all(filters: EstimateFilters, pagination: Pagination) -&gt; PaginatedResult[Estimate]`
7. Implementare metodo `update(estimate: Estimate) -&gt; Estimate`
8. Implementare metodo `soft_delete(id: UUID) -&gt; bool`
9. Implementare metodo `get_active_by_ticker(ticker_id: UUID) -&gt; List[Estimate]`
10. Usare async/await per tutte le operazioni
**Acceptance Criteria:**
- [ ] Tutte le operazioni CRUD funzionano
- [ ] Paginazione cursor-based implementata
- [ ] Filtri applicati correttamente
- [ ] Soft delete imposta flag, non cancella
- [ ] Transazioni gestite correttamente
---
## TASK 2.13: Creazione Repository MarketData
**Descrizione:** Implementare repository per accesso dati MarketData.
**Microstep:**
1. Creare file `backend/src/market_data/repositories/market_data_repository.py`
2. Definire classe `MarketDataRepository`
3. Implementare metodo `upsert_daily(ticker_id: UUID, data: List[MarketDataRow])` con ON CONFLICT UPDATE
4. Implementare metodo `get_history(ticker_id: UUID, start: date, end: date) -&gt; List[MarketData]`
5. Implementare metodo `get_latest_price(ticker_id: UUID) -&gt; Optional[MarketData]`
6. Implementare metodo `get_latest_prices_batch(ticker_ids: List[UUID]) -&gt; Dict[UUID, MarketData]`
7. Implementare metodo `get_aggregated(ticker_id: UUID, interval: str) -&gt; List[AggregatedData]` per intervalli 1D/1W/1M
**Acceptance Criteria:**
- [ ] Upsert non crea duplicati
- [ ] Query batch evita N+1
- [ ] Aggregazioni calcolate lato DB
- [ ] Performance accettabile per 10 anni di dati
---
## TASK 2.14: Creazione Service EstimateService
**Descrizione:** Implementare service layer per orchestrazione business logic stime.
**Microstep:**
1. Creare file `backend/src/estimates/services/estimate_service.py`
2. Definire classe `EstimateService`
3. Iniettare dipendenze: `EstimateRepository`, `MarketDataProvider`, `EventPublisher`
4. Implementare metodo `create_estimate(command: CreateEstimateCommand) -&gt; Estimate`:
- Validare input
- Recuperare prezzo corrente da provider
- Calcolare target_price e stop_loss da percentuali
- Creare Estimate
- Pubblicare evento ESTIMATE_CREATED
- Salvare evento in EstimateEvent
5. Implementare metodo `update_estimate(command: UpdateEstimateCommand) -&gt; Estimate`
6. Implementare metodo `close_estimate(id: UUID, exit_price: Decimal, reason: str) -&gt; Estimate`
7. Implementare metodo `check_and_update_targets(estimate_id: UUID)` per verificare hit target/stop
**Acceptance Criteria:**
- [ ] Validazione input completa
- [ ] Eventi pubblicati per ogni operazione
- [ ] Transazione atomica (DB + evento)
- [ ] Errori business sollevano eccezioni tipizzate
---
## TASK 2.15: Creazione Service EstimateHistoryService (Event Sourcing)
**Descrizione:** Implementare service per ricostruzione stato storico stime.
**Microstep:**
1. Creare file `backend/src/estimates/services/estimate_history_service.py`
2. Definire classe `EstimateHistoryService`
3. Iniettare `EstimateEventRepository`
4. Implementare metodo `get_state_at(estimate_id: UUID, at_time: datetime) -&gt; EstimateSnapshot`:
- Recuperare tutti gli eventi fino a at_time
- Ricostruire stato applicando eventi in ordine
5. Implementare metodo `get_audit_trail(estimate_id: UUID) -&gt; List[AuditEntry]`:
- Restituire lista eventi con metadata human-readable
6. Implementare metodo `get_changes_between(estimate_id: UUID, start: datetime, end: datetime) -&gt; List[Change]`
**Acceptance Criteria:**
- [ ] Stato ricostruito correttamente per qualsiasi timestamp
- [ ] Audit trail completo e ordinato
- [ ] Performance accettabile per stime con molti eventi
---
## TASK 2.16: Creazione API Router Estimates
**Descrizione:** Implementare endpoint REST per gestione stime.
**Microstep:**
1. Creare file `backend/src/estimates/api/routes.py`
2. Creare router FastAPI con prefix `/api/estimates`
3. Implementare endpoint `POST /` per creazione stima
4. Implementare endpoint `GET /` per lista stime con filtri (status, ticker, date_range, ai_model)
5. Implementare endpoint `GET /{id}` per dettaglio singola stima
6. Implementare endpoint `PATCH /{id}` per aggiornamento parziale
7. Implementare endpoint `DELETE /{id}` per chiusura/cancellazione
8. Implementare endpoint `GET /{id}/history` per audit trail
9. Tutti gli endpoint restituiscono `ApiResponse` standard
10. Aggiungere dependency injection per services
**Acceptance Criteria:**
- [ ] Tutti gli endpoint documentati con OpenAPI
- [ ] Request validation con Pydantic
- [ ] Response conforme a schema ApiResponse
- [ ] Errori restituiti con codici appropriati (400, 404, 500)
- [ ] Filtri funzionanti e combinabili
---
## TASK 2.17: Creazione API Router Market Data
**Descrizione:** Implementare endpoint REST per dati di mercato.
**Microstep:**
1. Creare file `backend/src/market_data/api/routes.py`
2. Creare router FastAPI con prefix `/api/market`
3. Implementare endpoint `GET /price/{ticker}` per prezzo corrente
4. Implementare endpoint `GET /history/{ticker}` con query params: start_date, end_date, interval
5. Implementare endpoint `GET /fundamentals/{ticker}` per dati fondamentali
6. Implementare endpoint `GET /search` con query param `q` per autocomplete ticker
7. Aggiungere caching headers appropriati (Cache-Control)
**Acceptance Criteria:**
- [ ] Prezzi restituiti con metadata (source, timestamp, stale flag)
- [ ] History supporta aggregazione 1D/1W/1M
- [ ] Search restituisce max 10 risultati ordinati per rilevanza
- [ ] Cache headers impostati correttamente
Nota: tutti gli endpoint leggono i dati tramite MarketDataProvider (TASK 2.18–2.19), senza dipendere direttamente da yfinance.
---
TASK 2.18: Definizione MarketDataProvider Astratto
Descrizione:Definire un’interfaccia MarketDataProvider per disaccoppiare la logica di business dalla specifica sorgente dati (Yahoo oggi, altri provider domani).
Microstep:
Creare file backend/src/market_data/domain/providers.py.
Definire Protocol/classe astratta MarketDataProvider con metodi:
get_current_price(ticker: str) -&gt; PriceData
get_historical_prices(ticker: str, start: date, end: date, interval: str) -&gt; list[PriceData]
get_fundamentals(ticker: str) -&gt; FundamentalsData.
Definire dataclass Pydantic/Domain PriceData e FundamentalsData da usare come contratti interni.
Aggiornare i servizi esistenti in backend/src/market_data/services/ (es. MarketDataService) per dipendere da MarketDataProvider invece che chiamare direttamente yfinance.
Preparare stub/placeholder per futuri provider (es. FinnhubMarketDataProvider) con NotImplementedError.
Acceptance Criteria:
Tutta la logica di mercato usa MarketDataProvider e non dipende da yfinance direttamente.
MarketDataService riceve il provider via dependency injection FastAPI.
I test possono usare un FakeMarketDataProvider per simulare dati senza chiamate esterne.
---
TASK 2.19: Caching &amp; Backoff per MarketDataProvider
Descrizione:Ridurre chiamate a Yahoo/Finnhub e gestire in modo resiliente timeouts e rate-limit, usando cache in memoria e backoff.
Microstep:
Creare file backend/src/infra/cache/memory_cache.py con una semplice cache LRU/TTL (es. cachetools.TTLCache).
Creare classe CachedMarketDataProvider in backend/src/market_data/infrastructure/cached_provider.py che implementa MarketDataProvider e wrappa un provider sottostante (YahooMarketDataProvider).
Implementare TTL differenziato:
Prezzi correnti: TTL 60s.
Storico: TTL 1h.
Fundamentals: TTL 24h.
Aggiungere logica di backoff:
Su TimeoutError o HTTP 429/5xx, ritentare fino a N volte (es. 3) con ritardo esponenziale (es. 0.5s, 1s, 2s).
In caso di fallimento definitivo, se presente un valore in cache “stale”, restituirlo con flag stale=True nel PriceData/FundamentalsData.
Configurare via Settings i TTL e il numero massimo di retry.
Aggiornare la dependency injection in FastAPI per usare CachedMarketDataProvider come implementazione di default.
Acceptance Criteria:
Le chiamate ripetute allo stesso endpoint/ticker entro il TTL non generano chiamate esterne aggiuntive.
In caso di timeout/rate-limit, il sistema usa il dato in cache se disponibile e non va in errore 500 immediato.
I test coprono: cache hit, cache miss, fallback a dati stale, backoff su errori.
---
## TASK 2.20: Implementazione Google Drive Client
**Descrizione:** Creare client per interazione con Google Drive API.
**Microstep:**
1. Creare file `backend/src/infra/drive/client.py`
2. Definire classe `GoogleDriveClient`
3. Implementare autenticazione con Service Account usando credenziali da Settings
4. Implementare metodo `list_files(folder_id: str) -&gt; List[DriveFile]`
5. Implementare metodo `download_file(file_id: str) -&gt; bytes`
6. Implementare metodo `upload_file(folder_id: str, filename: str, content: bytes, mime_type: str) -&gt; DriveFile`
7. Implementare metodo `update_file(file_id: str, content: bytes) -&gt; DriveFile`
8. Implementare metodo `create_temp_file(folder_id: str, filename: str) -&gt; DriveFile` per pattern file temporaneo
9. Implementare metodo `delete_file(file_id: str) -&gt; bool`
10. Aggiungere logging e metriche per ogni operazione
**Acceptance Criteria:**
- [ ] Autenticazione funziona con Service Account
- [ ] Tutte le operazioni CRUD funzionano
- [ ] Errori API gestiti con eccezioni tipizzate
- [ ] Timeout configurabile
### Sync Engine &amp; retro‑compatibilità (TASK 2.20–2.23)
Questi task coprono il nuovo Sync Engine con Google Drive e garantiscono la piena retro‑compatibilità con i file legacy (backup JSON e History_*.csv) tramite test E2E dedicati.
---
## TASK 2.21: Implementazione CSV Parser Legacy
**Descrizione:** Creare parser bidirezionale per formato CSV legacy TickerTracker.
**Microstep:**
1. Creare file `backend/src/sync/infra/csv_parser.py`
2. Definire classe `LegacyCsvParser`
3. Implementare metodo `parse_estimates_csv(content: bytes) -&gt; List[LegacyEstimateRow]`:
- Gestire encoding UTF-8 con BOM
- Mappare le 120+ colonne del formato legacy
- Gestire colonne vuote o mancanti senza crash
- Restituire lista di dataclass con dati parsed
4. Implementare metodo `export_estimate_to_csv_row(estimate: Estimate, fundamentals: dict) -&gt; str`:
- Mappare dati puliti nel formato "piatto" legacy
- Gestire valori None
5. Implementare metodo `parse_history_csv(content: bytes) -&gt; List[LegacyHistoryRow]`
6. Implementare metodo `export_history_to_csv(data: List[MarketData]) -&gt; bytes`
7. Creare file di mapping colonne per documentazione
**Acceptance Criteria:**
- [ ] Parse gestisce file reali legacy senza errori
- [ ] Round-trip parse -&gt; export -&gt; parse produce stessi dati
- [ ] Colonne mancanti hanno default sensati
- [ ] Encoding gestito correttamente
Nota: la retro‑compatibilità del formato legacy è validata dai test E2E del TASK 2.23.
---
## TASK 2.22: Implementazione Sync Service
**Descrizione:** Implementare service per sincronizzazione bidirezionale con Drive.
**Microstep:**
1. Creare file `backend/src/sync/services/sync_service.py`
2. Definire classe `SyncService`
3. Iniettare: `GoogleDriveClient`, `LegacyCsvParser`, `EstimateRepository`, `MarketDataRepository`, `SyncJobRepository`
4. Implementare metodo `run_initial_import()`:
- Scaricare file JSON backup e CSV history da Drive
- Parsare e importare stime nel DB
- Creare SyncJob con risultato
5. Implementare metodo `sync_estimate_to_drive(estimate_id: UUID)`:
- Recuperare stima e fundamentals
- Esportare in formato CSV
- Aggiornare file Drive con pattern file temporaneo
- Calcolare e salvare checksum
6. Implementare metodo `run_daily_history_sync()`:
- Per ogni ticker attivo, aggiornare file History_*.csv su Drive
7. Implementare logica di conflict resolution: last-writer-wins con logging conflitti
**Acceptance Criteria:**
- [ ] Import non crea duplicati (idempotente)
- [ ] Export usa file temporaneo per atomicità
- [ ] Checksum verificato dopo ogni operazione
- [ ] Conflitti loggati per review manuale
Nota: la retro‑compatibilità del formato legacy è validata dai test E2E del TASK 2.23.
---
## TASK 2.23: Test Retro‑compatibilità Backup &amp; History Legacy (Sync Engine)
Descrizione:Validare che il nuovo backend mantenga la piena retro-compatibilità con i file legacy (backup JSON e History_*.csv) prodotti dalla versione HTML+GAS.
Microstep:
Creare file backend/tests/e2e/test_legacy_compatibility.py.
Aggiungere fixture che carica 1–2 file JSON di backup reali e 1–2 file History_*.csv reali da una cartella tests/fixtures/legacy/.
Scrivere test test_import_backup_json_roundtrip:
Importare il backup JSON con gli stessi path usati da SyncService.run_initial_import().
Esportare lo stato corrente del DB in un nuovo JSON “simulato”.
Verificare che numero di stime, ticker e campi chiave (ticker, data apertura, target %, stop %, status) coincidano.
Scrivere test test_import_history_csv_roundtrip:
Parsare un CSV legacy con LegacyCsvParser.parse_history_csv.
Importare i dati in MarketDataRepository.
Esportare nuovamente con LegacyCsvParser.export_history_to_csv.
Verificare che dati OHLC e date siano identici (a parte eventuali colonne vuote aggiuntive).
Aggiungere un test test_sync_estimate_to_drive_does_not_break_legacy_file_format:
Usare sync_estimate_to_drive(estimate_id) con un estimate di test.
Scaricare il file aggiornato da un Drive finto (o mockato) e verificare che le colonne obbligatorie del formato legacy siano tutte presenti e nell’ordine previsto.
Acceptance Criteria:
Import + export di backup JSON non perde nessuna stima né cambia i valori chiave.
Import + export di CSV storico produce gli stessi valori OHLC e date.
I file generati dal nuovo SyncService sono ancora leggibili dallo script HTML+GAS originale.
I test e2e possono essere eseguiti localmente con pytest senza dipendenze da Drive reale (mocks/fixtures).
Questi task coprono il nuovo Sync Engine con Google Drive e garantiscono la piena retro‑compatibilità con i file legacy (backup JSON e History_*.csv) tramite test E2E dedicati.
---
## TASK 2.24: Setup Background Worker (APScheduler)
**Descrizione:** Configurare worker per job schedulati di sync e aggiornamento.
**Microstep:**
1. Installare dipendenza `apscheduler`
2. Creare file `backend/src/infra/scheduler/scheduler.py`
3. Configurare `AsyncIOScheduler` con timezone UTC
4. Definire job `refresh_market_data`: ogni 5 minuti durante orari di mercato
5. Definire job `daily_history_sync`: ogni giorno alle 23:00 UTC
6. Definire job `refresh_materialized_views`: ogni 5 minuti
7. Definire job `check_targets`: ogni minuto per verificare hit target/stop
8. Implementare hook startup/shutdown per FastAPI
9. Aggiungere logging per inizio/fine ogni job
10. Aggiungere metrica per durata e successo/fallimento job
**Acceptance Criteria:**
- [ ] Scheduler parte con l'applicazione
- [ ] Job eseguono agli orari configurati
- [ ] Shutdown graceful dei job in corso
- [ ] Errori nei job non crashano l'applicazione
---
## TASK 2.25: Implementazione Pattern Outbox per Eventi
**Descrizione:** Creare pattern outbox per pubblicazione affidabile eventi verso Drive.
**Microstep:**
1. Creare modello SQLAlchemy `OutboxEvent`: `id`, `event_type`, `payload` (JSONB), `created_at`, `processed_at` (nullable), `error` (nullable), `retry_count`
2. Creare migrazione Alembic
3. Modificare `EstimateService` per salvare eventi in outbox nella stessa transazione del DB
4. Creare `OutboxProcessor` che:
- Legge eventi non processati
- Esegue azione (es. sync verso Drive)
- Marca come processato o incrementa retry_count
5. Schedulare `OutboxProcessor` ogni 30 secondi
6. Implementare dead letter: dopo N retry, marca come failed e alerta
**Acceptance Criteria:**
- [ ] Eventi salvati atomicamente con dati business
- [ ] Processor riprova eventi falliti
- [ ] Dead letter per eventi irrecuperabili
- [ ] Nessuna perdita di eventi
---
# SEZIONE 3: SICUREZZA, OSSERVABILITÀ, GOVERNANCE
---
## TASK 3.1: Implementazione Security Middleware
Priorità: Fase 2 (necessario solo in scenari multi‑utente / produzione, NON blocca l'ambiente locale single‑user).
**Descrizione:** Creare middleware FastAPI per sicurezza centralizzata.
**Microstep:**
1. Creare file `backend/src/infra/security/middleware.py`
2. Definire classe `SecurityMiddleware`
3. Implementare aggiunta security headers a ogni response:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (solo se HTTPS)
- `Content-Security-Policy` configurabile
4. Implementare validazione API key da header `X-API-Key` (opzionale, configurabile)
5. Implementare logging request con campi: method, path, status, duration, client_ip
6. Registrare middleware in applicazione FastAPI
**Acceptance Criteria:**
- [ ] Headers presenti in tutte le response
- [ ] API key validata se configurata
- [ ] Logging strutturato per ogni request
- [ ] Middleware non rallenta significativamente (&lt;1ms overhead)
---
## TASK 3.2: Implementazione Rate Limiting
Priorità: Fase 2 (necessario solo in scenari multi‑utente / produzione, NON blocca l'ambiente locale single‑user).
**Descrizione:** Aggiungere rate limiting per protezione API.
**Microstep:**
1. Installare dipendenza `slowapi`
2. Creare file `backend/src/infra/security/rate_limit.py`
3. Configurare `Limiter` con storage Redis
4. Definire limiti di default: 100 req/minuto per IP
5. Definire limiti specifici per endpoint sensibili:
- `/api/chat`: 10 req/minuto
- `/api/estimates` POST: 30 req/minuto
- `/api/market/price`: 60 req/minuto
6. Implementare response 429 con header `Retry-After`
7. Aggiungere whitelist per IP interni/admin
**Acceptance Criteria:**
- [ ] Rate limit applicato correttamente
- [ ] Storage Redis per condivisione tra istanze
- [ ] Response 429 include Retry-After
- [ ] Whitelist funzionante
---
## TASK 3.3: Implementazione Input Validation Avanzata
**Descrizione:** Creare validatori Pydantic v2 riutilizzabili e centralizzati per
input sicuro. I validatori vivono in un unico modulo shared e vengono importati
dagli schema esistenti — non sostituiscono i vincoli di dominio già presenti.
**Contesto infrastrutturale:**
- `src/shared/schemas/` contiene già: `api_response.py`, `pagination.py`
- Schema target da aggiornare: `estimates/schemas/commands.py`,
`estimates/schemas/filters.py`
- I Field(gt=0, le=100) / Field(le=1000) già presenti in `commands.py` sono
vincoli di dominio specifici: NON vanno rimossi né sostituiti
---
**Microstep:**
1. Creare file `backend/src/shared/schemas/validators.py`
2. Implementare `sanitize_ticker(v: str) -&gt; str`:
- Regex: `^[A-Z0-9.\-]{1,10}$` (uppercase, dopo `.upper()`)
- Solleva `ValueError` con msg: `"Ticker must be 1–10 characters: A-Z, 0-9, dot or dash"`
- Esempio valido: `"AAPL"`, `"BRK.B"` | Invalido: `"aapl"`, `"TOOLONGNAME1"`, `"AA PL"`
3. Implementare `sanitize_text(v: str, *, max_len: int = 500) -&gt; str`:
- Rimuove tag HTML con `re.sub(r"&lt;[^&gt;]+&gt;", "", v)`
- Strip whitespace, tronca a `max_len` caratteri
- Solleva `ValueError` se dopo strip il risultato è vuoto e il campo era obbligatorio
- Non solleva errore su stringa vuota (la nullable-ness è responsabilità dello schema)
4. Implementare `validate_price(v: Decimal) -&gt; Decimal`:
- Deve essere `&gt; 0`
- Deve essere `&lt;= Decimal("999999.999999")` (range ragionevole)
- Normalizzare a max 6 decimali con `v.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)`
- Solleva `ValueError`: `"Price must be positive and ≤ 999,999.999999"`
5. Implementare `validate_percentage(v: Decimal) -&gt; Decimal`:
- Range: `&gt;= Decimal("-100")` e `&lt;= Decimal("1000")`
- Normalizzare a 4 decimali con `v.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)`
- Solleva `ValueError`: `"Percentage must be between -100% and +1000%"`
- ⚠️ Non usare questo validatore per sostituire `Field(le=100)` su `stop_loss_percent`
in `commands.py` — quel vincolo di dominio è più restrittivo e resta invariato
6. Implementare `validate_date_range(start: datetime, end: datetime) -&gt; None`:
- Deve soddisfare: `start &lt;= end`
- Span massimo: `(end - start).days &lt;= 3650` (10 anni)
- Solleva `ValueError`: `"start_date must be ≤ end_date"`
- Solleva `ValueError`: `"Date range cannot exceed 10 years"`
7. Applicare i validatori agli schema esistenti:
**`estimates/schemas/commands.py`** — modifiche minime:
- `CloseEstimateCommand.exit_price`: aggiungere `@field_validator("exit_price")`
che chiama `validate_price(v)`
- `CreateEstimateCommand.ai_reasoning` e `UpdateEstimateCommand.ai_reasoning`:
aggiungere `@field_validator` che chiama `sanitize_text(v, max_len=2000)`
- Non modificare `target_profit_percent`, `stop_loss_percent`, `ai_confidence`:
i loro `Field(gt=0, le=...)` sono vincoli di dominio, non di sicurezza
**`estimates/schemas/filters.py`** — modifiche minime:
- Aggiungere `@model_validator(mode="after")` su `EstimateFilters` che chiama
`validate_date_range(self.created_after, self.created_before)` solo se
entrambi i campi sono non-None (same logic for closed_after/closed_before)
8. Aggiornare `src/shared/schemas/__init__.py`:
- Esportare tutti e 5 i validatori pubblici
---
**Acceptance Criteria:**
- [ ] `sanitize_ticker("aa pl!")` solleva `ValidationError` con messaggio leggibile
- [ ] `sanitize_text("&lt;script&gt;alert(1)&lt;/script&gt;testo")` restituisce `"testo"` senza tag
- [ ] `validate_price(Decimal("0"))` e `validate_price(Decimal("9999999"))` sollevano errore
- [ ] `validate_percentage(Decimal("1001"))` solleva errore;
`validate_percentage(Decimal("-100"))` passa
- [ ] `validate_date_range(2026-01-01, 2025-01-01)` solleva errore (start &gt; end)
- [ ] `validate_date_range(2020-01-01, 2031-01-02)` solleva errore (&gt; 10 anni)
- [ ] I `Field(le=100)` esistenti su `stop_loss_percent` rimangono invariati
- [ ] `pytest tests/ -x --tb=short` — tutti i test precedenti (315) continuano a passare
- [ ] Copertura test ≥ 90% per `validators.py` (ogni branch, ogni messaggio di errore)
- [ ] Nessun input può causare SQL injection o XSS (verificato da test dedicati)
---
**File modificati attesi:**
- `src/shared/schemas/validators.py` ← NEW
- `src/shared/schemas/__init__.py` ← update export
- `src/estimates/schemas/commands.py` ← field_validator su exit_price e ai_reasoning
- `src/estimates/schemas/filters.py` ← model_validator su date ranges
- `tests/unit/shared/test_validators.py` ← NEW (min 20 test cases)
**File da NON toccare:**
- `src/shared/domain/value_objects/` — i VO hanno già la loro validazione
- `src/infra/security/` — sicurezza di rete separata dalla validazione input
- Qualsiasi altro schema al di fuori di `estimates/`
---
### Istruzioni per LLM
- Usa `@field_validator` con `@classmethod` (Pydantic v2 — no `@validator`)
- Usa `@model_validator(mode="after")` per validazioni cross-field
- I messaggi di errore devono essere in inglese, senza stack trace, comprensibili
da un utente finale (es. "Ticker must be 1–10 characters: A-Z, 0-9, dot or dash")
- Non introdurre dipendenze esterne per sanitizzazione HTML — usa solo `re` stdlib
- `validate_date_range` è una funzione standalone, non un validator decorato:
viene chiamata dai `@model_validator` degli schema, non usata standalone su field
- Alla fine, produci elenco puntato con file modificati e output di
`pytest tests/ --tb=short -q` completo
---
## TASK 3.4: Implementazione Encryption at Rest
**Descrizione:** Creare tipo SQLAlchemy per campi cifrati nel database.
**Microstep:**
1. Creare file `backend/src/infra/security/encryption.py`
2. Implementare classe `EncryptedString` che estende `TypeDecorator`
3. Usare `cryptography.fernet` per cifratura simmetrica
4. Implementare `process_bind_param`: cifra prima di salvare
5. Implementare `process_result_value`: decifra dopo lettura
6. Chiave di cifratura da Settings (SecretStr)
7. Documentare campi che usano questo tipo
8. Implementare utility per rotazione chiave
**Acceptance Criteria:**
- [ ] Dati cifrati nel DB non leggibili direttamente
- [ ] Lettura/scrittura trasparente per l'applicazione
- [ ] Chiave gestita in modo sicuro
- [ ] Procedura rotazione documentata
---
## TASK 3.5: Setup Structured Logging con Correlation ID
**Descrizione:** Configurare logging strutturato JSON con correlation ID per tracing.
**Microstep:**
1. Installare dipendenza `structlog`
2. Creare file `backend/src/infra/logging/config.py`
3. Configurare structlog con processors: add_log_level, TimeStamper(ISO), JSONRenderer
4. Creare ContextVar `correlation_id` per request tracing
5. Creare middleware che:
- Legge header `X-Correlation-ID` o genera nuovo UUID
- Imposta ContextVar
- Aggiunge correlation_id alla response
6. Creare processor structlog che aggiunge correlation_id a ogni log
7. Configurare livelli log da Settings (DEBUG in dev, INFO in prod)
**Acceptance Criteria:**
- [ ] Tutti i log sono JSON
- [ ] Correlation ID presente in ogni log entry
- [ ] Correlation ID propagato in response header
- [ ] Livello log configurabile per ambiente
---
## TASK 3.6: Implementazione Metriche Prometheus
Priorità: Fase 2 (opzionale per ambiente locale single‑user; implementare solo se servono metriche/monitoring avanzati).
**Descrizione:** Esporre metriche business e tecniche per monitoring.
**Microstep:**
1. Installare dipendenza `prometheus-client`
2. Creare file `backend/src/infra/metrics/metrics.py`
3. Definire metriche business:
- `Counter` estimates_created_total (labels: ticker, ai_model)
- `Counter` estimates_closed_total (labels: ticker, outcome)
- `Gauge` active_estimates_total (labels: status)
- `Gauge` current_portfolio_pnl
4. Definire metriche tecniche:
- `Histogram` api_request_duration_seconds (labels: endpoint, method, status)
- `Counter` yahoo_api_calls_total (labels: endpoint, status)
- `Counter` drive_sync_operations_total (labels: operation, status)
- `Counter` cache_hits_total / cache_misses_total (labels: cache_name)
5. Creare endpoint `GET /metrics` che espone metriche in formato Prometheus
6. Creare helper decorator `@track_duration` per misurare latenza
**Acceptance Criteria:**
- [ ] Endpoint /metrics restituisce formato Prometheus valido
- [ ] Metriche aggiornate in tempo reale
- [ ] Labels permettono drill-down
- [ ] Histogram ha bucket appropriati per latenze
---
## TASK 3.7: Implementazione Health Checks Completi
Priorità: Fase 2 (opzionale per ambiente locale single‑user; implementare solo se servono metriche/monitoring avanzati).
**Descrizione:** Creare endpoint health check per tutte le dipendenze.
**Microstep:**
1. Creare file `backend/src/infra/health/health_service.py`
2. Definire dataclass `ComponentHealth`: name, status (HEALTHY/DEGRADED/UNHEALTHY), latency_ms, message
3. Definire dataclass `SystemHealth`: status, version, uptime_seconds, components
4. Implementare check per ogni componente:
- Database: `SELECT 1`
- Redis: `PING`
- Yahoo API: get price per AAPL (ticker sempre disponibile)
- Google Drive: list files nella folder configurata
5. Implementare `check_all()` che esegue check in parallelo
6. Creare endpoint `GET /health` con SystemHealth completo
7. Creare endpoint `GET /health/ready` per Kubernetes readiness (solo DB)
8. Creare endpoint `GET /health/live` per Kubernetes liveness (solo processo vivo)
**Acceptance Criteria:**
- [ ] /health restituisce stato tutti i componenti
- [ ] Componenti non critici in DEGRADED non rendono sistema UNHEALTHY
- [ ] /health/ready fallisce se DB non disponibile
- [ ] /health/live sempre OK se processo risponde
---
## TASK 3.8: Implementazione Data Quality Monitor
Priorità: Fase 2 (opzionale per ambiente locale single‑user; implementare solo se servono metriche/monitoring avanzati).
**Descrizione:** Creare sistema di monitoraggio qualità dati di mercato.
**Microstep:**
1. Creare file `backend/src/market_data/services/quality_monitor.py`
2. Definire dataclass `QualityRule`: name, description, check_fn, severity
3. Definire dataclass `QualityIssue`: ticker, rule_name, severity, message, detected_at
4. Implementare regole di default:
- Prezzi positivi
- No gap &gt; 5 giorni lavorativi
- Variazione giornaliera &lt; 50%
- Volume &gt; 0
5. Implementare metodo `run_checks(ticker: str) -&gt; List[QualityIssue]`
6. Implementare metodo `run_all_checks() -&gt; Dict[str, List[QualityIssue]]`
7. Schedulare check giornaliero
8. Loggare/alertare su issue critici
**Acceptance Criteria:**
- [ ] Regole coprono scenari comuni di data corruption
- [ ] Issue loggati con dettagli sufficienti per debug
- [ ] Alert per issue severity=critical
- [ ] Report giornaliero generato
---
## TASK 3.9: Implementazione Data Lineage Tracking
Priorità: Fase 2 (opzionale per ambiente locale single‑user; implementare solo se servono metriche/monitoring avanzati).
**Descrizione:** Aggiungere metadati di provenienza a tutti i dati di mercato.
**Microstep:**
1. Creare file `backend/src/shared/domain/lineage.py`
2. Definire Enum `DataSource`: YAHOO_FINANCE, FINNHUB, MANUAL_ENTRY, DRIVE_SYNC, CALCULATED
3. Definire mixin `LineageTracked` con campi: data_source, source_timestamp, ingestion_timestamp, quality_score
4. Applicare mixin a modello MarketData
5. Creare migrazione Alembic per nuove colonne
6. Modificare provider e import per popolare campi lineage
7. Esporre lineage negli endpoint API (campo opzionale includable)
**Acceptance Criteria:**
- [ ] Ogni record MarketData ha lineage completo
- [ ] Source timestamp riflette quando il dato è stato generato alla fonte
- [ ] Quality score calcolato (freshness + completeness)
- [ ] API permette di filtrare/ordinare per lineage
---
## TASK 3.10: Configurazione Connection Pooling Ottimizzato
Priorità: Media (consigliato dopo l'MVP per migliorare performance e stabilità, ma non blocca l'uso locale base).
**Descrizione:** Ottimizzare pool connessioni database per performance e resilienza.
**Microstep:**
1. Modificare file `backend/src/shared/infra/database.py`
2. Configurare QueuePool con parametri:
- pool_size: 5 (dev) / 10 (prod)
- max_overflow: 10 (dev) / 20 (prod)
- pool_timeout: 30 secondi
- pool_recycle: 1800 secondi (30 min)
- pool_pre_ping: True
3. Leggere configurazione da Settings
4. Aggiungere metriche pool: connections_in_use, connections_available
5. Documentare tuning per diversi carichi
**Acceptance Criteria:**
- [ ] Pool configurato correttamente per ambiente
- [ ] pre_ping evita connessioni stale
- [ ] Metriche pool esposte
- [ ] Nessun connection leak sotto carico
---
## TASK 3.11: Implementazione Query Pagination Cursor-Based
Priorità: Fase 2 (necessario solo con dataset molto grandi; non blocca l'MVP locale).**Descrizione:** Implementare paginazione efficiente basata su cursore per grandi dataset.
**Microstep:**
1. Creare file `backend/src/shared/repositories/pagination.py`
2. Definire dataclass `CursorPagination`: cursor (optional), limit, direction (NEXT/PREV)
3. Definire dataclass `PaginatedResult[T]`: items, next_cursor, prev_cursor, has_more
4. Implementare funzione `encode_cursor(values: dict) -&gt; str` (base64 encode)
5. Implementare funzione `decode_cursor(cursor: str) -&gt; dict`
6. Implementare helper `apply_cursor_pagination(query, cursor, sort_columns)` per SQLAlchemy
7. Modificare repository MarketData per usare cursor pagination
8. Documentare formato cursore e limitazioni
**Acceptance Criteria:**
- [ ] Cursore opaco (non manipolabile dall'utente)
- [ ] Performance O(1) indipendente dalla pagina
- [ ] Navigazione avanti e indietro funzionante
- [ ] Gestione edge case: prima pagina, ultima pagina, dataset vuoto
---
##TASK 3.12: Docker Compose Ambiente Locale
Priorità: Alta (MVP - richiesto per avere un ambiente locale "one‑command" DB + backend + frontend).
Descrizione:Preparare un ambiente locale “one-command” con Docker Compose per DB, backend e frontend.
Microstep:
Creare file docker-compose.yml nella root del progetto.
Definire servizio db (PostgreSQL 16) con:
volume per i dati,
variabili d’ambiente (DB name, user, password) lette da .env.
Definire servizio backend che:
builda da ./backend (Dockerfile semplice con Python + requirements),
espone la porta 8000,
dipende da db,
usa variabili d’ambiente per DATABASE_URL e altre config base.
Definire servizio frontend che:
builda da ./frontend (Vite build),
serve i file statici con un Nginx minimale o con npm run dev in dev,
espone la porta 3000.
Creare file .env.example con valori di esempio per DB e configurazione minima.
Aggiornare il README principale con una sezione “Avvio rapido” che spiega:
cp .env.example .env,
docker compose up --build,
URL di accesso (es. http://localhost:3000).
Acceptance Criteria:
Con docker compose up --build il DB, il backend e il frontend partono senza configurazioni manuali extra.
Il frontend comunica correttamente con il backend all’interno di Docker (es. usando http://backend:8000 come baseURL).
La procedura di avvio rapido nel README è sufficiente per riprodurre l’ambiente da zero.
---
# SEZIONE 4: FRONTEND &amp; UX
---
## TASK 4.1: Setup Progetto Frontend (Vite + React 19)
**Descrizione:** Inizializzare progetto frontend con stack moderno.
**Microstep:**
1. Creare progetto con `npm create vite@latest frontend -- --template react-ts`
2. Installare dipendenze core: `react-router-dom`, `@tanstack/react-query`, `axios`
3. Installare dipendenze UI: `tailwindcss`, `postcss`, `autoprefixer`
4. Installare dipendenze form: `react-hook-form`, `zod`, `@hookform/resolvers`
5. Installare dipendenze charts: `recharts`
6. Installare dipendenze utility: `decimal.js`, `date-fns`
7. Configurare TailwindCSS
8. Configurare path aliases in tsconfig e vite.config
9. Creare struttura cartelle: `features/`, `shared/`, `app/`
10. Creare file README con convenzioni
**Acceptance Criteria:**
- [ ] `npm run dev` avvia dev server
- [ ] `npm run build` produce build di produzione
- [ ] TypeScript strict mode abilitato
- [ ] TailwindCSS funzionante
- [ ] Path aliases funzionanti
---
## TASK 4.2: Creazione Struttura Feature Modules
**Descrizione:** Organizzare codice frontend in moduli per funzionalità.
**Microstep:**
1. Creare cartella `frontend/src/features/estimates/` con sottocartelle: `components/`, `hooks/`, `api/`, `types/`
2. Creare cartella `frontend/src/features/portfolio/` con stessa struttura
3. Creare cartella `frontend/src/features/market-data/` con stessa struttura
4. Creare cartella `frontend/src/features/chat-ai/` con stessa struttura
5. Creare cartella `frontend/src/shared/` con sottocartelle: `components/`, `hooks/`, `utils/`, `types/`, `api/`
6. Creare cartella `frontend/src/app/` per routing e layout
7. Creare file index.ts in ogni cartella per esportazioni pubbliche
8. Documentare convenzione in README
**Acceptance Criteria:**
- [ ] Ogni feature è self-contained
- [ ] Shared contiene solo codice riutilizzabile
- [ ] Import tra feature passano per index pubblici
- [ ] Nessun import circolare
---
## TASK 4.3: Configurazione React Query
**Descrizione:** Configurare TanStack Query per data fetching centralizzato.
**Microstep:**
1. Creare file `frontend/src/app/providers/QueryProvider.tsx`
2. Configurare QueryClient con defaults:
- staleTime: 5 minuti per dati generici
- gcTime: 30 minuti
- retry: 3 con backoff
- refetchOnWindowFocus: true
3. Creare QueryClientProvider wrapper
4. Configurare devtools in development
5. Creare hook custom `useApiQuery` che wrappa useQuery con gestione errori standard
6. Creare hook custom `useApiMutation` che wrappa useMutation con gestione errori e toast
**Acceptance Criteria:**
- [ ] QueryClient configurato correttamente
- [ ] Devtools visibili in dev
- [ ] Hook custom semplificano uso
- [ ] Errori gestiti uniformemente
---
## TASK 4.4: Creazione Client API Tipizzato
**Descrizione:** Creare client HTTP tipizzato per comunicazione con backend.
**Microstep:**
1. Creare file `frontend/src/shared/api/client.ts`
2. Configurare istanza axios con baseURL da variabile ambiente
3. Aggiungere interceptor request per:
- Aggiungere header Authorization (se presente token)
- Aggiungere header X-Correlation-ID (genera UUID)
4. Aggiungere interceptor response per:
- Estrarre data da ApiResponse
- Trasformare errori in formato uniforme
5. Creare file `frontend/src/shared/api/types.ts` con tipi ApiResponse, ApiError
6. Creare funzioni tipizzate: `get&lt;T&gt;`, `post&lt;T&gt;`, `patch&lt;T&gt;`, `delete&lt;T&gt;`
**Acceptance Criteria:**
- [ ] Tutte le chiamate usano client centralizzato
- [ ] Tipi response inferiti correttamente
- [ ] Errori hanno struttura uniforme
- [ ] Correlation ID propagato
---
TASK 4.5: Wrapper Decimale per Calcoli Finanziari (FE)
Descrizione:Usare una libreria decimale in frontend per tutti i calcoli monetari e percentuali, evitando i number JS nativi.
Microstep:
Aggiungere dipendenza decimal.js (o big.js) al progetto frontend.
Creare file frontend/src/shared/finance/decimalMoney.ts.
Definire type MoneyDecimal con campi: amount: Decimal, currency: string.
Implementare funzioni helper:
parseMoneyFromString(value: string, currency: string) -&gt; MoneyDecimal
formatMoney(m: MoneyDecimal) -&gt; string
calculatePnL(entry: MoneyDecimal, current: MoneyDecimal, quantity: Decimal).
Sostituire nei componenti EstimateCard, EstimateForm, Dashboard l’uso di number per importi con MoneyDecimal/helper.
Acceptance Criteria:
Nessun calcolo di P&amp;L, prezzi o percentuali usa più number JS puro.
I risultati di P&amp;L coincidono con quelli calcolati dal backend a parità di input.
I valori mostrati all’utente non soffrono di errori di arrotondamento “classici” JS (es. 0.1+0.2 ≠ 0.3000004).
---
## TASK 4.6: Implementazione API Hooks per Estimates
**Descrizione:** Creare hook React Query per operazioni su stime.
**Microstep:**
1. Creare file `frontend/src/features/estimates/api/queries.ts`
2. Implementare `useEstimates(filters)`: lista stime con filtri
3. Implementare `useEstimate(id)`: singola stima con dettagli
4. Implementare `useEstimateHistory(id)`: audit trail stima
5. Creare file `frontend/src/features/estimates/api/mutations.ts`
6. Implementare `useCreateEstimate()`: creazione nuova stima
7. Implementare `useUpdateEstimate()`: aggiornamento stima
8. Implementare `useCloseEstimate()`: chiusura stima
9. Configurare invalidation corretta delle query dopo mutation
**Acceptance Criteria:**
- [ ] Hook restituiscono stati: loading, error, data
- [ ] Filtri riflessi in query key per caching corretto
- [ ] Mutation invalida query correlate
- [ ] Tipi TypeScript completi
---
TASK 4.7: Error Boundary Globale &amp; Gestione Errori UX
Descrizione:Gestire in modo uniforme errori runtime e di rete, con un ErrorBoundary e notifiche consistenti.
Microstep:
Creare componente frontend/src/app/components/AppErrorBoundary.tsx che:
intercetta errori React e mostra una schermata di fallback con bottone “Riprova/Ricarica pagina”.
Wrappare il router principale / App root con AppErrorBoundary.
Creare hook useNotify in frontend/src/shared/ui/useNotify.ts per mostrare toast di errore/successo (riusando il sistema di toast che già hai).
Integrare useNotify nei hook useApiQuery/useApiMutation per mostrare errori di business (es. ticker non trovato) in modo uniforme.
Acceptance Criteria:
Un errore JavaScript in un componente non “rompe” tutta l’app ma mostra la schermata di fallback.
Gli errori di rete/API sono mostrati all’utente con messaggio leggibile e coerente.
I toast non si sovrappongono caoticamente (throttling/raggruppamento base).
---
## TASK 4.8: Implementazione Componente EstimateForm
**Descrizione:** Creare form per creazione/modifica stime con validazione.
**Microstep:**
1. Creare file `frontend/src/features/estimates/components/EstimateForm.tsx`
2. Definire schema Zod per validazione: ticker (required), direction, target_profit_percent, stop_loss_percent, notes
3. Configurare react-hook-form con zodResolver
4. Implementare campo ticker con autocomplete (usa API search)
5. Implementare campi numerici con validazione range
6. Implementare preview calcoli (target price, stop loss price) in tempo reale
7. Implementare submit con useCreateEstimate
8. Mostrare errori validazione inline
9. Mostrare errori API con toast/alert
**Acceptance Criteria:**
- [ ] Validazione client-side completa
- [ ] Autocomplete ticker funzionante
- [ ] Preview calcoli aggiornato in tempo reale
- [ ] Submit disabilitato durante invio
- [ ] Errori mostrati chiaramente
---
## TASK 4.9: Implementazione Componente EstimateCard
**Descrizione:** Creare card per visualizzazione singola stima in lista.
**Microstep:**
1. Creare file `frontend/src/features/estimates/components/EstimateCard.tsx`
2. Mostrare: ticker, direction badge, status badge
3. Mostrare prezzi: entry, current, target, stop loss
4. Mostrare P&amp;L: valore assoluto e percentuale con colore (verde/rosso)
5. Mostrare: data apertura, giorni aperti
6. Mostrare: AI model badge, confidence score
7. Implementare click handler per navigazione a dettaglio
8. Implementare menu azioni: edit, close, delete
9. Rendere componente responsive (card su mobile, row su desktop)
**Acceptance Criteria:**
- [ ] Tutti i dati chiave visibili
- [ ] Colori P&amp;L corretti (verde positivo, rosso negativo)
- [ ] Azioni accessibili
- [ ] Layout responsive
---
## TASK 4.10: Implementazione Componente EstimatesList
**Descrizione:** Creare lista stime con filtri e ordinamento.
**Microstep:**
1. Creare file `frontend/src/features/estimates/components/EstimatesList.tsx`
2. Usare useEstimates hook per dati
3. Implementare filtri: status (dropdown), ticker (autocomplete), date range (date picker)
4. Implementare ordinamento: by date, by P&amp;L, by ticker
5. Implementare virtualizzazione lista per performance (react-window)
6. Mostrare skeleton durante loading
7. Mostrare empty state quando nessun risultato
8. Mostrare error state con retry button
9. Implementare infinite scroll o paginazione
**Acceptance Criteria:**
- [ ] Filtri aggiornano query in tempo reale
- [ ] Ordinamento funzionante
- [ ] Virtualizzazione per liste lunghe (&gt;100 items)
- [ ] Stati loading/empty/error gestiti
- [ ] Scroll infinito o paginazione funzionante
---
## TASK 4.11: PWA Base (Manifest + Service Worker)
**Descrizione:**
Abilitare una PWA base per permettere installazione su desktop/mobile e caching leggero delle risorse statiche.
**Microstep:**
1. Creare `frontend/public/manifest.webmanifest` con nome app, icone, theme/background color e start_url.
2. Aggiungere il link al manifest in `index.html` e meta tag base (theme-color).
3. Aggiungere un service worker semplice (workbox o custom) per:
- cache-first su asset statici (JS/CSS/font),
- network-first sulle API (nessun caching aggressivo dei dati di mercato).
4. Aggiornare la build Vite per includere registrazione del service worker solo in production.
5. Verificare con Lighthouse che l'app sia installabile come PWA.
**Acceptance Criteria:**
- [ ] L'app è installabile come PWA in Chrome/Edge.
- [ ] Le risorse statiche sono servite dalla cache in offline/connessione lenta.
- [ ] Le chiamate API continuano a usare il network per evitare dati di mercato stantii.
---
## TASK 4.12: Accessibilità Base &amp; Skeleton i18n
**Descrizione:**
Migliorare l'accessibilità dei componenti chiave e preparare lo scheletro per localizzazione futura (es. IT/EN).
**Microstep:**
1. Installare `react-aria` o libreria analoga solo se necessario; in alternativa, usare pattern accessibili manuali (ruoli ARIA, label, focus management).
2. Aggiornare i componenti chiave (`EstimateForm`, `EstimatesList`, `Dashboard`) per:
- avere `aria-label`/`aria-describedby` sui controlli di input,
- supportare navigazione da tastiera (tab order corretto, focus visibile),
- avere contrasti colore adeguati (verifica con strumenti DevTools).
3. Aggiungere libreria di i18n leggera (`react-i18next`) e creare:
- `frontend/src/shared/i18n/config.ts`,
- file `locales/it/common.json` e `locales/en/common.json` con un piccolo set di stringhe (titolo app, menu, etichette principali).
4. Collegare il router/layout principale al provider i18n e usare `t()` in almeno 2–3 punti (es. titoli pagina, label bottoni principali).
5. Documentare nel README di frontend come aggiungere nuove chiavi di traduzione.
**Acceptance Criteria:**
- [ ] I principali flussi (creazione stima, lista stime) sono navigabili da tastiera.
- [ ] I controlli di form hanno label chiare e leggibili anche da screen reader.
- [ ] Esiste un setup i18n funzionante con almeno IT/EN, anche se l'app resta principalmente in italiano.
---
## TASK 4.13: Implementazione Dashboard Portfolio
**Descrizione:** Creare dashboard con metriche aggregate portfolio.
**Microstep:**
1. Creare file `frontend/src/features/portfolio/components/Dashboard.tsx`
2. Mostrare metriche top-level: total P&amp;L, total invested, active estimates count
3. Mostrare breakdown per status: open, closed win, closed loss
4. Implementare grafico P&amp;L cumulativo nel tempo (Recharts)
5. Implementare grafico distribuzione per ticker (pie chart)
6. Implementare tabella top performers / worst performers
7. Usare aggregazioni server-side per performance
8. Implementare refresh periodico (ogni 5 min)
**Acceptance Criteria:**
- [ ] Metriche aggregate corrette
- [ ] Grafici interattivi con tooltip
- [ ] Performance accettabile con molti dati
- [ ] Refresh automatico funzionante
---
## TASK 4.14: Implementazione Price Chart
**Descrizione:** Creare componente grafico prezzi con candlestick/line.
**Microstep:**
1. Creare file `frontend/src/features/market-data/components/PriceChart.tsx`
2. Accettare props: ticker, dateRange, chartType (line/candlestick)
3. Usare hook per fetch dati storici con aggregazione appropriata
4. Implementare grafico linea con Recharts
5. Implementare overlay con entry price, target, stop loss della stima associata
6. Implementare zoom in/out con cambio aggregazione (1D -&gt; 1W -&gt; 1M)
7. Implementare tooltip con dettagli OHLCV
8. Mostrare loading skeleton durante fetch
**Acceptance Criteria:**
- [ ] Grafico renderizza correttamente dati storici
- [ ] Zoom cambia livello aggregazione
- [ ] Overlay livelli prezzo visibili
- [ ] Tooltip informativo
- [ ] Performance fluida anche con molti datapoint
---
## TASK 4.15: Implementazione Chat AI Component
**Descrizione:** Creare componente chat per interazione con AI.
**Microstep:**
1. Creare file `frontend/src/features/chat-ai/components/ChatInterface.tsx`
2. Implementare lista messaggi con distinzione user/assistant
3. Implementare input con invio su Enter e bottone
4. Implementare hook `useSendChatMessage` per POST a /api/chat
5. Mostrare indicatore typing durante attesa risposta
6. Supportare markdown nella risposta AI
7. Implementare scroll automatico a nuovo messaggio
8. Persistere cronologia chat in sessionStorage
**Acceptance Criteria:**
- [ ] Messaggi distinti visivamente per ruolo
- [ ] Input funziona con Enter e click
- [ ] Indicatore loading durante attesa
- [ ] Markdown renderizzato (grassetto, elenchi, codice)
- [ ] Scroll a nuovo messaggio
---
# SEZIONE 5: TESTING, CI/CD, OPERAZIONI
---
## TASK 5.1: Setup Test Framework Backend
**Descrizione:** Configurare framework testing per backend Python.
**Microstep:**
1. Verificare dipendenze: pytest, pytest-asyncio, pytest-cov, httpx
2. Creare file `backend/tests/conftest.py`
3. Configurare fixture per database test (PostgreSQL in container o SQLite in-memory)
4. Configurare fixture per client HTTP (TestClient async)
5. Configurare fixture per mock services (Yahoo, Drive)
6. Creare cartelle: `tests/unit/`, `tests/integration/`, `tests/e2e/`
7. Configurare pytest.ini con markers (unit, integration, e2e)
8. Configurare coverage minima 80%
**Acceptance Criteria:**
- [ ] `pytest tests/unit` esegue test unitari
- [ ] `pytest tests/integration` esegue test con DB
- [ ] Database test isolato da produzione
- [ ] Coverage report generato
---
## TASK 5.2: Scrivere Unit Test per Value Objects
**Descrizione:** Test completi per Money, Percentage, PriceTarget.
**Microstep:**
1. Creare file `backend/tests/unit/shared/test_money.py`
2. Testare creazione Money con vari input (Decimal, int, float, string)
3. Testare operazioni aritmetiche (add, sub, mul)
4. Testare errore su currency mismatch
5. Testare round con vari decimali
6. Testare serializzazione/deserializzazione
7. Creare file `backend/tests/unit/shared/test_percentage.py`
8. Testare from_basis_points
9. Testare apply_to Money
10. Creare file `backend/tests/unit/shared/test_price_target.py`
11. Testare validazioni LONG e SHORT
12. Testare risk_reward_ratio
**Acceptance Criteria:**
- [ ] Coverage 100% sui value objects
- [ ] Edge cases coperti (zero, negativo, overflow)
- [ ] Errori attesi sollevano eccezioni corrette
---
## TASK 5.3: Scrivere Unit Test per EstimateService
**Descrizione:** Test unitari per logica business stime.
**Microstep:**
1. Creare file `backend/tests/unit/estimates/test_estimate_service.py`
2. Creare mock per EstimateRepository, MarketDataProvider, EventPublisher
3. Testare create_estimate: calcolo corretto target/stop da percentuali
4. Testare create_estimate: recupero prezzo corrente
5. Testare create_estimate: pubblicazione evento
6. Testare close_estimate: calcolo P&amp;L corretto
7. Testare check_and_update_targets: rilevamento hit target
8. Testare check_and_update_targets: rilevamento hit stop
9. Testare errori: ticker non trovato, prezzo non disponibile
**Acceptance Criteria:**
- [ ] Ogni metodo pubblico testato
- [ ] Mock verificano chiamate corrette
- [ ] Scenari errore coperti
- [ ] No dipendenze esterne nei test
---
## TASK 5.4: Scrivere Integration Test per API Estimates
**Descrizione:** Test integrazione per endpoint estimates.
**Microstep:**
1. Creare file `backend/tests/integration/test_estimates_api.py`
2. Setup: database test pulito, mock Yahoo provider
3. Testare POST /api/estimates: creazione stima valida
4. Testare POST /api/estimates: validazione input (ticker invalido, percentuali fuori range)
5. Testare GET /api/estimates: lista vuota
6. Testare GET /api/estimates: lista con filtri
7. Testare GET /api/estimates/{id}: stima esistente
8. Testare GET /api/estimates/{id}: stima non esistente (404)
9. Testare PATCH /api/estimates/{id}: aggiornamento
10. Testare DELETE /api/estimates/{id}: chiusura
**Acceptance Criteria:**
- [ ] Ogni endpoint testato per happy path
- [ ] Errori 400, 404, 500 testati
- [ ] Database pulito tra test
- [ ] Response conforme a schema ApiResponse
---
## TASK 5.5: Implementare Property-Based Testing per P&amp;L
**Descrizione:** Test basati su proprietà per calcoli finanziari.
**Microstep:**
1. Installare dipendenza `hypothesis`
2. Creare file `backend/tests/properties/test_pnl_calculations.py`
3. Testare proprietà: P&amp;L long = -P&amp;L short (simmetria)
4. Testare proprietà: P&amp;L = 0 quando entry == exit
5. Testare proprietà: P&amp;L chain è additivo (entry-&gt;A-&gt;B = (entry-&gt;A) + (A-&gt;B))
6. Testare proprietà: P&amp;L% * entry_price ≈ P&amp;L assoluto
7. Generare prezzi con strategies Decimal nel range ragionevole
8. Aggiungere esempi espliciti per edge cases
**Acceptance Criteria:**
- [ ] Proprietà verificate per migliaia di input random
- [ ] Nessun errore di arrotondamento
- [ ] Edge cases espliciti documentati
---
## TASK 5.6: Setup Test Framework Frontend
**Descrizione:** Configurare framework testing per frontend React.
**Microstep:**
1. Installare dipendenze: vitest, @testing-library/react, @testing-library/jest-dom, msw
2. Configurare vitest.config.ts
3. Configurare setupTests.ts con jest-dom matchers
4. Configurare MSW per mock API
5. Creare cartelle: `__tests__/unit/`, `__tests__/components/`, `__tests__/integration/`
6. Creare helper per render con providers (QueryClient, Router, i18n)
**Acceptance Criteria:**
- [ ] `npm run test` esegue test
- [ ] MSW intercetta chiamate API
- [ ] Helper render semplifica setup test
- [ ] Coverage report generato
---
## TASK 5.7: Scrivere Component Test per EstimateForm
**Descrizione:** Test componente per form stime.
**Microstep:**
1. Creare file `frontend/src/features/estimates/__tests__/EstimateForm.test.tsx`
2. Testare render iniziale: tutti i campi presenti
3. Testare validazione: errore se ticker vuoto
4. Testare validazione: errore se percentuale fuori range
5. Testare autocomplete: mostra suggerimenti ticker
6. Testare submit: chiamata API con dati corretti
7. Testare submit: gestione errore API
8. Testare submit: loading state durante invio
**Acceptance Criteria:**
- [ ] Tutti i campi form testati
- [ ] Validazione client-side testata
- [ ] Interazione API mockate con MSW
- [ ] Stati loading/error testati
---
## TASK 5.8: Setup E2E Test con Playwright
**Descrizione:** Configurare test end-to-end con Playwright.
**Microstep:**
1. Installare `@playwright/test`
2. Configurare playwright.config.ts
3. Configurare webServer per avviare backend e frontend
4. Creare file `e2e/setup/global-setup.ts` per seed database test
5. Creare test: flusso creazione stima end-to-end
6. Creare test: flusso visualizzazione portfolio
7. Creare test: flusso chat AI
8. Configurare screenshot/video su failure
9. Configurare esecuzione su CI
**Acceptance Criteria:**
- [ ] Test eseguono contro app completa
- [ ] Database seeded con dati test
- [ ] Screenshot catturati su failure
- [ ] Test passano in CI
---
## TASK 5.9: Implementare Chaos Testing
**Descrizione:** Test di resilienza per scenari di fallimento.
**Microstep:**
1. Creare file `backend/tests/chaos/test_resilience.py`
2. Testare: Yahoo API timeout -&gt; usa cache
3. Testare: Yahoo API errore -&gt; usa cache stale
4. Testare: Database pool esaurito -&gt; 503 graceful
5. Testare: Drive sync fallisce parzialmente -&gt; dati esistenti non corrotti
6. Testare: Rete intermittente -&gt; retry funziona
7. Aggiungere marker pytest `@pytest.mark.chaos`
8. Documentare scenari e risultati attesi
**Acceptance Criteria:**
- [ ] Sistema non crasha su fallimenti esterni
- [ ] Fallback a cache funziona
- [ ] Errori restituiti sono informativi
- [ ] Dati non corrotti da fallimenti parziali
---
## TASK 5.10: Configurare CI Pipeline (GitHub Actions)
**Descrizione:** Creare pipeline CI completa.
**Microstep:**
1. Creare file `.github/workflows/ci.yml`
2. Definire trigger: push su main/develop, pull request
3. Definire job `backend-lint`: ruff, mypy
4. Definire job `backend-test`: pytest con coverage, services PostgreSQL/Redis
5. Definire job `backend-security`: Trivy scan
6. Definire job `frontend-lint`: eslint, tsc
7. Definire job `frontend-test`: vitest con coverage
8. Definire job `e2e-test`: Playwright su entrambi i servizi
9. Configurare caching per dependencies
10. Configurare upload coverage a Codecov
**Acceptance Criteria:**
- [ ] Pipeline esegue su ogni PR
- [ ] Fallimento blocca merge
- [ ] Coverage report su Codecov
- [ ] Tempo esecuzione &lt; 10 minuti
---
## TASK 5.11: Configurare CD Pipeline (Deploy)
**Descrizione:** Estendere pipeline per deploy automatico.
**Microstep:**
1. Estendere `.github/workflows/ci.yml` o creare `cd.yml`
2. Definire job `build-images`: build Docker backend e frontend
3. Definire job `push-images`: push a GitHub Container Registry
4. Definire job `deploy-staging`: deploy automatico su staging (dopo merge su develop)
5. Definire job `deploy-production`: deploy manuale su production (dopo merge su main, richiede approval)
6. Configurare environments GitHub per staging e production
7. Configurare secrets per registry e deploy target
**Acceptance Criteria:**
- [ ] Immagini Docker buildate e pushate
- [ ] Deploy staging automatico
- [ ] Deploy production richiede approval
- [ ] Rollback possibile
---
## TASK 5.12: Implementare Feature Flags
**Descrizione:** Creare sistema feature flags per rollout graduali.
**Microstep:**
1. Creare file `backend/src/infra/feature_flags/service.py`
2. Definire Enum `FeatureFlag` con flag iniziali: NEW_DASHBOARD_UI, AI_RECOMMENDATIONS, DRIVE_SYNC_V2
3. Implementare `FeatureFlagService` con storage Redis
4. Implementare metodo `is_enabled(flag, user_id)`: check globale, poi percentage rollout, poi whitelist
5. Implementare metodo `enable(flag, percentage)`
6. Implementare metodo `disable(flag)`
7. Creare endpoint admin `POST /api/admin/feature-flags` per gestione
8. Creare dependency FastAPI per inject service
**Acceptance Criteria:**
- [ ] Flag possono essere abilitati globalmente
- [ ] Rollout percentuale funziona (deterministico per user)
- [ ] Whitelist override funziona
- [ ] Stato flag persistito in Redis
---
## TASK 5.13: Implementare Backup Automatico
**Descrizione:** Creare sistema backup database automatico.
**Microstep:**
1. Creare file `backend/scripts/backup.py`
2. Implementare funzione `create_full_backup()`:
- Esegui pg_dump con compressione
- Cifra output con Fernet (chiave da settings)
- Upload a storage (S3 o Drive folder dedicato)
- Log risultato
3. Implementare funzione `verify_backup(backup_path)`:
- Scarica backup
- Decifra
- Verifica con pg_restore --list
4. Schedulare backup giornaliero (APScheduler o cron)
5. Schedulare verifica settimanale
6. Implementare retention policy: mantieni ultimi 30 backup
7. Implementare alerting su fallimento
**Acceptance Criteria:**
- [ ] Backup creato giornalmente
- [ ] Backup cifrato
- [ ] Verifica integrità funzionante
- [ ] Alert su fallimento
- [ ] Cleanup vecchi backup automatico
---
## TASK 5.14: Creare Docker Compose Completo
**Descrizione:** Docker Compose per tutti i servizi in produzione-like.
**Microstep:**
1. Creare file `docker-compose.prod.yml`
2. Definire servizio `db`: PostgreSQL 16 con volume persistente
3. Definire servizio `redis`: Redis 7 con volume persistente
4. Definire servizio `backend`: immagine custom, env vars da file .env, healthcheck
5. Definire servizio `frontend`: Nginx con build statico, proxy pass a backend
6. Definire servizio `scheduler`: stesso backend ma comando diverso per worker
7. Configurare network interna tra servizi
8. Configurare resource limits per ogni servizio
9. Creare file `.env.prod.example` con variabili richieste
**Acceptance Criteria:**
- [ ] `docker compose -f docker-compose.prod.yml up` avvia tutto
- [ ] Servizi comunicano internamente
- [ ] Solo frontend esposto all'esterno
- [ ] Healthcheck funzionanti
- [ ] Dati persistono tra restart
---
## TASK 5.15: Creare Runbook Operativo
**Descrizione:** Documentare procedure operative e troubleshooting.
**Microstep:**
1. Creare file `docs/runbook/README.md` con indice
2. Creare `docs/runbook/startup-shutdown.md`: procedure avvio/stop servizi
3. Creare `docs/runbook/monitoring.md`: dove guardare metriche, log, alert
4. Creare `docs/runbook/database-recovery.md`: procedura restore da backup
5. Creare `docs/runbook/yahoo-outage.md`: azioni durante outage Yahoo
6. Creare `docs/runbook/drive-sync-issues.md`: troubleshooting sync
7. Creare `docs/runbook/scaling.md`: come scalare servizi
8. Includere comandi copia-incolla per ogni procedura
9. Includere contatti e escalation path
**Acceptance Criteria:**
- [ ] Ogni scenario comune documentato
- [ ] Comandi eseguibili direttamente
- [ ] RTO/RPO definiti per ogni scenario
- [ ] Rivisto da secondo paio di occhi
---
## TASK 5.16: Documentare API con OpenAPI
**Descrizione:** Verificare e arricchire documentazione OpenAPI.
**Microstep:**
1. Verificare che tutti gli endpoint abbiano docstring
2. Aggiungere esempi request/response a ogni endpoint
3. Documentare tutti i codici errore possibili
4. Aggiungere descrizioni ai parametri query/path
5. Configurare metadata OpenAPI (title, version, description, contact)
6. Verificare schema generato su /docs
7. Esportare openapi.json per uso esterno
8. Creare pagina docs custom se necessario
**Acceptance Criteria:**
- [ ] /docs mostra documentazione completa
- [ ] Esempi funzionanti per ogni endpoint
- [ ] Errori documentati
- [ ] Schema esportabile
---
## TASK 5.17: Creare Script Migrazione Dati v2.4 -&gt; v3.0
**Descrizione:** Script per migrare dati da versione legacy.
**Microstep:**
1. Creare file `backend/scripts/migrate_from_legacy.py`
2. Implementare funzione `connect_to_drive()`: autenticazione
3. Implementare funzione `download_legacy_data()`: scarica JSON e CSV da Drive
4. Implementare funzione `parse_legacy_json(content)`: parsing stime legacy
5. Implementare funzione `parse_legacy_history(content)`: parsing prezzi storici
6. Implementare funzione `transform_to_new_schema(legacy_data)`: mapping campi
7. Implementare funzione `validate_transformed_data(data)`: validazione
8. Implementare funzione `import_to_database(data)`: insert nel nuovo DB
9. Implementare funzione `verify_migration()`: confronto conteggi e totali
10. Creare report migrazione con statistiche
**Acceptance Criteria:**
- [ ] Script eseguibile da riga di comando
- [ ] Tutti i dati legacy importati
- [ ] Validazione previene import dati corrotti
- [ ] Report finale mostra successo/errori
- [ ] Idempotente (rilanciabile senza duplicati)
---
# APPENDICE: Dipendenze tra Task
Priorità MVP (ambiente locale single‑user):
- Sezione 1: tutti i task 1.1–1.8.
- Sezione 2: 2.1–2.6, 2.10, 2.12–2.13, 2.16–2.21, 2.24–2.27.
- Sezione 3: solo 3.10 (facoltativo) e 3.12 (obbligatorio); il resto è Fase 2.
- Sezione 4: 4.1–4.10, 4.7; 4.11–4.12 subito dopo se vuoi completare UX.
- Sezione 5: almeno test unitari/lint (5.x base), E2E/CI/CD restano Fase 2.
```
Sezione 1 (Setup base):
1.1 → 1.2 → 1.3 → 1.4 → 1.5
1.6 (parallelo a 1.3-1.5)
1.8 (parallelo, richiede solo 1.1)
Sezione 2 (Backend):
2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6 → 2.10
2.7, 2.8, 2.9 (paralleli dopo 2.3)
2.11 (richiede 2.4, 2.6)
2.12 (richiede 2.4, 2.10)
2.13 (richiede 2.6, 2.10)
2.14 (richiede 2.12)
2.15 (richiede 2.5, 2.12)
2.16 (richiede 2.14)
2.17 → 2.18 → 2.19
2.20 → 2.21 → 2.22 → 2.23 (collegati 2.21, 2.22, 2.23)
2.24 (richiede 2.11, 2.22)
2.25 (richiede 2.24)
Sezione 3 (Sicurezza/Observability):
Tutti paralleli dopo completamento 2.20.
- 3.12: priorità alta (MVP locale).
- 3.10: priorità media (post-MVP).
- 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.11: Fase 2 (opzionali per uso single‑user).
Sezione 4 (Frontend):
4.1 → 4.2 → 4.3 → 4.4
4.5 → 4.6, 4.7, 4.8 , 4.9, 4.10, 4.11, 4.12
4.13 (richiede 4.6)
4.14 (richiede 4.6)
4.15 (richiede 4.5)
Sezione 5 (Testing/CI):
5.1 → 5.2, 5.3, 5.4, 5.5
5.6 → 5.7
5.8 (richiede 5.1, 5.6)
5.9 (richiede 5.4)
5.10 (richiede 5.4, 5.7)
5.11 (richiede 5.10)
5.12-5.17 (paralleli dopo setup base)
```
---
# NOTE PER L'LLM ESECUTORE
1. **Esegui un task alla volta** e verifica gli acceptance criteria prima di procedere
2. **Chiedi chiarimenti** se un requisito è ambiguo
3. **Documenta** ogni scelta implementativa non ovvia
4. **Testa** ogni componente prima di passare al successivo
5. **Committa** con messaggi descrittivi che referenziano il task ID
6. **Segnala** blocchi o dipendenze mancanti
# Executive Summary
Questa versione **v1.5 Integrato** recepisce i rilievi emersi nell'AGENTS Analysis e li incorpora nel Piano Operativo v1.4. L’obiettivo è eliminare ambiguità esecutive per gli agenti LLM/umani, ridurre la duplicazione, allineare numerazioni e rendere il progetto più governabile.
**Principali miglioramenti**:
• Riallineamento numerazione task backend con introduzione formale del **TASK 2.0** (Poetry) come prerequisito.
• Unificazione del percorso **Docker Compose** (evita file/istruzioni in conflitto tra sezioni).
• Sostituzione dei link GitHub hardcoded con **percorsi relativi** per robustezza a branch/rename.
• Chiarezza sul tooling: **Poetry** come default; "uv" opzionale (richiede microstep dedicati se adottato).
• Pulizia header/sezioni e centralizzazione di **Regole Globali** (evita ripetizioni).
# Decisioni &amp; Correzioni derivate dall’AGENTS Analysis
## Criticità Prioritarie
Numerazione Task: Allineata tra root e backend. Il **TASK 2.0** (Setup Poetry) diventa prerequisito esplicito di **TASK 2.1** (SQLAlchemy).
Sovrapposizione Task Docker: Convergenza su un percorso unico: compose base → dev → prod; eliminata ambiguità su sovrascrittura/estensione.
Link Hardcoded: Sostituiti con percorsi relativi per resilienza a rename/branch e lavoro locale.
Tooling Poetry vs uv: Poetry è lo standard; `uv` opzionale con microstep dedicati se/quando adottato.
## Problemi Secondari &amp; Cleanup
Header errati nelle sezioni: Ripuliti/ricollocati per coerenza semantica.
Dipendenze cross-section e visibilità: Dichiarate dipendenze inter-sezione con note operative; gli agenti possono referenziare prerequisiti cross-section quando necessario.
Regole ripetute nel frontend (decimal.js): Accentrate in **Standard di Qualità** e referenziate dai singoli moduli.
Task mancanti nel tracker root: Allineata la tabella di marcia con l’inclusione del TASK 2.0 e riferimenti incrociati aggiornati.
# Estratti Operativi Chiave da v1.4
## Changelog v1.4 (estratto)
• Aggiunto **TASK 2.0** — Setup Progetto Python con Poetry (prerequisito di tutti i task backend).
• Aggiornata dipendenza di **TASK 2.1** su 2.0 e allineamento tra `Piano-operativo-v1.4.md` e `backend/AGENTS.md`.
• Creati file standardizzati: `pyproject.toml`, `Makefile`, `.python-version`, `scripts/check_deps.py`, `requirements*.txt`, `backend/README.md`.
# Piano di Bonifica (Sintesi Esecutiva)
• Riallineare numerazione: confermare TASK 2.0 nel tracker root; aggiornare riferimenti nei sotto-documenti.
• Unificare i task Docker: percorso evolutivo unico su compose (base→dev→prod).
• Relativizzare i link: sostituire URL GitHub con path relativi.
• Pulizia header: rimuovere header errati nelle sezioni Docker.
• Centralizzare regole ripetute (es. decimal.js) nello standard globale.
# Matrice Impatto × Priorità (AGENTS Analysis → v1.5)
Tema
Impatto
Priorità
Owner
Numerazione Task
Alto (ambiguità esecuzione)
P1
Backend Lead
Docker Compose
Medio-Alto (duplicazione)
P1
DevOps
Link Hardcoded
Medio (manutenzione)
P2
Docs/Dev
Poetry vs uv
Medio (toolchain)
P2
Backend Lead
Regole Globali
Medio (consistenza)
P2
Frontend Lead
# Appendice — Note per LLM Esecutori
• Eseguire un task alla volta rispettando gli acceptance criteria.
• Blocchi o ambiguità vanno segnalati prima di procedere.
• Usare il Makefile per uniformare comandi di sviluppo.
• Aggiornare sempre `requirements*.txt` quando si modifica `pyproject.toml`.