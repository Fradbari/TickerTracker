# Alembic Workflow — Task 2.10

Migrazioni database asincrone (asyncpg). Source of truth: `alembic/versions/`.

## Comandi comuni

Tutti i comandi vanno lanciati da `backend/` con `.venv` attivo.

```bash
# Stato corrente
alembic current

# Applica tutte le migration pendenti
alembic upgrade head

# Rollback di una sola migration
alembic downgrade -1

# Cronologia in ordine
alembic history --verbose

# Genera una nuova migration (autogenerate)
alembic revision --autogenerate -m "add new column"
```

## ⚠️ Gotcha autogenerate

Per funzionare serve che **tutti i modelli siano importati** in `alembic/env.py`, e che `target_metadata = Base.metadata` (NON `None`). Senza questo, autogenerate non vede nessuna tabella e produce file vuoti.

Per le partial indexes con espressioni su Enum (`status = 'OPEN'`), Alembic non rende l'espressione: usare `text("status = 'OPEN'")` raw.

## Migrazioni correnti

| Revision | Descrizione |
|---|---|
| `f9f513c6220d` | Schema iniziale: 10 tabelle core (tickers, market_data, estimates, estimate_events, sync_jobs, users, roles, user_roles, ai_model_runs, + audit) |
| `e97b3b8578e1` | Materialized view `estimate_summary_view` (CQRS) + 4 indici, incluso UNIQUE su `id` (richiesto per `REFRESH MATERIALIZED VIEW CONCURRENTLY`) |

Vedi `backend/docs/ESTIMATE_SUMMARY_VIEW.md` per i dettagli della migration CQRS.

## Scripting manuale

Refresh materialized view:

```bash
# Concurrent (no lock, raccomandato in prod)
python scripts/refresh_estimate_summary_view.py

# Con statistiche post-refresh
python scripts/refresh_estimate_summary_view.py --stats

# Standard con lock (più veloce, ferma letture)
python scripts/refresh_estimate_summary_view.py --no-concurrent
```

## ⚠️ Schema corrotto durante i test

Se vedi `relation "market_data" does not exist` in test:

```bash
alembic upgrade head
```

Se rimane:

```bash
# Ricostruisci da zero (dev only, distrugge i dati)
alembic downgrade base
alembic upgrade head
```

## File chiave

- `alembic.ini` — config (SQLAlchemy URL letto da env)
- `alembic/env.py` — importa modelli, configura asyncpg
- `alembic/script.py.mako` — template per nuove migration
- `alembic/versions/` — file di migration auto-generati
