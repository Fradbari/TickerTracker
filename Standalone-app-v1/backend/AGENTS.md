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

ID: TASK 2.1
Area: backend/infra
Fase: MVP
Dipendenze: -

## TASK 2.1: Setup Progetto Python con Poetry & Dipendenze Complete

**Descrizione:** Inizializzare pyproject.toml con TUTTE le dipendenze necessarie per MVP e Fase 2, evitando installazioni frammentate.

**Microstep:**

1. Creare `backend/pyproject.toml` con metadata progetto
2. Configurare dipendenze MVP:
   - Core: fastapi, uvicorn[standard], pydantic, pydantic-settings
   - Database: sqlalchemy[asyncio], asyncpg, alembic
   - API esterne: google-api-python-client, google-auth-httplib2, google-auth-oauthlib, yfinance
   - Cache: redis[hiredis]
   - Scheduler: apscheduler
3. Configurare dipendenze Fase 2 (opzionali):
   - Security: cryptography, slowapi
   - Observability: structlog, prometheus-client
4. Configurare dipendenze sviluppo: pytest, pytest-asyncio, pytest-cov, ruff, mypy, httpx
5. Configurare tool.ruff, tool.mypy, tool.pytest.ini_options
6. Creare `Makefile`, `.python-version`, `scripts/check_deps.py`
7. Esportare `requirements.txt` e `requirements-dev.txt`

**Acceptance Criteria:**

- [ ] `poetry install` completa senza errori
- [ ] `make check-deps` verifica dipendenze critiche
- [ ] `requirements*.txt` sincronizzati con pyproject.toml
- [ ] TASK 2.1 può partire immediatamente senza installare altro

[... resto del contenuto invariato ...]
