# Gestione Outage Yahoo Finance

**RPO:** Età dell'ultimo dato in cache

Il sistema gestisce i disservizi di Yahoo Finance su 3 livelli incrementali:

1. **Cache Redis attiva**: Il sistema continua automaticamente restituendo i dati in memoria se validi temporalmente.
2. **Cache scaduta**: Attivare il Feature Flag usando l'API per forzare l'uso della cache scaduta (stale data):
   `POST /api/admin/feature-flags` body: `{"USE_STALE_CACHE": true}`
3. **Outage prolungato**: Se l'outage supera i 3-5 giorni lavorativi, avviare procedura di notifica massiva utenti.