# AGENTS — docker

ID: TASK 2.2
Area: docker
Fase: MVP
Dipendenze: TASK 2.1

## TASK 2.2: Setup Docker Compose Base (DB + Redis)

**Descrizione:** Configurare il `docker-compose.base.yml` per i servizi infrastrutturali comuni (Database e Cache).

**Microstep:**

1. Creare file [`docker-compose.base.yml`](../docker-compose.base.yml) nella root del progetto (`Standalone-app-v1/`)
2. Definire servizio `db` con immagine postgres:16
3. Configurare variabili ambiente: `POSTGRES_USER=tickertracker`, `POSTGRES_PASSWORD=devpassword`, `POSTGRES_DB=tickertracker_dev`
4. Configurare volume persistente per dati `postgres-data:/var/lib/postgresql/data`
5. Configurare healthcheck per PostgreSQL:
  ```
  yaml
   test: ["CMD-SHELL", "pg_isready -U tickertracker"]
   interval: 10s
   timeout: 5s
   retries: 5
   ```
6. Definire servizio `redis` con immagine redis:7-alpine
7. Configurare volume persistente per Redis: redis-data:/data
8. Configurare healthcheck per Redis
  ```
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 3s
  retries: 5
  ```
9. Definire network `ticker-network` condivisa tra servizi
10. Esporre porte esternamente: 5432:5432 (PostgreSQL), 6379:6379 (Redis)

**Acceptance Criteria:**

- [x] `docker compose -f docker-compose.base.yml up -d` avvia entrambi i servizi
- [x] PostgreSQL accessibile su localhost:5432
- [x] Redis accessibile su localhost:6379
- [x] Healthcheck passa per entrambi i servizi (healthy status)
- [x] Dati persistono dopo restart container
- [x] Network ticker-network creata e condivisa

**Stato:** ✅ COMPLETATO (2026-02-04)

---

### Istruzioni per LLM
-Crea solo docker-compose.base.yml - NON creare docker-compose.override.yml
-Usa flag -f esplicito nei comandi per chiarezza
-Network ticker-network sarà riusata da docker-compose.dev.yml (TASK 3.12)
-Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
-Alla fine, produci un elenco puntato con file modificati e test eseguiti.


ID: TASK 3.12
Area: docker
Fase: MVP
Dipendenze: ✅ TASK 2.2 (Complete), TASK 2.20, TASK 4.1

## **TASK 3.12: Docker Compose Ambiente Locale (Dev)**


Priorità: Alta (MVP - richiesto per avere un ambiente locale "one‑command").

**Descrizione:**  
Creare `docker-compose.dev.yml` che estende `base` includendo backend e frontend per lo sviluppo.

**Microstep:**

- Creare file [`docker-compose.dev.yml`](../docker-compose.dev.yml) nella root.
- Definire servizio `backend` che:
  - builda da [`./backend`](../backend) ([`Dockerfile`](../backend/Dockerfile) dev),
  - dipende da `db` e `redis` (definiti in base),
  - espone porta 8000,
  - monta volume `./backend:/app` per hot-reload.
- Definire servizio `frontend` che:
  - builda da [`./frontend`](../frontend),
  - espone porta 3000,
  - monta volume `./frontend:/app` per hot-reload.
- Aggiornare il [`README`](../README.md) con comando di avvio unificato:
  - `docker compose -f docker-compose.base.yml -f docker-compose.dev.yml up --build`

**Acceptance Criteria:**

- [ ] Il comando combinato avvia tutti i 4 servizi (db, redis, backend, frontend).
- [ ] Hot-reload funzionante per backend e frontend.
- [ ] Frontend comunica con backend via network docker interna.
- [ ] README aggiornato con procedura corretta.

---

---

### Istruzioni per LLM
- Non modificare file fuori da [repo root] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.14
Area: docker
Fase: MVP
Dipendenze: -

## TASK 5.14: Creare Docker Compose Completo

**Descrizione:** Docker Compose per tutti i servizi in produzione-like.

**Microstep:**

1. Creare file [`docker-compose.prod.yml`](../docker-compose.prod.yml)
2. Definire servizio `db`: PostgreSQL 16 con volume persistente
3. Definire servizio `redis`: Redis 7 con volume persistente
4. Definire servizio `backend`: immagine custom, env vars da file .env, healthcheck
5. Definire servizio `frontend`: Nginx con build statico, proxy pass a backend
6. Definire servizio `scheduler`: stesso backend ma comando diverso per worker
7. Configurare network interna tra servizi
8. Configurare resource limits per ogni servizio
9. Creare file [`.env.prod.example`](../.env.prod.example) con variabili richieste

**Acceptance Criteria:**

- [ ] `docker compose -f docker-compose.prod.yml up` avvia tutto
- [ ] Servizi comunicano internamente
- [ ] Solo frontend esposto all'esterno
- [ ] Healthcheck funzionanti
- [ ] Dati persistono tra restart

---

### Istruzioni per LLM
- Non modificare file fuori da [docker-compose.prod.yml] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.