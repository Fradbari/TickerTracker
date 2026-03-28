# Scalabilità dei Servizi (Scaling)

TickerTracker è stato progettato per supportare la scalabilità orizzontale dei componenti non provvisti di stato (stateless), come il `backend` FastAPI e il `frontend` web (Nginx).

## Scalare il Backend

Per aumentare il numero di repliche del backend, utilizzare l'opzione `--scale` di Docker Compose:

```bash
# Scala il backend a 3 repliche
docker compose -f docker-compose.prod.yml up -d --scale backend=3
```

In questa configurazione, Nginx non agisce nativamente come bilanciatore di carico se non lo configuriamo. Attualmente, tramite la rete Docker interna, Docker stesso offre un DNS round-robin che bilancia tra i diversi container che rispondono al nome `backend`. Per configurazioni più robuste, è opportuno mappare l'indirizzo IP del bilanciatore esterno o istanziare Nginx come load balancer esplicito nel file di configurazione `nginx.conf`.

## Considerazioni su PostgreSQL e Redis

**PostgreSQL**: Quando si aumenta il numero di istanze del backend, anche il numero delle connessioni al database aumenta. Assicurarsi di dimensionare il connection pooling di SQLAlchemy (`pool_size` e `max_overflow` in `database.py`) in modo che il totale massimo di connessioni (repliche * pool_size) non superi il limite `max_connections` tollerato da PostgreSQL 16. Se necessario, implementare `PgBouncer`.

**Redis**: Supporta elevato throughput. Scalare Redis richiede l'utilizzo del clustering (fuori dallo scope di questa installazione base via Docker Compose).

## Scalare lo Scheduler

Lo scheduler **NON DEVE ESSERE SCALATO** a meno che non si utilizzi uno store comune per lock distribuiti in APScheduler (come Redis o PostgreSQL con logica di lock). Se scalato senza accorgimenti, causerà invii multipli o run duplicati dei task programmati (come i backup o il fetch da Google Drive).
Attualmente deve mantenere `replicas: 1`.