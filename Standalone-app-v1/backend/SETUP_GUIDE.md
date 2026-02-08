# Backend Setup Guide - Local Development

## Prerequisites
- Python 3.12+
- Docker Desktop running
- Git

## Quick Setup (Windows)

### 1. Clone & Navigate
```powershell
cd "C:\Users\francesco.dilecce\OneDrive - LUTECH SPA\Documenti\2. PERSONALI\3. Altro\Ticker Tracker\AI Studio\Standalone-app-v1"
```

### 2. Start Docker Containers
```powershell
.\docker-manage.ps1 up

# Wait for healthcheck (10 seconds)
timeout /t 10

# Verify DB is ready
docker exec tickertracker-db pg_isready -U tickertracker
# Expected: localhost:5432 - accepting connections
```

### 3. Setup Python Virtual Environment
```powershell
cd backend

# Create venv (if not exists)
python -m venv .venv

# Activate venv
.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | findstr pydantic
# Expected: pydantic 2.5.3
```

### 4. Configure Environment
```powershell
# .env file should already exist from git pull
# Verify it contains correct credentials
type .env | findstr DATABASE_URL
# Expected: DATABASE_URL=postgresql+asyncpg://tickertracker:devpassword@localhost:5432/tickertracker_dev
```

### 5. Run Database Migrations
```powershell
# Check current migration status
alembic current

# Apply all pending migrations
alembic upgrade head

# Verify migrations applied
alembic current
# Expected: 7f1c0d6b4a62 (head)
```

### 6. Verify Database Schema
```powershell
docker exec tickertracker-db psql -U tickertracker -d tickertracker_dev -c "\dt"
# Expected: List of tables including estimates with is_deleted column

# Check materialized view
docker exec tickertracker-db psql -U tickertracker -d tickertracker_dev -c "\d estimate_summary_view"
```

### 7. Start Backend Server
```powershell
# From backend directory with venv activated
uvicorn src.main:app --reload

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

### 8. Test Endpoints
```powershell
# In new terminal
curl http://localhost:8000/health
# Expected: {"success": true, "data": {"status": "ok"}, ...}

curl http://localhost:8000/health/ready
# Expected: {"success": true, "data": {"status": "ready", ...}}
```

---

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'pydantic'`
**Solution**: Install dependencies in venv
```powershell
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Error: `password authentication failed for user "user"`
**Solution**: Verify .env file has correct DATABASE_URL
```powershell
type .env | findstr DATABASE_URL
# Should show: postgresql+asyncpg://tickertracker:devpassword@localhost:5432/tickertracker_dev
```

### Error: Docker container not running
**Solution**: Restart Docker containers
```powershell
.\docker-manage.ps1 down
.\docker-manage.ps1 up
timeout /t 10
```

### Error: Alembic can't find migrations
**Solution**: Ensure you're in backend directory
```powershell
pwd  # Should show: ...\Standalone-app-v1\backend
dir alembic\versions  # Should list migration files
```

---

## Development Workflow

### Daily Startup
```powershell
# 1. Start containers (if not running)
.\docker-manage.ps1 up

# 2. Activate venv
cd backend
.venv\Scripts\Activate.ps1

# 3. Run migrations (if any new)
alembic upgrade head

# 4. Start server
uvicorn src.main:app --reload
```

### Before Git Commit
```powershell
# Run tests (when available)
pytest

# Check code style (when configured)
ruff check .
mypy src/
```

### Shutdown
```powershell
# Stop backend: Ctrl+C in uvicorn terminal

# Stop containers (optional, can leave running)
.\docker-manage.ps1 down
```

---

## Common Commands

### Database
```powershell
# Connect to PostgreSQL
docker exec -it tickertracker-db psql -U tickertracker -d tickertracker_dev

# List tables
\dt

# Describe table
\d estimates

# Run query
SELECT COUNT(*) FROM estimates;

# Exit
\q
```

### Alembic
```powershell
# Check current version
alembic current

# View migration history
alembic history --verbose

# Create new migration
alembic revision --autogenerate -m "description"

# Upgrade to specific version
alembic upgrade <revision_id>

# Downgrade one version
alembic downgrade -1

# Show pending migrations
alembic show <revision_id>
```

### Docker
```powershell
# View logs
docker logs tickertracker-db --tail 50
docker logs tickertracker-redis --tail 50

# Check container status
docker ps | findstr tickertracker

# Restart single container
docker restart tickertracker-db

# Remove all data (destructive!)
docker volume rm standalone-app-v1_postgres-data
```

---

## Next Steps

After successful setup:
1. ✅ TASK 2.11 completed (materialized view)
2. ✅ Migration 7f1c0d6b4a62 applied (soft delete)
3. 🚀 Ready for TASK 2.12 (Repository Pattern)
4. 🚀 Ready for TASK 2.13 (MarketData Repository)
