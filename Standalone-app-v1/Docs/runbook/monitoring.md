# Monitoring e Health

**RTO: n/a | RPO: n/a** (Scenario di osservabilità)

## Metriche (Prometheus / Grafana)
Il sistema espone le metriche in formato Prometheus all'endpoint:
```bash
curl -s http://localhost/api/v1/metrics
```
Le dashboard sono accessibili in Grafana (se configurato sull'host monitoraggio).
*Esempio PromQL per verificare il rate di errore HTTP:*
```promql
rate(http_requests_total{status=~"5.."}[5m])
```

## Log Strutturati JSON
Il backend emette log in formato JSON per l'ingestione tramite stack ELK o Grafana Loki.
Comando rapido per visualizzare i log del backend in real-time tramite Docker:
```bash
# Eseguire dalla root del progetto:
cd Standalone-app-v1/
docker compose -f docker-compose.prod.yml logs backend -f
```

## Alert (Alertmanager)
Gli allarmi vengono gestiti via Alertmanager. Verificare gli alert pendenti interrogando l'API (se configurato):
```bash
curl -s http://alertmanager:9093/api/v2/alerts | jq
```

## Riferimenti implementativi (dev)
Questo runbook descrive *come consumare* l'osservabilità in produzione. Per i dettagli implementativi:
- Metriche Prometheus: [`../../backend/docs/METRICS.md`](../../backend/docs/METRICS.md)
- Logging strutturato JSON + correlation ID: [`../../backend/docs/LOGGING.md`](../../backend/docs/LOGGING.md)
- Endpoint di health (`/health`, `/health/ready`, `/health/pool`): [`../../backend/docs/HEALTH.md`](../../backend/docs/HEALTH.md)

## Contatti ed Escalation
Vedi [CONTACTS.md](CONTACTS.md) per i riferimenti di escalation in caso di comportamenti anomali persistenti.
