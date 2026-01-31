# Backend - Core Application Logic

## Scope
Questa sezione contiene SOLO task per il backend Python/FastAPI:
- Bounded context: `estimates/`, `market_data/`, `sync/`, `analytics/`, `shared/`
- Infra: `yahoo/`, `drive/`, `cache/`, `logging/`, `security/`, `scheduler/`, `outbox/`
- Value objects, repositories, services, API routes
- Database migrations (Alembic)
- Configurazione (pydantic-settings)

**Non modificare**:
- File di Docker/compose (vedi `Docker/AGENTS.md`)
- File di test/CI (vedi `Docs/AGENTS.md`)
- Codice frontend (vedi `Frontend/AGENTS.md`)

---

# SEZIONE 1: LINEE GUIDA TRASVERSALI (Backend)

[... contenuto esistente della Sezione 1 rimane invariato ...]

---

# SEZIONE 2: BACKEND & DATA

---

## NOTE NUMERAZIONE

**TASK 2.2**: Originariamente "Setup Docker Compose per PostgreSQL e Redis".  
Spostato in `Docker/AGENTS.md` durante riorganizzazione architetturale.  
La numerazione backend non è stata riallineata per preservare riferimenti storici e dipendenze esistenti.  
Per dettagli su Docker Compose, consultare `Docker/AGENTS.md` → TASK 2.2.

---

ID: TASK 2.0
Area: backend/infra
Fase: MVP
Dipendenze: -

## TASK 2.0: Setup Progetto Python con Poetry e Requirements Completi

**Descrizione:** Inizializzare il progetto Python backend con dependency management moderno (Poetry) e file requirements completo per tutti i task MVP e Fase 2. Questo task è prerequisito fondamentale per tutti gli altri task backend.

**Microstep:**

1. Creare file `backend/pyproject.toml` con metadati progetto e configurazione Poetry
2. Configurare dipendenze CORE in `[tool.poetry.dependencies]`:
   - python >= 3.11
   - fastapi, uvicorn[standard], pydantic, pydantic-settings
3. Aggiungere dipendenze DATABASE & ORM:
   - sqlalchemy[asyncio], asyncpg, alembic
4. Aggiungere dipendenze CACHE:
   - redis
5. Aggiungere dipendenze MARKET DATA (TASK 2.18-2.19):
   - yfinance, finnhub-python (optional)
6. Aggiungere dipendenze GOOGLE DRIVE (TASK 2.20):
   - google-api-python-client, google-auth, google-auth-oauthlib, google-auth-httplib2
7. Aggiungere dipendenze SICUREZZA (TASK 3.1, 3.4):
   - cryptography, python-jose[cryptography], passlib[bcrypt]
8. Aggiungere dipendenze SCHEDULING (TASK 2.24):
   - apscheduler
9. Aggiungere dipendenze OBSERVABILITY - Fase 2 (TASK 3.5, 3.6):
   - structlog, prometheus-client
10. Aggiungere dipendenze RATE LIMITING - Fase 2 (TASK 3.2):
    - slowapi
11. Aggiungere dipendenze UTILITY:
    - python-multipart, cachetools, python-dotenv
12. Configurare dipendenze SVILUPPO in `[tool.poetry.group.dev.dependencies]`:
    - pytest, pytest-asyncio, pytest-cov, httpx, ruff, mypy, black, faker
13. Configurare sezione `[tool.ruff]` per linting
14. Configurare sezione `[tool.mypy]` con strict mode
15. Configurare sezione `[tool.pytest.ini_options]`
16. Creare file `backend/.python-version` con contenuto: `3.11`
17. Generare `backend/requirements.txt` con comando:
    ```bash
    poetry export -f requirements.txt --output requirements.txt --without-hashes
    ```
18. Generare `backend/requirements-dev.txt`:
    ```bash
    poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
    ```
19. Creare `backend/Makefile` con comandi:
    - `make install` - installa con Poetry
    - `make install-pip` - installa con pip (fallback)
    - `make lint` - linting con ruff
    - `make format` - formattazione con black
    - `make typecheck` - type checking con mypy
    - `make test` - esegui test
    - `make test-cov` - test con coverage
    - `make run` - avvia server uvicorn
    - `make export-requirements` - rigenera requirements.txt
    - `make check-deps` - verifica dipendenze installate
20. Creare script `backend/scripts/check_deps.py` per verificare installazione dipendenze
21. Aggiornare `backend/README.md` con istruzioni installazione per Poetry e pip

**Acceptance Criteria:**

- [ ] `poetry install` completa senza errori
- [ ] `pip install -r requirements.txt` funziona come alternativa
- [ ] `make check-deps` verifica installazione dipendenze
- [ ] `make lint` esegue ruff senza errori su codice base pulito
- [ ] `make typecheck` esegue mypy
- [ ] `make test` esegue pytest (anche se tests/ è vuoto inizialmente)
- [ ] File `pyproject.toml` include TUTTE le dipendenze per MVP + Fase 2
- [ ] File `requirements.txt` sincronizzato con `pyproject.toml`
- [ ] File `.python-version` presente per gestori versioni (pyenv, asdf)
- [ ] Script `check_deps.py` funzionante ed eseguibile

**Note Importanti:**
- Questo task è **prerequisito fondamentale** per TUTTI i task backend successivi
- `requirements.txt` deve essere rigenerato con `make export-requirements` quando si aggiungono dipendenze
- Per ambienti production, usare `requirements.txt` con versioni pinned esatte
- Il Makefile fornisce comandi standardizzati per tutto il team di sviluppo

---

### Istruzioni per LLM
- Creare TUTTI i file elencati nei microstep.
- Seguire esattamente le versioni specificate per le dipendenze.
- Verificare che tutte le dipendenze siano allineate con i task che le richiedono.
- Testare l'installazione sia con Poetry che con pip.
- Alla fine, produci un elenco puntato con file creati e verifiche eseguite.

---

ID: TASK 2.1
Area: backend/infra
Fase: MVP
Dipendenze: TASK 2.0

## TASK 2.1: Setup SQLAlchemy e Database Connection Pool

**Descrizione:** Configurare SQLAlchemy con connection pooling ottimizzato.

[... resto del contenuto invariato ...]
