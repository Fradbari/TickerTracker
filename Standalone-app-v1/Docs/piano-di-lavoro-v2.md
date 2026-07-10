# Piano di lavoro v2 — Documento unico di governo, fase di sviluppo TickerTracker v3.0

> **Ruolo di questo file:** unico documento di governo della fase di sviluppo. Sostituisce e
> consolida `Docs/Piano-di-lavoro.md`, `Docs/Stato-avanzamento-pdl.md` (piano di armonizzazione
> doc, CHIUSO M0–M7) e `Docs/Piano-operativo-v1.7.docx` (piano operativo storico), tutti rimossi
> dal repo il 2026-07-10. Testo integrale dei file rimossi: git history (HEAD di riferimento
> `feef0f4`) + estratto testuale del docx in `Docs/archive/Piano-operativo-v1.7-estratto.md`.
>
> **Gerarchia fonti di verità (invariata):** [`CLAUDE.md`](../CLAUDE.md) = onboarding +
> invarianti architetturali · root [`AGENTS.md`](../AGENTS.md) = task ledger canonico + Progress
> Tracker · questo file = governo di fase (roadmap, regole di sessione, evidenze). Se questo file
> contraddice il ledger o il codice su disco, **vincono ledger e disco** — aggiornare questo file.
>
> **Regola di manutenzione:** ad ogni chiusura di task/azione aggiornare §1 (snapshot), §2
> (tracker consolidato) e §7 (evidenze). §7 non si cancella: si appende.

---

## §1 — Stato corrente (snapshot)

| Chiave | Valore |
|---|---|
| **Data snapshot** | 2026-07-10 |
| **Branch** | `vibe-claude` (unico branch di lavoro, vincolo utente) |
| **HEAD di riferimento** | `feef0f4` — `docs: record M7 completion — doc-harmonization plan CLOSED (M0-M7 done)` |
| **Piano armonizzazione doc** | CHIUSO — M0–M7 ✅ (storia e commit: §7.1) |
| **File `.md` tracciati** | 58 (misura raw: `rtk proxy git ls-files '*.md' \| grep -vc node_modules`, invariato dopo questo intervento: −2 file continuità, +2 nuovi: questo file + archivio) |
| **Agent-def pinnati (M7)** | `code-reviewer`=opus · `backend-dev`=opus · `frontend-dev`=sonnet · `task-planner`=sonnet · `docs-dev`=haiku (tunabile per costi) |
| **Fase corrente** | Sviluppo prodotto: chiusura MVP residuo → Sprint UX → Fase 2 (§3) |

### Output `validate_dependencies.py` (eseguito 2026-07-10, da `Standalone-app-v1/`)

```text
$ PYTHONIOENCODING=utf-8 python scripts/validate_dependencies.py
✓ 68 task caricati (+16 noti solo dal Progress Tracker)
✓ Relazioni dipendenza: 75
Task per sezione: S1=7 · S2=25 · S3=3 · S4=18 · S5=15
✅ Nessun errore critico · ✅ Nessun warning
Entry points (6): TASK 1.1, 2.1, 2.17, 2.20, 4.1, 5.14
✅ VALIDAZIONE SUPERATA — EXIT=0
```

### Analisi di sufficienza dei validatori (richiesta esplicita utente)

`validate_dependencies.py` copre **solo** il grafo dipendenze task (ID, riferimenti, cicli,
sequenze). **Non copre**: link `.md` rotti, anchor invalidi, coerenza contatori del Progress
Tracker. I check link/anchor esistevano solo come script inline nel vecchio piano (M6 step 1–2),
persi con la sua rimozione. **Rimedio deployato in questo intervento:**

- **`scripts/validate_docs.py`** (nuovo) — porta a script permanente i due check M6:
  (1) ogni link Markdown relativo verso file `.md` risolve a un file esistente (risoluzione
  relativa al file sorgente, non alla CWD); (2) ogni anchor `#...` linkato corrisponde a uno slug GitHub reale
  del file target (underscore mantenuti, emoji/punteggiatura rimossi, accenti mantenuti).
  Esclusioni: `node_modules/`, `.venv/`, `Docs/archive/` (testo storico non normativo).
  Output ASCII-only (nessun crash cp1252 su Windows). Uso: `python scripts/validate_docs.py`
  da `Standalone-app-v1/`. EXIT=0 = verde.
- **Gate pre-commit completo** (aggiornato in `CLAUDE.md` §Atomic-dev Workflow):
  `python scripts/validate_dependencies.py && python scripts/validate_docs.py`.
- **Non automatizzato** (check manuale, candidato a estensione futura del validator):
  coerenza contatori/statistiche del Progress Tracker root vs checkbox reali — oggi
  incoerenti, vedi §7.9.

---

## §2 — Progress Tracker consolidato

**Fonte canonica: root [`AGENTS.md`](../AGENTS.md) §Progress Tracker** — non duplicare là dove
si aggiorna qui e viceversa: si aggiorna **prima** il root, poi questo snapshot. Snapshot al
2026-07-10, contato dalle checkbox reali (87 checkbox totali, 68 `[x]`, 19 `[ ]`):

### Task CHIUSI (68) — sintesi per area

| Area | Task chiusi | Owner (track agent) |
|---|---|---|
| Setup & fondamenta | 1.1–1.8 (8/8) | backend-dev / frontend-dev |
| Backend core & data | 2.1–2.7, 2.10–2.24 (22) | backend-dev |
| Frontend MVP | 4.1–4.5, 4.6-hooks, 4.6–4.9, 4.11, 4.12, 4.16 (13) | frontend-dev |
| Testing base | 5.2, 5.3, 5.4, 5.6 (4) | backend-dev / frontend-dev |
| Sicurezza & observability | 3.1–3.9 (9) | backend-dev |
| Frontend advanced | 4.13, 4.14, 4.15 (3) | frontend-dev |
| Testing & CI/CD | 5.7–5.11, 5.15, 5.17 (7) | docs-dev / backend-dev |
| Docker | 3.12, 5.14 (2) | docker-dev *(def assente — fallback docs-dev)* |

Dettaglio microstep e completion-history: `backend/AGENTS.md`, `frontend/AGENTS.md`,
`Docker/AGENTS.md`, `Docs/AGENTS.md`, `backend/docs/history/`.

### Task APERTI (19) — con owner

| ID | Titolo | Track / Agente | Nota stato |
|---|---|---|---|
| 4.5b | Componenti UI Shared (Button, Input, Card, Badge, Spinner, Toast, Modal) | frontend-dev | MVP residuo |
| 4.10 | CloseEstimateModal Component | frontend-dev | MVP residuo; dipende da 4.6 ✅ |
| 5.1 | Setup Test Framework Backend | backend-dev | ⚠️ probabilmente già fatto de-facto (5.2–5.4 ✅, pytest configurato) — verificare e chiudere, §7.10 |
| TASK C | Sprint UX — Barra inferiore (indicatore Yahoo) | frontend-dev + backend-dev | ordine sprint: 1° |
| TASK D | Sprint UX — Nuova Stima / stato Finnhub | frontend-dev + backend-dev | ordine sprint: 2° |
| TASK B | Sprint UX — Admin operativa completa | frontend-dev | ordine sprint: 3° |
| TASK A | Sprint UX — System Logs unificati | frontend-dev + backend-dev | ordine sprint: 4° |
| 2.8 | Modello User e Role RBAC (auth completa) | backend-dev | Fase 2 |
| 2.9 | Modello SyncJob | backend-dev | Fase 2 — ⚠️ repo `sync_job` già citato in CLAUDE.md §Outbox: verify-first (§7.10) |
| 2.25 | Modello AiModelRun | backend-dev | Fase 2 — ⚠️ entity già esistente in `backend/src/analytics/domain/entities.py`: verify-first (§7.10) |
| 2.26 | Pattern Outbox per Eventi | backend-dev | Fase 2 — ⚠️ `OutboxProcessor` già esistente in `backend/src/infra/outbox/`: verify-first (§7.10) |
| 2.27 | API Router Analytics | backend-dev | Fase 2 — scaffolding vuoto confermato (`analytics/api/` = solo `__init__.py`) |
| 2.28 | AI Prompt Service | backend-dev | Fase 2 — *da definire* |
| 3.10 | OpenTelemetry Tracing | backend-dev | Fase 2 — *da definire* |
| 3.11 | Circuit Breaker | backend-dev | Fase 2 — *da definire* |
| 5.12 | Feature Flags | backend-dev | spec in `backend/AGENTS.md` |
| 5.13 | Backup Automatico Database | backend-dev | spec in `backend/AGENTS.md` |
| 5.5 | Property-Based Testing per P&L | backend-dev | Fase 2 testing |
| 5.16 | Documentare API con OpenAPI (export/versioning formale) | docs-dev | Fase 2 |

---

## §3 — Roadmap fasi di sviluppo rimanenti (ordinate)

Ogni step: descrizione · agente assegnato · criterio di done. Workflow per ogni step: (1)
`task-planner` verifica dipendenze e produce microstep nel track `AGENTS.md`; (2) esecuzione via
agente di track; (3) `code-reviewer` sul diff; (4) aggiornare tracker root + questo file (§1, §2,
§7); (5) gate: `validate_dependencies.py` + `validate_docs.py` verdi prima del commit.

### Fase A — Chiusura MVP (priorità massima)

| # | Step | Descrizione | Agente | Criterio di done |
|---|---|---|---|---|
| A0 | Riconciliazione tracker | Verify-first sui task sospetti già implementati (5.1, 2.9, 2.25, 2.26 — §7.10): enumerare filesystem/codice reale (regola discovery-driven: mai fidarsi dei nomi presupposti, grep di contenuto), marcare `[x]` solo con evidenza, aggiornare contatori/statistiche root `AGENTS.md` (§7.9) | task-planner | Tracker root coerente: checkbox = stato reale su disco; statistiche ricalcolate dalle checkbox; validator verde |
| A1 | TASK 4.5b | Componenti UI shared: Button, Input, Card, Badge, Spinner, Toast, Modal in `frontend/src/shared/components/` (riuso obbligatorio cross-feature, invariante CLAUDE.md) | frontend-dev | Componenti presenti + tipizzati, zero duplicati nelle feature, test Vitest, `npx tsc --noEmit` verde, `npm run test:coverage` verde |
| A2 | TASK 4.10 | CloseEstimateModal: chiusura manuale stima (exit_price, conferma, mutation via API client centralizzato, invalidazione query) | frontend-dev | Modal montato e funzionante su detail/list, usa componenti shared (A1), test componente, tsc verde |
| A3 | TASK 5.1 | Formalizzare/chiudere setup test framework backend (pytest + marker `unit/integration/e2e/slow/chaos/properties` già in `backend/pyproject.toml`) | backend-dev | Se già de-facto completo: evidenza documentata e task `[x]`; altrimenti colmare i gap (coverage config, fixtures condivise) |

### Fase B — Sprint UX (ordine vincolante: C → D → B → A)

Microstep dettagliati: `frontend/AGENTS.md` §SPRINT UX e `backend/AGENTS.md` §SPRINT UX.
Vincoli sprint: stringhe utente in italiano; mai esporre API key al frontend; riusare endpoint
esistenti (no duplicati); `ApiResponse` standard; `npx tsc --noEmit` verde dopo ogni task.

| # | Step | Descrizione | Agente | Criterio di done |
|---|---|---|---|---|
| B1a | TASK C-backend | Endpoint status esteso: timestamp ultima chiamata Yahoo + esito ultimo tentativo (riuso endpoint status esistente, no nuovo polling) | backend-dev | Status espone timestamp+esito; nessun endpoint nuovo; test |
| B1b | TASK C | Barra inferiore (`AppStatusBar.tsx`): rimuovere `Sync Now` + badge GDrive; indicatore Yahoo elapsed-time con soglie (<5m ok, 5–30m warning, >30m/fallito danger) | frontend-dev | Microstep 1–6 del track ledger soddisfatti; nessun dead code; tsc verde |
| B2a | TASK D-backend | Flag `finnhub_key_configured` nel payload config/admin, derivato da `Settings.FINNHUB_API_KEY` (SecretStr), mai serializzare il segreto | backend-dev | Flag booleano presente; segreto mai in response; test |
| B2b | TASK D | Nuova Stima (`EstimateForm.tsx`, `InsertEstimate.tsx`): banner Finnhub non configurata + CTA Admin; fallback validazione simbolo via Yahoo al blur; symbol-search reale se configurata | frontend-dev | Microstep 1–5 soddisfatti; copy italiano; tsc verde |
| B3 | TASK B | Admin operativa (`AdminSettings.tsx`): Finnhub (verifica+salvataggio senza mostrare segreto), campo GDrive folder, backup/ripristino con feedback, `PRICE_UPDATE_INTERVAL_MINUTES` reale | frontend-dev | Microstep 1–5 soddisfatti; config persistite via backend (no solo-localStorage per config di sistema); tsc verde |
| B4a | TASK A-backend | `POST /api/logs/frontend` sul router logs esistente; schema pydantic payload; stesso storage/stream dei log viewer con `source: frontend`; sanitizzazione details | backend-dev | Endpoint attivo; eventi visibili nel viewer; nessun segreto loggato; test |
| B4b | TASK A | `frontendLogger.ts` (buffer+flush fire-and-forget) + viewer con colonna/filtro `source` | frontend-dev | Eventi route/api_error/azioni-chiave inviati; viewer distingue frontend/backend; tsc verde |

### Fase C — Fase 2: Auth & advanced backend

| # | Step | Descrizione | Agente | Criterio di done |
|---|---|---|---|---|
| C1 | TASK 2.8 | User/Role RBAC completo (JWT auth; modelli base `User`/`Role` già presenti da MVP 2.7 — qui la parte auth multi-utente) | backend-dev | Auth JWT funzionante; RBAC sui router; test integration; nessun secret in chiaro |
| C2 | TASK 2.9 | Modello/repo SyncJob (verify-first: repo `sync_job` già citato come esistente) | backend-dev | Stato reale accertato; gap colmati; migrazione Alembic se serve schema |
| C3 | TASK 2.25 + 2.26 | AiModelRun + Outbox: riconciliare tracker con implementazione esistente (`OutboxProcessor`, dead-letter, retry — invarianti già in CLAUDE.md); completare solo i gap reali | backend-dev | Evidenza per ogni acceptance criterion; task chiusi o gap-list scritta nel track ledger |
| C4 | TASK 2.27 | API Router Analytics (oggi scaffolding vuoto: solo `domain/entities.py` ha contenuto) | backend-dev | Router+service+repository+schemas reali; OpenAPI aggiornata; test |
| C5 | TASK 2.28 | AI Prompt Service (*da definire* — richiede definizione requisiti con utente prima dell'esecuzione) | task-planner → backend-dev | Spec scritta e approvata nel ledger, poi implementazione con acceptance criteria propri |

### Fase D — Fase 2: Observability & resilienza

| # | Step | Descrizione | Agente | Criterio di done |
|---|---|---|---|---|
| D1 | TASK 5.12 | Feature Flags (spec in `backend/AGENTS.md`) | backend-dev | Acceptance criteria del ledger soddisfatti |
| D2 | TASK 5.13 | Backup automatico DB (spec in `backend/AGENTS.md`; runbook `database-recovery.md` da aggiornare) | backend-dev + docs-dev | Backup schedulato+testato; runbook aggiornato |
| D3 | TASK 3.10 | OpenTelemetry Tracing (*da definire*) | task-planner → backend-dev | Spec approvata, poi tracing su richieste API + job scheduler |
| D4 | TASK 3.11 | Circuit Breaker (*da definire*; candidato: provider market-data, già con caching/backoff da 2.19) | task-planner → backend-dev | Spec approvata, poi breaker su chiamate esterne con metriche |

### Fase E — Fase 2: Testing & documentazione finale

| # | Step | Descrizione | Agente | Criterio di done |
|---|---|---|---|---|
| E1 | TASK 5.5 | Property-based testing P&L (marker `properties` già definito in pyproject) | backend-dev | Proprietà su Money/Percentage/P&L (commutatività, round-trip, invarianti LONG/SHORT); suite verde |
| E2 | TASK 5.16 | OpenAPI export/versioning formale | docs-dev | Spec esportata e versionata; ogni endpoint documentato |

### Decisioni aperte (richiedono l'utente — NON eseguire senza approvazione)

| Tema | Contesto | Opzioni |
|---|---|---|
| PWA Base | Presente nel piano operativo storico (docx TASK 4.11: manifest + service worker), assente dal ledger attuale | reintrodurre come nuovo task 4.x / scartare |
| Accessibilità & skeleton i18n | Idem (docx TASK 4.12); nota: `shared/i18n/` esiste già nel tree frontend | reintrodurre / considerare assorbito / scartare |

---

## §4 — Dipendenze tecniche e vincoli architetturali

**Fonte canonica invarianti: [`CLAUDE.md`](../CLAUDE.md) §Critical Architectural Invariants** —
qui solo l'indice, non copiare: Decimal ovunque (mai float; `DECIMAL(10,4)`/`(8,4)`; VO `Money`/
`Percentage`/`PriceTarget` frozen) · API client centralizzato frontend (`shared/api/client.ts`,
no fetch diretto) · feature isolation (zero cross-import, comunicazione solo via `shared/`, sia
frontend che backend bounded contexts) · componenti shared riusati · errori via `AppErrorBoundary`
+ `useNotify` · Zod v4 `.refine()` (mai `z.coerce.number()`) · Outbox append-only
(`infra/outbox/`, max 5 retry → DEAD_LETTER, consumer idempotenti) · CQRS materialized view
(`estimate_summary_view`, refresh CONCURRENTLY ogni 5 min).

**Stack pinnato:** Python 3.11+ / Poetry / FastAPI / SQLAlchemy async / Alembic · React **18**
(`^18.2.0` da `frontend/package.json` — fonte di verità, NON 19) / Vite / TS / React Query /
decimal.js / Zod v4 · PostgreSQL 16 + Redis 7 · APScheduler.

**Grafo dipendenze dei task aperti** (completo: root `AGENTS.md` §Dettaglio Dipendenze; gate
automatico: `validate_dependencies.py`):

- 4.5b → nessun blocco (4.5 ✅); 4.10 richiede 4.6 ✅ → **entrambi liberi**.
- Sprint UX: nessuna dipendenza dal ledger numerato; ordine interno C → D → B → A; ogni task
  frontend dipende dalla propria controparte backend (B1a→B1b, B2a→B2b, B4a→B4b).
- 2.8 → 2.9, 2.25 (auth prima dei modelli Fase 2 collegati); 2.24 ✅ → 2.26; 2.12 ✅ → 2.27 → 2.28.
- 3.10, 3.11: paralleli, post-2.20 ✅ → liberi (ma *da definire*).
- 5.5 richiede 5.1 (da riconciliare in A0/A3); 5.16 libero.

**Vincoli operativi tecnici** (dettaglio: `CLAUDE.md` §Non-obvious Quirks): Alembic richiede
modelli importati in `env.py` + partial index via `text(...)` · Vitest senza `--run` appende in
watch (CI hang) · tooling Node solo in `frontend/`, Poetry solo da `backend/` · `get_settings()`
cached (`lru_cache`) — mutare `.env` + restart · Playwright alla root repo (non `frontend/`) ·
`docker-manage.*` = infra-only (backend spawn: `docker compose up --build`).

---

## §5 — Regole operative per prompt futuri (invarianti di sessione)

Valide per **ogni** sessione su questo repo, finché non revocate dall'utente:

1. **`rtk proxy git …`** per ogni verifica load-bearing (conteggi, guard, discovery, status): il
   proxy rtk intercetta `git` e può alterarne/riassumerne l'output (osservato storicamente:
   `git status --porcelain` → stringa `ok`).
2. **Root repo con spazio nel nome** (`Ticker Tracker/`): mai `cd` non quotato; usare
   `ROOT="$(rtk proxy git rev-parse --show-toplevel)"` + `git -C "$ROOT" …`.
3. **Casing cartelle solo via `git ls-files`** — mai `find`/`ls` su Windows (filesystem
   case-insensitive genera falsi positivi). Casing reale: `Docs/`, `Docker/` uppercase;
   `backend/docs/` lowercase — sono due `docs` distinti, non uniformare.
4. **Validatori con `PYTHONIOENCODING=utf-8`** su Windows (emoji → crash cp1252 in
   `validate_dependencies.py`; `validate_docs.py` è ASCII-only ma la regola resta prudente).
5. **Branch: solo `vibe-claude`.** Nessun branch nuovo senza richiesta esplicita utente.
6. **Workflow atomico** (dettaglio `CLAUDE.md`): task dal ledger root con `blockedBy` vuoto →
   `task-planner` per microstep → agente di track → tracker root aggiornato → gate validatori →
   commit. **Mai inventare un task ID. Mai saltare i validatori.**
7. **Boundary di track:** non modificare file fuori dalla propria sezione; cambi cross-track =
   un unico task tracciato nel ledger. `docker-dev` non ha def in `.claude/agents` → fallback
   `docs-dev`.
8. **Verify-first / discovery-driven:** mai marcare un task `[x]`/`[ ]` per nome presupposto —
   enumerare i file reali e cercare per contenuto (es. routing: grep `RouterProvider|<Route|path:`,
   non `ls` su cartelle presunte). Un `ls` vuoto non è prova di assenza.
9. **Azioni distruttive/load-bearing inline** dal thread principale (mai delegate a subagent);
   idempotenti e motivate (`git rm --ignore-unmatch`, check condizionali prima di agire).
10. **Commit atomici e reversibili** per step/milestone, messaggio che referenzia il task ID.
    Modalità: step-by-step con pausa per review utente, salvo diversa indicazione.
11. **Ad ogni chiusura task/azione:** aggiornare root `AGENTS.md` (tracker) + questo file
    (§1 snapshot, §2, §7 evidenze). Prima il ledger, poi lo snapshot.
12. **Modifiche ad `.claude/agents/*.md`:** solo la riga frontmatter `model:`
    (valori: opus/sonnet/haiku), mai il corpo.

---

## §6 — Prompt di ripresa (ready-to-paste per la prossima sessione)

```text
Leggi Standalone-app-v1/CLAUDE.md (onboarding + invarianti + quirks) e
Standalone-app-v1/Docs/piano-di-lavoro-v2.md (documento unico di governo:
§1 snapshot, §2 tracker consolidato, §3 roadmap, §5 regole di sessione, §7 evidenze).

Regole operative permanenti (dettaglio in piano-di-lavoro-v2.md §5):
- rtk proxy git ... per ogni verifica load-bearing;
- root repo con spazio nel nome -> mai cd non quotato, usa git -C "$ROOT";
- casing solo via git ls-files (mai find/ls su Windows);
- validatori: PYTHONIOENCODING=utf-8 python scripts/validate_dependencies.py
  && python scripts/validate_docs.py (entrambi VERDI al 2026-07-10);
- branch di lavoro: vibe-claude; mai inventare task ID; mai saltare i validatori.

Prossimo step: Fase A della roadmap (piano-di-lavoro-v2.md §3) — parti da A0
(riconciliazione tracker, agente task-planner), poi A1 = TASK 4.5b (frontend-dev).
Al termine di ogni task: aggiorna root AGENTS.md + piano-di-lavoro-v2.md §1/§2/§7.
```

---

## §7 — Evidenze, punti critici e blocchi

> **Regola:** sezione append-only, aggiornata ad ogni chiusura task/azione. Le voci risolte si
> marcano `[RISOLTO]`, non si eliminano.

### 7.1 Storia piano armonizzazione doc (CHIUSO) — riferimenti commit

M0 baseline (no commit) · M1 casing link `a82a3c0` · M2 migrazione contenuti `20d7f2e` ·
M3 CLAUDE.md `6c54bbd` · M4 gerarchia AGENTS `670cb21` · M5 cleanup 5 file `6e9241e`+`15be57c` ·
M6 verifica finale `6cda1a3` · M7 pin modelli agenti `f1b83fb` · fix validator (thread secondario)
`866a2b7`. Testo integrale del piano e dello stato: git history, es.
`rtk proxy git show feef0f4 -- "Standalone-app-v1/Docs/Piano-di-lavoro.md"` (idem
`Stato-avanzamento-pdl.md`). Decisioni permanenti già assorbite in §4/§5: cleanup conservativo;
no rename convenzione `AGENTS.md` né cartelle `Docs/`/`Docker/`; React 18 da `package.json`;
mapping modelli agenti tunabile.

### 7.2 [RISOLTO `866a2b7`] `validate_dependencies.py` — 14 errori = falsi positivi dello script

3 bug fixati (regex ID troncava suffissi `4.5b`/`4.6-hooks` → auto-cicli fantasma; `rec_stack`
non ripulito su early-return → cicli a cascata; Progress Tracker root mai parsato → task
3.1–3.9 "inesistenti"). Nessuna riga di dipendenza nei dati toccata. Rieseguito 2026-07-10:
VERDE (§1).

### 7.3 Interferenza proxy `rtk` sull'output git

Osservato storicamente output riassunto/alterato (`git status --porcelain` → `ok`; grep via rtk
tronca i risultati). Mitigazione permanente: §5.1. In questa sessione: anche `rtk grep` ha
troncato output (`[+71 more]`) — per ricerche usare i tool dedicati (Grep) o `rtk proxy`.

### 7.4 Commit anomalo `acd2a58` (rimozione `temp_estimate_body.json`)

Comparso in cronologia senza azione della sessione che lo osservò; causa non accertata (azione
utente fuori sessione o hook). Effetto pratico nullo (file già assente). Nessuna azione richiesta.

### 7.5 [APERTO] `## TASK 4.6` in `frontend/AGENTS.md` (~r.575) senza blocco metadata

Unico task con heading ma senza blocco `ID:/Area:/Fase:/Dipendenze:` — oggi risolto dal validator
solo perché `[x]` nel tracker root. Dipendenza plausibile: `TASK 4.6-hooks`; incongruenza da
chiarire: se il prerequisito fosse `4.5b` (ancora `[ ]`), perché 4.6 risulta `[x]`? Da risolvere
in **A0** con i microstep reali, non assumere.

### 7.6 [APERTO] Link `../src/...` residui nei blocchi task di `frontend/AGENTS.md`

Decine di link mal-risolti (es. r.47, 100+, 579+) fuori dallo scope del vecchio piano; NON
intercettati da `validate_docs.py` (valida solo target `.md`, non `.ts`/`.tsx`). Follow-up
docs-dev a basso rischio; candidato a estensione del validator.

### 7.7 [RISOLTO `6cda1a3`] 5 link `.md` rotti storici

Fix puntuali M6 (ALEMBIC repoint ×2, sync/infra README, shared README anchor emoji-slug, quirk
CLAUDE.md). Da M6 in poi il check è permanente via `validate_docs.py`.

### 7.8 [NUOVO 2026-07-10] Numerazione docx ≠ ledger + 2 task assenti

Il piano operativo storico (docx, ora archiviato) usa una numerazione **divergente** dal ledger:
docx 2.25=Outbox (ledger 2.26) · docx 2.8/2.9=SyncJob/AiModelRun (ledger 2.9/2.25; ledger
2.8=RBAC) · docx 3.10/3.11=ConnectionPooling/Pagination (implementati — deep-dive
`backend/docs/CONNECTION-POOL.md`/`PAGINATION.md`; ledger 3.10/3.11=OpenTelemetry/CircuitBreaker)
· docx 4.10=EstimatesList (ledger 4.6). **Mai usare il docx/archivio come fonte di ID.**
Due task del docx non esistono nel ledger attuale: **PWA Base** e **Accessibilità/i18n skeleton**
→ decisione utente in §3 "Decisioni aperte". Il docx dichiara inoltre "React 19" (errore storico
noto, verità = 18) e un "TASK 2.0 Poetry" mai formalizzato nel ledger (assorbito da 2.1).

### 7.9 [APERTO] Statistiche e contatori del tracker root incoerenti con le checkbox

La tabella "Statistiche Progresso" di root `AGENTS.md` dice **30/67 (45%)**, ma le checkbox reali
al 2026-07-10 sono **68 `[x]` / 87 totali** (Sprint UX incluso). Anche i contatori di sezione
sono stale: "Sezione 5 Base (0/5)" ma 4/5 `[x]`; "Sezione 3 (7/11)" ma 9 `[x]`; "Sezione 5
Completo (0/9)" ma 7/9 `[x]`; "Sezione 2 (21/21)" ma 22 voci; header "MVP (46 task)" vs item
reali. Da ricalcolare in **A0** (task-planner) — finché aperto, fidarsi delle **checkbox**, non
delle statistiche.

### 7.10 [APERTO] Task `[ ]` nel tracker ma probabilmente già implementati (verify-first)

Evidenze dal codice/invarianti: **2.26 Outbox** → `OutboxProcessor` esiste in
`backend/src/infra/outbox/` con dead-letter e retry (invariante CLAUDE.md); **2.25 AiModelRun** →
entity esistente in `backend/src/analytics/domain/entities.py`; **2.9 SyncJob** → repo `sync_job`
citato in CLAUDE.md §Outbox; **5.1 test framework** → 5.2–5.4 `[x]` e pytest pienamente
configurato. Riconciliare in **A0** con evidenza per acceptance criterion, senza fidarsi né del
tracker né di questa nota.

### 7.11 [NUOVO 2026-07-10] Consolidamento documentale v2 — eccezioni decadute

Con la rimozione di `Piano-di-lavoro.md`, `Stato-avanzamento-pdl.md` e del docx decadono le
eccezioni storiche M6 (grep step-3 sui 2 file di continuità; 4 falsi positivi step-1; baseline
`/tmp/tt_md_baseline.txt`). `Docs/archive/` è escluso da `validate_docs.py` (testo storico non
normativo). Conteggio `.md` tracciati: invariato a 58 (−2 +2); il docx (binario) esce dal repo ma
resta in git history.

Blocco riscontrato in esecuzione (2026-07-10): un primo `rtk proxy git add` su file nuovi sotto
`Docs/` è risultato **no-op silenzioso** (exit 0, file rimasti untracked, mostrati da `git
status` con `docs/` lowercase); il retry identico ha funzionato registrando il casing corretto.
Regola pratica aggiunta: **dopo ogni `git add`, verificare lo staging con
`rtk proxy git status --porcelain` + `git ls-files`** prima di considerare l'azione conclusa.

### 7.12 [APERTO, minore] `Docs/superpowers/plans/` citata ma non tracciata

La mappa in `Docs/AGENTS.md` cita `superpowers/plans/` come "storico", ma `git ls-files` non
mostra file tracciati sotto quel path (probabile cartella untracked/vuota). Verificare e
allineare la mappa alla prossima manutenzione docs.
