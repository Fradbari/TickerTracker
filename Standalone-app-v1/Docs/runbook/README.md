# TickerTracker - Operational Runbook

| Scenario | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|----------|-------------------------------|--------------------------------|
| DB Crash / Data Corruption | < 30 min | 24h (Ultimo backup giornaliero) |
| Yahoo Finance Outage | 0 (Cache Hit) / < 5 min manual | n/a (Dati vecchi nella cache) |
| Drive Sync Failure | < 10 min | Nessuna perdita dati locale |

Contatti per Escalation:
Vedi [CONTACTS.md](CONTACTS.md) o contatta [MAINTAINER] per emergenze bloccanti.
