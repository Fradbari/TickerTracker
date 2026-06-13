# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start (Development Environment)

1. **Environment Setup**
   - Copy environment variables: `cp .env.example .env` (root) and `cp backend/.env.example backend/.env`
   - Add required API keys (Google, Yahoo, Gemini, etc.) to `.env` files.

2. **Infrastructure (PostgreSQL + Redis)**
   - Using the helper script (recommended):
     - Windows PowerShell: `.\docker-manage.ps1 up`
     - Linux/macOS Bash: `./docker-manage.sh up`
   - Or directly with Docker Compose: `docker compose -f docker-compose.base.yml up -d`

3. **Backend**
   - Install dependencies: `cd backend && poetry install`
   - Activate virtual environment: `poetry shell` (or `source .venv/bin/activate`)
   - Apply database migrations: `alembic upgrade head`
   - Start development server: `uvicorn src.main:app --reload` (will be available at http://localhost:8000)

4. **Frontend**
   - Install dependencies: `cd frontend && npm install`
   - Start development server: `npm run dev` (will be available at http://localhost:3000)
   - The frontend automatically proxies to the backend via Docker network (`VITE_API_TARGET=http://backend:8000`) when using `docker compose up`.

5. **Full Stack (Docker Compose)**
   - One-command start: `docker compose up --build` (starts PostgreSQL, Redis, Backend, Frontend)
   - Services:
     - Frontend: http://localhost:3000
     - Backend API: http://localhost:8000
     - Swagger UI: http://localhost:8000/docs
     - PostgreSQL: localhost:5432
     - Redis: localhost:6379

## Common Commands

### Backend (Poetry)

| Command | Description |
|---------|-------------|
| `poetry install` | Install dependencies |
| `poetry shell` | Activate virtual environment |
| `ruff check src/ tests/` | Linting |
| `ruff format src/ tests/` | Format code |
| `mypy src/` | Type checking |
| `pytest tests/` | Run all tests |
| `pytest -m unit tests/` | Run unit tests only |
| `pytest -m integration tests/` | Run integration tests only |
| `pytest --cov=src --cov-report=html tests/` | Run tests with coverage |
| `alembic upgrade head` | Apply database migrations |
| `alembic revision --autogenerate -m "msg"` | Generate new migration |
| `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000` | Run dev server |
| `python scripts/validate_dependencies.py` | Validate task dependencies graph |
| `make <target>` | See `backend/Makefile` for shortcuts (lint, format, typecheck, test, test-cov, etc.) |

### Frontend (npm)

| Command | Description |
|---------|-------------|
| `npm install` | Install dependencies |
| `npm run dev` | Start Vite dev server (http://localhost:3000) |
| `npm run build` | Build for production (`dist/` folder) |
| `npm run preview` | Preview production build |
| `npm run lint` | ESLint |
| `npm run type-check` | TypeScript compilation check (`tsc --noEmit`) |
| `npm run test` | Run Vitest unit tests |
| `npm run test:coverage` | Run tests with coverage report |
| `npm run test -- --run <testName>` | Run a specific test (e.g., `npm run test -- --run "estimate service"` ) |

### Docker & Infrastructure

| Command | Description |
|---------|-------------|
| `docker compose -f docker-compose.base.yml up -d` | Start only PostgreSQL & Redis |
| `docker compose -f docker-compose.base.yml down` | Stop infrastructure |
| `docker compose up --build` | Start full stack (infra + backend + frontend) |
| `docker compose down -v` | Stop and remove volumes (⚠️ deletes all data) |
| `.\docker-manage.ps1 up` \| `./docker-manage.sh up` | Start PostgreSQL & Redis (Windows/Linux) |
| `.\docker-manage.ps1 health` \| `./docker-manage.sh health` | Check health |
| `.\docker-manage.ps1 logs` \| `./docker-manage.sh logs` | Follow logs |
| `.\docker-manage.ps1 clean` \| `./docker-manage.sh clean` | Remove containers and volumes |

### Validation & Miscellaneous

- `python scripts/validate_dependencies.py` – Validate the AGENTS.md dependency graph (run from repository root).
- `cd backend && poetry run pip list` – List installed packages.
- `cd frontend && npx vitest ui` – Launch Vitest UI for interactive testing.

## Code Architecture Overview

### Backend (Python/FastAPI)

- **Architectural Style**: Clean Architecture with Domain-Driven Design (DDD), CQRS, and Event Sourcing.
- **Layers** (within `backend/src/`):
  - **Domain**: Entities, Value Objects (e.g., `Money`, `Percentage`, `PriceTarget`), domain events, repositories interfaces.
  - **Application**: Services (use cases), DTOs, application events.
  - **Infrastructure**: Implementations of repositories (SQLAlchemy), external clients (Yahoo Finance, Google Drive), API routers, authentication, background jobs.
  - **API**: FastAPI routers, request/response schemas, dependency injection.
  - **Shared**: Cross‑cutting utilities, caching, logging, configuration.
- **Persistence**:
  - PostgreSQL 16 with SQLAlchemy 2.0 (async) + AsyncPG driver.
  - Alembic for migrations (see `backend/alembic/versions/`).
  - **Event Sourcing**: The `estimate_events` table stores an immutable audit trail of every estimate change.
  - **CQRS**: Read‑optimized materialized view `estimate_summary_view` (updated via `REFRESH MATERIALIZED VIEW CONCURRENTLY`) provides sub‑5 ms dashboard queries.
- **Key Features**:
  - Rate limiting (via `slowapi` – planned for Fase 2).
  - Prometheus metrics & structured logging (Fase 2).
  - Role‑Based Access Control (RBAC) with `users`, `roles`, `user_roles` tables.
  - Background scheduling (APScheduler) for jobs like market data sync.
  - Decimal precision for monetary calculations (Python `Decimal` / `decimal.js` on frontend).

### Frontend (React 19 + TypeScript + Vite)

- **UI Library**: React with hooks (`react-hook-form`, `react-query` for server state).
- **Styling**: TailwindCSS via `@tailwindcss/vite`.
- **State Management**: React Query (`@tanstack/react-query`) for caching, background updates, and optimistic updates.
- **Financial Calculations**: `decimal.js` for exact decimal arithmetic.
- **Internationalization**: `i18next` with HTTP backend for dynamic language loading.
- **Charting**: `recharts` for financial charts.
- **Windowing**: `react-window` for large lists (e.g., ticker table).
- **Testing**: Vitest + React Testing Library + Playwright for E2E (see `e2e/` folder).
- **Structure** (`frontend/src/`):
  - `components/` – Reusable UI elements (buttons, inputs, modals, tables, charts).
  - `hooks/` – Custom React hooks (data fetching, form handling, websockets).
  - `pages/` – Route‑level components (aligned with `react-router-dom`).
  - `services/` – API client wrappers (axios instances).
  - `store/` – Global state (if any, otherwise React Query).
  - `utils/` – Helper functions (formatting, parsing, decimal helpers).
  - `locales/` – Translation JSON files for i18next.

### Infrastructure

- **Docker Compose**:
  - `docker-compose.base.yml` – PostgreSQL 16 + Redis 7 (shared network `ticker-network`).
  - `docker-compose.yml` – Adds backend and frontend services, mounts source code for hot‑reload, sets `VITE_API_TARGET=http://backend:8000`.
  - `docker-compose.prod.yml` – Production‑ready configuration (planned).
- **Google Drive Sync**: Bidirectional sync engine (see `backend/src/sync/`) using Google Drive API; state tracked via `sync_jobs` table.
- **CI/CD**: GitHub Actions workflows (`.github/workflows/ci.yml`) run lint, type check, unit tests, integration tests, security scanning (Trivy), and E2E tests (Playwright) on every push.

## Testing Guidelines

- **Backend**:
  - Unit tests live in `backend/tests/unit/`; integration tests in `backend/tests/integration/`; E2E in `backend/tests/e2e/` (if any).
  - Use `pytest` with markers (`unit`, `integration`, `e2e`, `slow`, `chaos`, `properties`).
  - Mock external services (Yahoo Finance, Google) using `httpx` or `responses`‑style fixtures; see existing tests for patterns.
  - Aim for high coverage on domain logic and services.
- **Frontend**:
  - Unit tests with Vitest + React Testing Library in `frontend/src/__tests__/` or alongside components.
  - Use `msw` (Mock Service Worker) to intercept API calls.
  - Snapshot testing for stable UI output (optional).
  - E2E tests with Playwright located in the root `e2e/` directory; run via `npx playwright test` or `npm run test:e2e` if defined.
- **Running a Single Test**:
  - Backend: `pytest tests/unit/shared/domain/value_objects/test_money.py::test_money_addition`
  - Frontend: `npm run test -- --run "estimate service creates correct decimal"` (or use Vitest's `-t` flag: `npx vitest -t "estimate service"`).
  - Docker services: use the helper script `.\docker-manage.ps1 logs` to tail logs while testing.

## Task Tracking (AGENTS.md)

- The repository uses an **Atomic Development** workflow tracked via `AGENTS.md` files:
  - Root `AGENTS.md` – Global progress tracker and dependency graph.
  - Section‑specific files: `backend/AGENTS.md`, `frontend/AGENTS.md`, `docker/AGENTS.md`, `docs/AGENTS.md`.
- Before starting work, consult the relevant `AGENTS.md` to understand the current task ID (e.g., `TASK 2.7`), its description, dependencies, and acceptance criteria.
- After completing a microstep, update the corresponding `AGENTS.md` with completion notes and move to the next task.
- Validate the dependency graph with `python scripts/validate_dependencies.py` (run from repository root) to ensure no circular dependencies and that all referenced tasks exist.

## Notes

- **Environment Variables**: Never commit real secrets. Use `.env` files (git‑ignored) and reference them in `docker-compose.yml` via `${VAR_NAME}`.
- **Hot Reload**: When using `docker compose up --build`, the backend and frontend containers mount the local source code, so changes trigger automatic reload.
- **Database Resets**: To start with a clean database (for testing), run `docker compose -f docker-compose.base.yml down -v` then bring it back up.
- **License**: MIT – see `LICENSE` file at repository root.
- **Questions**: If any part of the architecture or setup is unclear, consult the `README.md`, `Piano-Operativo-v1.7.md`, or the specific `AGENTS.md` files.

--- 

*This CLAUDE.md is intended to give future instances of Claude Code a concise yet comprehensive starting point for productive work in this repository.*