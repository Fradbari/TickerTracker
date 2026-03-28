# Monitoring e Health

**Log Applicativi:**
I log Docker per il backend in produzione sono visibili tramite:
`docker logs tickertracker-backend-prod --follow`

**Endpoint di Health e Metriche:**
- Health Check: `GET /api/v1/health`
- Metriche Interne: `GET /api/v1/metrics`

Assicurarsi che gli healthcheck di Docker (`docker ps`) segnino lo stato come "healthy".