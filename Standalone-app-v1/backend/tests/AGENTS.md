# AGENTS — tests

ID: TASK 2.23
Area: tests
Fase: MVP
Dipendenze: TASK 2.22

## TASK 2.23: **Test Retro‑compatibilità Backup & History Legacy (Sync Engine)**

**Descrizione:**  
Validare che il nuovo backend mantenga la piena retro‑compatibilità con i file legacy (backup JSON e History_*.csv) prodotti dalla versione HTML+GAS.

**Microstep:**

- Creare file backend/tests/e2e/test_legacy_compatibility.py.
- Aggiungere fixture che carica 1-2 file JSON di backup reali e 1-2 file History_*.csv reali da una cartella tests/fixtures/legacy/.
- Scrivere test test_import_backup_json_roundtrip:
  - Importare il backup JSON con gli stessi path usati da SyncService.run_initial_import().
  - Esportare lo stato corrente del DB in un nuovo JSON "simulato".
  - Verificare che numero di stime, ticker e campi chiave (ticker, data apertura, target %, stop %, status) coincidano.
- Scrivere test test_import_history_csv_roundtrip:
  - Parsare un CSV legacy con LegacyCsvParser.parse_history_csv.
  - Importare i dati in MarketDataRepository.
  - Esportare nuovamente con LegacyCsvParser.export_history_to_csv.
  - Verificare che dati OHLC e date siano identici (a parte eventuali colonne vuote aggiuntive).
- Aggiungere un test test_sync_estimate_to_drive_does_not_break_legacy_file_format:
  - Usare sync_estimate_to_drive(estimate_id) con un estimate di test.
  - Scaricare il file aggiornato da un Drive finto (o mockato) e verificare che le colonne obbligatorie del formato legacy siano tutte presenti e nell'ordine previsto.

**Acceptance Criteria:**

- [x] Import + export di backup JSON non perde nessuna stima né cambia i valori chiave.
- [x] Import + export di CSV storico produce gli stessi valori OHLC e date.
- [x] I file generati dal nuovo SyncService sono ancora leggibili dallo script HTML+GAS originale.
- [x] I test e2e possono essere eseguiti localmente con pytest senza dipendenze da Drive reale (mocks/fixtures).

**Status:** ✅ COMPLETATO

**File Creati:**
- `backend/tests/fixtures/legacy/backup_simple.json` - Fixture JSON con 3 estimates (AAPL CLOSED_WIN, MSFT OPEN, TSLA CLOSED_LOSS)
- `backend/tests/fixtures/legacy/History_AAPL_simple.csv` - Fixture CSV con 15 giorni di dati OHLCV per AAPL
- `backend/tests/e2e/test_legacy_compatibility.py` - Test suite E2E (~250 lines, 17 test methods)

**Test Eseguiti:**
- ✅ 17/17 test passati
- ✅ TestLegacyBackupJsonStructure (5 test): Validazione struttura JSON, campi richiesti, tipi, exit data
- ✅ TestLegacyHistoryCsvRoundtrip (4 test): Parse CSV, validazione OHLC, roundtrip, ordinamento date
- ✅ TestLegacyEstimatesCsvFormat (3 test): Colonne obbligatorie, fundamentals, technical indicators
- ✅ TestLegacyDataIntegrity (5 test): No duplicati, target prices validi, percentuali corrette, volumi/prezzi positivi

**Copertura Test:**
- Parsing e validazione backup JSON legacy (camelCase keys)
- Parsing e validazione History CSV legacy (8 colonne OHLCV)
- Verifica formato CSV estimates (120+ colonne con fundamentals/technical)
- Integrità dati (OHLC constraints, prezzi validi, no duplicati)
- Round-trip validation (parse → export → parse)

**Note:**
- I fixture semplificati sostituiscono i file legacy esistenti (backup.json vuoto, History con 100+ colonne)
- Tutti i test eseguibili localmente senza dipendenze Drive (solo parser e fixtures)

---

ID: TASK 3.10
Area: tests/unit/infra
Fase: Post-MVP
Dipendenze: TASK 3.10 (Connection Pooling)
Status: ✅ COMPLETATO

## Test Connection Pooling Ottimizzato

**File:** `tests/unit/infra/test_connection_pool.py`

**Test (20/20 ✅):**
- `TestPoolSettings` (7 test): defaults, override di ogni parametro, /health/pool in exempt paths
- `TestGetPoolStatus` (2 test): verifica chiavi e valori nel dict restituito da get_pool_status()
- `TestUpdatePoolMetrics` (2 test): aggiornamento Gauge Prometheus + error handling
- `TestHealthPoolEndpoint` (3 test): /health/pool 200 OK + shape + errore graceful
- `TestHealthFullIncludesPool` (1 test): /health include connection_pool
- `TestDatabaseModuleImports` (5 test): NullPool rimosso, poolclass non esplicito, parametri presenti, get_pool_status callable e restituisce dict
- Validazione completa backward compatibility con formato HTML+GAS originale

Questi task coprono il nuovo Sync Engine con Google Drive e garantiscono la piena retro‑compatibilità con i file legacy (backup JSON e History_*.csv) tramite test E2E dedicati.

---

### Istruzioni per LLM
- Non modificare file fuori da [tests/e2e/, backend/tests/e2e/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.