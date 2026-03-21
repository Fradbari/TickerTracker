# Docs

ID: TASK 5.1
Area: ci-cd
Fase: MVP
Dipendenze: -

## TASK 5.1: Setup Test Framework Backend

**Descrizione:** Configurare framework testing per backend Python.

**Microstep:**

1. Verificare dipendenze: pytest, pytest-asyncio, pytest-cov, httpx
2. Creare file [`backend/tests/conftest.py`](../backend/tests/conftest.py)
3. Configurare fixture per database test (PostgreSQL in container o SQLite in-memory)
4. Configurare fixture per client HTTP (TestClient async)
5. Configurare fixture per mock services (Yahoo, Drive)
6. Creare cartelle: [`tests/unit/`](../backend/tests/unit), [`tests/integration/`](../backend/tests/integration), [`tests/e2e/`](../backend/tests/e2e)
7. Configurare [`pytest.ini`](../backend/pytest.ini) con markers (unit, integration, e2e)
8. Configurare coverage minima 80%

**Acceptance Criteria:**

- [ ] `pytest tests/unit` esegue test unitari
- [ ] `pytest tests/integration` esegue test con DB
- [ ] Database test isolato da produzione
- [ ] Coverage report generato

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/tests/conftest.py, pytest tests/integration, pytest tests/unit, tests/e2e/, tests/integration/, tests/unit/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.2
Area: ci-cd
Fase: MVP
Dipendenze: TASK 5.1

## TASK 5.2: Scrivere Unit Test per Value Objects

**Descrizione:** Test completi per Money, Percentage, PriceTarget.

**Microstep:**

1. Creare file [`backend/tests/unit/shared/test_money.py`](../backend/tests/unit/shared/test_money.py)
2. Testare creazione Money con vari input (Decimal, int, float, string)
3. Testare operazioni aritmetiche (add, sub, mul)
4. Testare errore su currency mismatch
5. Testare round con vari decimali
6. Testare serializzazione/deserializzazione
7. Creare file [`backend/tests/unit/shared/test_percentage.py`](../backend/tests/unit/shared/test_percentage.py)
8. Testare from_basis_points
9. Testare apply_to Money
10. Creare file [`backend/tests/unit/shared/test_price_target.py`](../backend/tests/unit/shared/test_price_target.py)
11. Testare validazioni LONG e SHORT
12. Testare risk_reward_ratio

**Acceptance Criteria:**

- [x] Coverage 100% sui value objects
- [x] Edge cases coperti (zero, negativo, overflow)
- [x] Errori attesi sollevano eccezioni corrette

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/tests/unit/shared/test_money.py, backend/tests/unit/shared/test_percentage.py, backend/tests/unit/shared/test_price_target.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.3
Area: ci-cd
Fase: MVP
Dipendenze: TASK 5.1

## TASK 5.3: Scrivere Unit Test per EstimateService

**Descrizione:** Test unitari per logica business stime.

**Microstep:**

1. Creare file [`backend/tests/unit/estimates/test_estimate_service.py`](../backend/tests/unit/estimates/test_estimate_service.py)
2. Creare mock per EstimateRepository, MarketDataProvider, EventPublisher
3. Testare create_estimate: calcolo corretto target/stop da percentuali
4. Testare create_estimate: recupero prezzo corrente
5. Testare create_estimate: pubblicazione evento
6. Testare close_estimate: calcolo P&L corretto
7. Testare check_and_update_targets: rilevamento hit target
8. Testare check_and_update_targets: rilevamento hit stop
9. Testare errori: ticker non trovato, prezzo non disponibile

**Acceptance Criteria:**

- [x] Ogni metodo pubblico testato
- [x] Mock verificano chiamate corrette
- [x] Scenari errore coperti
- [x] No dipendenze esterne nei test

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/tests/unit/estimates/test_estimate_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.4
Area: ci-cd
Fase: MVP
Dipendenze: TASK 5.1

## TASK 5.4: Scrivere Integration Test per API Estimates

**Descrizione:** Test integrazione per endpoint estimates.

**Microstep:**

1. Creare file [`backend/tests/integration/test_estimates_api.py`](../backend/tests/integration/test_estimates_api.py)
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

### Istruzioni per LLM
- Non modificare file fuori da [backend/tests/integration/test_estimates_api.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.5
Area: ci-cd
Fase: MVP
Dipendenze: TASK 5.1

## TASK 5.5: Implementare Property-Based Testing per P&L

**Descrizione:** Test basati su proprietà per calcoli finanziari.

**Microstep:**

1. Installare dipendenza `hypothesis`
2. Creare file [`backend/tests/properties/test_pnl_calculations.py`](../backend/tests/properties/test_pnl_calculations.py)
3. Testare proprietà: P&L long = -P&L short (simmetria)
4. Testare proprietà: P&L = 0 quando entry == exit
5. Testare proprietà: P&L chain è additivo (entry->A->B = (entry->A) + (A->B))
6. Testare proprietà: P&L% * entry_price ≈ P&L assoluto
7. Generare prezzi con strategies Decimal nel range ragionevole
8. Aggiungere esempi espliciti per edge cases

**Acceptance Criteria:**

- [ ] Proprietà verificate per migliaia di input random
- [ ] Nessun errore di arrotondamento
- [ ] Edge cases espliciti documentati

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/tests/properties/test_pnl_calculations.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.6
Area: ci-cd
Fase: Fase 2
Dipendenze: -

## TASK 5.6: Setup Test Framework Frontend

**Descrizione:** Configurare framework testing per frontend React.

**Microstep:**

1. Installare dipendenze: vitest, @testing-library/react, @testing-library/jest-dom, msw
2. Configurare [`vitest.config.ts`](../frontend/vitest.config.ts)
3. Configurare [`setupTests.ts`](../frontend/src/setupTests.ts) con jest-dom matchers
4. Configurare MSW per mock API
5. Creare cartelle: [`__tests__/unit/`](../frontend/src/__tests__/unit), [`__tests__/components/`](../frontend/src/__tests__/components), [`__tests__/integration/`](../frontend/src/__tests__/integration)
6. Creare helper per render con providers (QueryClient, Router, i18n)

**Acceptance Criteria:**

- [ ] `npm run test` esegue test
- [ ] MSW intercetta chiamate API
- [ ] Helper render semplifica setup test
- [ ] Coverage report generato

---

### Istruzioni per LLM
- Non modificare file fuori da [__tests__/components/, __tests__/integration/, __tests__/unit/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.7
Area: ci-cd
Fase: Fase 2
Dipendenze: TASK 5.6

## TASK 5.7: Scrivere Component Test per EstimateForm

**Descrizione:** Test componente per form stime.

**Microstep:**

1. Creare file [`frontend/src/features/estimates/__tests__/EstimateForm.test.tsx`](../frontend/src/features/estimates/__tests__/EstimateForm.test.tsx)
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

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/estimates/__tests__/EstimateForm.test.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.8
Area: ci-cd
Fase: Fase 2
Dipendenze: TASK 5.1, TASK 5.6

## TASK 5.8: Setup E2E Test con Playwright

**Descrizione:** Configurare test end-to-end con Playwright.

**Microstep:**

1. Installare `@playwright/test`
2. Configurare [`playwright.config.ts`](../playwright.config.ts)
3. Configurare webServer per avviare backend e frontend
4. Creare file [`e2e/setup/global-setup.ts`](../e2e/setup/global-setup.ts) per seed database test
5. Creare test: flusso creazione stima end-to-end in [`e2e/estimates.spec.ts`](../e2e/estimates.spec.ts)
6. Creare test: flusso visualizzazione portfolio in [`e2e/portfolio.spec.ts`](../e2e/portfolio.spec.ts)
7. Creare test: flusso chat AI in [`e2e/chat.spec.ts`](../e2e/chat.spec.ts)
8. Configurare screenshot/video su failure
9. Configurare esecuzione su CI

**Acceptance Criteria:**

- [ ] Test eseguono contro app completa
- [ ] Database seeded con dati test
- [ ] Screenshot catturati su failure
- [ ] Test passano in CI

---

### Istruzioni per LLM
- Non modificare file fuori da [@playwright/test, e2e/setup/global-setup.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.9
Area: ci-cd
Fase: Fase 2
Dipendenze: TASK 5.4

## TASK 5.9: Implementare Chaos Testing

**Descrizione:** Test di resilienza per scenari di fallimento.

**Microstep:**

1. Creare file [`backend/tests/chaos/test_resilience.py`](../backend/tests/chaos/test_resilience.py)
2. Testare: Yahoo API timeout -> usa cache
3. Testare: Yahoo API errore -> usa cache stale
4. Testare: Database pool esaurito -> 503 graceful
5. Testare: Drive sync fallisce parzialmente -> dati esistenti non corrotti
6. Testare: Rete intermittente -> retry funziona
7. Aggiungere marker pytest `@pytest.mark.chaos`
8. Documentare scenari e risultati attesi

**Acceptance Criteria:**

- [ ] Sistema non crasha su fallimenti esterni
- [ ] Fallback a cache funziona
- [ ] Errori restituiti sono informativi
- [ ] Dati non corrotti da fallimenti parziali

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/tests/chaos/test_resilience.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.10
Area: ci-cd
Fase: MVP
Dipendenze: TASK 5.4, TASK 5.7

## TASK 5.10: Configurare CI Pipeline (GitHub Actions)

**Descrizione:** Creare pipeline CI completa.

**Microstep:**

1. Creare file [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
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
- [ ] Tempo esecuzione < 10 minuti

---

### Istruzioni per LLM
- Non modificare file fuori da [.github/workflows/ci.yml] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.11
Area: ci-cd
Fase: MVP
Dipendenze: TASK 5.10

## TASK 5.11: Configurare CD Pipeline (Deploy)

**Descrizione:** Estendere pipeline per deploy automatico.

**Microstep:**

1. Estendere [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) o creare [`cd.yml`](../.github/workflows/cd.yml)
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

### Istruzioni per LLM
- Non modificare file fuori da [.github/workflows/ci.yml, cd.yml] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.15
Area: docs
Fase: MVP
Dipendenze: -

## TASK 5.15: Creare Runbook Operativo

**Descrizione:** Documentare procedure operative e troubleshooting.

**Microstep:**

1. Creare file [`docs/runbook/README.md`](../docs/runbook/README.md) con indice
2. Creare [`docs/runbook/startup-shutdown.md`](../docs/runbook/startup-shutdown.md): procedure avvio/stop servizi
3. Creare [`docs/runbook/monitoring.md`](../docs/runbook/monitoring.md): dove guardare metriche, log, alert
4. Creare [`docs/runbook/database-recovery.md`](../docs/runbook/database-recovery.md): procedura restore da backup
5. Creare [`docs/runbook/yahoo-outage.md`](../docs/runbook/yahoo-outage.md): azioni durante outage Yahoo
6. Creare [`docs/runbook/drive-sync-issues.md`](../docs/runbook/drive-sync-issues.md): troubleshooting sync
7. Creare [`docs/runbook/scaling.md`](../docs/runbook/scaling.md): come scalare servizi
8. Includere comandi copia-incolla per ogni procedura
9. Includere contatti e escalation path

**Acceptance Criteria:**

- [ ] Ogni scenario comune documentato
- [ ] Comandi eseguibili direttamente
- [ ] RTO/RPO definiti per ogni scenario
- [ ] Rivisto da secondo paio di occhi

---

### Istruzioni per LLM
- Non modificare file fuori da [docs/runbook/README.md, docs/runbook/database-recovery.md, docs/runbook/drive-sync-issues.md, docs/runbook/monitoring.md, docs/runbook/scaling.md, docs/runbook/startup-shutdown.md, docs/runbook/yahoo-outage.md] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.16
Area: docs
Fase: MVP
Dipendenze: -

## TASK 5.16: Documentare API con OpenAPI

**Descrizione:** Verificare e arricchire documentazione OpenAPI.

**Microstep:**

1. Verificare che tutti gli endpoint abbiano docstring
2. Aggiungere esempi request/response a ogni endpoint
3. Documentare tutti i codici errore possibili
4. Aggiungere descrizioni ai parametri query/path
5. Configurare metadata OpenAPI (title, version, description, contact)
6. Verificare schema generato su [`/docs`](../docs)
7. Esportare [`openapi.json`](../openapi.json) per uso esterno
8. Creare pagina docs custom se necessario

**Acceptance Criteria:**

- [ ] /docs mostra documentazione completa
- [ ] Esempi funzionanti per ogni endpoint
- [ ] Errori documentati
- [ ] Schema esportabile

---

### Istruzioni per LLM
- Non modificare file fuori da [repo root] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 5.17
Area: docs
Fase: MVP
Dipendenze: TASK 2.21, TASK 2.22

## TASK 5.17: Creare Script Migrazione Dati v2.4 → v3.0

**Descrizione:** Script per migrare dati da versione legacy TickerTracker v2.4 a v3.0.

**Microstep:**

1. Creare file [`backend/scripts/migrate_from_legacy.py`](../backend/scripts/migrate_from_legacy.py)
2. Implementare funzione `connect_to_drive()`: autenticazione Google Drive
3. Implementare funzione `download_legacy_data()`: scarica JSON e CSV da Drive
4. Implementare funzione `parse_legacy_json(content)`: parsing stime legacy da backup JSON
5. Implementare funzione `parse_legacy_history(content)`: parsing prezzi storici da CSV
6. Implementare funzione `transform_to_new_schema(legacy_data)`: mapping campi legacy → v3.0
7. Implementare funzione `validate_transformed_data(data)`: validazione dati post-trasformazione
8. Implementare funzione `import_to_database(data)`: insert nel nuovo DB PostgreSQL
9. Implementare funzione `verify_migration()`: confronto conteggi e totali legacy vs migrated
10. Creare report migrazione con statistiche (success/errors, record migrati, anomalie)

**Acceptance Criteria:**

- [ ] Script eseguibile da riga di comando: `python backend/scripts/migrate_from_legacy.py`
- [ ] Tutti i dati legacy importati correttamente (estimates + market_data)
- [ ] Validazione previene import dati corrotti
- [ ] Report finale mostra: # stime migrate, # errori, # warning
- [ ] Idempotente: rilanciabile senza duplicati (check via ticker+date)
- [ ] Test con fixture dati legacy reali in [`tests/fixtures/legacy/`](../backend/tests/fixtures/legacy)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/scripts/migrate_from_legacy.py, tests/fixtures/legacy/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.
- Il mapping legacy deve preservare: ticker, direzione LONG/SHORT, prezzi entry/target/stop, date apertura/chiusura, PnL realizzato.