# AGENTS — sync

ID: TASK 2.8
Area: sync
Fase: Fase 2
Dipendenze: TASK 2.3

## TASK 2.8: Definizione Modello SQLAlchemy - SyncJob

**Descrizione:** Creare modello per tracciare i job di sincronizzazione con Google Drive.

**Microstep:**

1\. Creare file `backend/src/sync/domain/entities.py`

2\. Definire Enum `SyncJobType`: INITIAL_IMPORT, DAILY_HISTORY_UPDATE, ON_ESTIMATE_SAVE, MANUAL_SYNC

3\. Definire Enum `SyncJobStatus`: PENDING, RUNNING, COMPLETED, FAILED, PARTIAL

4\. Definire classe `SyncJob`: `id` (UUID), `job_type` (Enum), `status` (Enum), `started_at`, `finished_at` (nullable), `error_message` (Text, nullable), `filename` (String), `checksum_before` (String), `checksum_after` (String), `records_processed` (Integer), `records_failed` (Integer)

5\. Definire indice su `started_at` per ordinamento cronologico

**Acceptance Criteria:**

- [ ] Tutti i tipi di job rappresentati

- [ ] Stati permettono tracking completo del ciclo di vita

- [ ] Checksum permette verifica integrità

- [ ] Contatori permettono monitoraggio successo/fallimento

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/sync/, backend/src/sync/domain/entities.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.21
Area: sync
Fase: MVP
Dipendenze: TASK 2.20

## TASK 2.21: Implementazione CSV Parser Legacy

**Descrizione:** Creare parser bidirezionale per formato CSV legacy TickerTracker.

**Microstep:**

1\. Creare file `backend/src/sync/infra/csv_parser.py`

2\. Definire classe `LegacyCsvParser`

3\. Implementare metodo `parse_estimates_csv(content: bytes) -> List[LegacyEstimateRow]`:

- Gestire encoding UTF-8 con BOM

- Mappare le 120+ colonne del formato legacy

- Gestire colonne vuote o mancanti senza crash

- Restituire lista di dataclass con dati parsed

4\. Implementare metodo `export_estimate_to_csv_row(estimate: Estimate, fundamentals: dict) -> str`:

- Mappare dati puliti nel formato "piatto" legacy

- Gestire valori None

5\. Implementare metodo `parse_history_csv(content: bytes) -> List[LegacyHistoryRow]`

6\. Implementare metodo `export_history_to_csv(data: List[MarketData]) -> bytes`

7\. Creare file di mapping colonne per documentazione

**Acceptance Criteria:**

- [ ] Parse gestisce file reali legacy senza errori

- [ ] Round-trip parse -> export -> parse produce stessi dati

- [ ] Colonne mancanti hanno default sensati

- [ ] Encoding gestito correttamente

Nota: la retro‑compatibilità del formato legacy è validata dai test E2E del TASK 2.23.

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/sync/, backend/src/sync/infra/csv_parser.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.22
Area: sync
Fase: MVP
Dipendenze: TASK 2.21

## TASK 2.22: Implementazione Sync Service

**Descrizione:** Implementare service per sincronizzazione bidirezionale con Drive.

**Microstep:**

1\. Creare file `backend/src/sync/services/sync_service.py`

2\. Definire classe `SyncService`

3\. Iniettare: `GoogleDriveClient`, `LegacyCsvParser`, `EstimateRepository`, `MarketDataRepository`, `SyncJobRepository`

4\. Implementare metodo `run_initial_import()`:

- Scaricare file JSON backup e CSV history da Drive

- Parsare e importare stime nel DB

- Creare SyncJob con risultato

5\. Implementare metodo `sync_estimate_to_drive(estimate_id: UUID)`:

- Recuperare stima e fundamentals

- Esportare in formato CSV

- Aggiornare file Drive con pattern file temporaneo

- Calcolare e salvare checksum

6\. Implementare metodo `run_daily_history_sync()`:

- Per ogni ticker attivo, aggiornare file History_*.csv su Drive

7\. Implementare logica di conflict resolution: last-writer-wins con logging conflitti

**Acceptance Criteria:**

- [ ] Import non crea duplicati (idempotente)

- [ ] Export usa file temporaneo per atomicità

- [ ] Checksum verificato dopo ogni operazione

- [ ] Conflitti loggati per review manuale

Nota: la retro‑compatibilità del formato legacy è validata dai test E2E del TASK 2.23.

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/sync/, backend/src/sync/services/sync_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.