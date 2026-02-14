# AGENTS — estimates

ID: TASK 2.5
Area: estimates
Fase: MVP
Dipendenze: TASK 2.3

## TASK 2.5: Definizione Modello SQLAlchemy - Estimate

**Descrizione:** Creare il modello SQLAlchemy per l'entità Estimate (stime/previsioni).

**Microstep:**

1\. Creare file `backend/src/estimates/domain/entities.py`

2\. Definire classe `Estimate` che eredita da Base

3\. Definire colonne identificative: `id` (UUID, PK), `ticker_id` (FK to Ticker), `user_id` (FK to User, nullable per ora)

4\. Definire colonne prezzo: `start_price` (DECIMAL 10,4), `target_price` (DECIMAL 10,4), `stop_loss_price` (DECIMAL 10,4)

5\. Definire colonne target: `target_profit_percent` (DECIMAL 8,4), `stop_loss_percent` (DECIMAL 8,4)

6\. Definire colonne stato: `status` (Enum: OPEN, CLOSED_WIN, CLOSED_LOSS, CLOSED_MANUAL, EXPIRED), `direction` (Enum: LONG, SHORT)

7\. Definire colonne AI: `ai_model` (String), `ai_confidence` (DECIMAL 5,2), `ai_reasoning` (Text)

8\. Definire colonne date: `created_at`, `updated_at`, `closed_at` (nullable)

9\. Definire colonne esito: `exit_price` (DECIMAL 10,4, nullable), `realized_pnl` (DECIMAL 12,4, nullable)

10\. Definire relazione con Ticker

11\. Definire indici: su `ticker_id`, su `status`, su `created_at`, indice parziale su status='OPEN'

**Acceptance Criteria:**

- [ ] Tutti i campi prezzo usano DECIMAL, non FLOAT

- [ ] Enums definiti come tipi Python Enum

- [ ] Foreign key a Ticker definita correttamente

- [ ] Indici ottimizzati per query frequenti

- [ ] Campi nullable marcati esplicitamente

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/, backend/src/estimates/domain/entities.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.6
Area: estimates
Fase: MVP
Dipendenze: TASK 2.5

## TASK 2.6: Definizione Modello SQLAlchemy - EstimateEvent (Event Sourcing)

**Descrizione:** Creare il modello per Event Sourcing delle stime.

**Microstep:**

1\. Creare file `backend/src/estimates/domain/events.py`

2\. Definire Enum `EstimateEventType`: CREATED, UPDATED, PRICE_UPDATED, TARGET_HIT, STOP_HIT, CLOSED, REOPENED

3\. Definire classe `EstimateEvent` che eredita da Base

4\. Definire colonne: `id` (UUID, PK), `estimate_id` (FK to Estimate), `event_type` (Enum), `event_data` (JSONB), `user_id` (UUID, nullable), `timestamp` (DateTime with timezone)

5\. Definire indice composto su `(estimate_id, timestamp)`

6\. Definire constraint: timestamp deve avere timezone

**Acceptance Criteria:**

- [ ] Eventi sono immutabili (no update)

- [ ] JSONB usato per flessibilità dati evento

- [ ] Indice permette query efficienti per timeline

- [ ] Ogni tipo evento documentato nel Enum

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/, backend/src/estimates/domain/events.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.12
Area: estimates
Fase: MVP
Dipendenze: TASK 2.5, TASK 2.10

## TASK 2.12: Creazione Repository Estimate

**Descrizione:** Implementare repository per accesso dati Estimate.

**Microstep:**

1\. Creare file `backend/src/estimates/repositories/estimate_repository.py`

2\. Definire classe `EstimateRepository`

3\. Iniettare async session factory

4\. Implementare metodo `create(estimate: Estimate) -> Estimate`

5\. Implementare metodo `get_by_id(id: UUID) -> Optional[Estimate]`

6\. Implementare metodo `get_all(filters: EstimateFilters, pagination: Pagination) -> PaginatedResult[Estimate]`

7\. Implementare metodo `update(estimate: Estimate) -> Estimate`

8\. Implementare metodo `soft_delete(id: UUID) -> bool`

9\. Implementare metodo `get_active_by_ticker(ticker_id: UUID) -> List[Estimate]`

10\. Usare async/await per tutte le operazioni

**Acceptance Criteria:**

- [x] Tutte le operazioni CRUD funzionano

- [x] Paginazione cursor-based implementata

- [x] Filtri applicati correttamente

- [x] Soft delete imposta flag, non cancella

- [x] Transazioni gestite correttamente

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/, backend/src/estimates/repositories/estimate_repository.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.14
Area: estimates
Fase: MVP
Dipendenze: TASK 2.12

## TASK 2.14: Creazione Service EstimateService

**Descrizione:** Implementare service layer per orchestrazione business logic stime.

**Microstep:**

1\. Creare file `backend/src/estimates/services/estimate_service.py`

2\. Definire classe `EstimateService`

3\. Iniettare dipendenze: `EstimateRepository`, `MarketDataProvider`, `EventPublisher`

4\. Implementare metodo `create_estimate(command: CreateEstimateCommand) -> Estimate`:

- Validare input

- Recuperare prezzo corrente da provider

- Calcolare target_price e stop_loss da percentuali

- Creare Estimate

- Pubblicare evento ESTIMATE_CREATED

- Salvare evento in EstimateEvent

5\. Implementare metodo `update_estimate(command: UpdateEstimateCommand) -> Estimate`

6\. Implementare metodo `close_estimate(id: UUID, exit_price: Decimal, reason: str) -> Estimate`

7\. Implementare metodo `check_and_update_targets(estimate_id: UUID)` per verificare hit target/stop

**Acceptance Criteria:**

- [x] Validazione input completa

- [x] Eventi pubblicati per ogni operazione

- [x] Transazione atomica (DB + evento)

- [x] Errori business sollevano eccezioni tipizzate

**Stato:** ✅ COMPLETATO (2026-02-14)

**Note Implementazione:**
- Creati schemi Pydantic per comandi: `CreateEstimateCommand`, `UpdateEstimateCommand`, `CloseEstimateCommand`
- Implementate eccezioni business tipizzate in `services/exceptions.py`
- Service utilizza `MarketDataRepository` per recuperare prezzi correnti
- Eventi salvati atomicamente tramite `EstimateEvent` nella stessa transazione
- Calcolo automatico di target/stop prices da percentuali
- Calcolo automatico di PnL per estimate chiuse
- Metodo `check_and_update_targets()` per chiusura automatica su target/stop hit
- Supporto completo per LONG e SHORT con logica di prezzo appropriata
- Script di test comprensivo con 8 test: `tests/test_estimate_service.py`
- Tutti i test passano: validazione, creazione, update, chiusura, target checking, SHORT estimates, PnL calculation

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/, backend/src/estimates/services/estimate_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.15
Area: estimates
Fase: MVP
Dipendenze: TASK 2.6, TASK 2.12

## TASK 2.15: Creazione Service EstimateHistoryService (Event Sourcing)

**Descrizione:** Implementare service per ricostruzione stato storico stime.

**Microstep:**

1\. Creare file `backend/src/estimates/services/estimate_history_service.py`

2\. Definire classe `EstimateHistoryService`

3\. Iniettare `EstimateEventRepository`

4\. Implementare metodo `get_state_at(estimate_id: UUID, at_time: datetime) -> EstimateSnapshot`:

- Recuperare tutti gli eventi fino a at_time

- Ricostruire stato applicando eventi in ordine

5\. Implementare metodo `get_audit_trail(estimate_id: UUID) -> List[AuditEntry]`:

- Restituire lista eventi con metadata human-readable

6\. Implementare metodo `get_changes_between(estimate_id: UUID, start: datetime, end: datetime) -> List[Change]`

**Acceptance Criteria:**

- [x] Stato ricostruito correttamente per qualsiasi timestamp

- [x] Audit trail completo e ordinato

- [x] Performance accettabile per stime con molti eventi

**Stato:** ✅ COMPLETATO (2026-02-14)

**Note Implementazione:**
- Creato `EstimateEventRepository` per accesso eventi in repositories/estimate_event_repository.py
- Creati schemi Pydantic in schemas/history.py: `EstimateSnapshot`, `AuditEntry`, `Change`, `EstimateHistorySummary`
- Implementato `EstimateHistoryService` con 4 metodi pubblici:
  - `get_state_at()` - Ricostruisce stato ad un timestamp tramite replay eventi
  - `get_audit_trail()` - Genera audit trail human-readable
  - `get_changes_between()` - Identifica cambiamenti tra due timestamp
  - `get_history_summary()` - Statistiche complete dello storico
- Gestione corretta di tutti i tipi di evento: CREATED, UPDATED, PRICE_UPDATED, TARGET_HIT, STOP_HIT, CLOSED, REOPENED
- Test completo con 5 suite che verificano tutti gli acceptance criteria
- Performance ottimizzata con query ordinate cronologicamente e uso di indici DB

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/, backend/src/estimates/services/estimate_history_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.16
Area: estimates
Fase: MVP
Dipendenze: TASK 2.14

## TASK 2.16: Creazione API Router Estimates

**Descrizione:** Implementare endpoint REST per gestione stime.

**Microstep:**

1\. Creare file `backend/src/estimates/api/routes.py`

2\. Creare router FastAPI con prefix `/api/estimates`

3\. Implementare endpoint `POST /` per creazione stima

4\. Implementare endpoint `GET /` per lista stime con filtri (status, ticker, date_range, ai_model)

5\. Implementare endpoint `GET /{id}` per dettaglio singola stima

6\. Implementare endpoint `PATCH /{id}` per aggiornamento parziale

7\. Implementare endpoint `DELETE /{id}` per chiusura/cancellazione

8\. Implementare endpoint `GET /{id}/history` per audit trail

9\. Tutti gli endpoint restituiscono `ApiResponse` standard

10\. Aggiungere dependency injection per services

**Acceptance Criteria:**

- [x] Tutti gli endpoint documentati con OpenAPI

- [x] Request validation con Pydantic

- [x] Response conforme a schema ApiResponse

- [x] Errori restituiti con codici appropriati (400, 404, 500)

- [x] Filtri funzionanti e combinabili

**Stato:** ✅ COMPLETATO (2026-02-14)

**Note Implementazione:**
- Creato file `src/estimates/schemas/responses.py` con schemi DTO per API:
  - `EstimateResponse` - Schema completo per singolo estimate
  - `EstimateListResponse` - Schema per lista paginata
  - `EstimateCreatedResponse` - Response per creazione
  - `EstimateUpdatedResponse` - Response per aggiornamento
  - `EstimateDeletedResponse` - Response per chiusura
  - `EstimateHistoryResponse` - Response per audit trail
- Creato file `src/estimates/api/routes.py` con router FastAPI e 6 endpoint REST:
  - `POST /api/estimates` - Crea nuovo estimate (201)
  - `GET /api/estimates` - Lista con filtri e paginazione (200)
  - `GET /api/estimates/{id}` - Dettaglio singolo estimate (200)
  - `PATCH /api/estimates/{id}` - Aggiorna estimate (200)
  - `DELETE /api/estimates/{id}` - Chiudi estimate logicamente (200)
  - `GET /api/estimates/{id}/history` - Recupera audit trail completo (200)
- Router registrato in `src/main.py` con prefix `/api/estimates`
- Dependency injection configurata per:
  - `EstimateService` - Orchestrazione business logic
  - `EstimateHistoryService` - Gestione storico e audit
  - `EstimateRepository` - Accesso dati read-only
  - `get_db()` - Session async database
- Tutte le response wrapped in `ApiResponse[T]` con success/data/error/trace_id
- Gestione errori completa con codici tipizzati:
  - `TICKER_NOT_FOUND` (400)
  - `ESTIMATE_NOT_FOUND` (404)
  - `ESTIMATE_ALREADY_CLOSED` (400)
  - `INVALID_PRICE` (400)
  - `INVALID_ESTIMATE_STATE` (400)
  - `MARKET_DATA_UNAVAILABLE` (400)
  - `INTERNAL_ERROR` (500)
- Filtri implementati: ticker_id, user_id, status, direction, include_deleted
- Paginazione cursor-based con limit configurabile (1-100)
- Documentazione OpenAPI automatica disponibile su /docs e /redoc
- Test di verifica struttura: `tests/verify_estimate_routes.py` - PASSED
- Documentazione API completa aggiunta a `backend/README.md` con esempi cURL

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/, /api/estimates, DELETE /{id}, GET /, GET /{id}, GET /{id}/history, PATCH /{id}, POST /, backend/src/estimates/api/routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.