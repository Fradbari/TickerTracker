# TickerTracker v3.0 🚀

**TickerTracker v3.0** è un sistema avanzato e professionale per il tracciamento delle stime di trading, progettato con un'architettura robusta basata su **DDD (Domain-Driven Design)**, **CQRS** e **Event Sourcing**.

L'applicazione permette di gestire stime di acquisto/vendita (Long/Short), monitorare i target di prezzo in tempo reale, sincronizzare i dati con Google Drive e interagire con un assistente AI per l'analisi del portfolio.

---

## 🏗️ Architettura & Tech Stack

L'applicazione segue i principi del Clean Architecture e separazione dei ruoli (Separation of Concerns).

### Backend
- **Framework**: Python 3.11+ con **FastAPI**.
- **Database**: **PostgreSQL 16** (SQLAlchemy + Alembic per le migrazioni).
- **Cache**: **Redis** per rate limiting e caching dei dati di mercato.
- **Patterns**: Event Sourcing per l'audit trail delle stime, CQRS con Materialized Views per query prestazionali.
- **Provider Dati**: Integrazione con Yahoo Finance (via yfinance).

### Frontend
- **Framework**: **React 19** + **TypeScript**.
- **Build Tool**: **Vite**.
- **Styling**: **TailwindCSS**.
- **Data Fetching**: **React Query** (TanStack Query).
- **Calcoli Finanziari**: **decimal.js** per massima precisione decimale.

### Infrastruttura
- **Containerizzazione**: Docker e Docker Compose.
- **Sync**: Motore di sincronizzazione bidirezionale con **Google Drive API**.

---

## 📂 Struttura del Progetto

```bash
Standalone-app-v1/
├── backend/            # Codice sorgente Python/FastAPI
│   ├── src/            # Core logic (Domain, Services, API)
│   ├── infra/          # Integrazioni esterne (Yahoo, Drive, DB)
│   └── tests/          # Unit e Integration tests
├── frontend/           # Codice sorgente React/TypeScript
│   ├── src/            # Features, components e hooks
│   └── tests/          # Component e Unit tests
├── Docker/             # Configurazioni Docker e AGENTS specifici
├── Docs/               # Documentazione tecnica e test E2E/CI-CD
└── AGENTS.md           # Guida principale per lo sviluppo atomico
```

---

## 🚀 Avvio Rapido (Ambiente Docker)

Il modo più semplice per avviare l'intero ambiente locale (Single-User) è utilizzare Docker Compose.

### 1. Prerequisiti
- Docker e Docker Compose installati sul sistema.
- Un account Google Cloud con API Drive abilitate (per la sincronizzazione).

### 2. Configurazione
Copia il file di esempio per le variabili d'ambiente e configuralo:

```bash
cp backend/.env.example backend/.env
# Inserisci le tue chiavi API (Google, Yahoo, Gemini) nel file .env
```

### 3. Esecuzione
Avvia tutti i servizi (DB, Backend, Frontend):

```bash
docker compose up --build
```

L'applicazione sarà disponibile ai seguenti indirizzi:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Linee Guida per lo Sviluppo

Il progetto adotta un approccio **Atomic Development**. Ogni modifica deve essere tracciata tramite i file `AGENTS.md` presenti in ogni sezione.

1. **Consulta `AGENTS.md`**: Leggi la roadmap dei task e le dipendenze prima di iniziare basandoti sugli ID (es. TASK 1.1).
2. **Standard di Codifica**:
    - **Backend**: Usa sempre `Decimal` per valori monetari. Segui il layering api → services → repositories → domain.
    - **Frontend**: Usa `decimal.js` per i calcoli. Utilizza i componenti della cartella `shared/`.
3. **Test prima di procedere**: Assicurati che ogni nuovo microstep passi i test unitari.

---

## 📄 Licenza & Documentazione
Per dettagli operativi, consulta il **Piano Operativo v1.3** e i file di documentazione nella cartella `Docs/`.
