# Security Middleware — Task 1.7 + 3.1 + 3.2

Sistema multi-livello di protezione delle request. Tutti i test coprono comportamento end-to-end.

## 1. Security Headers

Header HTTP standard applicati a ogni risposta:

| Header | Valore | Scopo |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Previene MIME sniffing |
| `X-Frame-Options` | `DENY` | Blocca clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Protezione XSS (legacy IE/Edge) |
| `Strict-Transport-Security` | solo HTTPS | Enforce HSTS |
| `Content-Security-Policy` | configurabile | Vedi `CSP_POLICY` |

## 2. API Key Authentication (Task 3.1)

Opzionale, **disabilitata in dev locale**. Quando `ENABLE_API_KEY_AUTH=true`, ogni richiesta deve includere `X-API-Key`. La validazione usa `secrets.compare_digest` per resistenza ai timing attack.

```env
ENABLE_API_KEY_AUTH=true
API_KEY=your-secret-api-key
API_KEY_EXEMPT_PATHS=/health,/health/ready,/health/db,/docs,/openapi.json,/redoc
```

## 3. Content Security Policy

```env
CSP_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
```

Impostare `CSP_POLICY=` (vuoto) per disabilitare l'header.

## 4. Rate Limiting (Task 3.2)

Redis-backed tramite `slowapi`. Default per-endpoint:

| Endpoint | Limite |
|---|---|
| Tutti gli endpoint | `100/minute` |
| `POST /api/estimates` | `30/minute` |
| `GET /api/market/price/{ticker}` | `60/minute` |
| `POST /api/chat` | `10/minute` |

```env
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_SLOWAPI_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_WHITELIST_IPS=["127.0.0.1","::1"]
```

In assenza di Redis c'è fallback automatico in-memory (no crash). Le risposte 429 includono `Retry-After` e `X-RateLimit-Limit`.

**⚠️ I route handler con `@limiter.limit()` devono avere sia `request: Request` che `response: Response` come parametri** (richiesto da slowapi per iniettare gli header).

## 5. CORS

Origin di default: `http://localhost:3000` (React dev) e `http://localhost:5173` (Vite dev). Estensione via `CORS_ORIGINS=https://example.com,https://other.com`.

## 6. Middleware Execution Order

Dal più esterno al più interno:

```
Request
  → _RequestContextMiddleware [3.2]   (popola ContextVar request corrente)
  → SlowAPIMiddleware [3.2]           (applica rate limit)
  → SecurityMiddleware [3.1]          (valida API Key)
  → RateLimitMiddleware [1.7]         (fallback legacy rate limiter)
  → CORSMiddleware                    (CORS headers)
  → SecurityHeadersMiddleware         (security response headers)
  → Routes
```

La `_RequestContextMiddleware` popola la `ContextVar` con la request corrente (necessaria per la whitelist IP zero-arg di slowapi).

## Test Coverage

| Modulo | Test |
|---|---|
| `test_security_middleware.py` | 29 (Task 3.1) |
| `test_rate_limit.py` | 33 (Task 3.2) |
| `test_middleware.py` | 16 (Task 1.7) |

## File chiave

- Middleware: `src/shared/infra/security_middleware.py`
- Rate limit: `src/shared/infra/security/rate_limit.py`
- API Key + CSP: `src/shared/infra/security/middleware.py`
