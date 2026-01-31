# Rapporto di Analisi AGENTS.md - TickerTracker v3.0

Questo documento riassume l'analisi della coerenza e della struttura dei file `AGENTS.md` presenti nel progetto.

## 1. Problemi Critici, Strutturali e Infrastrutturali

### 1.1 Incoerenza nella Numerazione dei Task
Esiste un disallineamento tra il "Piano Atomico" principale (`Standalone-app-v1/AGENTS.md`) e i file di dettaglio (es. `backend/AGENTS.md`).
- **Root**: TASK 2.1 è "Setup Progetto Python con Poetry/uv".
- **Backend**: TASK 2.0 è "Setup Progetto Python...", mentre TASK 2.1 è "Setup SQLAlchemy".
- **Impatto**: Un LLM che segue la numerazione del root potrebbe saltare il TASK 2.0 del backend o confondere le dipendenze.

### 1.2 Sovrapposizione e Duplicazione Task Docker
In `Standalone-app-v1/Docker/AGENTS.md`:
- **TASK 2.2**: Crea `docker-compose.yml` per DB e Redis.
- **TASK 3.12**: Crea `docker-compose.yml` per DB, Backend e Frontend.
- **Problema**: Entrambi puntano allo stesso file fisico nella root. Non è chiaro se il 3.12 debba sovrascrivere o estendere il 2.2. Sarebbe meglio un unico task evolutivo o istruzioni di estensione chiare.

### 1.3 Link GitHub Hardcoded
Quasi tutti i file `AGENTS.md` contengono link assoluti del tipo `https://github.com/Fradbari/TickerTracker/blob/...`.
- **Problema**: Questi link sono fragili. Se il repo viene clonato in locale, rinominato o se si lavora su un branch, i link puntano a versioni potenzialmente obsolete o errate.
- **Soluzione**: Usare path relativi (es. `../backend/src/...`).

### 1.4 Incoerenza Tooling (Poetry vs uv)
Il file root menziona `Poetry/uv`, ma il TASK 2.0 nel backend definisce microstep solo per `Poetry`. Se si intende supportare `uv`, i microstep dovrebbero rifletterlo.

---

## 2. Problemi Secondari e di Esecuzione

### 2.1 Errori di Copia-Incolla negli Header
In `Standalone-app-v1/Docker/AGENTS.md`, è presente l'header `# SEZIONE 4: FRONTEND & UX`, che non appartiene alla sezione Docker.

### 2.2 Dipendenze Cross-Section
Il TASK 1.8 (Frontend) dipende dal TASK 1.1 (Backend). Sebbene le dipendenze funzionali siano normali, le istruzioni di "Scope" dicono di non guardare fuori dalla propria sezione. Questo può creare blocchi se un agente non ha visibilità sui prerequisiti di altre sezioni.

### 2.3 Ridondanza delle Regole
La regola "Usa decimal.js" è ripetuta ossessivamente in ogni sub-folder del frontend. È corretto ribadirla, ma una sezione "Regole Globali" nel root `AGENTS.md` o in `frontend/AGENTS.md` sarebbe più pulita.

### 2.4 Task Mancanti nel Tracker Root
Il TASK 2.0 (prerequisito fondamentale del backend) non è censito nella tabella di marcia del root `AGENTS.md`.

---

## 3. Suggerimenti Vari e Opzionali

### 3.1 Uniformità Linguistica
Il progetto usa un mix di Italiano (descrizioni) e Inglese (ID, Area, Fase). Sarebbe preferibile una scelta univoca o una separazione più netta.

### 3.2 README del Progetto
Manca un `README.md` nella root del repository (attualmente è solo in `Standalone-app-v1/`). Questo rende difficile l'orientamento iniziale per un utente/agente che approda sul repo.

### 3.3 Path dei File nei Microstep
In alcuni task di `market_data`, i path variano tra `domain/market_data.py` e `domain/entities.py`. È bene standardizzare la struttura (es. chiamare tutti i modelli `entities.py` o tutti col nome dell'entità).

---

## Azioni Suggerite (Piano di Bonifica)

1. **Riallineare la numerazione**: Portare il TASK 2.0 nel tracker root o rinumerare i task backend partendo da 2.1.
2. **Unificare i Task Docker**: Definire un percorso di crescita per il `docker-compose.yml` invece di task che sembrano sovrapporsi.
3. **Relativizzare i link**: Sostituire tutti i link `github.com` con path relativi al repository.
4. **Pulizia Header**: Rimuovere gli header errati in `Docker/AGENTS.md`.
5. **Centralizzare le regole**: Creare una sezione "Standard di Qualità" chiara per evitare ripetizioni.
