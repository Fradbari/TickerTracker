# Gestione Errori Google Drive Sync

In caso di problemi con Drive API (es. *rate limit* o problemi di connettività), fare riferimento al test di Chaos engineering `test_drive_sync_partial_failure` (Task 5.9) integrato nei collaudi automatizzati, che documenta il comportamento atteso in caso di fallimento parziale.

Il sistema memorizza internamente le modifiche in stato di `PENDING` o `FAILED` che verranno poi automaticamente riprovate dallo scheduler nei cicli successivi per garantire eventual consistence. Nessuna modifica locale viene persa.