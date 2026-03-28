# TickerTracker - Operational Runbook

Benvenuti nel Runbook Operativo di TickerTracker. Questo documento raccoglie tutte le procedure per il supporto e la manutenzione in un ambiente di produzione.

## Indice delle Procedure

- [Avvio e Spegnimento (Startup/Shutdown)](startup-shutdown.md)
- [Ripristino Database (Recovery)](database-recovery.md)
- [Gestione Outage Yahoo Finance](yahoo-outage.md)
- [Monitoring e Health](monitoring.md)
- [Gestione Errori Google Drive Sync](drive-sync-issues.md)
- [Scalabilità dei Servizi (Scaling)](scaling.md)
- [Contatti per Escalation](CONTACTS.md)

## Policy di Ripristino

| Scenario | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|----------|-------------------------------|--------------------------------|
| DB Crash / Data Corruption | < 30 min | 24h (Ultimo backup giornaliero) |
| Yahoo Finance Outage | 0 (Cache Hit) / < 5 min manual | n/a (Dati vecchi nella cache) |
| Drive Sync Failure | < 10 min | Nessuna perdita dati locale |

Vedi [CONTACTS.md](CONTACTS.md) per emergenze bloccanti.
