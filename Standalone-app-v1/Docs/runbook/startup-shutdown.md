# Avvio e Spegnimento

Per la gestione dei container Docker, utilizzare in via preferenziale i comandi nativi tramite la CLI di `docker compose`. Questo assicura che il setup sia costantemente manutenibile senza dipendere da script non standardizzati.

## Comandi Operativi

```bash
# Avvio (Modalità "Detached")
docker compose -f docker-compose.prod.yml up -d

# Verifica salute e stato container
docker compose -f docker-compose.prod.yml ps

# Arresto "Graceful" (mantiene i volumi persistenti intatti)
docker compose -f docker-compose.prod.yml down

# Arresto Distruttivo (elimina anche i volumi persistenti del Database e di Redis - USARE CON ESTREMA CAUTELA)
docker compose -f docker-compose.prod.yml down -v
```

## Ordine di Avvio Obbligatorio
Il file `docker-compose.prod.yml` usa `depends_on` con la condizione `service_healthy`. Questa gerarchia avvierà il sistema unicamente nel seguente ordine logico di precedenza:

1. **PostgreSQL** e **Redis**
2. **Backend**, in attesa del ping di db/redis.
3. **Scheduler** (parallelo al backend, attende db/redis)
4. **Frontend**, in attesa dello start del backend.