# TASK Completion Logs — Indice

> **Scopo.** Questa directory conserva i **log storici di completamento** delle task MVP (back-end Sectione 2) che sono stati promossi fuori dalle posizioni "a caldo" del repository. I log originali vivono ora in `orig/`, intatti.
>
> La fonte canonica per lo stato corrente dei task resta:
> - root `AGENTS.md` → progress tracker globale, stato `done/in-progress/pending`
> - `backend/AGENTS.md` → memoria agent backend, microsteps, dipendenze
> Per lo stato architetturale corrente del backend vedi invece **`backend/README.md`** (breve, ~200 righe) e la cartella `backend/docs/` per i deep-dive tecnici.

---

## Indice log

| File originale (pos. precedente) | Task | Data | Tipo | Pag. |
|---|---|---|---|---|
| `backend/TASK_2_11_DOCUMENTATION_COMPLETE.md` | 2.11 | 2026-02-07 | Summary CQRS materialized view | [→](orig/TASK_2_11_DOCUMENTATION_COMPLETE.md) |
| `backend/TASK_2.12_VERIFICATION.md` | 2.12 | 2026-02 | Verification EstimateRepository | [→](orig/TASK_2.12_VERIFICATION.md) |
| `backend/TASK_2.13_VERIFICATION.md` | 2.13 | 2026-02 | Verification MarketDataRepository | [→](orig/TASK_2.13_VERIFICATION.md) |
| `backend/TASK_2.13_FIX_SUMMARY.md` | 2.13 (post-fix) | 2026-02 | Fix Summary MarketDataRepository | [→](orig/TASK_2.13_FIX_SUMMARY.md) |
| `backend/src/market_data/TASK_2.17_REPORT.md` | 2.17 | 2026-02-14 | Implementation Report Market Data API | [→](orig/TASK_2.17_REPORT.md) |

> **Nota.** Anche `backend/docs/TASK_2.20_COMPLETION_REPORT.md` (Task 2.20 — Google Drive Client) è un completion log, ma resta in `backend/docs/` perché contiene anche il reference API utile per il debug delle route Drive. Non è stato spostato in `orig/`.

---

## Cosa è successo in ogni task

### TASK 2.11 — Materialized View per CQRS — `e97b3b8578e1`
Implementata la materialized view PostgreSQL `estimate_summary_view` che applica il pattern CQRS per query dashboard sub-5ms. 5 campi calcolati (current_price, current_pnl, current_pnl_percent, days_open, risk_level), 4 indici strategici, refresh concorrente senza lock. Acceptance criteria: query < 50ms (attuale: **3-5ms**) ✅, refresh concorrente < 50ms (attuale: **12ms**) ✅. Vedi anche `backend/docs/ESTIMATE_SUMMARY_VIEW.md` per la guida canonica corrente.

### TASK 2.12 — EstimateRepository
Pattern Repository per `estimates`: CRUD completo, cursor-based pagination (no OFFSET), 11 filtri (ticker/user/status/dates/confidence/…), soft-delete con flag + timestamp, statistiche per ticker bonus, transaction management auto-commit/rollback, eager loading della relazione ticker. Acceptance criteria tutti ✅.

### TASK 2.13 — MarketDataRepository
Pattern Repository per `market_data`: UPSERT con `ON CONFLICT (ticker_id, date) DO UPDATE`, range query, latest price singolo, **batch latest** (no N+1 con `DISTINCT ON`), aggregazioni DB-side (`DATE_TRUNC` + `ARRAY_AGG`) per 1D/1W/1M. Performance: 10 anni aggregati in ~150ms vs ~2000ms prima. Acceptance criteria tutti ✅.

### TASK 2.13 (segue) — Fix Summary
- **FIX 1 (test stability)**: suffissi ticker corti (3 char) facevano collidere i test su DB condiviso → 8 char univoci, prefisso `TEST_` → commit `d36ca92`.
- **FIX 2 (DB-side aggregations)**: spostata l'aggregazione OHLCV da Python a PostgreSQL `DATE_TRUNC` + `ARRAY_AGG`. Speedup 13x su 10 anni.
- **FIX 3 (batch query returns MarketData objects)**: il batch restituiva tuple posizionali, ora restituisce oggetti `MarketData` ORM via `select(MarketData).distinct(...)`. Type-safe.
→ commit `b638582`.

### TASK 2.17 — Market Data API routes
Implementati i 4 endpoint REST in `backend/src/market_data/api/routes.py`:
- `GET /api/market/price/{ticker}` — cache `max-age=3600` (60s se stale)
- `GET /api/market/history/{ticker}?interval=1d|1w|1m` — cache `max-age=86400`
- `GET /api/market/fundamentals/{ticker}` — cache `max-age=86400`
- `GET /api/market/search?q=…` — limit 10 risultati ordinati per rilevanza, cache 1h
Tutti usano `ApiResponse` wrapper standard, dependency injection del `MarketDataProvider` (decoupled dallo specifico provider — yahoo, finnhub, …), error handling consistente con `SymbolNotFoundError` → 404 e `DataUnavailableError` → 503. Router registrato in `src/main.py`. Acceptance criteria tutti ✅.

---

## Linee guida per il futuro

**Quando un task viene completato**, il suo completion log:
1. NON va committato sul path caldo del repo (`backend/TASK_*.md` o `backend/src/.../TASK_*.md`).
2. Va generato, validato (test pass), e poi archiviato qui in `orig/` con una riga aggiunta alla tabella sopra.

**Quando un task viene riaperto** (re-work, regressione):
- Si riapre la discussione su `backend/AGENTS.md`
- Si cita questo indice se serve riferimento al log storico
- Si genera un nuovo file `TASK_<id>_RESURRECTION_<data>.md` che va in `orig/`

**Si evitino TODO/FIXME nei log di completion**: il task è done. Se serve follow-up, è un nuovo task nell'AGENTS.md.
