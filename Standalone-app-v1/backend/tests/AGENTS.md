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

- Import + export di backup JSON non perde nessuna stima né cambia i valori chiave.
- Import + export di CSV storico produce gli stessi valori OHLC e date.
- I file generati dal nuovo SyncService sono ancora leggibili dallo script HTML+GAS originale.
- I test e2e possono essere eseguiti localmente con pytest senza dipendenze da Drive reale (mocks/fixtures).

Questi task coprono il nuovo Sync Engine con Google Drive e garantiscono la piena retro‑compatibilità con i file legacy (backup JSON e History_*.csv) tramite test E2E dedicati.

---

### Istruzioni per LLM
- Non modificare file fuori da [tests/e2e/, backend/tests/e2e/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.