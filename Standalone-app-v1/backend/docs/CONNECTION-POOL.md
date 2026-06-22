# Connection Pool — Task 3.10

DB engine usa `AsyncAdaptedQueuePool` (SQLAlchemy `QueuePool` async wrapper), parametri configurabili via env.

## Variabili d'ambiente

| Variabile | Default | Note |
|---|---|---|
| `DB_POOL_SIZE` | 5 | Connessioni persistenti (5 dev, 10 prod) |
| `DB_MAX_OVERFLOW` | 10 | Extra oltre `pool_size` (10 dev, 20 prod) |
| `DB_POOL_TIMEOUT` | 30 | Secondi di attesa per una connessione |
| `DB_POOL_RECYCLE` | 1800 | Secondi dopo i quali viene riciclata (30 min) |
| `DB_POOL_PRE_PING` | True | Esegue `SELECT 1` prima di usare la connessione |

## Diagnostica

```bash
# Status pool dedicato
curl http://localhost:8000/health/pool
# {"pool_size": 5, "checked_in": 5, "checked_out": 0, "overflow": 0, "invalid": 0}

# Incluso anche in /health
curl http://localhost:8000/health | jq .connection_pool

# Metriche Prometheus
curl http://localhost:8000/metrics | grep db_pool
# db_pool_checked_out, db_pool_checked_in, db_pool_overflow, db_pool_size
```

## Tuning per ambiente

```env
# Development (default)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Production (esempio)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=15
DB_POOL_RECYCLE=900
```

## Implementazione

- Engine config: `src/shared/infra/database.py` (settings-driven)
- Gauge Prometheus: `db_pool_size` / `db_pool_checked_out` / `db_pool_checked_in` / `db_pool_overflow`
- Status endpoint: `src/shared/api/health_routes.py` (`/health/pool`)

Vedi: `backend/docs/METRICS.md` per il pattern `track_duration` e per la registrazione delle gauge.
