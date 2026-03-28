# Avvio e Spegnimento

Assicurarsi di utilizzare gli script forniti per l'ambiente operativo:
- **Linux/Mac**: `./docker-manage.sh`
- **Windows**: `.\docker-manage.ps1`

## Ordine di Avvio Obbligatorio
1. **PostgreSQL** (Database primario)
2. **Redis** (Cache e messaggistica)
3. **Backend** (API e logica)
4. **Frontend** (Nginx proxy/static)

Verificare con `docker compose -f docker-compose.prod.yml ps` che tutti i container siano *healthy*.