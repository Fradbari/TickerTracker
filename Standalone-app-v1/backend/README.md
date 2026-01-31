# TickerTracker Backend

## Descrizione

Backend Python/FastAPI per TickerTracker v3.0 - Sistema di tracking stime trading con architettura DDD/CQRS/Event Sourcing.

## Requisiti

- Python 3.11+
- PostgreSQL 16+ (per ambiente di sviluppo: Docker Compose)
- Redis 7+ (per ambiente di sviluppo: Docker Compose)

## Installazione

### Opzione 1: Poetry (Raccomandato)

Poetry è il gestore di dipendenze raccomandato per questo progetto.

```bash
# Installa Poetry se non presente
curl -sSL https://install.python-poetry.org | python3 -

# Installa dipendenze
cd backend
make install

# Oppure manualmente
poetry install
```

### Opzione 2: pip (Fallback)

Se preferisci usare pip tradizionale:

```bash
cd backend

# Crea virtual environment
python -m venv venv

# Attiva virtual environment
# Su Linux/macOS:
source venv/bin/activate
# Su Windows:
venv\Scripts\activate

# Installa dipendenze
make install-pip

# Oppure manualmente
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Verifica Installazione

```bash
make check-deps
```

Questo comando verifica che tutte le dipendenze critiche siano installate correttamente.

## Configurazione

1. Copia il file di configurazione esempio:
```bash
cp .env.example .env
```

2. Modifica `.env` con i tuoi valori:
```env
# Database
DATABASE_URL=postgresql+asyncpg://ticker:password@localhost:5432/tickertracker

# Cache
REDIS_URL=redis://localhost:6379/0

# Security (genera con: python -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=your-encryption-key-here
JWT_SECRET=your-jwt-secret-here

# Google Drive (opzionale per sync)
GOOGLE_SERVICE_ACCOUNT_JSON={...}
DRIVE_FOLDER_ID=your-folder-id

# API Keys (opzionali)
FINNHUB_API_KEY=your-finnhub-key  # Fase 2
```

## Avvio Database (Sviluppo)

Utilizza Docker Compose per avviare PostgreSQL e Redis:

```bash
# Dalla root del progetto
docker compose up -d db redis
```

Oppure consulta `../Docker/AGENTS.md` per dettagli sul setup Docker completo.

## Comandi Utili

Il progetto include un `Makefile` con comandi standardizzati:

### Sviluppo

```bash
make run          # Avvia server di sviluppo (http://localhost:8000)
make format       # Formatta codice con black e ruff
make lint         # Controlla codice con ruff
make typecheck    # Controlla tipi con mypy
```

### Testing

```bash
make test             # Esegui tutti i test
make test-unit        # Solo unit tests
make test-integration # Solo integration tests
make test-cov         # Test con coverage report (genera htmlcov/)
```

### Database

```bash
make migrate         # Applica migrazioni
make migrate-down    # Rollback ultima migrazione
make migrate-new     # Crea nuova migrazione auto-generata
```

### Utility

```bash
make check-deps          # Verifica dipendenze installate
make export-requirements # Rigenera requirements.txt da pyproject.toml
make clean               # Rimuovi file temporanei e cache
make help                # Mostra tutti i comandi disponibili
```

## Struttura Progetto

```
backend/
├── src/                  # Codice sorgente
│   ├── estimates/        # Bounded Context: Stime
│   ├── market_data/      # Bounded Context: Dati di mercato
│   ├── sync/             # Bounded Context: Sincronizzazione Drive
│   ├── analytics/        # Bounded Context: Analytics e AI
│   ├── shared/           # Codice condiviso (value objects, utils)
│   │   ├── domain/       # Valore objects immutabili
│   │   │   └── value_objects/
│   │   │       ├── money.py            # ✅ [1.3] Value Object Money
│   │   │       └── percentage.py       # ✅ [1.4] Value Object Percentage
│   │   ├── api/          # Schema e utility API
│   │   ├── schemas/      # Modelli Pydantic condivisi
│   │   │   └── api_response.py     # ✅ [1.2] Risposta API standardizzata
│   │   └── services/     # Servizi condivisi
│   ├── infra/            # Infrastruttura (database, cache, providers)
│   └── main.py           # Entry point FastAPI
├── tests/                # Test
│   ├── unit/             # Unit tests
│   │   └── shared/
│   │       └── domain/
│   │           ├── test_money.py       # ✅ [1.3] 36 test passanti
│   │           └── test_percentage.py  # ✅ [1.4] 39 test passanti
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── alembic/              # Migrazioni database
├── scripts/              # Script di utilità
├── pyproject.toml        # Configurazione Poetry e tools
├── requirements.txt      # Dipendenze production (pip)
├── requirements-dev.txt  # Dipendenze development (pip)
└── Makefile              # Comandi standardizzati
```

## Implementation Progress

### Phase 1: Foundation & API Structure (4/8 task)

| Task | Descrizione | Status | Tests |
|------|-----------|--------|-------|
| 1.1 | Setup Struttura Layer Backend | ✅ COMPLETATO | - |
| 1.2 | Modello Risposta API Standard | ✅ COMPLETATO | - |
| 1.3 | Value Object Money | ✅ COMPLETATO | 36 ✓ |
| 1.4 | Value Object Percentage | ✅ COMPLETATO | 39 ✓ |

## Documentazione API

Una volta avviato il server, la documentazione interattiva è disponibile su:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architettura

Il backend segue i principi di:

- **Domain-Driven Design (DDD)**: Organizzazione in bounded contexts
- **CQRS**: Separazione command/query
- **Event Sourcing**: Tracciamento completo delle modifiche alle stime
- **Clean Architecture**: Dipendenze verso l'interno, domain al centro

### Layering

Ogni bounded context segue una struttura layered:

- **api/**: Router FastAPI e dependency injection
- **schemas/**: Schema Pydantic per request/response
- **domain/**: Entità, value objects, aggregates
- **services/**: Business logic e orchestrazione
- **repositories/**: Accesso dati e persistenza

## Contribuire

Prima di committare:

```bash
make format      # Formatta codice
make lint        # Verifica linting
make typecheck   # Verifica tipi
make test        # Esegui test
```

## Note per Sviluppatori

### Aggiungere Dipendenze

Con Poetry:
```bash
poetry add nome-pacchetto
make export-requirements  # Aggiorna requirements.txt
```

Con pip:
```bash
pip install nome-pacchetto
pip freeze > requirements.txt  # Aggiorna manualmente
```

### Gestione Migrazioni

Dopo aver modificato i modelli SQLAlchemy:

```bash
make migrate-new  # Crea migrazione
# Rivedi il file generato in alembic/versions/
make migrate      # Applica migrazione
```

### Rigenerare requirements.txt

Se modifichi `pyproject.toml`, rigenera i file requirements:

```bash
make export-requirements
```

## Link Utili

- [AGENTS.md](./AGENTS.md) - Piano atomico task backend
- [../Docs/Piano-operativo-v1.4.md](../Docs/Piano-operativo-v1.4.md) - Piano operativo completo
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Licenza

Proprietario - © 2026 Francesco Di Lecce
