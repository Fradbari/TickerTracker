# AGENTS — docker

ID: TASK 2.2
Area: docker
Fase: MVP
Dipendenze: TASK 2.1

## TASK 2.2: Setup Docker Compose per PostgreSQL e Redis

**Descrizione:** Configurare container Docker per database e cache di sviluppo.

**Microstep:**

1. Creare file [`docker-compose.yml`](../docker-compose.yml) nella root del progetto
2. Definire servizio `db` con immagine postgres:16
3. Configurare variabili ambiente: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
4. Configurare volume persistente per dati PostgreSQL
5. Configurare healthcheck per PostgreSQL
6. Definire servizio `redis` con immagine redis:7-alpine
7. Configurare volume persistente per Redis
8. Configurare healthcheck per Redis
9. Definire network condivisa tra servizi
10. Creare file [`docker-compose.override.yml`](../docker-compose.override.yml) per configurazioni locali (porte esposte)

**Acceptance Criteria:**

- [ ] `docker compose up -d` avvia entrambi i servizi
- [ ] PostgreSQL accessibile su localhost:5432
- [ ] Redis accessibile su localhost:6379
- [ ] Healthcheck passa per entrambi i servizi
- [ ] Dati persistono dopo restart container

---

### Istruzioni per LLM
- Non modificare file fuori da [docker-compose.override.yml, docker-compose.yml] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.12
Area: docker
Fase: MVP
Dipendenze: TASK 2.2, TASK 2.20, TASK 4.1

## **TASK 3.12: Docker Compose Ambiente Locale (Estensione)**

Priorità: Alta (MVP - richiesto per avere un ambiente locale "one‑command" DB + backend + frontend).

**Descrizione:**  
Estendere il `docker-compose.yml` creato nel TASK 2.2 per includere anche i servizi backend e frontend, permettendo un avvio completo dell'applicazione.

**Microstep:**

- Aggiornare il file [`docker-compose.yml`](../docker-compose.yml) nella root del progetto.
- Definire servizio db (PostgreSQL 16) con:
  - volume per i dati,
  - variabili d'ambiente (DB name, user, password) lette da [`.env`](../.env.example).
- Definire servizio backend che:
  - builda da [`./backend`](../backend) ([`Dockerfile`](../backend/Dockerfile) semplice con Python + requirements),
  - espone la porta 8000,
  - dipende da db,
  - usa variabili d'ambiente per DATABASE_URL e altre config base.
- Definire servizio frontend che:
  - builda da [`./frontend`](../frontend) (Vite build),
  - serve i file statici con un Nginx minimale o con npm run dev in dev,
  - espone la porta 3000.
- Creare file [`.env.example`](../.env.example) con valori di esempio per DB e configurazione minima.
- Aggiornare il [`README`](../README.md) principale con una sezione "Avvio rapido" che spiega:
  - cp .env.example .env,
  - docker compose up --build,
  - URL di accesso (es. <http://localhost:3000>).

**Acceptance Criteria:**

- Con docker compose up --build il DB, il backend e il frontend partono senza configurazioni manuali extra.
- Il frontend comunica correttamente con il backend all'interno di Docker (es. usando <http://backend:8000> come baseURL).
- La procedura di avvio rapido nel README è sufficiente per riprodurre l'ambiente da zero.

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