# Gestione Errori Google Drive Sync

**RTO: < 10 min | RPO: Nessuna perdita dati locale**

In caso di fallimento della sincronizzazione verso Google Drive, il sistema è progettato per trattenere permanentemente in locale lo stato (Pending/Failed) affinché non avvenga corruzione dati. Fare riferimento al test di Chaos engineering `test_drive_sync_partial_failure` (Task 5.9) integrato nei collaudi automatizzati.

## Troubleshooting Passi:

### 1. Verificare Credenziali OAuth
Accertarsi che il Google Service Account sia valido e che la variabile `GOOGLE_SERVICE_ACCOUNT_CREDENTIALS` nel file `.env` sia valorizzata correttamente con il path del JSON.

### 2. Ispezionare i log di Errore (Sync Logs)
I log dettagliati delle operazioni con drive identificano eventuali rate limit (429) o problemi di permessi:
```bash
# Eseguire dalla root del progetto:
cd Standalone-app-v1/
docker compose -f docker-compose.prod.yml logs scheduler | grep -i "drive"
```

### 3. Ripristino Sincronizzazione / Riesecuzione Manuale
Poiché gli stati di sync falliti vengono memorizzati come `FAILED` o `PENDING`, verranno automaticamente ripresi al successivo ciclo della job APScheduler. Per forzare immediatamente una sincronizzazione manuale riavviare tempestivamente il worker scheduler:
```bash
cd Standalone-app-v1/
docker compose -f docker-compose.prod.yml restart scheduler
```

### 4. Verifica Integrità Post-Failure
Assicurarsi che nel database le entry "sync_status" si aggiornino allo stato `Y` verificando via client DB:
```bash
cd Standalone-app-v1/
docker compose -f docker-compose.prod.yml exec db psql -U tt_prod_user -d tickertracker_prod -c "SELECT * FROM sync_operations WHERE status = 'FAILED';"
```

## Riferimento implementativo (dev)
Per il meccanismo del pattern Outbox, i job APScheduler (retry, dead-letter, idempotenza) e gli stati `FAILED`/`PENDING`: [`../../backend/docs/SCHEDULER.md`](../../backend/docs/SCHEDULER.md).

## Contatti ed Escalation
Per supporto con le credenziali API di Google Cloud, consultare [CONTACTS.md](CONTACTS.md).
