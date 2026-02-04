# Docker Configuration & Documentation

Questo folder contiene la documentazione relativa alla containerizzazione di TickerTracker v3.0.

## 📋 Task Tracker

### ✅ TASK 2.2: Setup Docker Compose Base
- **Status**: COMPLETE ✅
- **Files**: `docker-compose.base.yml` (root)
- **Services**: PostgreSQL 16, Redis 7
- **Documentation**: [TASK_2_2_IMPLEMENTATION_SUMMARY.md](../docs/TASK_2_2_IMPLEMENTATION_SUMMARY.md)

### ⏳ TASK 3.12: Docker Compose Dev Environment
- **Status**: PENDING (Dependency: TASK 2.2 ✅)
- **Files**: `docker-compose.dev.yml` (root)
- **Services**: Backend (FastAPI), Frontend (React), extends base
- **Documentation**: Will be in docs/TASK_3_12_*

### ⏳ TASK 5.14: Docker Compose Production
- **Status**: PENDING (Dependency: TASK 2.2 ✅)
- **Files**: `docker-compose.prod.yml` (root)
- **Configuration**: Production-optimized, extends base
- **Documentation**: Will be in docs/TASK_5_14_*

---

## 📁 File Structure

```
Standalone-app-v1/
├── docker-compose.base.yml           # Infrastructure (DB + Cache)
├── docker-compose.dev.yml            # Development (extends base) [PENDING]
├── docker-compose.prod.yml           # Production (extends base) [PENDING]
├── docker-manage.ps1                 # Windows management script
├── docker-manage.sh                  # Linux/macOS management script
├── docker/
│   ├── AGENTS.md                     # Docker-specific tasks and progress
│   └── README.md                     # This file
├── data/
│   ├── postgres/                     # PostgreSQL volume mount
│   └── redis/                        # Redis volume mount
└── scripts/
    └── test_docker_services.py       # Connectivity test script
```

---

## 🚀 Quick Start

### 1. Start Infrastructure Services (DB + Cache)

**Windows (PowerShell)**:
```powershell
.\docker-manage.ps1 up
.\docker-manage.ps1 health
```

**Linux/macOS (Bash)**:
```bash
chmod +x docker-manage.sh
./docker-manage.sh up
./docker-manage.sh health
```

**Direct (Any OS)**:
```bash
docker compose -f docker-compose.base.yml up -d
docker compose -f docker-compose.base.yml ps
```

### 2. Test Connectivity

```bash
python scripts/test_docker_services.py
```

Expected output:
```
✓ PostgreSQL OK - PostgreSQL 16.x on x86_64-pc-linux-gnu
✓ Redis OK - v7.2.x - Memory: 2.5M
✓ PostgreSQL Advanced OK - INSERT/SELECT/DELETE funzionante

✓ TUTTE LE CONNESSIONI FUNZIONANO CORRETTAMENTE
```

### 3. Stop Services

**Windows**:
```powershell
.\docker-manage.ps1 down
```

**Linux/macOS**:
```bash
./docker-manage.sh down
```

**Direct**:
```bash
docker compose -f docker-compose.base.yml down
```

---

## 🔧 Management Commands

### docker-manage.ps1 (Windows)

```powershell
.\docker-manage.ps1 up          # Start services
.\docker-manage.ps1 down        # Stop and remove
.\docker-manage.ps1 restart     # Restart containers
.\docker-manage.ps1 status      # Show container status
.\docker-manage.ps1 ps          # List containers (same as status)
.\docker-manage.ps1 logs        # Follow logs (Ctrl+C to exit)
.\docker-manage.ps1 health      # Run healthchecks
.\docker-manage.ps1 clean       # Remove volumes (DESTRUCTIVE!)
.\docker-manage.ps1 help        # Show help
```

### docker-manage.sh (Linux/macOS)

Same commands as PowerShell version:
```bash
./docker-manage.sh up
./docker-manage.sh down
./docker-manage.sh logs
# etc...
```

### Direct Docker Compose

```bash
# Start services
docker compose -f docker-compose.base.yml up -d

# View status
docker compose -f docker-compose.base.yml ps

# View logs
docker compose -f docker-compose.base.yml logs -f

# Stop services
docker compose -f docker-compose.base.yml down

# Remove volumes (DATA LOSS!)
docker compose -f docker-compose.base.yml down -v

# Verify configuration
docker compose -f docker-compose.base.yml config
```

---

## 📊 Services Overview

### PostgreSQL 16-Alpine

| Property | Value |
|----------|-------|
| Image | postgres:16-alpine |
| Container Name | tickertracker-postgres |
| Port | 5432 |
| User | tickertracker |
| Password | devpassword (dev only!) |
| Database | tickertracker_dev |
| Healthcheck | pg_isready -U tickertracker |
| Volume | postgres-data:/var/lib/postgresql/data |

**Connection String**:
```
postgresql+asyncpg://tickertracker:devpassword@localhost:5432/tickertracker_dev
```

### Redis 7-Alpine

| Property | Value |
|----------|-------|
| Image | redis:7-alpine |
| Container Name | tickertracker-redis |
| Port | 6379 |
| Password | devpassword (dev only!) |
| Max Memory | 256MB |
| Policy | allkeys-lru |
| Healthcheck | redis-cli --raw incr ping |
| Volume | redis-data:/data |

**Connection String**:
```
redis://:devpassword@localhost:6379/0
```

---

## 🔗 Network

### ticker-network (Bridge Network)

- **Driver**: bridge
- **Subnet**: 172.20.0.0/16
- **Service Discovery**: By container name (DNS resolution)

**Container Names for Service-to-Service Communication**:
- PostgreSQL: `db` (port 5432 internal)
- Redis: `redis` (port 6379 internal)

Example from another service:
```python
# Connect from backend container to PostgreSQL
import psycopg2
conn = psycopg2.connect(
    host="db",  # Container name in ticker-network
    port=5432,
    user="tickertracker",
    password="devpassword",
    database="tickertracker_dev"
)
```

---

## 💾 Data Persistence

### Volume Strategy

Both services use **named volumes** with local driver:

```yaml
volumes:
  postgres-data:
    driver: local
    device: ${PWD}/data/postgres
  
  redis-data:
    driver: local
    device: ${PWD}/data/redis
```

### Data Survival

| Scenario | Data Survives |
|----------|---------------|
| Container stop | ✅ Yes |
| Container restart | ✅ Yes |
| Container rebuild | ✅ Yes |
| Image upgrade | ✅ Yes |
| `docker compose down` | ✅ Yes (volume persists) |
| `docker compose down -v` | ❌ No (volume deleted) |

### Accessing Data

**PostgreSQL Data** (on host machine):
```bash
ls -la data/postgres/

# Raw PostgreSQL files:
# - pg_wal/      (write-ahead logs)
# - global/      (cluster data)
# - base/        (databases)
# - pg_* files   (system files)
```

**Redis Data** (on host machine):
```bash
ls -la data/redis/

# RDB snapshot:
# - dump.rdb     (Redis database snapshot)
# - appendonly.aof (append-only file for persistence)
```

---

## 🔐 Security Notes

### Development Security

⚠️ **NOT FOR PRODUCTION**:
- Password: `devpassword` (hardcoded in docker-compose.base.yml)
- Ports: Exposed to localhost only (fine for development)
- No TLS/SSL (fine for development)
- No authentication for Redis ACL (fine for development)

### Production Security (TASK 5.14)

For production deployment:
1. **Use secrets** instead of hardcoded passwords
   ```bash
   openssl rand -base64 32  # Generate secure password
   ```
2. **Internal network only** - Remove port mappings
3. **TLS connections** - Enable PostgreSQL SSL
4. **Redis authentication** - Use strong passwords
5. **Resource limits** - CPU and memory restrictions
6. **Monitoring** - Healthchecks with alerting

---

## 🐛 Troubleshooting

### Docker Daemon Not Running

```
Error: failed to connect to the docker API at ...
```

**Fix**:
1. Start Docker Desktop (Windows/macOS)
2. Or start Docker daemon: `sudo systemctl start docker` (Linux)

### Ports Already in Use

```
Error: bind: address already in use
```

**Find process**:
```bash
netstat -ano | findstr :5432     # Windows
lsof -i :5432                     # Linux/macOS
```

**Fix**: Change port mapping in docker-compose.base.yml
```yaml
db:
  ports:
    - "5433:5432"  # Map to different host port
```

### Healthcheck Failing

```bash
# View detailed logs
docker compose -f docker-compose.base.yml logs db
docker compose -f docker-compose.base.yml logs redis

# Run manual healthcheck
docker exec tickertracker-postgres pg_isready -U tickertracker
docker exec tickertracker-redis redis-cli --raw incr ping
```

### Volume Permission Issues (Linux)

```bash
Error: Permission denied: /var/lib/postgresql/data
```

**Fix**:
```bash
sudo chown -R 999:999 data/postgres
sudo chown -R 999:999 data/redis
```

### Cannot Connect from Host

**Verify**:
1. Services are running: `docker compose -f docker-compose.base.yml ps`
2. Healthchecks pass: `docker compose -f docker-compose.base.yml ps` (check STATUS)
3. Ports are exposed: `netstat -an | grep 5432` or `lsof -i :5432`
4. Firewall allows: Check Windows Firewall or Linux iptables

---

## 📚 Documentation References

- **TASK 2.2 Complete**: [TASK_2_2_IMPLEMENTATION_SUMMARY.md](../docs/TASK_2_2_IMPLEMENTATION_SUMMARY.md)
- **TASK 2.2 Status**: [TASK_2_2_STATUS_REPORT.md](../docs/TASK_2_2_STATUS_REPORT.md)
- **Task Progress**: [AGENTS.md](./AGENTS.md)
- **Main README**: [../README.md](../README.md)

---

## 🔄 Deployment Strategy

### Development (TASK 3.12)

```bash
# Start infrastructure
docker compose -f docker-compose.base.yml up -d

# Start backend + frontend
docker compose -f docker-compose.base.yml -f docker-compose.dev.yml up --build

# Services:
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
# - Backend: localhost:8000
# - Frontend: localhost:3000
```

### Production (TASK 5.14)

```bash
# Start infrastructure + production services
docker compose -f docker-compose.base.yml -f docker-compose.prod.yml up -d

# Services:
# - PostgreSQL: internal only
# - Redis: internal only
# - Backend: :8000 (behind reverse proxy)
# - Frontend: :80/443 (behind reverse proxy)
```

---

## ✨ Implementation Status

| Component | Status | File | Task |
|-----------|--------|------|------|
| PostgreSQL 16 | ✅ Complete | docker-compose.base.yml | 2.2 |
| Redis 7 | ✅ Complete | docker-compose.base.yml | 2.2 |
| Healthchecks | ✅ Complete | docker-compose.base.yml | 2.2 |
| Volumes | ✅ Complete | docker-compose.base.yml | 2.2 |
| Network | ✅ Complete | docker-compose.base.yml | 2.2 |
| Management Scripts | ✅ Complete | docker-manage.ps1/.sh | 2.2 |
| Test Script | ✅ Complete | scripts/test_docker_services.py | 2.2 |
| Dev Environment | ⏳ Pending | docker-compose.dev.yml | 3.12 |
| Prod Environment | ⏳ Pending | docker-compose.prod.yml | 5.14 |

---

**Last Updated**: February 4, 2026  
**TASK**: 2.2 (Setup Docker Compose Base)  
**Status**: ✅ COMPLETE & DOCUMENTED
