# Prometheus Metrics — Task 3.6

Counter/Gauge/Histogram per business + technical metrics. Endpoint `/metrics` esposto per scrape Prometheus.

## Endpoint

```bash
curl http://localhost:8000/metrics
```

Aggiunto a `API_KEY_EXEMPT_PATHS` di default, quindi scrapable anche con `ENABLE_API_KEY_AUTH=true`.

## Decorator `@track_duration`

Misura automaticamente la durata di una funzione async (o sync) e la registra come histogram con label opzionali.

```python
from src.shared.infra.metrics import track_duration

@track_duration(metric="estimate_create")
async def create_estimate(self, command: CreateEstimateCommand) -> Estimate:
    ...
```

Output Prometheus: `estimate_create_duration_seconds_bucket{le="0.005"}` etc.

## Metriche business

| Nome | Tipo | Label | Dove |
|---|---|---|---|
| `estimate_total` | Counter | `direction`, `status` | Servizio estimate |
| `market_price_fetched_total` | Counter | `provider`, `cache_hit` | Provider layer |
| `outbox_event_processed_total` | Counter | `event_type`, `status` | OutboxProcessor |

## Metriche tecniche

| Nome | Tipo | Descrizione |
|---|---|---|
| `db_pool_size` | Gauge | Dimensione pool |
| `db_pool_checked_out` | Gauge | Connessioni in uso |
| `db_pool_checked_in` | Gauge | Connessioni idle |
| `db_pool_overflow` | Gauge | Overflow attivo |
| `request_duration_seconds` | Histogram | Per-endpoint |
| `http_requests_total` | Counter | Per status code |

Le gauge del pool sono aggiornate ad ogni scrape, vedi `backend/docs/CONNECTION-POOL.md`.

## Test Coverage

24 test in `backend/tests/infra/test_metrics.py`. Coprono:
- Counter increment
- Gauge set/inc/dec
- Histogram bucketing
- Label cardinality
- `/metrics` endpoint format

## File chiave

- Metrics primitives: `src/shared/infra/metrics/metrics.py`
- Routes: `src/shared/infra/metrics/routes.py`

## Vedere anche

- Runbook monitoring (ops): [`../../Docs/runbook/monitoring.md`](../../Docs/runbook/monitoring.md)
