# Cursor-Based Pagination — Task 3.11

Costo **O(1) per pagina** indipendente dalla dimensione del dataset. Implementato in `src/shared/repositories/pagination.py`.

## Endpoint esposto

```
GET /api/market/history/{ticker}/paginated
```

## Query parameters

| Parametro | Default | Descrizione |
|---|---|---|
| `cursor` | — | Cursore opaco dalla risposta precedente |
| `direction` | `next` | `next` (avanti) oppure `prev` (indietro) |
| `limit` | `50` | Items per pagina (1–500) |
| `start_date` | — | Filtro data minima `YYYY-MM-DD`, opzionale |
| `end_date` | — | Filtro data massima `YYYY-MM-DD`, opzionale |

## Navigazione

```bash
# Prima pagina (no cursor)
curl "http://localhost:8000/api/market/history/AAPL/paginated?limit=10"

# Pagina successiva (usa next_cursor della risposta)
curl "http://localhost:8000/api/market/history/AAPL/paginated?limit=10&cursor=<next_cursor>"

# Con filtro date
curl "http://localhost:8000/api/market/history/AAPL/paginated?start_date=2024-01-01&end_date=2024-12-31&limit=20"
```

## Formato risposta

```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "items": [...],
    "next_cursor": "eyJkYXRlIjogIjIwMjQtMDEtMTUifQ",
    "prev_cursor": null,
    "has_more": true,
    "total_in_page": 50,
    "limit": 50
  },
  "trace_id": "uuid-string"
}
```

## Note

- Il cursore è **opaco** (base64url, no padding). I client non devono interpretarne il contenuto.
- `start_date`/`end_date` delimitano la finestra dati e restano fissi per tutta la navigazione.
- Navigazione **sequenziale**: non si salta a pagine arbitrarie.

## Test coverage

42 test in `backend/tests/shared/test_pagination.py`. Indici usati:
- `(created_at, id)` su `estimates` per sort
- `(ticker_id, date)` su `market_data` per range query
