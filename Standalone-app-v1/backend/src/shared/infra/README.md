## `shared/infra` - Infrastructure Layer

Questo modulo contiene le preoccupazioni a livello di infrastruttura condivise in tutta l'applicazione.

### Gestione della Configurazione (`config.py`)

**Scopo**: Sistema di configurazione multi-ambiente che utilizza Pydantic Settings con un approccio security-first.

**Caratteristiche Principali**:
- 🔐 **Protezione dei Segreti**: Tutti i valori sensibili utilizzano il tipo `SecretStr` (URL database, chiavi API, chiavi di cifratura)
- 🌍 **Multi-Ambiente**: Supporto per configurazioni local/staging/production
- 📝 **Variabili d'Ambiente**: Caricamento da file `.env` con valori predefiniti di fallback
- 🔄 **Pattern Singleton**: Funzione `get_settings()` con caching per garantire un'unica istanza
- ✅ **Validazione**: Validazione Pydantic v2 per tutti i campi, inclusi i tipi Literal

**Campi di Configurazione**:
- **Ambiente**: `ENVIRONMENT` (local/staging/production), `DEBUG`, `LOG_LEVEL`
- **Database**: `DATABASE_URL` (SecretStr)
- **API Esterne**: `YAHOO_CACHE_TTL`, `GEMINI_API_KEY`, `FINNHUB_API_KEY`
- **Google Drive**: `GOOGLE_SERVICE_ACCOUNT_JSON`, `DRIVE_FOLDER_ID`
- **Sicurezza**: `ENCRYPTION_KEY`, `JWT_SECRET`

**Usage Example**:
```python
from src.shared.infra.config import get_settings

# Get cached settings instance
settings = get_settings()

# Access configuration
if settings.ENVIRONMENT == "production":
    db_url = settings.DATABASE_URL.get_secret_value()
    log_level = settings.LOG_LEVEL
```

**Test Coverage**: 27 test che coprono creazione, validazione, segreti, caricamento dell'ambiente e comportamento singleton.

## Directory Structure

```
shared/infra/
├── __init__.py
├── config.py          # Multi-environment configuration with Pydantic Settings
├── cache/             # Caching layer (future)
├── drive/             # Google Drive integration (future)
├── logging/           # Structured logging setup (future)
├── security/          # Encryption and security utilities (future)
└── yahoo/             # Yahoo Finance API integration (future)
```

## Notes

- Tutti i campi segreti utilizzano `SecretStr` e sono mascherati correttamente nei log
- Il file `.env` viene caricato automaticamente dalla root del progetto (escluso da git via .gitignore)
- Usa `.env.example` come template per configurare il tuo ambiente
- `get_settings()` viene messo in cache per prevenire ripetute operazioni di I/O su file
