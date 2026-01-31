# Backend Layering Convention

Questa directory contiene il codice sorgente del backend TickerTracker, organizzato secondo i principi del **Domain-Driven Design (DDD)** e del layering esplicito.

## Bounded Contexts
Il sistema è diviso in contesti delimitati per garantire l'isolamento della logica di business:
- `estimates/`: Gestione del ciclo di vita delle stime di trading.
- `market_data/`: Recupero e caching dei prezzi in tempo reale e storici.
- `sync/`: Sincronizzazione dei dati con Google Drive.
- `analytics/`: Calcolo di metriche e performance del portfolio.
- `shared/`: Codice comune, value objects e utility riutilizzabili.

## Layering all'interno di ogni contesto
Ogni contesto segue una struttura a layer rigorosa:

1. **`api/`**: Contiene i router FastAPI e la logica di gestione delle richieste HTTP.
2. **`schemas/`**: Definizioni dei modelli Pydantic per la validazione di input (DTO) e l'output delle API.
3. **`domain/`**: Il "cuore" del sistema. Contiene entità, value objects e logica di business pura (agnostica rispetto all'infrastruttura).
4. **`services/`**: Layer di orchestrazione. Coordina le operazioni tra il dominio e i repository.
5. **`repositories/`**: Implementazioni dell'accesso ai dati (SQLAlchemy, Redis).

## Infrastruttura (`infra/`)
Contiene le integrazioni con sistemi esterni e configurazioni trasversali:
- `yahoo/`: Client per l'integrazione con Yahoo Finance API.
- `drive/`: Client per l'integrazione con Google Drive API.
- `cache/`: Configurazioni e astrazioni per il caching (Redis).
- `logging/`: Configurazioni per il logging strutturato e la tracciabilità.
- `security/`: Middleware di sicurezza e gestione dell'autenticazione/autorizzazione.

## Regole di Dipendenza
- Le dipendenze devono fluire verso l'interno: `api` -> `services` -> `domain` <- `repositories`.
- Il layer `domain` non deve dipendere da librerie esterne (se possibile) o da altri layer.
- `shared/` può essere importato da qualsiasi altro layer/contesto.
