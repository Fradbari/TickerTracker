# Piano di lavoro — Armonizzazione documentazione `.md` TickerTracker v3.0

> **Provenienza:** copia integrale, alla data indicata, del piano approvato in modalità Plan Mode e salvato localmente in `C:\Users\francesco.dilecce\.claude\plans\caveman-using-superpowers-role-programm-mellow-sketch.md`. Questo file **non è** `Docs/HANDOFF.md` (quel file è uno degli oggetti che il piano stesso migra e poi elimina in M5) — è la copia di lavoro persistita nel repo per continuità cross-sessione.
> **Stato di avanzamento:** vedi `Docs/Stato-avanzamento-pdl.md`, aggiornato ad ogni milestone.
> **Copiato il:** 2026-07-01, dopo il completamento di M1.
> **Stato milestone (aggiornato 2026-07-03):** M0–M6 ✅ completate e committate — M1 `a82a3c0` · M2 `20d7f2e` · M3 `6c54bbd` · M4 `670cb21` · M5 `6e9241e`+`15be57c` · M6 `6cda1a3` — **M7 ⏳ prossima (ultima)**. Il corpo sottostante è la copia storica del piano approvato (non riscritta); deviazioni motivate ed eccezioni attive (guard 58 non 56; eccezioni M6 step-1/step-3 per i 2 file di continuità) vivono in `Stato-avanzamento-pdl.md` §8. **`validate_dependencies.py`**, FAIL pre-esistente e fuori scope al momento di M6, è stato **risolto e committato in thread secondario** (`866a2b7`, 3 bug nello script, dati `AGENTS.md` intatti — ora VERDE; dettaglio in `Stato-avanzamento-pdl.md` §8). Prossimo step fuori piano: chip aperto per aggiungere blocco metadata a `TASK 4.6` in `frontend/AGENTS.md` (§8).

---

# Armonizzazione documentazione `.md` — TickerTracker v3.0

## Context

La repo `Standalone-app-v1/` contiene **60 file `.md`** di progetto (esclusi `node_modules`/`.venv`), accumulati in più sessioni di refactor doc. La documentazione è frammentata e parzialmente incoerente: link con casing rotto, un piano `.cursor` ormai stale, sezioni duplicate tra `CLAUDE.md` e root `AGENTS.md`, bug documentali noti (HANDOFF §3), e una sprint-spec standalone (`agents-sprint-fix.md`) fuori dal task ledger.

Obiettivo: ridurre a **3 classi documentali** chiare e non ridondanti — (1) `CLAUDE.md` fonte unica di onboarding/invarianti, (2) gerarchia `AGENTS.md` (root + 4 track) come task ledger atomico che richiama esplicitamente gli agenti `.claude/agents`, (3) cleanup mirato dei file obsoleti dopo migrazione dei contenuti utili. Mantenendo intatti i deep-dive tecnici, i runbook e i README (decisione utente: **conservativo**).

Decisioni utente che vincolano il piano:
- **Cleanup conservativo** — si eliminano solo obsoleti/ridondanti; si mantengono `backend/docs/` (15 deep-dive), `Docs/runbook/` (8), tutti i README.
- **Mantieni la convenzione `AGENTS.md`** — niente rename in `AGENTS-BACKEND.md`: i 5 agenti in `.claude/agents/*.md` leggono `backend/AGENTS.md`, `frontend/AGENTS.md`, ecc. per nome esatto. Rinominare li romperebbe.
- **Mantieni `Piano-operativo-v1.7.docx`** — unico business plan, binario, referenziato dalla Doc Map.

---

## Phase 1 — DISCOVERY: mappa documentale (AS-IS)

Inventario completo (60 `.md` progetto). Categorie e ridondanze:

| Classe target | File | Stato / ridondanza |
|---|---|---|
| **1 · Entry point** | `CLAUDE.md` | Buono. r.1 "React 18/Vite" è **corretto** (`frontend/package.json` = react ^18.2.0). Doc Map usa path lowercase ma cartelle su disco sono `Docs/`,`Docker/`. |
| **2 · Ledger root** | `AGENTS.md` (root) | Buono come ledger. Ridondante: §"Regole Globali" (duplica CLAUDE invarianti), §"Risorse Utili", §"Support". Bug: Progress Tracker incoerente (sez. Frontend MVP vs checklist). NON richiama gli agenti `.claude/agents`. |
| **2 · Track** | `backend/AGENTS.md`, `frontend/AGENTS.md`, `Docker/AGENTS.md`, `Docs/AGENTS.md` | Owner microstep per track. Bug: `Docs/AGENTS.md:30` backtick non chiuso; `frontend/AGENTS.md:22-23` path `../src` errato (va `./src`). Non nominano esplicitamente l'agente di track. |
| **Mantieni (deep-dive dev)** | `backend/docs/*.md` (15: API-REFERENCE, SECURITY, SCHEDULER, ALEMBIC, PAGINATION, METRICS, LOGGING, HEALTH, ENCRYPTION, VALIDATION, CONNECTION-POOL, DATA-QUALITY, LINEAGE, MARKET_DATA_PROVIDER, ESTIMATE_SUMMARY_VIEW) | OK. Owner = Doc Map. Mancano back-link → runbook (WP6, 4 file). |
| **Mantieni (history)** | `backend/docs/history/TASK-COMPLETION-LOGS.md` + `history/orig/*` (6 TASK_* + README) | OK. Archivio completion logs. |
| **Mantieni (ops)** | `Docs/runbook/*.md` (8: README, CONTACTS, startup-shutdown, database-recovery, drive-sync-issues, monitoring, scaling, yahoo-outage) | OK. TASK 5.15. `monitoring.md` ha endpoint stale `/api/v1/metrics`→`/metrics`. |
| **Mantieni (README)** | root `README.md`, `backend/README.md`, `frontend/README.md`, `Docker/README.md`, `e2e/README.md`, + 6 README di modulo (`backend/src/...`, `frontend/src/shared`) | OK. root README r.42 dice "React 18"; r.241 link a `agents-sprint-fix.md` (da aggiornare dopo cleanup). |
| **Mantieni (reference)** | `backend/src/sync/infra/COLUMN_MAPPING.md` | OK. Referenziato da backend/AGENTS.md. |
| **ELIMINA (dopo migrazione)** | `.cursor/plans/armonizzazione_md_docs_9e122796.plan.md` | **Stale**: descrive 11 nested AGENTS.md inesistenti (esistono solo 5) e lavoro HANDOFF già fatto. Nulla da migrare. |
| **ELIMINA (dopo migrazione)** | `Docs/HANDOFF.md` | Handoff di sessione. Contiene work pendente (BUG-1..4, WP5-7) da **eseguire**, non migrare; Storico Sessioni + comandi duplicano README/CLAUDE. |
| **ELIMINA (dopo migrazione)** | `Docs/agents-sprint-fix.md` | Sprint UX attivo (TASK C/D/B/A). Migrare i task nel ledger (root + frontend/backend AGENTS.md) poi eliminare. |
| **ELIMINA (dopo migrazione)** | `Docs/PROJECT-STATUS.md` | Snapshot storico 2026-06-13 + delta log. Migrare delta ancora validi in CLAUDE §"Things That Were Wrong", poi eliminare. |
| **ELIMINA (dopo migrazione)** | `backend/SETUP_GUIDE.md` | Path clone **stale** (`…\AI Studio\…`); setup Windows **già** coperto da `backend/README.md`. Foldare solo delta accurato (scarta il path stale), poi eliminare. |
| **Scope limitato** | `.claude/agents/*.md` (5) | Corpo **non toccato**; solo il campo frontmatter `model:` aggiornato in **M7** (tuning modelli). Oggi tutti `model: inherit`. |
| **Fuori scope** | `.github/deprecated_copilot_models_priority.md`, `Docs/Piano-operativo-v1.7.docx` | Non toccare (docx = business plan mantenuto). |

---

## Phase 2 — TO-BE: architettura target

Gerarchia a livelli, regola d'oro = *se un'info vive in un livello, i superiori la linkano, non la copiano*:

```
CLAUDE.md            (classe 1) onboarding + invarianti + Doc Map + roster agenti
  └─ AGENTS.md root  (classe 2) task ledger + Progress Tracker + guida ai 4 track + richiamo .claude/agents
       ├─ backend/AGENTS.md   microstep backend  → agente backend-dev
       ├─ frontend/AGENTS.md  microstep frontend → agente frontend-dev
       ├─ Docker/AGENTS.md    microstep docker   → agente docker-dev (def assente: vedi nota)
       └─ Docs/AGENTS.md      microstep testing/CI/runbook → agente docs-dev
  └─ Mantieni: backend/docs/ (dev) · Docs/runbook/ (ops) · README · docx
```

Nota agenti (no ambiguità): `.claude/agents/` contiene 5 def reali (`backend-dev`, `frontend-dev`, `docs-dev`, `task-planner`, `code-reviewer`). **`docker-dev` è citato in CLAUDE.md/HANDOFF ma il file def NON esiste.** Regola di risoluzione: dove manca un agente dedicato, nominarlo seguito dal fallback esplicito a un agente noto. Caso concreto: `Docker/AGENTS.md` nomina l'agente come **`docker-dev` (agent def assente — fallback: `docs-dev`)**. Non creare nuovi agenti non richiesti.

---

## Phase 3 — ESECUZIONE: milestone (atomiche, riprendibili, 1 commit per milestone)

Lavorare **direttamente sul branch corrente `vibe-claude`** (nessun branch nuovo). Ogni milestone = 1 commit reversibile. **Nessuna eliminazione prima di M5**, e solo dopo aver verificato che la migrazione (M2) è completa. Esecuzione delegabile all'agente `docs-dev`.

> **Decisione casing (verificata, no rinomina)**: le cartelle-doc top-level restano **`Docs/` e `Docker/` (uppercase)**. Verifica eseguita: nessun `Dockerfile`, `docker-compose*.yml`, `docker-manage.*`, workflow CI, script o codice le referenzia (build context = solo `./backend`, `./frontend`; `backend/.dockerignore: docs/` riguarda `backend/docs/` lowercase; `docker/…-action@v*` sono nomi di GitHub Action, non path). Quindi si normalizzano i **link** al casing reale su disco — niente rename, zero impatto Docker. La normalizzazione link (M1) precede ogni edit di contenuto, così CLAUDE/AGENTS scrivono subito link corretti e M6 non trova rotture.
>
> **Casing reale su disco (rispettare nei link):** top-level `Docs/`, `Docker/` = **uppercase**; annidata `backend/docs/` = **lowercase**. Sono due `docs` distinti: non uniformare.

### M0 — Setup + baseline
- Confermare `git status` clean su `vibe-claude`. Nessun branch nuovo.
- Registrare baseline conteggio `.md` **tracciati**, **eseguendo dalla root della repo** (`Ticker Tracker/`) — obbligatorio: uno dei 5 file da rimuovere (`.cursor/plans/…plan.md`) sta **fuori** da `Standalone-app-v1/`; un baseline preso dalla subdir lo escluderebbe e il guard `N−5` reggerebbe per ragioni sbagliate. Comando: `git ls-files '*.md' | grep -vc node_modules` → valore **N** (`git ls-files` deterministico; `find` conteggerebbe cache untracked tipo `.pytest_cache/README.md`). Annotare nel commit M0: `[baseline: N md tracciati]`. (Discovery: N = 61, di cui 54 sotto `Standalone-app-v1/` + 7 fuori — i 5 agenti `.claude/agents`, `.cursor/plans/…`, `.github/…`.)
- Il guard di M5 usa la **stessa CWD = root repo**: atteso **N−5**.
- **Verificato:** `.cursor/plans/…plan.md` è **tracciato** e **non** in `.gitignore` (`git check-ignore` → not ignored) → rientra in N; N reale misurato = **61**, guard M5 = **56**.
- ⚠️ **RTK proxy — rischio sulle verifiche:** in questa repo un proxy `rtk` intercetta `git` e può alterare/riassumere l'output (osservato: `git status --porcelain` ha restituito `ok`). Le verifiche load-bearing (baseline N, guard `N−5`, grep di M1/M6, check temp-file) vanno eseguite **raw** con `rtk proxy git …` per evitare falsi risultati.
- Salvare la **lista baseline** (non solo il conteggio) in un file **fuori dalla repo**: `BASE="/tmp/tt_md_baseline.txt"` (Git Bash su Windows mappa `/tmp`; in alternativa la scratchpad di sessione dell'agente esecutore). **Mai** sotto `Ticker Tracker/` (verrebbe conteggiato/committato, falsando il guard). Poi: `rtk proxy git ls-files '*.md' | grep -v node_modules | sort > "$BASE"`. Serve al guard-lista di M5: il solo conteggio `N` non rileva uno swap ("rimosso deep-dive X, aggiunto Y" → resta N−5); la lista sì.

### M1 — Normalizzazione casing dei LINK (no rinomina cartelle)
- Passata su tutti i `.md` mantenuti: ogni link verso le cartelle-doc top-level usa `Docs/` / `Docker/` (uppercase). Es. in `CLAUDE.md`, root `README.md`, root `AGENTS.md`: `](./docs/` → `](./Docs/`, `](./docker/` → `](./Docker/`. **Lasciare invariati** i link a `backend/docs/` (lowercase corretto).
- **Done criterion M1** (link-target-aware): filtrare per **contenuto del link**, non per path del file sorgente. Il vecchio `grep -v 'backend/docs'` sull'intera riga escludeva erroneamente i **file sorgente** dentro `backend/docs/` (un link mal-cased scritto lì sarebbe sfuggito). Uso `-h` (toglie il prefisso file) così il filtro colpisce solo i **link-target** legittimi. Da `Standalone-app-v1/`:
  ```bash
  grep -rhoE '\]\((\.{0,2}/)*(docs|docker)/[^)]*' --include='*.md' . | grep -v 'backend/docs' | sort -u
  ```
  → **0 righe** (nessun link lowercase verso le top-level `Docs/`/`Docker/`). Se >0, ri-eseguire con `grep -rnoE …` (senza `-h`) per localizzare. **Copertura:** il grep gira su **tutti** i `.md` (`-r … .` da `Standalone-app-v1/`) → include i sorgenti in `frontend/`, `Docs/runbook/`, ecc. La regex `(\.{0,2}/)*(docs|docker)/` matcha `docs`/`docker` solo se **direttamente** dopo sequenze `./`/`../` (riferimento top-level-relativo): un link legittimo `](../../backend/docs/x.md)` **non** matcha affatto (`backend/` precede `docs/`) → né falso positivo né escluso per sbaglio; un link mal-cased `](../../docs/x.md)` da dentro `frontend/src/shared/` **viene** segnalato. **Verifica autorevole del casing:** lo step 1 di M6 su filesystem **case-sensitive** (CI Linux) segnala i link mal-cased come rotti (`os.path.exists` fallisce); su Windows (case-insensitive) passerebbero.
- **Perché il check è solo su `*.md`:** non si rinomina alcuna cartella, quindi i file non-`.md` non vanno toccati. Verificato (grep) che nessuno dipende comunque dalle top-level `Docs/`/`Docker/`: compose ×3 (build context `./backend`,`./frontend`), Dockerfile ×2 (`COPY . .` nei context), **`docker-manage.ps1`/`.sh` (solo `docker-compose.base.yml`)**, CI `cd.yml` (`docker/…-action` = nomi action), codice/URL. Unico match `backend/.dockerignore: docs/` = `backend/docs/` lowercase → invariato.

### M2 — Migrazione contenuti (NESSUNA cancellazione)
Estrarre il valore residuo dei file che M5 eliminerà, verso i target:
- Da `Docs/HANDOFF.md`: ogni item pendente è assegnato a un milestone con file/riga target (**Done criterion HANDOFF** — niente "fatto generico"; non basta scrivere una riga qualsiasi):
  | Item HANDOFF | Milestone | Target |
  |---|---|---|
  | BUG-1 Progress Tracker incoerente | M4 | root `AGENTS.md` (sez. "Frontend MVP" vs checklist), verificando i componenti reali in `frontend/src/features/*/components/` |
  | BUG-2 backtick non chiuso | M4 | `Docs/AGENTS.md:30` |
  | BUG-3 path `../src` errato | M4 | `frontend/AGENTS.md:22-23` (`../src` → `./src`) |
  | BUG-4 SETUP_GUIDE path stale | M2 | fold **solo** step unici&accurati; **scarta** il path clone stale `…\AI Studio\…` (è il bug); `backend/README.md` copre già Windows |
  | WP5 dedup invarianti | M4 | root `AGENTS.md` (rimuovi §"Regole Globali"/"Risorse Utili"/"Support") |
  | WP6 back-link runbook | M4 | `backend/docs/{HEALTH,METRICS,LOGGING,SCHEDULER}.md` |
  | WP7 versione React | M3 + M4 | **Deriva da `frontend/package.json`** (verificato `^18.2.0` → React **18**). Correggi le occorrenze **errate** '19'→'18'; NON toccare le '18' già corrette |
  Sprint-UX coperto dal bullet seguente — **non duplicarlo** (non esiste alcun `MEMORY.md` di progetto; non crearne).
  - **Verifica igiene-sigle (post-M4) — NON è prova di implementazione:** `grep -n "BUG-[1-4]\|WP[567]" Standalone-app-v1/AGENTS.md Standalone-app-v1/CLAUDE.md` → **0** garantisce solo che le sigle HANDOFF non restino appiccicate nei target (vivono solo in `HANDOFF.md`, che M5 elimina). **Attenzione:** questo grep passerebbe a 0 anche se WP6/WP7 non fossero mai stati scritti — WP6 vive in `backend/docs/`, WP7 in `README.md`, non in AGENTS/CLAUDE. L'avvenuta **implementazione** di ogni item è coperta dal proprio done-criterion, non da questo grep:
    | Item | Done criterion (dove) |
    |---|---|
    | BUG-1 | M4 — check discovery-driven filesystem ↔ due sezioni |
    | BUG-2 / BUG-3 | M4 — edit a riga target (`Docs/AGENTS.md:30`, `frontend/AGENTS.md:22-23`) |
    | BUG-4 | M2 — `grep -c "AI Studio" backend/README.md` = 0 (path stale non migrato) + fold ragionato; README già copre Windows |
    | WP5 | M4 — assenza §"Regole Globali"/"Risorse Utili"/"Support" in root `AGENTS.md` |
    | WP6 | M4 — `grep -lE "runbook/(monitoring\|yahoo-outage)" …HEALTH/METRICS/LOGGING/SCHEDULER.md \| wc -l` = 4 |
    | WP7 | Versione da `frontend/package.json` = React **18**. `grep -rn "React 19" --include='*.md' Standalone-app-v1` = 0 (corrette le '19' errate); **NON** toccare le '18' già giuste |
- Da `Docs/agents-sprint-fix.md`: trasporre i 4 task. **Done criterion M2 (vincolante, non ambiguo):**
  1. In root `AGENTS.md`, nuova §"Sprint UX" con 4 checkbox: `- [ ] TASK C — Barra inferiore`, `- [ ] TASK D — Nuova Stima/Finnhub`, `- [ ] TASK B — Admin operativa`, `- [ ] TASK A — System Logs`.
  2. In `frontend/AGENTS.md`, per ogni TASK un blocco microstep con **file/riga target**: TASK C → `frontend/src/components/layout/AppStatusBar.tsx`; TASK D → `features/estimates/components/{EstimateForm,InsertEstimate}.tsx`; TASK B → `features/admin/components/AdminSettings.tsx`; TASK A → viewer System Logs + nuovo `shared/services/frontendLogger.ts`.
  3. In `backend/AGENTS.md`, le parti backend: flag `finnhub_key_configured` (router config/admin), endpoint `POST /api/logs/frontend`, timestamp ultima chiamata Yahoo su endpoint status.
  - **Verifica (da `Standalone-app-v1/`) — quantità + qualità:**
    - *Quantità* (entrambi devono passare): root `grep -c "TASK [CDBA]" AGENTS.md` → **≥ 4** (le 4 checkbox §Sprint UX); track `grep -c "TASK [CDBA]" frontend/AGENTS.md` → **≥ 4**. Se i task fossero solo in uno dei due file, un conteggio < 4 fa fallire correttamente.
    - *Qualità* (blocca il failure silenzioso più probabile): `grep -c` conta occorrenze, **non** blocchi reali — "TASK C" ripetuto in prosa passerebbe.
      - Frontend — file target attesi: `grep -cE "AppStatusBar|EstimateForm|InsertEstimate|AdminSettings|frontendLogger" frontend/AGENTS.md` → **≥ 4**.
      - **Backend** (M2 prescrive anche blocchi backend, facili da dimenticare: il check frontend ≥4 passerebbe comunque): `grep -cE "finnhub_key_configured|/api/logs/frontend|[Yy]ahoo" backend/AGENTS.md` → **≥ 2**.
      - **Spot-check manuale obbligatorio (simmetrico frontend + backend):** il `grep -c` conta occorrenze ovunque, incluse note/commenti — l'errore silenzioso tipico è scrivere "vedere anche `/api/logs/frontend`" in una nota introduttiva invece di un microstep. Confermare a mano che:
        - *frontend*: ognuno dei 4 blocchi ha un path `.tsx`/`.ts` target + microstep;
        - *backend*: ogni item è un **microstep strutturato** (metodo+endpoint / flag + router/file target), non una menzione di passaggio: `POST /api/logs/frontend` con file router, `finnhub_key_configured` sul router config/admin, timestamp Yahoo sull'endpoint status.
- Da `Docs/PROJECT-STATUS.md`: spostare i delta ancora veri e non già presenti **sotto l'heading esatto già esistente** in `CLAUDE.md` — `## Things That Were Wrong Before — Do Not Perpetuate` (verificato presente). **Non** crearne uno con nome diverso/troncato: un heading variante genererebbe uno slug diverso e romperebbe eventuali link `#things-that-were-wrong-…`.
- Da `backend/SETUP_GUIDE.md`: `backend/README.md` copre **già** il setup Windows (venv `Activate.ps1`, PowerShell, righe 23/33/39/…). Foldare solo eventuali step unici&accurati; **scartare** il path clone stale `…\AI Studio\…` (è BUG-4) e i pin obsoleti (migration head, pydantic). Done-criterion: `grep -c "AI Studio" backend/README.md` = **0**; niente grep-parola su 'windows' (già presente).

> ⚠️ **Ownership M2 vs M4 (evita sovrascritture cross-sessione su file condivisi)**: `root AGENTS.md` e i track `*/AGENTS.md` sono toccati sia in M2 sia in M4. Confine netto:
> - **M2 scrive SOLO** il contenuto migrato da `agents-sprint-fix.md` (le 4 checkbox §"Sprint UX" in root + i blocchi microstep nei track).
> - **M4 NON tocca** quelle sezioni: si occupa esclusivamente di dedup §Regole Globali/Risorse/Support, §"Agenti disponibili", righe in testa per-track e BUG-1/2/3.
> - Prima di ogni edit in M4: `grep -n "Sprint UX" Standalone-app-v1/AGENTS.md` → se la sezione esiste, **preservarla** (non riscriverla). Idem per i blocchi microstep nei track. **Verifica BUG-4:** vedi bullet SETUP_GUIDE di M2 — `grep -c "AI Studio" backend/README.md` = 0 + fold ragionato (il grep su 'windows' è inutile: `backend/README.md` ce l'ha già).
> - **README — nessun overlap:** `backend/README.md` è toccato **solo in M2** (BUG-4 fold). `root README.md` è toccato **solo in M4** (WP7 versione React + link sweep) **e M5** (fix ref ai file rimossi). WP7 = allineare a React **18** (da `package.json`): correggere le '19' **errate** (`README.md` r.22 ecc.), **non** toccare le '18' corrette (`CLAUDE.md` r.1, `README.md` r.42). I due README non si sovrappongono tra milestone.
- Da `.cursor` plan: nulla (stale).

### M3 — Classe 1: `CLAUDE.md` (fonte unica)
- **Versione React = `frontend/package.json`** (verificato `^18.2.0` → React **18**): `CLAUDE.md` r.1 ("React 18/Vite") è **corretto**, NON cambiarlo. WP7 corregge le '19' errate altrove (vedi M4), non r.1.
- Doc Map: link al casing reale (top-level `Docs/`/`Docker/` uppercase, post-M1); rimuovere/riallineare riferimenti ai file che M5 eliminerà (`PROJECT-STATUS`, `HANDOFF`); puntare "stato corrente" → root `AGENTS.md` Progress Tracker.
- Verificare roster = solo i 5 agenti reali in `.claude/agents`; per `docker-dev` usare la dicitura fallback definita in Phase 2.

### M4 — Classe 2: gerarchia `AGENTS.md` + link sweep
- **root `AGENTS.md`**: rimuovere §"Regole Globali"/"Risorse Utili"/"Support" (link a CLAUDE); correggere incoerenza Progress Tracker (BUG-1); aggiungere §**"Agenti disponibili"** che richiama `.claude/agents` e mappa track→agente (con fallback `docker-dev`→`docs-dev`); integrare §"Sprint UX" da M2.
  - **Done criterion BUG-1 (oggettivo, discovery-driven)**: lo stato dei 4 task contesi (4.10, 4.11, 4.12, 4.16) deve essere (a) determinato da **ciò che esiste davvero** sul filesystem e (b) **identico** tra le due rappresentazioni in `AGENTS.md` (checklist "Progress Tracker" ↔ narrativa "Priorità Implementazione → Frontend MVP"). **Non** partire da nomi presupposti (eviterebbe falsi `MISSING`): prima enumerare i file reali, poi mappare i task. Da `Standalone-app-v1/`:
    ```bash
    # 1) componenti feature realmente presenti (NON assume nomi)
    ls frontend/src/features/*/components/*.tsx 2>/dev/null
    # 2) router/layout: rilevamento per CONTENUTO, robusto a cartelle assenti
    grep -rlE "createBrowserRouter|RouterProvider|<Routes|createRoutesFromElements" frontend/src 2>/dev/null
    find frontend/src/app -type f \( -iname '*rout*' -o -iname '*layout*' \) 2>/dev/null
    ```
    Poi, per ciascun task conteso, marcarlo `[x]` **solo se** risulta un componente/wiring che lo implementa (4.10 → `CloseEstimateModal.tsx` *o* equivalente reale; 4.11/4.12 → componente portfolio; 4.16 → **non basta** l'import di `RouterProvider`: servono le **definizioni di route** dell'app — `path:` o `<Route ` per `/`, `/estimates`, `/estimates/:id`, `/estimates/new` — **e** `AppLayout` montato; un `RouterProvider` stub senza route non conta. Check: `grep -rnE "path:\s*['\"]/|<Route\s" frontend/src/app 2>/dev/null`). **Regola anti-falso-negativo:** un `ls` vuoto **non** è prova di assenza — il `2>/dev/null` sopprime solo l'errore "cartella inesistente". Marcare `[ ]` **solo dopo** un check di contenuto negativo (es. zero match a `RouterProvider`/`<Routes` in tutto `frontend/src` ⇒ 4.16 davvero non implementato); se `app/router|layout` non esiste ma il routing è altrove, vale il routing trovato al punto 2. Allineare **entrambe** le sezioni allo stato così accertato. Guard: `grep -c "- \[" AGENTS.md` stabile tra due run senza edit; spot-check su 3 voci → nessuna riga marca `[x]`/✅ un task il cui componente **non** compare nell'elenco.
- **4 track AGENTS.md**: atomicità/token-minimal, zero duplicazione invarianti (solo link a CLAUDE); fix BUG-2 (`Docs/AGENTS.md:30`), BUG-3 (`frontend/AGENTS.md:22-23`). Ogni track dichiara **in testa**, con una riga esplicita e self-contained, l'agente che lo gestisce (così chi apre solo quel file sa chi opera, senza leggere CLAUDE/root):
  - `backend/AGENTS.md` → `> **Agente:** backend-dev`
  - `frontend/AGENTS.md` → `> **Agente:** frontend-dev`
  - `Docs/AGENTS.md` → `> **Agente:** docs-dev`
  - `Docker/AGENTS.md` → `> **Agente:** docker-dev (def assente — questo file è gestito da docs-dev come fallback)`
- WP6: `## Vedere anche` runbook in `backend/docs/{HEALTH,METRICS,LOGGING,SCHEDULER}.md`. **Done criterion WP6 (da `Standalone-app-v1/`):** `grep -lE "runbook/(monitoring|yahoo-outage)" backend/docs/HEALTH.md backend/docs/METRICS.md backend/docs/LOGGING.md backend/docs/SCHEDULER.md | wc -l` → **4** (ognuno dei 4 file ha il back-link runbook). Il grep-sigle di M2 non lo garantisce: WP6 non lascia una sigla `WP6` nei file, quindi la sua assenza passerebbe silenziosa senza questo check dedicato.
- Link sweep: `Docs/runbook/monitoring.md` endpoint `/api/v1/metrics`→`/metrics`. **WP7 versione React (direzione corretta):** allineare a React **18** (`package.json` = ^18.2.0); correggere '19'→'18' dove **errato**: `README.md` r.22, `frontend/AGENTS.md` header ("React 19 engineer"), root `AGENTS.md` TASK 4.1. **Non** toccare `CLAUDE.md` r.1 né `README.md` r.42 (già "18"). Check: `grep -rn "React 19" --include='*.md' Standalone-app-v1` = 0. (I link ai file che M5 rimuove si correggono in M5.)
- **Aggiunta post-M1** (link rotti pre-esistenti scoperti durante la discovery di M1, non casing ma target mancante — includere nel link sweep di questa milestone): `Docker/README.md` righe 11/368/369 → `TASK_2_2_IMPLEMENTATION_SUMMARY.md`, `TASK_2_2_STATUS_REPORT.md` (inesistenti); `backend/src/sync/infra/README.md:179` → `TASK_2.21_COMPLETION_REPORT.md` (inesistente). Verificare se i contenuti sono recuperabili altrove (es. `backend/docs/history/`) o se il link va rimosso/ripuntato.

### M5 — Cleanup (solo dopo M2–M4 verificate)
- `git rm` con path relativi alla **root della repo**. Per evitare rotture da `cd` non quotato su path con spazi (`Ticker Tracker/` → un `cd` senza virgolette finirebbe in `Ticker`, inesistente), **non fare `cd`**: risolvere la root e usare `git -C` (quotato). Da qualsiasi CWD dentro la repo:
  ```bash
  ROOT="$(rtk proxy git rev-parse --show-toplevel)"      # es. .../Ticker Tracker
  git -C "$ROOT" rm --ignore-unmatch \
         .cursor/plans/armonizzazione_md_docs_9e122796.plan.md \
         "Standalone-app-v1/Docs/HANDOFF.md" \
         "Standalone-app-v1/Docs/agents-sprint-fix.md" \
         "Standalone-app-v1/Docs/PROJECT-STATUS.md" \
         "Standalone-app-v1/backend/SETUP_GUIDE.md"
  ```
  `git -C "$ROOT"` esegue nella root corretta senza dipendere da un `cd` fragile (lo spazio resta protetto dentro `$ROOT` quotato). `--ignore-unmatch` mantiene l'idempotenza: file già rimosso non fa uscire `1` né aborta la riga lasciando gli altri orfani. Il guard-lista di M5 resta la verifica autorevole.
- Correggere i riferimenti ora pendenti ai file rimossi (es. root `README.md` r.241 → root `AGENTS.md` §"Sprint UX").
- **Mantenere** `Docs/Piano-operativo-v1.7.docx` e tutti i deep-dive/runbook/README.
- **File debug stray** `Standalone-app-v1/temp_estimate_body.json` (non-`.md`): **stato ambiguo** per l'interferenza del proxy `rtk` (vedi M0). Letture raw alla stesura del piano (`rtk proxy git ls-tree HEAD -- …`, `rtk proxy git ls-files -- …`): **assente** da HEAD, index e disco; lo snapshot iniziale della sessione lo dava come deletion staged (` D`). **Azione condizionale e idempotente** (da root repo, raw): eseguire `rtk proxy git ls-files -- Standalone-app-v1/temp_estimate_body.json` — se restituisce il path (o il file compare in HEAD/disk), allora `git rm --ignore-unmatch "Standalone-app-v1/temp_estimate_body.json"` + commit; altrimenti è già rimosso, nessuna azione. Non è `.md` → fuori dal guard `N−5`. **Aggiornamento post-M1:** un commit `acd2a58 chore: remove temp_estimate_body.json...` è comparso in cronologia indipendentemente da questo piano (vedi Stato-avanzamento §Incongruenze) — ri-verificare comunque con lo stesso comando prima di agire, per idempotenza.
- **Guard lista (autorevole — blocca lo swap file)**: `diff "$BASE" <(rtk proxy git ls-files '*.md' | grep -v node_modules | sort)` deve mostrare **esattamente 5 righe rimosse** (`<`) e **0 aggiunte** (`>`): `.cursor/plans/…plan.md`, `Standalone-app-v1/Docs/{HANDOFF,agents-sprint-fix,PROJECT-STATUS}.md`, `Standalone-app-v1/backend/SETUP_GUIDE.md`. Qualunque altra differenza (un `.md` diverso uscito, o uno nuovo entrato) = errore → fermarsi. Il solo conteggio non lo rileverebbe.
- **Guard conteggio** (sanity rapido, da root repo): `rtk proxy git ls-files '*.md' | grep -vc node_modules` → **N−5** (= 56). Ridondante col guard-lista ma veloce.

### M6 — Verifica finale (ordine vincolante)
1. **Link `.md` rotti** — `validate_dependencies.py` NON copre questo (valida solo il grafo dipendenze task Python del backend; un link rotto in CLAUDE/AGENTS passa verde). I link Markdown sono relativi **al file che li contiene**, non al CWD: lo script risolve ogni link rispetto alla dir del file sorgente. Il grep scansiona **tutti** i `.md` ricorsivamente (`--include='*.md' .`, non una lista fissa di cartelle) → copre anche `e2e/README.md` e ogni futuro `.md`, non solo `Docs|backend|frontend|Docker`. Eseguire **da `Standalone-app-v1/`** (il `cd` è parte del comando):
   ```bash
   cd Standalone-app-v1
   grep -rn "](.*\.md" --include='*.md' . \
     | grep -v "node_modules\|.venv" \
     | python -c "
import sys, os, re
broken = 0
for line in sys.stdin:
    # grep -rn → <srcfile>:<lineno>:<contenuto>. Match ancorato sul PRIMO ':<cifre>:'
    # → robusto a ':' nel contenuto E a drive-letter Windows: anche 'C:\\...:30:'
    # risolve giusto, perché \\d+ richiede una CIFRA dopo il ':' (dopo 'C:' c'è '\\',
    # non una cifra) → (.+?) si espande fino al vero ':30:'. In più, post 'cd', i
    # srcfile sono path RELATIVI (Docs/..., backend/...): il drive-letter non compare.
    m = re.match(r'^(.+?):\d+:(.*)$', line)
    if not m:
        continue
    srcfile, content = m.group(1), m.group(2)
    for link in re.findall(r'\]\(([^)]+\.md)', content):
        target = link.split('#')[0]
        if target.startswith(('http://', 'https://')):
            continue
        resolved = os.path.normpath(os.path.join(os.path.dirname(srcfile), target))
        if not os.path.exists(resolved):
            print('BROKEN:', srcfile, '->', link)
            broken += 1
sys.exit(1 if broken else 0)
" && echo "All .md links OK"
   ```
   Atteso: `All .md links OK`. La risoluzione relativa-al-sorgente evita falsi positivi indipendentemente dal layout dei path.
   > **Nota path con spazi:** la root repo contiene spazi (`Ticker Tracker/`). Lo script non copre link Markdown verso path con spazi non codificati (es. `](../Ticker Tracker/…)`). Tali link **non esistono** nei `.md` del progetto (tutti i link interni sono relativi sotto `Standalone-app-v1/`); se il grep finale producesse righe con `%20` o spazi letterali nel target, risolverle manualmente.
   > **Nota anchor:** lo script di step 1 valida solo l'esistenza del **file** (`split('#')[0]`), non l'`#anchor`. La validazione anchor completa è lo step 2 (automatico, copre **tutti** i link — non una lista hardcoded che potrebbe ometterne qualcuno, es. quelli verso le sezioni create in M4).
2. **Anchor `.md` validati (automatico)** — calcola lo slug GitHub di ogni heading del file target e verifica che ogni `#anchor` linkato esista. Da `Standalone-app-v1/`:
   ```bash
   grep -rn "](.*\.md#" --include='*.md' . \
     | grep -v "node_modules\|.venv" \
     | python -c "
import sys, os, re
def slug(h):
    h = re.sub(r'^#+\s*', '', h.strip())
    h = h.replace('`', '').replace('*', '')       # strip code/emphasis come GitHub. NON rimuovere '_': GitHub lo MANTIENE nello slug (## ESTIMATE_SUMMARY_VIEW -> estimate_summary_view). Non "correggere" questo comportamento: gli underscore restano.
    h = h.lower()
    # \w in Python 3 e' Unicode di DEFAULT e NON locale-dipendente (locale solo con
    # re.LOCALE, qui non usato) -> deterministico su ogni macchina; tiene a/e' accentate
    # come GitHub. Divergenze solo su punteggiatura esotica -> BAD ANCHOR da verificare a mano.
    h = re.sub(r'[^\w\s-]', '', h, flags=re.U)
    return re.sub(r'\s+', '-', h)
bad = 0
for line in sys.stdin:
    m = re.match(r'^(.+?):\d+:(.*)$', line)
    if not m: continue
    src, content = m.group(1), m.group(2)
    for tgt, anc in re.findall(r'\]\(([^)#]+\.md)#([^)\s]+)\)', content):
        if tgt.startswith(('http://', 'https://')): continue
        path = os.path.normpath(os.path.join(os.path.dirname(src), tgt))
        if not os.path.exists(path): continue            # esistenza file = step 1
        heads = [slug(l) for l in open(path, encoding='utf-8') if l.lstrip().startswith('#')]
        if anc.lower() not in heads:
            print('BAD ANCHOR:', src, '->', tgt + '#' + anc); bad += 1
sys.exit(1 if bad else 0)
" && echo "All .md anchors OK"
   ```
   Copre **tutti** gli anchor (anche eventuali link a §"Agenti disponibili", §"Sprint UX" o altri heading creati in M3/M4). Le righe per-track `> **Agente:** …` sono **blockquote, non heading** → non generano anchor: nessun link deve puntarle come `#…`. Edge: heading **duplicati** (stesso testo → GitHub aggiunge suffisso `-1/-2` dal 2° in poi) → lo script li segnala `BAD ANCHOR`. **Azione esplicita (non trattare come falso positivo da scavalcare):** rendere l'heading duplicato **unico** rinominandolo, così lo slug è deterministico e senza suffisso; solo in subordine, aggiornare il link allo slug suffissato reale (`#…-1`). Ignorarlo lascerebbe un anchor rotto in produzione.
   **Fallback pratico per `BAD ANCHOR` (edge emoji/accenti):** heading con emoji (`## 📊 Progress Tracker`) o accenti (`Priorità`) possono divergere. Regola GitHub da applicare a mano al heading: lowercase → **rimuovi emoji e punteggiatura** → **mantieni** le lettere accentate (à/é/ù) → spazi→`-` (un'emoji rimossa lascia uno spazio → può dare un `-` iniziale, es. `#-progress-tracker`). Confrontare il link con questa regola (o aprendo l'anchor su GitHub) e correggere **il link o l'heading**, mai lo script.
3. Zero riferimenti residui ai 5 file rimossi: `grep -rn "HANDOFF\|agents-sprint-fix\|PROJECT-STATUS\|SETUP_GUIDE\|armonizzazione_md_docs" --include='*.md' Standalone-app-v1` → **0 ovunque**, inclusi i 6 README di modulo "da mantenere". Se uno di essi linka un file rimosso (es. `vedere anche Docs/HANDOFF.md`), correggere **quel singolo riferimento** (repuntare a root `AGENTS.md` o togliere la riga): è la sistemazione di un link penzolante, **non** una riscrittura del README → ammessa anche sui file kept. Nessun riferimento a file rimosso può sopravvivere.
4. `cd Standalone-app-v1 && PYTHONIOENCODING=utf-8 python scripts/validate_dependencies.py` → passa (grafo task Python). Precondizione: `test -e scripts/validate_dependencies.py` (verificato presente e tracciato alla stesura; referenziato da `CLAUDE.md`); se un giorno mancasse, saltare **questo** step segnalandolo — non far fallire l'intera M6. **Aggiornamento 2026-07-03:** al momento di M6 falliva per 14 errori poi rivelatisi bug nello script stesso (fixati in thread secondario, non in questo piano) — vedi `Stato-avanzamento-pdl.md` §8. Ora VERDE.
5. Spot-check rendering tabelle (es. ex-BUG-2).
6. `git diff --stat` per conferma scope.

### M7 — Tuning modelli agenti `.claude/agents/*.md`
Stato attuale (verificato): tutti e 5 gli agenti hanno `model: inherit` → ereditano il modello della sessione chiamante, che può risultare troppo pesante o troppo leggero secondo il contesto. Assegnare a ciascuno un modello fisso e proporzionato al carico. Consentiti solo `opus`/`sonnet`/`haiku`. **Modificare solo la riga frontmatter `model:`**, mai il corpo.

| Agente | `model:` | Motivo |
|---|---|---|
| `code-reviewer` | `opus` | Review correttezza/sicurezza/finanza: un difetto mancato costa di più → modello forte |
| `backend-dev` | `opus` | Codice finanziario DDD, migrazioni Alembic, event sourcing: alta posta sulla correttezza |
| `frontend-dev` | `sonnet` | Implementazione React/TS standard: bilanciato |
| `task-planner` | `sonnet` | Ragionamento su grafo dipendenze + planning, nessuna scrittura codice |
| `docs-dev` | `haiku` | Edit markdown/testo, basso carico di ragionamento |

**Done criterion M7:** `grep -H "^model:" .claude/agents/*.md` mostra i 5 valori attesi, **nessun `inherit` residuo**; `git diff` sui 5 file tocca **solo** la riga `model:` (corpo invariato). Mapping **tunabile** per contenere i costi: `backend-dev`→`sonnet` e/o `code-reviewer`→`sonnet` se si preferisce un profilo più leggero.

---

## File critici da modificare
- Normalizzazione casing **link** (no rinomina cartelle): `CLAUDE.md`, root `README.md`, root `AGENTS.md` (M1)
- `Standalone-app-v1/CLAUDE.md` (M3)
- `Standalone-app-v1/AGENTS.md` + `backend/AGENTS.md` + `frontend/AGENTS.md` + `Docker/AGENTS.md` + `Docs/AGENTS.md` (M4)
- `backend/docs/{HEALTH,METRICS,LOGGING,SCHEDULER}.md` (WP6, M4)
- `Docs/runbook/monitoring.md`, root `README.md`, `backend/README.md` (M2/M4)
- `git rm` (5 file) + fix riferimenti pendenti (M5)

## Verifica end-to-end
1. Link `.md`: 0 rotti **e** 0 anchor invalidi (script M6 step 1+2) — è questo, non `validate_dependencies.py`, a coprire i link doc.
2. `python scripts/validate_dependencies.py` verde (grafo task Python backend).
3. 0 riferimenti residui ai 5 file eliminati.
4. Link al casing reale su disco (top-level `Docs/`/`Docker/` uppercase; `backend/docs/` lowercase): 0 link lowercase verso le top-level.
5. Conteggio AGENTS.md = 5 (root + 4 track), ognuno con back-link a CLAUDE e richiamo agente di track (fallback `docker-dev`→`docs-dev`).
6. Sprint-UX migrato (da `Standalone-app-v1/`): `grep -c "TASK [CDBA]" AGENTS.md` ≥ 4 **e** `grep -c "TASK [CDBA]" frontend/AGENTS.md` ≥ 4.
7. Diff per-milestone reversibile (1 commit ciascuna).
