# AGENTS.md — Sprint Fix UX e Operatività

## Scopo
Questo documento definisce un piano operativo **vincolante** da eseguire nella sottocartella `Standalone-app-v1/` del repo `TickerTracker`, branch `test`.
L'obiettivo è correggere quattro aree emerse dopo il build/run Docker riuscito: System Logs incompleti, Admin incompleta, barra inferiore fuorviante, UX carente nella pagina Nuova Stima.

## Regole di esecuzione
- Lavorare **solo** sul branch `test`; non creare branch aggiuntivi.
- Prima di modificare file, leggere integralmente i file elencati nella sezione "Pre-analisi obbligatoria".
- Non introdurre refactor architetturali non richiesti.
- Non cambiare naming, layout, copy o componenti fuori dai task descritti, salvo stretta necessità tecnica.
- Non aggiungere librerie nuove senza necessità comprovata.
- Non esporre segreti o API key nel frontend, nei log o nelle response.
- Non usare `any`, `@ts-ignore`, `// eslint-disable`, cast non motivati o workaround temporanei, salvo un solo `// TODO:` puntuale e giustificato.
- Ogni task deve lasciare il progetto compilabile e coerente.
- Le stringhe rivolte all'utente devono essere in italiano e coerenti con il lessico già presente nell'app.
- Non rimuovere funzionalità backend esistenti se non esplicitamente richiesto; rimuovere solo la superficie UI non desiderata.
- Dove esistono endpoint già presenti, **riusarli ed estenderli**; non duplicare endpoint con semantica equivalente.

## Vincoli di consegna
- Eseguire i task nell'ordine indicato nella sezione "Ordine di esecuzione".
- Ogni task deve produrre un diff mirato, con modifiche limitate ai file necessari.
- Dopo ogni task eseguire almeno:
  1. `npx tsc --noEmit`
  2. test/unit test già esistenti pertinenti, se presenti
  3. verifica manuale UI del comportamento richiesto
- Commit atomici per task, senza mischiare fix indipendenti.
- Messaggi commit nel formato:
  - `fix(frontend): ...`
  - `fix(admin): ...`
  - `fix(logging): ...`
  - `fix(estimate-form): ...`

---

## Pre-analisi obbligatoria
Leggere questi file prima di scrivere codice:

### Frontend
1. `frontend/src/components/layout/AppStatusBar.tsx`
2. `frontend/src/features/admin/components/AdminDashboard.tsx`
3. `frontend/src/features/admin/components/AdminSettings.tsx`
4. `frontend/src/features/admin/components/SystemStatusCards.tsx`
5. `frontend/src/features/estimates/components/InsertEstimate.tsx`
6. `frontend/src/features/estimates/components/EstimateForm.tsx`
7. `frontend/src/features/market-data/**`
8. `frontend/src/app/providers/QueryProvider.tsx`
9. eventuale componente viewer System Logs / drawer informativo richiamato dal pulsante `i`

### Backend
10. router admin/config
11. router sync / gdrive
12. router/logs
13. middleware logging / request logging
14. router market-data / symbol-search / symbol-validate
15. modelli/settings persistiti lato backend


### Obiettivo della pre-analisi
Confermare con precisione:
- dove viene costruita la barra inferiore reale;
- dove vive il pulsante `Sync Now` e quali dipendenze UI richiama;
- quali campi admin esistono davvero oggi;
- quali endpoint esistono già e quali vanno estesi, non duplicati;
- come viene popolato il pannello System Logs;
- dove avviene la gestione del simbolo in `Nuova Stima`.

Se una di queste informazioni è incerta, fermarsi, leggere meglio il codice e poi procedere. Non improvvisare.

---

## TASK A — System Logs completi e utili

### Problema
Il pannello System Logs attuale non rappresenta davvero ciò che accade nell'applicazione.
Mancano almeno:
- navigazioni tra pagine;
- click utente rilevanti;
- errori di caricamento componenti;
- errori fetch/API lato frontend;
- eventi funzionali chiave utili al troubleshooting.

Il file di log allegato conferma che il logging attuale è principalmente backend/request oriented e non copre l'esperienza utente end-to-end.

### Obiettivo
Rendere il System Logs un punto unico di osservabilità minima applicativa, integrando eventi frontend e backend nello stesso flusso visualizzato.

### Vincoli specifici
- Non creare un sistema di analytics invasivo.
- Non loggare dati sensibili, token, api key, contenuti completi di payload business o dati personali inutili.
- Non tracciare ogni click indistintamente: loggare solo eventi utili e leggibili.
- Non introdurre polling aggressivo.

### Implementazione richiesta

#### A1 — path backend atteso
Cercare in `backend/routers/` o `backend/api/` il router che gestisce i log.
Non creare un nuovo router se ne esiste già uno, anche parziale.

#### A2 — Endpoint frontend logs riusando la pipeline attuale
- Verificare l'endpoint/log pipeline esistente dei logs.
- Se `GET /api/logs` esiste già per la lettura, aggiungere **un endpoint dedicato di ingest frontend** coerente con l'architettura esistente, ad esempio `POST /api/logs/frontend`, salvo endpoint equivalente già presente.
- Gli eventi frontend devono confluire nello stesso storage/stream di log già usato dal viewer, aggiungendo un campo chiaro `source: frontend`.

#### A3 — Contratto evento frontend tipizzato
Definire un payload tipizzato, minimale e stabile, con campi del tipo:
- `timestamp`
- `level` (`info` | `warn` | `error`)
- `event`
- `message`
- `path` opzionale
- `component` opzionale
- `details` opzionale e sanitizzato
- `source` valorizzato lato backend o frontend in modo coerente

Non includere mai API key, header Authorization, cookie o body completi di richieste sensibili.

#### A4 — Servizio frontend centralizzato
Creare un servizio unico di logging frontend, ad esempio `frontendLogger`, con buffer e flush controllato.
Deve supportare almeno:
- log navigazione pagina;
- log API error;
- log component error;
- log eventi UI rilevanti.

Vincoli:
- fire-and-forget;
- nessun blocco UX;
- fallback silenzioso in caso di errore del logger;
- niente `console.log` in produzione.

#### A5 — Eventi da coprire obbligatoriamente
1. Cambio pagina / route
2. Errori di chiamate API principali
3. Errori di rendering catturabili o boundary error, se già presente un error boundary
4. Click utente **solo** su azioni importanti, per esempio:
   - backup GDrive
   - ripristino GDrive
   - verifica/salvataggio Finnhub
   - salvataggio configurazioni Admin

Non loggare i click banali o rumorosi.

#### A6 — Viewer System Logs
Aggiornare il viewer dei log affinché:
- distingua chiaramente backend e frontend;
- mostri almeno `timestamp`, `source`, `level`, `event`, `message`;
- non rompa compatibilità con i log backend esistenti;
- se già esistono filtri, aggiungere o estendere il filtro `source`.

### File attesi coinvolti
- router/log service backend logs
- eventuale schema pydantic dei log frontend
- `frontend/src/shared/services/frontendLogger.ts` o equivalente
- entry point router/app per logging navigazione
- hook/API layer per logging errori
- viewer/pannello System Logs

### Acceptance criteria
- Aprendo il pannello System Logs si vedono anche eventi frontend rilevanti.
- Navigando tra pagine compare almeno un evento `page_navigation`.
- Forzando un errore API compare un evento `api_error` leggibile.
- Le entry mostrano chiaramente la sorgente `frontend` o `backend`.
- Nessun dato sensibile è esposto.
- `npx tsc --noEmit` verde.

---

## TASK B — Admin completa e aderente ai bisogni operativi

### Problema
La pagina Admin contiene già alcune sezioni, ma non espone in modo completo e robusto tutti i campi/controlli necessari per configurare l'applicazione operativa.
In particolare va verificata e completata rispetto a:
- API key Finnhub, verifica e salvataggio;
- configurazione Google Drive;
- backup/ripristino da Google Drive con feedback chiaro;
- configurazione `settings.PRICE_UPDATE_INTERVAL_MINUTES`;
- eventuali altri riferimenti già previsti dal backend ma non esposti in UI.

### Obiettivo
Allineare la Admin a ciò che il backend già supporta o deve supportare con minime estensioni, senza duplicare configurazioni o introdurre impostazioni incoerenti.

### Vincoli specifici
- La Admin deve essere la fonte UI principale per la configurazione runtime dell'app.
- Le impostazioni persistenti operative devono passare dal backend, non solo da `localStorage`, se hanno impatto reale sul sistema.
- Non lasciare configurazioni critiche divise in metà frontend e metà backend senza spiegazione.
- Se un'impostazione rimane solo locale al frontend, deve essere chiaramente una preferenza UI e non una configurazione di sistema.

### Implementazione richiesta

#### B1 — Mappatura configurazioni esistenti
Prima di modificare la UI, censire tutte le configurazioni realmente disponibili nel backend e classificarle in due gruppi:
1. **Configurazioni di sistema** persistite lato backend
2. **Preferenze UI locali** persistite lato frontend

Se oggi in `AdminSettings` esistono campi salvati in `localStorage` ma semanticamente sono configurazioni di sistema, non espandere l'ambiguità: segnalarla e correggerla solo se il backend già le supporta o se l'estensione è minima e coerente.

#### B2 — Finnhub
Verificare che la sezione Finnhub supporti davvero:
- inserimento API key;
- verifica esplicita;
- salvataggio solo a verifica riuscita, oppure comportamento equivalente già definito lato backend;
- feedback chiaro all'utente;
- stato configurata/non configurata esponibile senza mostrare il segreto.

Se la UI è già parzialmente presente, rifinirla e allinearla ai contratti backend, senza duplicare endpoint.

#### B3 — Google Drive: campo folder/config mancante
Aggiungere il campo di configurazione mancante per il riferimento cartella Google Drive, usando il nome/semantica reale supportata dal backend (`folder id`, `folder path` o equivalente reale; non inventare nomi se il backend usa già un termine preciso).

Requisiti minimi:
- input dedicato;
- caricamento valore corrente;
- salvataggio via backend;
- messaggio esplicativo corto su cosa inserire;
- nessuna persistenza solo locale per questa configurazione.

#### B4 — Google Drive: backup e ripristino
La sezione GDrive deve gestire in modo chiaro:
- avvio backup;
- avanzamento se già disponibile via SSE/event stream;
- ripristino;
- feedback di successo/errore;
- stato di configurazione GDrive.

Se l'endpoint di status espone già backup disponibili, usarli per una modale/lista di ripristino reale.
Se non li espone ancora ma l'estensione è minima e coerente, estendere l'endpoint esistente invece di crearne uno duplicato.

#### B5 — Intervallo aggiornamento prezzi
La configurazione di `PRICE_UPDATE_INTERVAL_MINUTES` deve essere chiaramente presente e persistita lato backend.
Verificare che:
- il valore mostrato sia quello reale del backend;
- il salvataggio usi l'endpoint già esistente o la sua estensione naturale;
- il copy spieghi che regola la frequenza di aggiornamento prezzi.

#### B6 — Verifica campi mancanti ulteriori
Durante la pre-analisi, confrontare Admin UI e configurazioni backend.
Se esistono altri campi di configurazione già supportati dal backend ma assenti dalla UI e rilevanti per l'operatività, aggiungerli **solo se**:
- sono chiaramente configurazioni amministrative;
- la loro esposizione è coerente con il layout attuale;
- non aprono scope nuovo non richiesto.

Non trasformare questo task in un refactor totale della console Admin.

### Acceptance criteria
- In Admin è presente un campo per la configurazione GDrive realmente usabile.
- La sezione Finnhub è coerente e completa lato UX.
- `PRICE_UPDATE_INTERVAL_MINUTES` è visibile, modificabile e persistito correttamente.
- Backup/ripristino GDrive forniscono feedback chiaro.
- Le configurazioni di sistema non dipendono impropriamente da `localStorage` se hanno effetto operativo reale.
- `npx tsc --noEmit` verde.

---

## TASK C — Barra inferiore: rimozione `Sync Now` e nuovo indicatore Yahoo

### Stato attuale confermato
La barra inferiore reale, come verificato da screenshot, mostra attualmente:
- `GDrive: Non configurato`
- `Sync Now`

Non mostra alcuna informazione relativa a Yahoo. 

### Problema
- Il pulsante `Sync Now` non è autoesplicativo e genera ambiguità operativa.
- Il badge `GDrive: Non configurato` occupa spazio in una barra globale ma non porta valore continuo su tutte le pagine. 
- Manca del tutto un indicatore utile sul recency state dell'aggiornamento prezzi via Yahoo, che invece è più rilevante nel contesto di monitoraggio. 

### Obiettivo
Semplificare la barra inferiore rimuovendo elementi poco chiari e sostituendoli con un indicatore realmente utile: **elapsed time dall'ultima chiamata Yahoo**. 

### Vincoli specifici
- Rimuovere il pulsante `Sync Now` **con tutte le sue dipendenze UI** nella barra/status area corrente.
- Se `Sync Now` richiama logiche backend ancora utili, non eliminare la funzionalità backend: eliminare l'accesso UI globale e, se necessario, lasciare la capability in area Admin o in endpoint non toccato.
- Rimuovere anche il badge `GDrive: Non configurato` dalla barra inferiore globale.
- Aggiungere ex novo l'indicatore Yahoo senza introdurre polling extra oltre quello già esistente per lo status.

### Implementazione richiesta

#### C1 — Individuazione precisa della barra reale
Prima di modificare il codice:
- trovare il componente realmente renderizzato nella barra inferiore vista in screenshot;
- identificare dove vengono costruiti `GDrive: Non configurato` e `Sync Now`;
- verificare se `AppStatusBar.tsx` è davvero il componente in uso o se esiste una seconda implementazione attiva.

Non modificare alla cieca il file sbagliato.

#### C2 — Rimozione `Sync Now`
- Eliminare il pulsante `Sync Now` dalla UI della barra inferiore.
- Eliminare anche eventuali handler, props, wiring, import icone e stato locale usati **solo** per quel pulsante in quella barra.
- Non lasciare dead code frontend associato al pulsante.
- Non introdurre un sostituto equivalente nella stessa posizione.

#### C3 — Rimozione badge GDrive nella barra
- Rimuovere il badge `GDrive: Non configurato` dalla barra inferiore globale.
- Lo stato GDrive deve restare consultabile in Admin, non nella status bar globale.

#### C4 — Nuovo indicatore Yahoo elapsed time
Aggiungere un indicatore che mostri da quanto tempo non vengono aggiornati i prezzi, basandosi sull'ultima chiamata Yahoo disponibile nello status backend.

Requisiti:
- usare il timestamp reale dell'ultima chiamata Yahoo se già presente nell'endpoint di status;
- se il timestamp non è oggi esposto, estendere **l'endpoint di status esistente** per includerlo;
- mostrare testo chiaro del tipo:
  - `Yahoo: aggiornato 24s fa`
  - `Yahoo: aggiornato 3m fa`
  - `Yahoo: aggiornato 1h 12m fa`
- in caso di assenza dato:
  - `Yahoo: nessun aggiornamento registrato`
- in caso di ultimo esito fallito, il testo deve renderlo evidente senza essere ambiguo, ad esempio:
  - `Yahoo: ultimo tentativo fallito 4m fa`

#### C5 — Aggiornamento elapsed lato frontend
- L'elapsed time deve aggiornarsi lato frontend con un timer locale leggero, riutilizzando il timestamp già ricevuto.
- Non aggiungere chiamate API al secondo.
- Il polling stato già esistente può restare con cadenza attuale, salvo necessità minima documentata.

#### C6 — Stato visivo
Definire una resa visiva semplice e coerente:
- stato normale recente: testo neutro o positivo;
- ritardo medio: warning discreto;
- ritardo elevato o ultimo tentativo fallito: warning/danger chiaro.

Le soglie vanno mantenute semplici e documentate nel codice.

### Implementazione soglie
Soglie suggerite (modificabili, ma documentate nel codice):
- < 5 minuti: stato normale
- 5–30 minuti: warning discreto
- > 30 minuti o ultimo esito fallito: warning/danger

### Acceptance criteria
- La barra inferiore non mostra più `Sync Now`.
- La barra inferiore non mostra più `GDrive: Non configurato`.
- La barra mostra un indicatore Yahoo introdotto ex novo con elapsed time leggibile.
- Nessun polling extra inutile.
- Nessun dead code residuo del pulsante nella barra.
- `npx tsc --noEmit` verde.

---

## TASK D — Nuova Stima: assenza Finnhub e fallback/suggerimento sul simbolo

### Problema
Durante la compilazione di un nuovo simbolo nella pagina `Nuova Stima`:
- non appare alcuna comunicazione chiara quando Finnhub non è configurata;
- non è evidente il comportamento di fallback/suggerimento sul ticker;
- l'utente non riceve guida sufficiente per procedere manualmente.

### Obiettivo
Rendere il campo simbolo robusto e autoesplicativo in entrambi gli scenari:
1. Finnhub configurata
2. Finnhub non configurata

### Vincoli specifici
- Non esporre mai la API key Finnhub al frontend.
- Esporre al frontend solo uno stato booleano o equivalente: configurata / non configurata.
- Non bloccare la creazione manuale della stima se Finnhub manca, salvo vincolo backend già esistente.
- Riutilizzare `symbol-search` e `symbol-validate` esistenti, se presenti.

### Implementazione richiesta

#### D1 — Stato configurazione Finnhub disponibile al frontend
Estendere o riusare l'endpoint config/admin già esistente per esporre un flag del tipo:
- `finnhub_key_configured: boolean`

Questo flag deve indicare solo la presenza/configurazione valida del segreto, mai il suo valore.

#### D2 — Hook/query dedicata
Creare o riusare una query frontend stabile per leggere lo stato Finnhub.
Requisiti:
- caching ragionevole;
- nessun refetch aggressivo;
- naming coerente con il layer API esistente.

#### D3 — Banner/hint quando Finnhub manca
Nel punto reale in cui l'utente inserisce il simbolo, mostrare un banner inline non invasivo quando Finnhub non è configurata.
Contenuto minimo:
- avviso che la ricerca automatica simboli non è disponibile;
- indicazione che si può comunque inserire manualmente il ticker;
- collegamento diretto o call-to-action verso la pagina Admin.

Il messaggio deve essere chiaro ma non allarmistico.

#### D4 — Fallback manuale con verifica Yahoo
Quando Finnhub non è configurata:
- il campo simbolo deve restare utilizzabile come input manuale;
- al blur, o in un punto UX equivalente non rumoroso, deve essere tentata la validazione del simbolo tramite l'endpoint Yahoo/market validation esistente;
- mostrare un feedback sintetico e comprensibile:
  - simbolo valido;
  - simbolo non trovato;
  - verifica non disponibile / errore rete.

Se la validazione Yahoo può anche restituire prezzo corrente o metadati minimi già disponibili, usarli in modo non invasivo. Non aprire scope nuovo se l'endpoint non lo supporta.

#### D5 — Se Finnhub esiste, usare davvero la ricerca assistita
Se nel progetto esiste già un componente o flusso di symbol search assistita, verificare che venga effettivamente montato e usato quando Finnhub è configurata.
Non lasciare codice di ricerca simboli già scritto ma non collegato.

#### D6 — UX copy coerente
Copy richiesto lato utente, adattabile ma con significato invariato:
- in assenza Finnhub: la ricerca automatica è disabilitata;
- l'utente può inserire il simbolo manualmente;
- esempi ticker sintetici sono benvenuti (`AAPL`, `MSFT`, `ENI.MI`).

### Acceptance criteria
- Se Finnhub non è configurata, l'utente vede un avviso chiaro vicino al campo simbolo.
- L'utente può comunque inserire manualmente il ticker.
- Il simbolo viene validato con fallback disponibile lato backend, se presente.
- Se Finnhub è configurata, la ricerca assistita funziona o viene correttamente montata.
- Nessuna API key viene esposta.
- `npx tsc --noEmit` verde.

---

## Ordine di esecuzione
Eseguire i task in questo ordine per minimizzare regressioni e ambiguità:

1. **Task C** — barra inferiore
2. **Task D** — Nuova Stima / Finnhub status / fallback ticker
3. **Task B** — Admin operativa completa
4. **Task A** — System Logs completi

Motivazione:
- Task C è il più circoscritto e aiuta a chiarire lo status endpoint reale.
- Task D dipende in parte dalla config admin/backend ma ha scope UX preciso.
- Task B consolida la superficie amministrativa.
- Task A è il più trasversale e va fatto quando i flussi UI sono stabilizzati.

---

## Esclusioni esplicite
Per evitare deviazioni, **non fare** in questo sprint:
- refactor globale del design system;
- migrazione totale di tutte le impostazioni da localStorage a backend, se non strettamente necessaria ai campi toccati;
- riscrittura dell'intera Admin console;
- introduzione di telemetry/analytics di prodotto avanzati;
- rimozione di endpoint backend ancora utili ma non più esposti in UI;
- modifica del dominio business delle stime;
- cambi ai modelli dati non necessari ai 4 task.

---

## Checklist finale obbligatoria
Prima di considerare chiuso il lavoro:
- [ ] branch corrente: `test`
- [ ] diff limitato ai file necessari
- [ ] `npx tsc --noEmit` senza errori
- [ ] nessun segreto esposto
- [ ] barra inferiore coerente con il nuovo requisito Yahoo
- [ ] Admin con campi operativi mancanti coperti
- [ ] Nuova Stima guidata correttamente in assenza Finnhub
- [ ] System Logs utili anche per eventi frontend
- [ ] nessun dead code evidente lasciato dopo rimozione `Sync Now`
- [ ] commit atomici e messaggi coerenti

---

## STOP conditions — Fermarsi e chiedere se:
- il componente della barra inferiore reale differisce da `AppStatusBar.tsx`
- l'endpoint di status non espone dati Yahoo
- il backend non supporta un campo equivalente a `finnhub_key_configured`
- la rimozione di `Sync Now` implica rimuovere logica usata altrove
Non procedere con assunzioni: fermarsi, descrivere il problema trovato, attendere conferma.