# AGENTS — estimates

ID: TASK 2.4
Area: estimates
Fase: MVP
Dipendenze: TASK 2.3

## TASK 2.4: Definizione Modello SQLAlchemy - Estimate

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

ID: TASK 2.5
Area: estimates
Fase: MVP
Dipendenze: TASK 2.4

## TASK 2.5: Definizione Modello SQLAlchemy - EstimateEvent (Event Sourcing)

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
Dipendenze: TASK 2.4, TASK 2.10

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

- [ ] Tutte le operazioni CRUD funzionano

- [ ] Paginazione cursor-based implementata

- [ ] Filtri applicati correttamente

- [ ] Soft delete imposta flag, non cancella

- [ ] Transazioni gestite correttamente

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

- [ ] Validazione input completa

- [ ] Eventi pubblicati per ogni operazione

- [ ] Transazione atomica (DB + evento)

- [ ] Errori business sollevano eccezioni tipizzate

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/, backend/src/estimates/services/estimate_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.15
Area: estimates
Fase: MVP
Dipendenze: TASK 2.5, TASK 2.12

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

- [ ] Stato ricostruito correttamente per qualsiasi timestamp

- [ ] Audit trail completo e ordinato

- [ ] Performance accettabile per stime con molti eventi

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

- [ ] Tutti gli endpoint documentati con OpenAPI

- [ ] Request validation con Pydantic

- [ ] Response conforme a schema ApiResponse

- [ ] Errori restituiti con codici appropriati (400, 404, 500)

- [ ] Filtri funzionanti e combinabili

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/, /api/estimates, DELETE /{id}, GET /, GET /{id}, GET /{id}/history, PATCH /{id}, POST /, backend/src/estimates/api/routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.