# Scalabilità dei Servizi (Scaling)

**RTO: < 5 min (scale up) | RPO: n/a** (Operazioni stateless)

TickerTracker è stato progettato per supportare la scalabilità orizzontale dei componenti non provvisti di stato o stateless, come il `backend` FastAPI e il `frontend` web (Nginx).

## Scalare il Backend

Per aumentare il numero di repliche del backend, muoversi nella cartella root del progetto e utilizzare l'opzione `--scale`:

```bash
cd Standalone-app-v1/
docker compose -f docker-compose.prod.yml up -d --scale backend=3
```

In questa configurazione, Nginx non agisce nativamente come bilanciatore di carico se non lo configuriamo. Attualmente, docker offre un DNS round-robin. Per configurazioni più robuste, è opportuno mappare l'indirizzo IP del bilanciatore esterno.

## Considerazioni su PostgreSQL e Redis

**PostgreSQL**: Quando si aumenta il numero di istanze del backend, anche il numero delle connessioni al database aumenta. Assicurarsi di dimensionare il connection pooling di SQLAlchemy (`pool_size` e `max_overflow` in `database.py`) in modo che il totale massimo di connessioni non superi il limite `max_connections` di PostgreSQL 16. Implementare `PgBouncer` se necessario.

**Redis**: Supporta elevato throughput nativamente.

## Scalare lo Scheduler

Lo scheduler **NON DEVE ESSERE SCALATO** a meno che non si utilizzi uno store per lock distribuiti (come Redis lock per APScheduler). In sua assenza, se scalato causerà invii multipli dei task programmati (come i backup) che opereranno in collisione.
Attualmente mantenere `replicas: 1`.

## Riferimento implementativo (dev)
Per il tuning del connection pooling (`pool_size`, `max_overflow`, diagnostica `/health/pool`): [`../../backend/docs/CONNECTION-POOL.md`](../../backend/docs/CONNECTION-POOL.md).

## Contatti ed Escalation
Vedi [CONTACTS.md](CONTACTS.md) per l'escalation path in caso di congestione o saturazione nodi.
