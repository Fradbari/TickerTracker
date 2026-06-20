# CLAUDE.md

Entry-point onboarding for Claude sessions on TickerTracker v3.0. Standalone FastAPI backend (Python 3.11+, Poetry, DDD/CQRS/Event Sourcing) + React 19/Vite frontend. PostgreSQL 16 + Redis. Root `AGENTS.md` is the canonical atomic-task ledger — this file is a session cheatsheet, not a task source.

## Sub-agent Roster (delegate, don't do it yourself)

| Agent | Spawn when | Touches |
|---|---|---|
| `task-planner` | Need a plan, unblocked-task selection, or dependency-graph query | none (read AGENTS.md only) |
| `backend-dev` | Any `backend/**` edit, FastAPI/SQLAlchemy/Alembic, Pytest, scheduler/job code | `backend/` |
| `frontend-dev` | Any `frontend/**` edit, React/TS/Vite, i18n, Zod schemas, Vitest | `frontend/` |
| `docker-dev` | `docker/**`, compose files, helper scripts, infra-only Docker changes | `docker/` |
| `docs-dev` | `docs/**`, markdown, runbook updates, PDF/docx conversion | `docs/` (does not exist yet — create it via task-planner) |
| `code-reviewer` | Before any commit or PR; reviews diff for correctness + reuse | diff only |
| `Explore` | Read-only search/audit across the tree when you need facts, not edits | none |

Boundary rule: do NOT modify files outside your section unless the change is explicitly part of a multi-track task agreed in `AGENTS.md`. If a backend change needs a frontend call-site update, that's one task — track it.

## Atomic-dev Workflow

1. Pick a task from root `AGENTS.md` whose `blockedBy` is empty and whose `track` matches your agent (backend/frontend/docker/docs).
2. Spawn `task-planner` to mentally walk the dependency graph and produce a microstep plan; write the microsteps into the section's `AGENTS.md` (`backend/AGENTS.md`, `frontend/AGENTS.md`, etc.).
3. Execute via the matching track agent (backend-dev / frontend-dev / docker-dev / docs-dev).
4. Update the `Progress Tracker` emoji legend in root `AGENTS.md` (pending → in-progress → done).
5. From repo root: `python scripts/validate_dependencies.py` — enforces the graph before you commit. Root `AGENTS.md` does not mention this script; the file lives at `scripts/validate_dependencies.py`.

Never invent a task ID. Never skip the validator.

## Critical Architectural Invariants

These are opinion-level rules, not derivable from the code. Violating them breaks the project.

**Decimal precision (backend):** ALL monetary calculations use Python `Decimal`. DB columns are `DECIMAL(10,4)` / `DECIMAL(8,4)`. Never `float`. Value Objects `Money` / `Percentage` / `PriceTarget` are frozen dataclasses with currency-must-match arithmetic and basis-points constructors (e.g. `Percentage.from_basis_points(100) == Decimal("0.01")`). `PriceTarget` rejects invalid LONG/SHORT configurations.

**API centralization (frontend):** All HTTP goes through `frontend/src/shared/api/client.ts`. Do not `fetch()` directly in components or features. Re-export typed wrappers (e.g. `estimatesApi.list()`) per-feature.

**Feature isolation (frontend):** Zero cross-feature imports under `frontend/src/features/*`. Features communicate only via `shared/`. The features in tree are: `admin`, `chat-ai`, `estimates`, `market-data`, `portfolio`.

**Shared component reuse (frontend):** Buttons, modals, form inputs, error boundaries, log viewer live under `frontend/src/shared/components/`. Use them; do not duplicate per feature.

**Error + notify (frontend):** Wrap app in `AppErrorBoundary` (mounted via `app/providers/index.tsx`, not directly in `App.tsx`). User-visible errors flow through a single `useNotify` hook (`shared/hooks/`) — no ad-hoc `alert()`/`console.error` UX.

**Zod v4 schemas (frontend):** Use `.refine()` for numeric coercion; do NOT use `z.coerce.number()` — it swallows nulls/empty strings silently.

**Outbox pattern (backend):** `EstimateEvent` is append-only; only `processed_at`, `retry_count`, `error` mutate. `OutboxProcessor` runs every 30s (lives in `backend/src/infra/outbox/outbox_processor.py`, NOT `backend/src/sync/` — the sync/ folder is Google-Drive sync, csv/json parsers, and `sync_job` repo only). Max 5 retries → `DEAD_LETTER` table; per-event commit isolation; mapping `CREATED/UPDATED/CLOSED → sync_estimate_to_drive`. Drive-sync consumers must be idempotent (re-delivery is safe).

**CQRS materialized view (backend):** `estimate_summary_view` enables sub-5ms dashboard reads. Refreshed via `REFRESH MATERIALIZED VIEW CONCURRENTLY` (the migration `e97b3b8578e1_…` adds the required unique index on `id` for CONCURRENT). Scheduled job `refresh_materialized_views` every 5 min. Manual script: `backend/scripts/refresh_estimate_summary_view.py`.

**Domain bounded contexts (backend):** No cross-feature imports. Communication only via `backend/src/shared/`. Mirrors the frontend rule.

## Real Layouts

**Frontend `frontend/src/`:** `app/` (providers, router), `components/{form,layout,ui}/`, `features/{admin,chat-ai,estimates,market-data,portfolio}/`, `shared/{api,components,finance,hooks,i18n,services,types,ui,utils}/`, `styles/`, `__tests__/`, `mocks/`. The old `pages/services/store/locales` scaffolding does not exist.

**Backend `backend/src/`:** `domain/`, `application/`, `infrastructure/` (with `infrastructure/outbox/`, `infrastructure/scheduler/`, `infrastructure/sync/`), `api/`, `shared/` (with `shared/schemas/`, `shared/repositories/`, `shared/core/`). Bounded contexts are organized under `domain/` and `application/`.

**Docker surface:**
- `docker-manage.ps1` / `docker-manage.sh` — thin helpers: `up`, `health`, `logs`, `down`, `clean`. Infra-only; does NOT spawn the backend.
- `docker-compose.base.yml` — db + redis only.
- `docker-compose.yml` — adds backend (line 60 `backend:` block), depends on db + redis.
- `docker-compose.prod.yml` — production overrides.
- Plain `docker compose up --build` from repo root WILL spawn backend + db + redis.

## Non-obvious Quirks

- **Alembic:** `alembic revision --autogenerate` requires models imported in `env.py`; `target_metadata = Base.metadata` (not `None`); `script_location = alembic` (relative to `backend/`); partial indexes use raw `text("status = 'OPEN'")` since Alembic can't render Enum partial-index expressions.
- **Vitest watch mode:** `npm run test` (no `-- --run`) enters watch and hangs CI — use `npm run test:coverage` or pass `--run`.
- **Frontend root vs `frontend/`:** install/run Node tooling inside `frontend/`. Backend Python lives in Poetry venv managed from `backend/`. Mixed installs at repo root are wrong.
- **Pytest markers:** `unit`, `integration`, `e2e`, `slow`, `chaos`, `properties` (defined in `backend/pyproject.toml` `[tool.pytest.ini_options]`). Run a single test with `pytest backend/tests/path/test_x.py::test_y -m unit` or via `make test TEST=...` in `backend/Makefile`.
- **e2e/ at repo root:** Playwright suite lives at repo root (`playwright.config.ts`) — not under `frontend/`. There is no `test:e2e` npm script; the root `package.json`'s `test` is a stub.
- **Settings cache:** `get_settings()` is `@lru_cache`-d. Secrets use Pydantic `SecretStr`. Mutate `.env`/restart — never expect a second call to differ.

## Things That Were Wrong Before — Do Not Perpetuate

- No `LICENSE` file at repo root (only sub-package licenses exist).
- `docs/AGENTS.md` does not exist. The "Docs" link in root `AGENTS.md` is a stale placeholder.
- `docs/Piano-operativo-v1.7.md` does not exist; only `docs/Piano-operativo-v1.7.docx` does.
- `AppErrorBoundary` is mounted by `app/providers/index.tsx`, not by `App.tsx` or `main.tsx`.
- Outbox + dead-letter logic is in `backend/src/infra/outbox/`, not `backend/src/sync/`.

## Quick References

- **Backend commands:** see `backend/Makefile` (`make <target>`) and `backend/pyproject.toml` scripts.
- **Frontend commands:** see `frontend/package.json` scripts (`dev`, `build`, `preview`, `test`, `test:coverage`, `lint`, `type-check`).
- **Root AGENTS.md (task ledger + dependency graph + Progress Tracker):** `AGENTS.md` at repo root.
- **Per-section agent memory:** `backend/AGENTS.md`, `frontend/AGENTS.md`, `docker/AGENTS.md`. (`docs/AGENTS.md` is referenced but does not exist.)
- **Dependency validator:** `python scripts/validate_dependencies.py` from repo root.

## Doc Ownership Map

| Topic | Owner | Path |
|---|---|---|
| Quick Start / docker-compose how-to | README.md | `README.md` |
| Father DB / env file recipes | `.env.example` + `docker-compose*.yml` comments | repo root + `docker/` |
| Atomic-dev task ledger + Progress Tracker | root AGENTS.md | `AGENTS.md` |
| Backend invariants / completed-task history | backend agent memory | `backend/AGENTS.md` |
| Frontend invariants / completed-task history | frontend agent memory | `frontend/AGENTS.md` |
| Docker surface details | docker agent memory | `docker/AGENTS.md` |
| Project status snapshot (was ~60 lines here) | sibling PROJECT_ANALYSIS.md | `PROJECT_ANALYSIS.md` |
| Operational runbooks | docs/runbook/ | `docs/runbook/` |
| Piano operativo (business plan, docx) | docs/ | `docs/Piano-operativo-v1.7.docx` |

If something here contradicts a file on disk, the file on disk wins — update this file.
