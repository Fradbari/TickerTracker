# API Reference — Endpoint esposti

Tutte le risposte seguono lo standard `ApiResponse[T]`:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "trace_id": "uuid-string"
}
```

In caso di errore:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  },
  "trace_id": "uuid-string"
}
```

Documentazione live e interattiva: `http://localhost:8000/docs` (Swagger UI) e `http://localhost:8000/redoc`.

---

## Estimates API — Task 2.16

API gestione stime trading con tracking completo e audit trail.

### POST `/api/estimates`

Crea una nuova stima. Il prezzo corrente è recuperato automaticamente.

```http
POST /api/estimates
Content-Type: application/json

{
  "ticker_id": "uuid",
  "direction": "LONG",
  "target_profit_percent": "15.0",
  "stop_loss_percent": "5.0",
  "ai_model": "gpt-4",
  "ai_confidence": "75.0",
  "ai_reasoning": "Strong bullish indicators"
}
```

Response 201:

```json
{
  "success": true,
  "data": {
    "estimate": {
      "id": "uuid",
      "ticker_id": "uuid",
      "direction": "LONG",
      "status": "OPEN",
      "start_price": "100.00",
      "target_price": "115.00",
      "stop_loss_price": "95.00"
    },
    "message": "Estimate created successfully"
  },
  "trace_id": "uuid"
}
```

### GET `/api/estimates`

Lista paginata con filtri.

Query parameters:

- `ticker_id` (UUID) — filtra per ticker
- `user_id` (UUID) — filtra per utente
- `status` (string) — `OPEN`, `CLOSED_WIN`, `CLOSED_LOSS`, `CLOSED_MANUAL`, `EXPIRED`
- `direction` (string) — `LONG`, `SHORT`
- `include_deleted` (bool) — include soft-deleted
- `limit` (int) — items per pagina (1–100)
- `cursor` (string) — cursore opaco della pagina precedente

### GET `/api/estimates/{id}`

Dettaglio singola stima.

### PATCH `/api/estimates/{id}`

Aggiorna una stima OPEN.

⚠️ La modifica di `target` / `stop` recalcola automaticamente `target_price` e `stop_loss_price` da `start_price` + percentuali.

### PATCH `/api/estimates/{id}/close` ← **non** `DELETE`

Chiude una stima fornendo un exit price. Lo status finale è calcolato dal backend confrontando exit vs target/stop:

| Condizione | Status finale |
|---|---|
| Exit ≥ target (LONG) oppure Exit ≤ target (SHORT) | `CLOSED_WIN` |
| Exit ≤ stop (LONG) oppure Exit ≥ stop (SHORT) | `CLOSED_LOSS` |
| Altro | `CLOSED_NEUTRAL` |

```http
PATCH /api/estimates/{id}/close
Content-Type: application/json

{
  "exit_price": "115.00"
}
```

### GET `/api/estimates/{id}/history`

Audit trail completo (event sourcing).

```json
{
  "success": true,
  "data": {
    "estimate_id": "uuid",
    "audit_trail": [
      {
        "event_id": "uuid",
        "event_type": "CREATED",
        "timestamp": "2024-01-15T10:00:00Z",
        "user_id": "uuid",
        "description": "Estimate created: LONG at $100.00"
      }
    ],
    "summary": {
      "total_events": 5,
      "first_event_at": "...",
      "last_event_at": "...",
      "event_type_counts": { "CREATED": 1, "UPDATED": 2, "CLOSED": 1 }
    }
  }
}
```

### Codici di errore comuni

| Codice | Significato |
|---|---|
| `TICKER_NOT_FOUND` | Ticker ID non esiste |
| `ESTIMATE_NOT_FOUND` | Estimate ID non trovato |
| `ESTIMATE_ALREADY_CLOSED` | Update/close su stima già chiusa |
| `INVALID_PRICE` | Prezzi calcolati non validi |
| `INVALID_ESTIMATE_STATE` | Stato non valido per l'operazione |
| `MARKET_DATA_UNAVAILABLE` | Dati mercato mancanti |
| `INTERNAL_ERROR` | Errore interno server |

---

## Market Data API — Task 2.17

| Endpoint | Method | Descrizione | Cache TTL |
|---|---|---|---|
| `/api/market/price/{ticker}` | GET | Prezzo corrente | 1h (60s se stale) |
| `/api/market/history/{ticker}` | GET | Storico OHLCV | 24h |
| `/api/market/history/{ticker}/paginated` | GET | Storico paginato cursor | 24h |
| `/api/market/fundamentals/{ticker}` | GET | Fondamentali | 24h |
| `/api/market/search` | GET | Ricerca simboli (max 10 risultati) | 1h |

Tutti usano `ApiResponse` wrapper. Dependency injection del `MarketDataProvider` (decoupled — yahoo, finnhub, fake).

Error handling:

| Eccezione | HTTP |
|---|---|
| `SymbolNotFoundError` | 404 |
| `DataUnavailableError` | 503 |
| Generic | 500 |

Vedi il log storico: `backend/docs/history/orig/TASK_2.17_REPORT.md`.

---

## Health endpoints — Task 3.7

| Endpoint | Cosa controlla |
|---|---|
| `GET /health` | App running |
| `GET /health/ready` | Tutti i servizi (DB, Redis, Yahoo, Drive) |
| `GET /health/pool` | Status pool DB (vedi `backend/docs/CONNECTION-POOL.md`) |

`503 Service Unavailable` se qualche dipendenza è `UNHEALTHY`.

## Metriche

`GET /metrics` (vedi `backend/docs/METRICS.md` — Prometheus format).
