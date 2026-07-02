# Structured Logging — Task 3.5

Logging strutturato JSON via `structlog` con correlation ID per tracciamento distribuito.

## Setup

```python
from src.shared.infra.logging.config import configure_logging

configure_logging(
    level="INFO",          # DEBUG in dev
    json_format=True,      # JSON in prod, console in dev
)
```

L'init è chiamato automaticamente in `src/main.py` su startup FastAPI.

## Come funziona

Ogni request ottiene un `request_id` (UUID) generato dal `CorrelationIDMiddleware`. Viene letto da `X-Request-ID` se il client lo fornisce, altrimenti generato. Il valore è esposto:

- Back in response: `X-Request-ID`
- In ogni log: campo strutturato `correlation_id`
- All'application code via ContextVar `request_id`

## Campi loggati per ogni richiesta

| Campo | Tipo | Note |
|---|---|---|
| `method` | str | HTTP method |
| `path` | str | URL path |
| `status_code` | int | Response status |
| `duration_ms` | float | Tempo totale request |
| `client_ip` | str | Client IP (X-Forwarded-For chain-aware) |
| `request_id` | UUID | Correlation ID |
| `user_id` | UUID | Se autenticato |

## Esempio output JSON

```json
{
  "event": "request_completed",
  "method": "POST",
  "path": "/api/estimates",
  "status_code": 201,
  "duration_ms": 47.3,
  "client_ip": "127.0.0.1",
  "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "timestamp": "2026-02-14T21:00:00Z",
  "level": "info"
}
```

## Disabilitare nei test

```env
REQUEST_LOG_ENABLED=false   # riduce noise nei test E2E
```

## Test Coverage

18 test in `backend/tests/infra/test_logging.py`. Coprono:
- Formato JSON valido
- ContextVar propagation tra middleware/service
- Correlation ID da header `X-Request-ID` oppure generato
- Performance overhead < 0.5ms/request

## File chiave

- Config: `src/shared/infra/logging/config.py`
- Middleware: `src/shared/infra/logging/correlation_middleware.py`
- ContextVar: `src/shared/infra/logging/context.py`

## Vedere anche

- Runbook monitoring (ops): [`../../Docs/runbook/monitoring.md`](../../Docs/runbook/monitoring.md)
