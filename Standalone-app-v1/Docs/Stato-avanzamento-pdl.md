# Stato di avanzamento — Piano-di-lavoro.md

> **Attenzione:** questo file **non è** `Docs/HANDOFF.md`. `HANDOFF.md` è uno degli oggetti che il Piano-di-lavoro migra e poi elimina (M5) — resta invariato finché M2/M5 non lo toccano secondo il piano. Questo file è la sintesi di continuità cross-sessione richiesta esplicitamente dall'utente, aggiornata ad ogni milestone.
> **Ultimo aggiornamento:** 2026-07-01, subito dopo il completamento e commit di M2.
> **Branch:** `vibe-claude` (nessun branch nuovo creato, per vincolo esplicito).
> **HEAD al momento della scrittura:** `20d7f2e` — `docs: migrate Sprint-UX, BUG-4 fold, analytics delta into ledgers (M2)`.

---

## 1. Obiettivo iniziale del lavoro

Armonizzare la documentazione `.md` di `Standalone-app-v1/` (60 file di progetto + `.cursor/plans/` fuori dalla subdir = 61 tracciati totali), oggi frammentata e in parte incoerente, riducendola a **3 classi documentali**:
1. `CLAUDE.md` — fonte unica di onboarding e invarianti architetturali.
2. Gerarchia `AGENTS.md` (root + 4 track: backend/frontend/Docker/Docs) — task ledger atomico, con richiamo esplicito agli agenti definiti in `.claude/agents/`.
3. Cleanup mirato dei file obsoleti/ridondanti, **solo dopo** aver migrato ogni contenuto ancora utile.

Deep-dive tecnici (`backend/docs/`), runbook operativi (`Docs/runbook/`) e tutti i README restano intatti (decisione utente: cleanup **conservativo**).

## 2. Piano approvato

Il piano completo è in `Docs/Piano-di-lavoro.md` (copia di `C:\Users\francesco.dilecce\.claude\plans\caveman-using-superpowers-role-programm-mellow-sketch.md`). Non lo riproduco qui — questo file racconta solo **stato, decisioni e deduzioni**, in complemento al piano stesso. Il piano è stato approvato dopo un numero elevato di round di revisione (~15+) in cui l'utente ha sistematicamente contestato ogni done-criterion vago, ogni rischio di falso positivo/negativo, e ogni assunzione non verificata — risultato: ogni milestone ha oggi un comando eseguibile o una tabella di corrispondenza esplicita come criterio di completamento, non descrizioni generiche.

Modalità di esecuzione scelta dall'utente: **milestone-by-milestone** — si esegue una milestone, si verifica, si committa, ci si ferma per review dell'utente prima di procedere alla successiva. Nessuna esecuzione autonoma end-to-end.

## 3. Stato corrente del piano

| Milestone | Stato | Commit |
|---|---|---|
| M0 — Setup + baseline | ✅ Completata | (nessun commit dedicato — dati di baseline riportati sotto) |
| M1 — Normalizzazione casing link | ✅ Completata e committata | `a82a3c0` |
| M2 — Migrazione contenuti | ✅ Completata e committata | `20d7f2e` |
| M3 — CLAUDE.md fonte unica | ⬜ Da iniziare | — |
| M4 — Gerarchia AGENTS.md + link sweep | ⬜ Da iniziare | — |
| M5 — Cleanup (git rm 5 file) | ⬜ Da iniziare | — |
| M6 — Verifica finale | ⬜ Da iniziare | — |
| M7 — Tuning modelli agenti | ⬜ Da iniziare | — |

**Prossima milestone da eseguire: M3.**

## 4. File modificati, creati, eliminati o da verificare

**Modificati e committati (M1, commit `a82a3c0`):**
- `Standalone-app-v1/AGENTS.md` — 7 link ricasati (`docs/`→`Docs/`, `docker/`→`Docker/`)
- `Standalone-app-v1/README.md` — 7 link ricasati
- `Standalone-app-v1/backend/AGENTS.md` — 2 link ricasati
- `Standalone-app-v1/backend/README.md` — 3 link ricasati
- `Standalone-app-v1/frontend/AGENTS.md` — 2 link ricasati
- `Standalone-app-v1/Docs/AGENTS.md` — 2 link ricasati

Totale: 6 file, 23 occorrenze link corrette (display backtick + target).

**Modificati e committati (M2, commit `20d7f2e`) — solo aggiunte, 0 cancellazioni, 89 insertions:**
- `Standalone-app-v1/AGENTS.md` — nuova §"🎯 Sprint UX" (checklist 4 task C/D/B/A) dopo Statistiche Progresso
- `Standalone-app-v1/frontend/AGENTS.md` — nuova §"SPRINT UX" con microstep TASK C/D/B/A + file target `.tsx`/`.ts` (AppStatusBar, EstimateForm, InsertEstimate, AdminSettings, frontendLogger)
- `Standalone-app-v1/backend/AGENTS.md` — nuova §"SPRINT UX (backend)": flag `finnhub_key_configured`, endpoint `POST /api/logs/frontend`, timestamp Yahoo su status
- `Standalone-app-v1/backend/README.md` — nuova §"Troubleshooting (sviluppo locale)" (fold BUG-4; path stale `AI Studio` NON migrato → grep=0; pin obsoleti scartati)
- `Standalone-app-v1/CLAUDE.md` — 1 bullet su analytics scaffolding vuoto sotto heading esistente "Things That Were Wrong Before"

Esecuzione via **3 subagent `docs-dev` paralleli** (file-set disgiunti). Done-criterion M2 ri-verificati dal thread principale con grep indipendenti: root `TASK [CDBA]`=4 ✅, frontend `TASK [CDBA]`=4 ✅, frontend filename-target=13 ✅, backend regex (finnhub/logs/Yahoo) PASS ✅, `AI Studio`=0 ✅.

**Creati in questa sessione (fuori dal piano, per continuità cross-sessione):**
- `Standalone-app-v1/Docs/Piano-di-lavoro.md` (questo passaggio)
- `Standalone-app-v1/Docs/Stato-avanzamento-pdl.md` (questo file)

**Non ancora toccati (target delle milestone future):**
- `Standalone-app-v1/CLAUDE.md` (M3)
- `Standalone-app-v1/AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`, `Docker/AGENTS.md`, `Docs/AGENTS.md` (M4 — ulteriori edit oltre M1)
- `backend/docs/{HEALTH,METRICS,LOGGING,SCHEDULER}.md` (M4, WP6 back-link)
- `Docs/runbook/monitoring.md` (M4, fix endpoint)
- `backend/README.md` (M2, fold BUG-4)
- `.claude/agents/*.md` (M7, solo riga `model:`)

**Da eliminare (M5, non ancora fatto):**
- `.cursor/plans/armonizzazione_md_docs_9e122796.plan.md`
- `Standalone-app-v1/Docs/HANDOFF.md`
- `Standalone-app-v1/Docs/agents-sprint-fix.md`
- `Standalone-app-v1/Docs/PROJECT-STATUS.md`
- `Standalone-app-v1/backend/SETUP_GUIDE.md`

**Da verificare (stato ambiguo, vedi §8 Incongruenze):**
- `Standalone-app-v1/temp_estimate_body.json` — risulta già assente da HEAD/index/disco al momento delle verifiche raw-git di M0, ma per motivi indipendenti dal piano (vedi §8).

## 5. Decisioni prese e loro motivazione

| Decisione | Motivazione |
|---|---|
| Cleanup **conservativo** (solo 5 file eliminati) | L'utente ha esplicitamente rifiutato l'opzione "aggressivo" (elimina ogni `.md` non nelle 3 classi): avrebbe cancellato 15 deep-dive tecnici, 8 runbook, 14 README senza modo pratico di migrarne il contenuto. |
| Mantenere convenzione `AGENTS.md` (no rename `AGENTS-BACKEND.md`) | I 5 agenti in `.claude/agents/*.md` leggono i file per **nome esatto** (`backend/AGENTS.md`, ecc.); rinominarli romperebbe i riferimenti a catena negli agent-def stessi. |
| Mantenere `Piano-operativo-v1.7.docx` | Unico business plan, binario, non migrabile come testo, referenziato dalla Doc Map di `CLAUDE.md`. |
| **Nessuna rinomina** di `Docs/`→`docs/`, `Docker/`→`docker/` | Verificato con grep su tutta la repo: nessun `Dockerfile`, `docker-compose*.yml`, `docker-manage.ps1/.sh`, workflow CI o script dipende dal casing delle cartelle-doc top-level. Si normalizzano solo i **link** al casing reale su disco — zero impatto Docker, zero rischio. |
| Lavorare direttamente su `vibe-claude`, nessun branch nuovo | Vincolo esplicito dell'utente — ha respinto la proposta iniziale di `docs/harmonization` come branch dedicato. |
| Esecuzione **milestone-by-milestone** (non tutto-in-una-volta) | Scelta esplicita dell'utente tra 4 opzioni proposte via `AskUserQuestion`, per massimizzare il controllo dopo un piano molto discusso. |
| WP7 invertito: allineare a React **18**, non 19 | `frontend/package.json` dichiara `"react": "^18.2.0"` — verificato con grep prima di agire. Il piano originale (derivato da `Docs/HANDOFF.md`) assumeva erroneamente che il codice fosse già su React 19; eseguirlo alla lettera avrebbe propagato un errore nei documenti "corretti". |
| BUG-4 riformulato: non serve un grep su "windows" | `backend/README.md` contiene **già** ampia copertura Windows (righe 23-195: venv `Activate.ps1`, PowerShell, docker-manage). Il vero difetto di `SETUP_GUIDE.md` è il path clone stale `…\AI Studio\…`; il done-criterion è ora `grep -c "AI Studio" backend/README.md` = 0, non un grep-parola generico che sarebbe passato comunque. |
| Modelli `.claude/agents`: `opus`/`opus`/`sonnet`/`sonnet`/`haiku` per code-reviewer/backend-dev/frontend-dev/task-planner/docs-dev | Aggiunto su richiesta esplicita dell'utente (M7, fuori dallo scope originale doc-only). Mapping pesato sul rischio: codice finanziario/review = modello forte; planning/frontend standard = bilanciato; edit markdown = leggero. Esplicitamente marcato come "tunabile" per contenere i costi. |

## 6. Deduzioni importanti

- **`frontend/package.json` è la fonte di verità per la versione React** (`^18.2.0`) — non `Docs/HANDOFF.md` né le occorrenze "React 19" sparse in vari doc, che sono l'errore da correggere.
- **`docker-manage.ps1`/`.sh` referenziano solo `docker-compose.base.yml`** — nessuna dipendenza dal casing delle cartelle doc, a conferma della decisione di non rinominare.
- **`.cursor/plans/armonizzazione_md_docs_9e122796.plan.md` è tracciato e NON in `.gitignore`** (verificato con `git check-ignore`) — rientra nel conteggio baseline N=61, non va escluso per errore.
- **`e2e/README.md` era l'unico `.md` sotto `Standalone-app-v1/` non coperto** dalla vecchia lista fissa di cartelle nel done-criterion di M6 (`Docs|backend|frontend|Docker|CLAUDE|AGENTS|README`). Corretto: il grep di M6 ora scansiona ricorsivamente **tutti** i `.md` (`--include='*.md' .`), non una lista di cartelle.
- **`scripts/validate_dependencies.py` esiste** (verificato tracciato + su disco) — M6 step 4 può contare su di esso, con precondizione `test -e` per resilienza futura.
- **Un proxy `rtk` intercetta i comandi `git`** in questa repo e può alterarne/riassumerne l'output silenziosamente (osservato: `git status --porcelain` ha restituito la stringa letterale `ok` invece dell'output reale). Ogni verifica load-bearing del piano (conteggi, guard, discovery) va eseguita con `rtk proxy git …` per bypassare l'interferenza.
- **Router/layout in frontend vanno rilevati per contenuto, non per nome file** — un `ls` vuoto su `frontend/src/app/router/` non prova che il routing non esista (potrebbe vivere altrove); il piano richiede un grep di contenuto (`RouterProvider`, `<Route`, `path:`) prima di marcare `[ ]` un task come non implementato.
- **Il conteggio da solo non basta a garantire l'assenza di regressioni in M5**: un agente potrebbe rimuovere un file sbagliato e aggiungerne un altro, mantenendo lo stesso totale N−5. Per questo il piano usa un **guard-lista** (`diff` riga-per-riga contro la baseline salvata) come verifica autorevole, non solo il conteggio.

## 7. Problemi incontrati

- **Primo tentativo di commit M1 fallito per errore di sintassi shell**: ho usato un heredoc in stile PowerShell (`@'...'@`) dentro il tool Bash (shell POSIX), producendo un messaggio di commit sporcato (iniziava con `@` letterale) e uno `git add` incompleto (mancava `Docs/AGENTS.md`, path con maiuscola, per un mismatch di casing nel comando). **Risolto** con `git reset --soft HEAD~1` seguito da ri-staging completo dei 6 file corretti e commit pulito con heredoc POSIX (`<<'EOF'`). Nessun oggetto Git dannoso è rimasto raggiungibile da `vibe-claude`.
- **Interferenza silenziosa del proxy `rtk`** durante una verifica di stato (`git status --porcelain` → `ok` invece dell'output reale) — ha richiesto di rieseguire i controlli bypassando il proxy con `rtk proxy git …`.

## 8. Incongruenze residue

- **Commit `acd2a58` ("chore: remove temp_estimate_body.json to clean up unused files") comparso in cronologia indipendentemente da questo piano.** Al momento del check iniziale di sessione (system-prompt gitStatus), l'HEAD era `e3d2ee9` e il file risultava come cancellazione non committata (`D` nel working tree). Alle verifiche raw-git eseguite durante M0 di questa sessione, il commit `acd2a58` era già presente in cronologia (tra `e3d2ee9` e `a82a3c0`) e il file risultava assente da HEAD/index/disco. **Non ho creato io questo commit** in questa sessione — non ho mai eseguito `git add`/`git commit` su quel file. Causa non accertata (possibile azione utente fuori sessione, o processo/hook automatico). **Effetto pratico sul piano:** l'azione condizionale di M5 per `temp_estimate_body.json` risulta già un no-op (il file è già rimosso); va comunque ri-verificata al momento di eseguire M5, per idempotenza, ma non richiede più intervento.
- **Due set di link rotti pre-esistenti** scoperti durante la discovery di M1 (non casing, target realmente mancante): `Docker/README.md` righe 11/368/369 → `TASK_2_2_IMPLEMENTATION_SUMMARY.md`, `TASK_2_2_STATUS_REPORT.md`; `backend/src/sync/infra/README.md:179` → `TASK_2.21_COMPLETION_REPORT.md`. Nessuno di questi target esiste nella repo. Aggiunta una nota in coda a M4 del `Piano-di-lavoro.md` per includerli nel link-sweep — non ancora risolti.
- **`$BASE` (baseline lista M0) salvata in `/tmp/tt_md_baseline.txt`** tramite il tool Bash di questa sessione (Git Bash su Windows mappa `/tmp` su disco reale). Una nuova sessione/finestra **potrebbe non avere accesso allo stesso path** se gira in un ambiente/sandbox diverso: da verificare all'avvio della prossima sessione, rigenerando la baseline con lo stesso comando se il file non risulta presente (il conteggio N=61 e la lista dei 5 file attesi in rimozione sono comunque riportati per esteso in questo documento e nel piano, quindi rigenerabili senza perdita di informazione).
- **[NEW, scoperta in M2] Incoerenza in `CLAUDE.md` §"Real Layouts" (backend)**: descrive il backend come `domain/`, `application/`, `infrastructure/`, `api/`, `shared/`, ma su disco il layout reale è **bounded-context-first** (`estimates/`, `market_data/`, `sync/`, `analytics/`, `shared/`, `infra/`) — coerente con la Struttura Progetto in `backend/README.md` e con `backend/AGENTS.md`. Segnalata dall'agente docs-dev durante M2 (verifica `analytics/`). **Fuori scope M2** (M2 aggiunge solo il bullet analytics); **candidata a correzione in M3** (CLAUDE.md fonte unica), da valutare insieme al fix Doc Map.

## 9. Vincoli espliciti

- Nessun nuovo branch Git — lavorare solo su `vibe-claude`.
- Cleanup conservativo: eliminare **solo** i 5 file elencati (§4); mantenere intatti deep-dive `backend/docs/`, runbook `Docs/runbook/`, tutti i README, il `.docx`.
- Non rinominare i file `AGENTS.md` di track.
- Non rinominare le cartelle `Docs/`/`Docker/` (verificato: nessuna dipendenza reale).
- Ogni milestone deve avere un criterio di completamento **oggettivo ed eseguibile** — niente istruzioni vaghe lasciate all'interpretazione dell'agente esecutore.
- Ogni azione rischiosa o distruttiva deve essere idempotente e motivata esplicitamente (es. `git rm --ignore-unmatch`, azione condizionale sul file di debug).
- Modifiche a `.claude/agents/*.md` (M7): **solo** la riga frontmatter `model:`, valori ammessi `opus`/`sonnet`/`haiku`, corpo dell'agente invariato.
- Modalità di esecuzione: **milestone-by-milestone**, con pausa e commit dopo ogni milestone per review dell'utente.
- `Docs/HANDOFF.md` è oggetto del piano (da migrare in M2, eliminare in M5) — non va confuso con questo file di stato né con esso sovrascritto.

## 10. Azioni già completate

1. Discovery completa (Phase 1 del piano): mappa di tutti i 60 (61 incl. `.cursor`) file `.md` tracciati, classificati per destino (Mantieni / Elimina dopo migrazione / Scope limitato / Fuori scope).
2. Design architettura target a 3 classi (Phase 2).
3. Oltre 15 round di revisione critica del piano di esecuzione (Phase 3), con hardening di ogni done-criterion: analisi impatto rename cartelle (docker-manage, compose, Dockerfile — verificato nessuna dipendenza), specificità dei criteri di migrazione Sprint-UX e HANDOFF (tabelle item→milestone→target), confini di ownership M2/M4 su file condivisi, verifica discovery-driven per BUG-1 (niente nomi di componenti presupposti), idempotenza di `git rm`, rischi CWD/percorsi-con-spazi, correttezza dello slug-validator per anchor (Unicode/underscore/emoji), guard-lista vs guard-conteggio per M5, copertura `e2e/README.md` in M6, verifica esistenza `validate_dependencies.py`, correzione versione React (18, non 19, verificata da `package.json`), aggiunta milestone M7 (tuning modelli agenti).
4. Piano finalizzato e salvato in `C:\Users\francesco.dilecce\.claude\plans\caveman-using-superpowers-role-programm-mellow-sketch.md`.
5. `ExitPlanMode` approvato dall'utente con modalità di esecuzione = milestone-by-milestone.
6. **M0** eseguita: confermato branch `vibe-claude`, working tree pulito (pre-M1), baseline N=61 `.md` tracciati calcolata e lista salvata in `/tmp/tt_md_baseline.txt`.
7. **M1** eseguita e committata (`a82a3c0`): 6 file, 23 occorrenze di link ricasate da `docs/`/`docker/` a `Docs/`/`Docker/`. Verificato: 0 link lowercase residui verso le top-level (solo falsi-positivi attesi su `backend/docs/`, non toccati, più i 2 set di link rotti pre-esistenti annotati in §8).
8. Auto-correzione di un primo tentativo di commit fallito (§7), senza lasciare stato sporco su `vibe-claude`.
9. Creazione di questo pacchetto di continuità cross-sessione (`Docs/Piano-di-lavoro.md` + questo file).
10. **M2** eseguita e committata (`20d7f2e`): migrazione contenuti senza cancellazioni. Sprint-UX (4 task) → root/frontend/backend `AGENTS.md`; fold BUG-4 (Troubleshooting) → `backend/README.md`; delta analytics → `CLAUDE.md`. Orchestrazione via 3 subagent `docs-dev` paralleli su file-set disgiunti; done-criterion ri-verificati dal thread principale (grep quantità+qualità tutti PASS) prima del commit.

## 11. Azioni ancora mancanti

Nell'ordine previsto dal piano:

- **M3** — `CLAUDE.md` come fonte unica: fix Doc Map (casing, riferimenti a file che M5 rimuoverà), verifica roster agenti. **Non** toccare la riga React (già corretta a 18). Valutare anche la correzione dell'incoerenza §"Real Layouts" backend segnalata in §8.
- **M4** — Gerarchia `AGENTS.md`: dedup root (BUG-1/WP5), fix BUG-2/BUG-3, banner agente per-track, back-link runbook (WP6), link sweep incluse le correzioni React 19→18 e i 2 link rotti pre-esistenti scoperti in M1.
- **M5** — Cleanup: `git rm` dei 5 file (con `--ignore-unmatch`, via `git -C`), fix riferimenti pendenti, ri-verifica `temp_estimate_body.json`, guard-lista e guard-conteggio.
- **M6** — Verifica finale: script link-rotti, script anchor-invalidi, zero riferimenti residui ai 5 file rimossi, `validate_dependencies.py`, spot-check tabelle, `git diff --stat`.
- **M7** — Tuning modelli 5 agenti (solo riga frontmatter `model:`).

## 12. Prossimo step minimo

Eseguire **M3** (`CLAUDE.md` fonte unica) seguendo esattamente i done-criterion già scritti in `Docs/Piano-di-lavoro.md` §M3: fix Doc Map (casing reale + riallineo/rimozione riferimenti a `PROJECT-STATUS`/`HANDOFF` che M5 eliminerà, "stato corrente" → root `AGENTS.md` Progress Tracker), verifica roster = 5 agenti reali (fallback `docker-dev`→`docs-dev`), **NON** toccare la riga React r.1 (già 18). Valutare la correzione dell'incoerenza §"Real Layouts" backend (§8). Poi verificare, committare, e fermarsi per review dell'utente prima di M4 — coerente con la modalità milestone-by-milestone.

**Nota M2 (appena completata):** i grep di igiene-sigle HANDOFF (`BUG-[1-4]`/`WP[567]`) e i guard di M5 restano da eseguire nelle rispettive milestone; M2 ha toccato **solo aggiunte** (0 cancellazioni), quindi il conteggio `.md` tracciati resta N=61 invariato (nessun file rimosso/aggiunto).

## 13. Prompt consigliato per la nuova finestra/sessione

```
Riprendi il lavoro di armonizzazione documentazione TickerTracker v3.0.

Leggi prima questi due file, in quest'ordine:
1. Standalone-app-v1/Docs/Stato-avanzamento-pdl.md — stato corrente, decisioni prese, incongruenze residue
2. Standalone-app-v1/Docs/Piano-di-lavoro.md — piano completo con i done-criterion di ogni milestone

Stato: M0 e M1 completate e committate (HEAD a82a3c0 su branch vibe-claude). Prossimo
step: eseguire M2 (migrazione contenuti — NESSUNA cancellazione) seguendo esattamente
i done-criterion descritti nel piano per M2.

Vincoli da rispettare senza eccezioni:
- Nessun nuovo branch — lavora solo su vibe-claude.
- Modalità milestone-by-milestone: esegui M2, verifica i done-criterion, committa,
  poi FERMATI per la mia review prima di procedere a M3.
- La repo ha una root con spazio nel nome ("Ticker Tracker/") — non usare `cd` non
  quotato su quel path; usa `git -C "$ROOT"` dove serve.
- Un proxy `rtk` in questa repo può alterare silenziosamente l'output di `git`
  (osservato su `git status --porcelain`) — per ogni verifica che conta (conteggi,
  guard, discovery) usa `rtk proxy git ...` per bypassarlo.
- Non confondere questi due file di continuità con Docs/HANDOFF.md, che è uno degli
  oggetti che il piano stesso migra (M2) ed elimina (M5) — resta un file distinto e
  ancora da toccare secondo il piano, non uno di gestione della sessione.

Prima di eseguire, conferma di aver letto lo stato e chiedimi conferma solo se trovi
un'ambiguità reale — altrimenti procedi con M2.
```
