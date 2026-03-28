# Gestione Outage Yahoo Finance

**RTO: 0 min (Cache Hit) / < 5 min manual | RPO: ultima sincronizzazione riuscita (Età cache)**

Il sistema gestisce i disservizi di Yahoo Finance su 3 livelli incrementali:

## 1. Livello Automatico: Cache Redis attiva
Il sistema continua automaticamente restituendo i dati in memoria se validi temporalmente. Nessuna azione utente necessaria.

## 2. Fallback: Uso dati 'Stale' (Cache scaduta)
Se la cache scade durante l'outage, i dati non verranno più serviti bloccando il frontend, a meno che non si forzi l'uso dell'ultimo snapshot disponibile nella cache.
Attivare il Feature Flag usando l'API per forzare l'uso dei dati scaduti:
```bash
# Eseguire dalla root del progetto:
cd Standalone-app-v1/
curl -X POST http://localhost/api/admin/feature-flags \
     -H "Content-Type: application/json" \
     -d '{"USE_STALE_CACHE": true}'
```

## 3. Gestione Manuale e Riconciliazione
Se l'outage dovesse prolungarsi, avviare una procedura di notifica massiva verso l'utenza tramite gli strumenti aziendali.
Una volta ripristinato il servizio, disabilitare il feature flag:
```bash
cd Standalone-app-v1/
curl -X POST http://localhost/api/admin/feature-flags \
     -H "Content-Type: application/json" \
     -d '{"USE_STALE_CACHE": false}'
```

## Contatti ed Escalation
In caso di unblocco necessario delle cache o supporto sui Feature Flag, fare riferimento a [CONTACTS.md](CONTACTS.md).
