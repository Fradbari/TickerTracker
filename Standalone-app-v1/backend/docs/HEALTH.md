# Health Checks — Task 3.7

`HealthService` controlla lo stato di **DB, Redis, Yahoo, Drive**. Espone 3 endpoint con granularità crescente.

## Endpoint

| Endpoint | Comportamento |
|---|---|
| `GET /health` (`/health/live`) | 200 OK se l'app gira. Non controlla dipendenze. |
| `GET /health/ready` | 200 OK se DB + Redis + Yahoo + Drive tutti `HEALTHY`. 503 altrimenti. |
| `GET /health/pool` | Vedi `backend/docs/CONNECTION-POOL.md` |

## Schema response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "status": "ready",                 // "ready" | "not_ready" | "ok"
    "checks": {
      "database": "HEALTHY",           // HEALTHY | UNHEALTHY | UNKNOWN
      "redis":    "HEALTHY",
      "yahoo":    "HEALTHY",
      "drive":    "HEALTHY"
    },
    "timestamp": "2026-02-14T21:00:00Z"
  },
  "error": null,
  "trace_id": "uuid"
}
```

Quando uno dei check è `UNHEALTHY`, lo status passa a `not_ready` e l'HTTP response è `503 Service Unavailable`.

## HealthService

Singleton: `src/shared/infra/health_service.py`

```python
from src.shared.infra.health_service import HealthService

status = await HealthService.run_all_checks()
# {"database": "HEALTHY", "redis": "HEALTHY", ...}
```

Aggiungere una nuova dipendenza è un one-liner: registri un nuovo `HealthCheckProtocol` e `HealthService` lo raccoglie.

## Test Coverage

13 test in `backend/tests/infra/test_health.py`.

## File chiave

- `src/shared/api/health_routes.py` — endpoint
- `src/shared/infra/health_service.py` — orchestrazione

## Per Kubernetes / Docker health probe

Vedi snippet in `backend/README.md` § Quick Start.

## Vedere anche

- Runbook monitoring (ops): [`../../Docs/runbook/monitoring.md`](../../Docs/runbook/monitoring.md)
- Runbook startup/shutdown (ops): [`../../Docs/runbook/startup-shutdown.md`](../../Docs/runbook/startup-shutdown.md)
