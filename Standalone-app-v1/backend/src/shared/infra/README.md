## `shared/infra` - Infrastructure Layer

Questo modulo contiene le preoccupazioni a livello di infrastruttura condivise in tutta l'applicazione.

### 1. Gestione della Configurazione (`config.py`)

**Scopo**: Sistema di configurazione multi-ambiente che utilizza Pydantic Settings con un approccio security-first.

**Caratteristiche Principali**:
- 🔐 **Protezione dei Segreti**: Tutti i valori sensibili utilizzano il tipo `SecretStr`
- 🌍 **Multi-Ambiente**: Supporto per configurazioni local/staging/production
- 📝 **Variabili d'Ambiente**: Caricamento da file `.env` con valori predefiniti di fallback
- 🔄 **Pattern Singleton**: Funzione `get_settings()` con caching
- ✅ **Validazione**: Validazione Pydantic v2 per tutti i campi

**Test Coverage**: 27 test ✓

---

### 2. Security Middleware (`security_middleware.py`)

**Scopo**: Middleware FastAPI per aggiungere sicurezza base alle risposte HTTP.

**Caratteristiche**:
- 🔒 **Security Headers**: Aggiunge header di sicurezza standard
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000`
  
- 🌐 **CORS Configuration**: Configura CORS per il frontend
  - Consente richieste da `localhost:3000` (React dev server)
  - Consente richieste da `localhost:5173` (Vite dev server)
  - Disabilitabile via `CORS_ORIGINS` nella configurazione
  
- ⚠️ **Rate Limiting**: Rate limit semplice in memoria per IP
  - Default: 60 richieste/minuto per IP
  - Disabilitabile via `ENABLE_RATE_LIMIT=false` per ambienti di sviluppo locale
  - Restituisce HTTP 429 quando il limite viene superato

**Usage**:
```python
from fastapi import FastAPI
from src.shared.infra.security_middleware import setup_security_middleware

app = FastAPI()
setup_security_middleware(app)  # Setup all middleware
```

**Test Coverage**: 16 test ✓

---

### 3. Health Check Routes (`../api/health_routes.py`)

**Scopo**: Endpoint di health check per monitoraggio e Docker health probes.

**Endpoints**:
- `GET /health` - Basic health check (always 200 OK if app is running)
- `GET /health/ready` - Readiness check (all dependencies OK)

**Docker Integration**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"
```

**Kubernetes Integration**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
```

**Response Format** (ApiResponse):
```json
{
  "success": true,
  "data": {
    "status": "ok"
  },
  "trace_id": "uuid-string",
  "error": null
}
```

**Test Coverage**: Health check endpoints fully tested as part of middleware tests

---

## Directory Structure

```
shared/infra/
├── __init__.py
├── config.py                  # ✅ [1.6] Multi-environment configuration
├── security_middleware.py     # ✅ [1.7] Security middleware + rate limiting
├── cache/                     # (future) Caching layer
├── drive/                     # (future) Google Drive integration
├── logging/                   # (future) Structured logging setup
├── security/                  # (future) Encryption and security utilities
└── yahoo/                     # (future) Yahoo Finance API integration
```

---

## Configurazione

### Environment Variables

```env
# Rate Limiting
ENABLE_RATE_LIMIT=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# CORS
CORS_ORIGINS=  # Lista comma-separated di origins aggiuntivi
```

### Disabilitare Rate Limit Localmente

Per sviluppo locale dove il rate limit può essere problematico:

```env
ENABLE_RATE_LIMIT=false
```

---

## Note

- Tutti i campi segreti utilizzano `SecretStr` e sono mascherati nei log
- Il file `.env` viene caricato automaticamente (escluso da git via .gitignore)
- `get_settings()` viene messo in cache per prevenire ripetute operazioni I/O
- Security headers vengono aggiunti a TUTTE le risposte HTTP
- Rate limiting è opzionale e può essere disabilitato per ambienti di sviluppo
