# AGENTS — market_data

ID: TASK 2.3
Area: market_data
Fase: MVP
Dipendenze: ✅ TASK 2.2 (Complete)

## TASK 2.3: Definizione Modello SQLAlchemy - Ticker

**Descrizione:** Configurare SQLAlchemy async base e creare primo modello Ticker.

### PARTE 1: Setup SQLAlchemy Base

1\. Creare file `backend/src/shared/infra/database.py`
2\. Importare `declarative_base` da SQLAlchemy
3\. Creare `Base = declarative_base()`
4\. Configurare async engine con `create_async_engine()`:
   - Pool size: 5 (dev), 20 (prod)
   - Echo: True (dev), False (prod)
   - DATABASE_URL da Settings
5\. Creare `AsyncSessionLocal` con `async_sessionmaker`
6\. Creare dependency `get_db()` per FastAPI injection
7\. Esportare `Base`, `engine`, `AsyncSessionLocal`, `get_db` da `__init__.py`

### PARTE 2: Creazione Modello Ticker

8\. Creare file `backend/src/market_data/domain/entities.py`
9\. Importare `Base` da `shared.infra.database`
10\. Definire classe `Ticker(Base)`:
    - `__tablename__ = "tickers"`
    - `id`: UUID primary key con `default=uuid.uuid4`
    - `symbol`: String(10), unique, not null, index
    - `name`: String(255), not null
    - `exchange`: String(50)
    - `currency`: String(3), default='USD'
    - `asset_type`: String(20), check constraint ('stock','etf','crypto')
11\. Aggiungere colonne audit:
    - `created_at`: DateTime, `default=func.now()`
    - `updated_at`: DateTime, `default=func.now()`, `onupdate=func.now()`
12\. Definire `__repr__` per debug
13\. Aggiungere `Index('ix_ticker_symbol', 'symbol')`


**Acceptance Criteria:**

- [ ] `Base` importabile da `shared.infra.database`
- [ ] Async engine si connette a PostgreSQL Docker
- [ ] `get_db()` dependency funziona con FastAPI
- [ ] Modello `Ticker` ha tutti i campi richiesti
- [ ] UUID generato automaticamente
- [ ] Timestamps gestiti automaticamente
- [ ] Constraint unique su `symbol`
- [ ] Indice su `symbol` definito

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/, backend/src/infra/cache/, backend/src/market_data/domain/entities.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.6
Area: market_data
Fase: MVP
Dipendenze: TASK 2.5

## TASK 2.6: Definizione Modello SQLAlchemy - MarketData

**Descrizione:** Creare il modello per dati storici di mercato (OHLCV).

**Microstep:**

1\. Creare file `backend/src/market_data/domain/market_data.py`

2\. Definire classe `MarketData` che eredita da Base

3\. Definire colonne: `ticker_id` (FK), `date` (Date), `open` (DECIMAL 10,4), `high` (DECIMAL 10,4), `low` (DECIMAL 10,4), `close` (DECIMAL 10,4), `volume` (BigInteger)

4\. Definire PK composta: `(ticker_id, date)`

5\. Definire colonne lineage: `data_source` (String), `ingested_at` (DateTime), `quality_score` (DECIMAL 3,2)

6\. Definire indici: su `date`, su `(ticker_id, date)` unique

**Acceptance Criteria:**

- [ ] PK composta impedisce duplicati per ticker+data

- [ ] Tutti i prezzi usano DECIMAL

- [ ] Volume usa BigInteger per supportare valori grandi

- [ ] Metadati lineage presenti per audit

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/, backend/src/infra/cache/, backend/src/market_data/domain/market_data.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.13
Area: market_data
Fase: MVP
Dipendenze: TASK 2.6, TASK 2.10

## TASK 2.13: Creazione Repository MarketData

**Descrizione:** Implementare repository per accesso dati MarketData.

**Microstep:**

1\. Creare file `backend/src/market_data/repositories/market_data_repository.py`

2\. Definire classe `MarketDataRepository`

3\. Implementare metodo `upsert_daily(ticker_id: UUID, data: List[MarketDataRow])` con ON CONFLICT UPDATE

4\. Implementare metodo `get_history(ticker_id: UUID, start: date, end: date) -> List[MarketData]`

5\. Implementare metodo `get_latest_price(ticker_id: UUID) -> Optional[MarketData]`

6\. Implementare metodo `get_latest_prices_batch(ticker_ids: List[UUID]) -> Dict[UUID, MarketData]`

7\. Implementare metodo `get_aggregated(ticker_id: UUID, interval: str) -> List[AggregatedData]` per intervalli 1D/1W/1M

**Acceptance Criteria:**

- [x] Upsert non crea duplicati
- [x] Query batch evita N+1
- [x] Aggregazioni calcolate lato Python per flessibilità
- [x] Performance accettabile per 10 anni di dati

**Implementation Notes:**

- MarketDataRepository usa ON CONFLICT (ticker_id, date) DO UPDATE per upsert atomico
- MarketDataRow: dataclass che rappresenta singola riga OHLCV con metadati
- AggregatedData: dataclass per OHLCV aggregato con period_start/end e interval
- get_latest_prices_batch usa window function per evitare N+1: `ROW_NUMBER() OVER (PARTITION BY ticker_id ORDER BY date DESC)`
- Aggregazioni (1W, 1M) calcolate in Python con dict grouping per flessibilità (alternativa: SQL GROUP BY)
- File: backend/src/market_data/repositories/market_data_repository.py (362 righe)
- Filter schemas: backend/src/market_data/schemas/filters.py con MarketDataFilters e MarketDataAggregationParams

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/, backend/src/infra/cache/, backend/src/market_data/repositories/market_data_repository.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.17
Area: market_data
Fase: MVP
Dipendenze: -

## TASK 2.17: Creazione API Router Market Data

**Descrizione:** Implementare endpoint REST per dati di mercato.

**Microstep:**

1\. Creare file `backend/src/market_data/api/routes.py`

2\. Creare router FastAPI con prefix `/api/market`

3\. Implementare endpoint `GET /price/{ticker}` per prezzo corrente

4\. Implementare endpoint `GET /history/{ticker}` con query params: start_date, end_date, interval

5\. Implementare endpoint `GET /fundamentals/{ticker}` per dati fondamentali

6\. Implementare endpoint `GET /search` con query param `q` per autocomplete ticker

7\. Aggiungere caching headers appropriati (Cache-Control)

**Acceptance Criteria:**

- [ ] Prezzi restituiti con metadata (source, timestamp, stale flag)

- [ ] History supporta aggregazione 1D/1W/1M

- [ ] Search restituisce max 10 risultati ordinati per rilevanza

- [ ] Cache headers impostati correttamente

Nota: tutti gli endpoint leggono i dati tramite MarketDataProvider (TASK 2.18-2.19), senza dipendere direttamente da yfinance.

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/, backend/src/infra/cache/, /api/market, GET /fundamentals/{ticker}, GET /history/{ticker}, GET /price/{ticker}, GET /search, backend/src/market_data/api/routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.18
Area: market_data
Fase: MVP
Dipendenze: TASK 2.17

**TASK 2.18: Definizione MarketDataProvider Astratto**

**Descrizione:**  
Definire un'interfaccia MarketDataProvider per disaccoppiare la logica di business dalla specifica sorgente dati (Yahoo oggi, altri provider domani).

**Microstep:**

- Creare file backend/src/market_data/domain/providers.py.
- Definire Protocol/classe astratta MarketDataProvider con metodi:
  - get_current_price(ticker: str) -> PriceData
  - get_historical_prices(ticker: str, start: date, end: date, interval: str) -> list[PriceData]
  - get_fundamentals(ticker: str) -> FundamentalsData.
- Definire dataclass Pydantic/Domain PriceData e FundamentalsData da usare come contratti interni.
- Aggiornare i servizi esistenti in backend/src/market_data/services/ (es. MarketDataService) per dipendere da MarketDataProvider invece che chiamare direttamente yfinance.
- Preparare stub/placeholder per futuri provider (es. FinnhubMarketDataProvider) con NotImplementedError.

**Acceptance Criteria:**

- [x] Tutta la logica di mercato usa MarketDataProvider e non dipende da yfinance direttamente.
- [x] MarketDataService riceve il provider via dependency injection FastAPI.
- [x] I test possono usare un FakeMarketDataProvider per simulare dati senza chiamate esterne.

**Stato:** ✅ COMPLETATO (2026-02-14)

**Note Implementazione:**
- Creato file `src/market_data/domain/providers.py` con interfaccia astratta `MarketDataProvider`
- Definiti contratti Pydantic: `PriceData` (OHLCV + metadata), `FundamentalsData` (metriche finanziarie)
- Interfaccia provider include metodi:
  - `get_current_price(symbol)` - Prezzo corrente
  - `get_historical_prices(symbol, start_date, end_date, interval)` - Storico
  - `get_fundamentals(symbol)` - Dati fondamentali
  - `search_symbol(query)` - Ricerca simboli
- Implementato `YahooMarketDataProvider` in `services/yahoo_provider.py` usando yfinance:
  - Supporto async con `asyncio.to_thread()` per chiamate bloccanti
  - Gestione errori con eccezioni tipizzate: `SymbolNotFoundError`, `DataUnavailableError`
  - Conversione automatica DataFrame -> PriceData con precisione Decimal
  - Timeout configurabile (default 30s)
- Implementato `FakeMarketDataProvider` in `services/provider_implementations.py` per testing:
  - Dati configurabili via `set_price()`, `set_fundamentals()`
  - Simulazione errori con `fail_on_symbol()`
  - Generazione dati storici deterministici
- Creati stub per provider futuri (tutti con NotImplementedError):
  - `FinnhubMarketDataProvider` - Real-time data, free tier 60 calls/min
  - `AlphaVantageMarketDataProvider` - Free tier 5 calls/min
  - `PolygonMarketDataProvider` - Delayed free tier
- Creato `MarketDataService` in `services/market_data_service.py`:
  - Dependency injection del provider nel costruttore
  - Metodi: `get_current_price()`, `sync_historical_data()`, `get_fundamentals()`, `search_symbols()`
  - Integrazione con `MarketDataRepository` per persistenza
  - Conversione automatica PriceData -> MarketDataRow
- Test completo in `tests/test_market_data_provider.py` - PASSED:
  - FakeProvider: 5 test passati (current price, historical, fundamentals, errors)
  - YahooProvider: Interface compliance verificata
  - Dependency injection pattern dimostrato con swapping provider
  - Stub providers verificati
- Exports aggiornati in `market_data/domain/__init__.py` e `market_data/services/__init__.py`

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/, backend/src/infra/cache/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.19
Area: market_data
Fase: MVP
Dipendenze: TASK 2.18
Stato: ✅ COMPLETATO (2026-02-14)

**TASK 2.19: Caching & Backoff per MarketDataProvider**

**Descrizione:**  
Ridurre chiamate a Yahoo/Finnhub e gestire in modo resiliente timeouts e rate‑limit, usando cache in memoria e backoff.

**Microstep:**

- Creare file backend/src/infra/cache/memory_cache.py con una semplice cache LRU/TTL (es. cachetools.TTLCache).
- Creare classe CachedMarketDataProvider in backend/src/market_data/infrastructure/cached_provider.py che implementa MarketDataProvider e wrappa un provider sottostante (YahooMarketDataProvider).
- Implementare TTL differenziato:
  - Prezzi correnti: TTL 60s.
  - Storico: TTL 1h.
  - Fundamentals: TTL 24h.
- Aggiungere logica di backoff:
  - Su TimeoutError o HTTP 429/5xx, ritentare fino a N volte (es. 3) con ritardo esponenziale (es. 0.5s, 1s, 2s).
  - In caso di fallimento definitivo, se presente un valore in cache "stale", restituirlo con flag stale=True nel PriceData/FundamentalsData.
- Configurare via Settings i TTL e il numero massimo di retry.
- Aggiornare la dependency injection in FastAPI per usare CachedMarketDataProvider come implementazione di default.

**Acceptance Criteria:**

- [x] Le chiamate ripetute allo stesso endpoint/ticker entro il TTL non generano chiamate esterne aggiuntive.
- [x] In caso di timeout/rate‑limit, il sistema usa il dato in cache se disponibile e non va in errore 500 immediato.
- [x] I test coprono: cache hit, cache miss, fallback a dati stale, backoff su errori.

**Implementazione Completata:**

File creati/modificati:
1. **src/infra/cache/memory_cache.py** (268 righe)
   - MemoryCache class con supporto TTL per-item
   - CachedValue dataclass con metadata (cached_at, ttl_seconds, is_stale property)
   - CacheKeyBuilder per chiavi consistenti
   - Thread-safe operations con RLock
   - Cache statistics (hits, misses, stale_hits, hit_rate)
   - Stale cache separata per fallback

2. **src/infra/cache/__init__.py**
   - Exports: MemoryCache, CachedValue, CacheKeyBuilder, get_global_cache

3. **src/market_data/infrastructure/cached_provider.py** (427 righe)
   - CachedMarketDataProvider decoratore che wrappa MarketDataProvider
   - CacheConfig dataclass per configurazione TTL e retry
   - TTL differenziati: current_price=60s, historical=3600s, fundamentals=86400s
   - Exponential backoff retry: 0.5s, 1s, 2s, 4s, 8s (max 3 retry)
   - Stale fallback: restituisce dati scaduti con is_stale=True se API fails
   - Retry su: TimeoutError, RateLimitExceededError, DataUnavailableError, 5xx errors
   - No retry su: client errors (4xx), SymbolNotFoundError

4. **src/market_data/infrastructure/__init__.py**
   - Exports: CachedMarketDataProvider, CacheConfig

5. **src/market_data/domain/providers.py**
   - Aggiunto campo `is_stale: bool = False` a PriceData
   - Aggiunto campo `is_stale: bool = False` a FundamentalsData

6. **src/market_data/api/dependencies.py** (93 righe)
   - get_market_data_provider(): Factory per provider cached (singleton)
   - get_uncached_provider(): Factory per provider senza cache
   - Configurazione via Settings

7. **src/market_data/api/__init__.py**
   - Exports: get_market_data_provider, get_uncached_provider

8. **src/shared/infra/config.py**
   - Sezione Cache Configuration:
     * CACHE_CURRENT_PRICE_TTL (default: 60s)
     * CACHE_HISTORICAL_PRICE_TTL (default: 3600s)
     * CACHE_FUNDAMENTALS_TTL (default: 86400s)
     * CACHE_MAX_SIZE (default: 1000)
   - Sezione Retry Configuration:
     * RETRY_MAX_ATTEMPTS (default: 3)
     * RETRY_INITIAL_BACKOFF (default: 0.5s)
     * RETRY_MAX_BACKOFF (default: 8.0s)
     * RETRY_BACKOFF_MULTIPLIER (default: 2.0)

9. **tests/test_cached_provider.py** (486 righe)
   - 8 test suites completi - tutti passati ✅
   - test_cache_hit_miss: Cache hit evita chiamate API
   - test_ttl_differentiation: TTL diversi per tipo dato
   - test_retry_with_backoff: Exponential backoff 0.1s, 0.2s
   - test_stale_data_fallback: Fallback a dati stale su errore API
   - test_no_stale_data_raises_error: Errore quando no stale data
   - test_rate_limit_handling: Retry su rate limit
   - test_cache_statistics: Tracking hits/misses/hit_rate
   - test_configuration_from_settings: Verifica struttura CacheConfig

Test results: **8/8 PASSED** in 5.33s

Acceptance criteria verification:
- ✅ Cache hit/miss: Chiamate ripetute non generano API calls
- ✅ Stale fallback: Sistema non va in errore 500 su timeout
- ✅ TTL differentiation: 60s / 1h / 24h funzionanti
- ✅ Exponential backoff: 0.5s → 1s → 2s → 4s → 8s
- ✅ Configuration: Tutti i parametri configurabili via Settings

Note tecniche:
- MemoryCache usa dict normale invece di cachetools.TTLCache per supportare TTL per-item
- CachedValue.is_stale property calcola automaticamente se scaduto
- Thread-safe con RLock per operazioni concorrenti
- LRU eviction manuale quando cache raggiunge maxsize
- Stale cache mantiene dati scaduti indefinitamente per fallback

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/, backend/src/infra/cache/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.8
Area: market_data
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.8: Implementazione Data Quality Monitor

Priorità: Fase 2 (opzionale per ambiente locale single‑user; implementare solo se servono metriche/monitoring avanzati).

**Descrizione:** Creare sistema di monitoraggio qualità dati di mercato.

**Microstep:**

1\. Creare file `backend/src/market_data/services/quality_monitor.py`

2\. Definire dataclass `QualityRule`: name, description, check_fn, severity

3\. Definire dataclass `QualityIssue`: ticker, rule_name, severity, message, detected_at

4\. Implementare regole di default:

- Prezzi positivi

- No gap > 5 giorni lavorativi

- Variazione giornaliera < 50%

- Volume > 0

5\. Implementare metodo `run_checks(ticker: str) -> List[QualityIssue]`

6\. Implementare metodo `run_all_checks() -> Dict[str, List[QualityIssue]]`

7\. Schedulare check giornaliero

8\. Loggare/alertare su issue critici

**Acceptance Criteria:**

- [x] Regole coprono scenari comuni di data corruption
- [x] Issue loggati con dettagli sufficienti per debug
- [x] Alert per issue severity=critical
- [x] Report giornaliero generato

**Stato:** ✅ COMPLETATO (2026-02-21)

**Note Implementazione:**

File creati/modificati:
1. **src/market_data/services/quality_monitor.py** (324 righe)
   - `QualityRule` dataclass: `name`, `description`, `check_fn`, `severity`
   - `QualityIssue` dataclass: `ticker`, `rule_name`, `severity`, `message`, `detected_at` (auto-UTC)
   - `__str__` su QualityIssue: `[SEVERITY] ticker / rule_name: message`
   - 4 regole di default in `DEFAULT_RULES`:
     - `positive_prices` (critical) — open/high/low/close > 0
     - `no_large_gaps` (warning) — gap ≤ 5 giorni calendario tra righe consecutive
     - `daily_change_lt50` (warning) — variazione close-to-close ≤ ±50%
     - `positive_volume` (warning) — volume > 0
   - `DataQualityMonitor`:
     - Costruttore: `rules`, `lookback_days=60`, `session_factory` (opzionale, default `AsyncSessionLocal`)
     - `run_checks(ticker)` — carica 60gg di history dal DB e applica tutte le regole
     - `run_all_checks()` — recupera tutti i simboli dal DB, esegue run_checks in parallelo con asyncio.gather
     - Logging structlog: WARNING per severity=warning, ERROR+alert=True per critical
     - `_log_summary()` — report giornaliero con ticker_with_issues, critical_count, warning_count

2. **src/market_data/services/\_\_init\_\_.py**
   - Aggiunto export: `DataQualityMonitor`, `QualityIssue`, `QualityRule`

3. **src/infra/scheduler/jobs.py**
   - Aggiunto `daily_quality_check()` job asincrono che istanzia `DataQualityMonitor()` e chiama `run_all_checks()`

4. **src/infra/scheduler/scheduler.py**
   - Registrato job `daily_quality_check` con `CronTrigger(hour=6, minute=0, timezone=UTC)`

5. **tests/unit/market_data/test_quality_monitor.py** (26 test — tutti PASSED)
   - 4 classi per test delle regole (positive_prices, no_large_gaps, daily_change_lt50, positive_volume)
   - Test DataQualityMonitor: run_checks con dati OK/KO/vuoti, run_all_checks multi-ticker
   - Test job scheduler (daily_quality_check)
   - Test completezza DEFAULT_RULES

Test results: **495/495 PASSED** (26 nuovi test aggiunti, zero regressioni, +0 failed)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/, backend/src/infra/cache/, backend/src/market_data/services/quality_monitor.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 3.9
Area: market_data / shared
Fase: Phase 3 — Observability
Dipendenze: ✅ TASK 3.8 (Complete)

## TASK 3.9: Data Lineage Tracking ✅ COMPLETATO

**Status**: ✅ COMPLETATO — 515/515 PASSED (20 nuovi test, zero regressioni)

### Acceptance Criteria

- [x] `DataSource` enum con from_legacy() per backward-compat con "yahoo" → "yahoo_finance"
- [x] `LineageTracked` mixin con 4 colonne: data_source, source_timestamp, ingestion_timestamp, quality_score
- [x] `compute_quality_score()` (freshness 0.6 + completeness 0.4, clamp 0–1)
- [x] `MarketData(LineageTracked, Base)` — eredita mixin, 3 colonne inline rimosse
- [x] `source_timestamp` aggiunto (nuovo campo, nullable)
- [x] `ingested_at` rinominato → `ingestion_timestamp`
- [x] Migrazione Alembic `a3b5c7d9e1f0` (offline-only, docstring documentato)
- [x] Repository `MarketDataRow` accetta `source_timestamp` opzionale
- [x] `market_data_service._store_price_data` usa `DataSource.YAHOO_FINANCE.value` + `source_timestamp`
- [x] `MarketDataLineageSchema` (Pydantic) in `src/market_data/schemas/lineage.py`
- [x] `GET /api/market/history/{ticker}?include_lineage=true` restituisce campi lineage
- [x] `quality_monitor.py` importa `DataSource` (TASK 3.9 alignment)
- [x] 20 unit test in `tests/unit/shared/test_lineage.py` — tutti PASSED

### File modificati / creati

| File | Azione | Note |
|------|--------|------|
| `src/shared/domain/lineage.py` | **CREATO** | `DataSource` enum, `LineageTracked` mixin, `compute_quality_score()` |
| `src/shared/domain/__init__.py` | MODIFICATO | Export `DataSource`, `LineageTracked` |
| `src/market_data/domain/market_data.py` | MODIFICATO | Aggiunto mixin, rimossi 3 campi inline, import puliti |
| `src/market_data/repositories/market_data_repository.py` | MODIFICATO | `MarketDataRow` + `source_timestamp`; `ingested_at` → `ingestion_timestamp` in INSERT/ON CONFLICT |
| `src/market_data/services/market_data_service.py` | MODIFICATO | `DataSource.YAHOO_FINANCE.value` + `source_timestamp=pd.timestamp` |
| `src/market_data/services/quality_monitor.py` | MODIFICATO | Import `DataSource`, aggiornato docstring |
| `src/market_data/schemas/lineage.py` | **CREATO** | `MarketDataLineageSchema` Pydantic |
| `src/market_data/schemas/__init__.py` | MODIFICATO | Export `MarketDataLineageSchema` |
| `src/market_data/api/routes.py` | MODIFICATO | `include_lineage: bool` param, `HistoricalPricePoint.lineage` field |
| `alembic/versions/a3b5c7d9e1f0_add_lineage_source_timestamp.py` | **CREATO** | Rename ingested_at→ingestion_timestamp + add source_timestamp |
| `tests/unit/shared/test_lineage.py` | **CREATO** | 20 unit test (DataSource, compute_quality_score, MarketData mixin) |

### Test eseguiti

```
tests/unit/shared/test_lineage.py — 20 PASSED
  TestDataSourceFromLegacy (8 test): from_legacy mapping; case insensitive; str mixin
  TestComputeQualityScore (7 test): fresh/stale/missing_volume/missing_ohlc/no_ts/clamped/type
  TestMarketDataInheritsLineage (5 test): issubclass, 4 fields, no ingested_at, source_timestamp nullable, compute_quality_score callable

Full suite: 515/515 PASSED (22.60s)
```