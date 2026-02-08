# AGENTS — market_data

ID: TASK 2.3
Area: market_data
Fase: MVP
Dipendenze: TASK 2.2

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

- Tutta la logica di mercato usa MarketDataProvider e non dipende da yfinance direttamente.
- MarketDataService riceve il provider via dependency injection FastAPI.
- I test possono usare un FakeMarketDataProvider per simulare dati senza chiamate esterne.

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

- Le chiamate ripetute allo stesso endpoint/ticker entro il TTL non generano chiamate esterne aggiuntive.
- In caso di timeout/rate‑limit, il sistema usa il dato in cache se disponibile e non va in errore 500 immediato.
- I test coprono: cache hit, cache miss, fallback a dati stale, backoff su errori.

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/, backend/src/infra/cache/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

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

- [ ] Regole coprono scenari comuni di data corruption

- [ ] Issue loggati con dettagli sufficienti per debug

- [ ] Alert per issue severity=critical

- [ ] Report giornaliero generato

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/, backend/src/infra/cache/, backend/src/market_data/services/quality_monitor.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.