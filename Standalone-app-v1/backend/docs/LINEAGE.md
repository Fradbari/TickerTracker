# Data Lineage Tracking — Task 3.9

Tracciabilità della provenienza dei dati `market_data` (chi/cosa/cuando/quale fonte/timestamp sorgente).

## Modifiche al modello `MarketData`

- `ingested_at` rinominato in `ingestion_timestamp`
- Aggiunta colonna `source_timestamp` (timestamp del dato alla fonte originale)
- Aggiunto mixin `LineageTracked` per ereditarietà

```python
from src.market_data.domain.lineage import LineageTracked

class MarketData(Base, LineageTracked):
    ...
```

I campi lineage:

| Campo | Tipo | Note |
|---|---|---|
| `ingestion_timestamp` | timestamp TZ | Quando il dato è stato scritto in DB |
| `source_timestamp` | timestamp TZ | Quando il dato è stato generato dalla fonte (es. fine giornata borsa) |
| `source_provider` | str enum | `YAHOO`, `FINNHUB`, `POLYGON`, `MANUAL`, `LEGACY_IMPORT` |
| `ingestion_run_id` | UUID | Collega al job di ingestion (vedi `sync_jobs`) |

## API param

```
GET /api/market/price/{ticker}?include_lineage=true
```

Restituisce in aggiunta i campi lineage nella response.

## Schema Pydantic

```python
from src.market_data.schemas.lineage import MarketDataLineageSchema
```

Vedi dettagli su come si compila automaticamente il lineage nell'hook `before_insert` del listener SQLAlchemy.

## Test Coverage

20 test in `backend/tests/market_data/test_lineage.py` (Task 3.9).

## Migrazione Alembic

Revision `a3b5c7d9e1f0` aggiunge `source_timestamp`, `source_provider`, rinomina `ingested_at` → `ingestion_timestamp`.

Vedi anche `backend/docs/SCHEDULER.md` per i job che popolano il lineage (`refresh_market_data`, `daily_history_sync`).
