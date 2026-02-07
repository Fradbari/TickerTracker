# TickerTracker Database Guide

## 📊 Database Architecture

TickerTracker v3.0 utilizza **PostgreSQL 16** con una architettura che combina Event Sourcing e CQRS pattern per garantire prestazioni ottimali e tracciabilità completa.

## 🗄️ Schema Overview

### Core Tables

#### 1. **tickers** - Ticker Information
Repository di tutti i ticker supportati (azioni, crypto, etc.).

**Campi principali:**
- `id` (UUID) - Primary key
- `symbol` (String, unique) - Ticker symbol (es. "AAPL", "TSLA")
- `name` (String) - Nome completo (es. "Apple Inc.")
- `exchange` (String) - Borsa di riferimento (es. "NASDAQ")
- `asset_type` (String) - Tipo asset (es. "STOCK", "CRYPTO")
- `currency` (String) - Valuta (es. "USD")
- `is_active` (Boolean) - Se il ticker è ancora tracciato

**Indexes:**
- Unique index su `symbol`
- Index su `is_active`

---

#### 2. **market_data** - Historical OHLCV Data
Dati storici di mercato per ogni ticker.

**Campi principali:**
- `id` (UUID) - Primary key
- `ticker_id` (UUID, FK) - Reference al ticker
- `date` (Date) - Data riferimento
- `open`, `high`, `low`, `close` (Decimal) - Prezzi OHLC
- `volume` (BigInteger) - Volume scambiato
- `source` (String) - Fonte dati (es. "yahoo_finance")

**Indexes:**
- Unique index su `(ticker_id, date, source)`
- Index su `date` per query temporali
- Index su `ticker_id` per filtrare per ticker

---

#### 3. **estimates** - Trading Estimates
Stime di trading (Long/Short) con target e stop-loss.

**Campi principali:**
- `id` (UUID) - Primary key
- `ticker_id` (UUID, FK) - Reference al ticker
- `user_id` (UUID, FK, nullable) - Reference all'utente (MVP: null)
- `start_price` (Decimal) - Prezzo di ingresso
- `target_price` (Decimal) - Prezzo obiettivo
- `stop_loss_price` (Decimal) - Prezzo stop-loss
- `target_profit_percent` (Decimal) - % profitto atteso
- `stop_loss_percent` (Decimal) - % perdita massima
- `status` (Enum) - OPEN, CLOSED_WIN, CLOSED_LOSS, CLOSED_MANUAL
- `direction` (Enum) - LONG o SHORT
- `ai_model`, `ai_confidence`, `ai_reasoning` - Campi AI
- `created_at`, `updated_at`, `closed_at` (Timestamp)
- `exit_price`, `realized_pnl` (Decimal, nullable) - Per stime chiuse

**Indexes:**
- Index su `status`
- Partial index su `(ticker_id, status)` WHERE status = 'OPEN'
- Index su `user_id`

---

#### 4. **estimate_events** - Event Sourcing
Tracciamento completo di tutti gli eventi sulle stime.

**Campi principali:**
- `id` (UUID) - Primary key
- `estimate_id` (UUID, FK) - Reference alla stima
- `event_type` (Enum) - CREATED, UPDATED, CLOSED, REOPENED, AI_SUGGESTION
- `event_data` (JSONB) - Dati specifici dell'evento
- `created_by` (UUID, nullable) - Chi ha causato l'evento
- `created_at` (Timestamp) - Quando è successo

**Indexes:**
- Index su `estimate_id` per ricostruire storia della stima
- Index su `event_type`
- Index su `created_at` per query temporali

**Pattern:** Event Sourcing completo - ogni modifica alla stima genera un evento immutabile.

---

#### 5. **sync_jobs** - Google Drive Sync Tracking
Tracciamento job di sincronizzazione con Google Drive.

**Campi principali:**
- `id` (UUID) - Primary key
- `job_type` (Enum) - INITIAL_IMPORT, DAILY_HISTORY_UPDATE, ON_ESTIMATE_SAVE, MANUAL_SYNC
- `status` (Enum) - PENDING, RUNNING, COMPLETED, FAILED, PARTIAL
- `started_at`, `finished_at` (Timestamp)
- `error_message` (Text, nullable)
- `filename` (String) - File Google Drive
- `checksum_before`, `checksum_after` (String, nullable)
- `records_processed`, `records_failed` (Integer)

**Indexes:**
- Index su `started_at` per query cronologiche
- Index su `status`

---

#### 6. **ai_model_runs** - AI Execution Tracking
Tracciamento esecuzioni modelli AI per monitoraggio costi/performance.

**Campi principali:**
- `id` (UUID) - Primary key
- `estimate_id` (UUID, FK, nullable) - Stima associata
- `model_name` (String) - Nome modello (es. "gemini-2.0-flash")
- `model_version` (String) - Versione modello
- `prompt_hash` (String) - Hash prompt per deduplicazione
- `prompt_tokens`, `completion_tokens` (Integer) - Token utilizzati
- `latency_ms` (Integer) - Latenza esecuzione
- `output_summary` (Text, nullable) - Riassunto output
- `raw_response` (JSONB, nullable) - Risposta completa
- `created_at` (Timestamp)

**Indexes:**
- Composite index su `(model_name, created_at)` per report temporali
- Index su `estimate_id`

---

#### 7-9. **users**, **roles**, **user_roles** - RBAC System
Sistema di autenticazione e autorizzazione (base per Fase 2).

**users:**
- `id` (UUID) - Primary key
- `email` (String, unique)
- `hashed_password` (String, nullable)
- `is_active` (Boolean)
- `created_at`, `updated_at` (Timestamp)

**roles:**
- `id` (UUID) - Primary key
- `name` (Enum) - ADMIN, USER, READONLY
- `description` (String)

**user_roles:** Tabella associativa many-to-many
- `user_id` (UUID, FK)
- `role_id` (UUID, FK)
- Primary key: `(user_id, role_id)`

**Indexes:**
- `users`: Unique su `email`, Index su `is_active`
- `roles`: Unique su `name`

---

## 🚀 CQRS Pattern - Materialized View

### **estimate_summary_view** - Dashboard Optimized View

**Purpose:** Pre-calcolare join complessi e metriche derivate per query dashboard < 50ms.

**What it does:**
- JOIN tra `estimates` e `market_data` per ottenere ultimo prezzo disponibile
- Calcola metriche in real-time:
  - `current_price` - Ultimo prezzo di mercato
  - `current_pnl` - PnL non realizzato (LONG/SHORT aware)
  - `current_pnl_percent` - PnL in percentuale
  - `days_open` - Giorni dalla creazione
  - `risk_level` - LOW/MEDIUM/HIGH basato su stop_loss_percent

**Performance:**
- Query time: **3-5ms** (target < 50ms) ✅
- Concurrent refresh: **~12ms**
- Zero downtime: `REFRESH MATERIALIZED VIEW CONCURRENTLY`

**Indexes:**
1. Unique index su `id` (required for concurrent refresh)
2. Index su `status` (filter OPEN/CLOSED)
3. Index su `ticker_id` (filter by ticker)
4. Composite index su `(status, created_at DESC)` (chronological sorting)

**Usage Examples:**
```sql
-- Get all open estimates with current metrics
SELECT * 
FROM estimate_summary_view 
WHERE status = 'OPEN' 
ORDER BY created_at DESC;

-- Get high-risk estimates
SELECT * 
FROM estimate_summary_view 
WHERE risk_level = 'HIGH' 
  AND status = 'OPEN';

-- Dashboard summary statistics
SELECT 
    status,
    COUNT(*) as count,
    AVG(current_pnl_percent) as avg_pnl_percent,
    SUM(current_pnl) as total_pnl
FROM estimate_summary_view
GROUP BY status;
```

**Refresh Strategy:**
```bash
# Manual refresh (recommended: concurrent)
python backend/scripts/refresh_estimate_summary_view.py

# With statistics
python backend/scripts/refresh_estimate_summary_view.py --stats

# Direct SQL (concurrent, no lock)
REFRESH MATERIALIZED VIEW CONCURRENTLY estimate_summary_view;
```

**When to Refresh:**
- After creating/updating/closing estimates
- After market data ingestion
- Scheduled (every 5-15 minutes in production)
- On-demand for dashboard page load

**Complete Guide:** See [backend/docs/ESTIMATE_SUMMARY_VIEW.md](../backend/docs/ESTIMATE_SUMMARY_VIEW.md)

---

## 🛠️ Database Setup & Migrations

### Initial Setup

1. **Start PostgreSQL** (Docker):
```bash
docker compose -f docker-compose.base.yml up -d db
```

2. **Run Migrations** (Alembic):
```bash
cd backend
alembic upgrade head
```

3. **Verify Schema**:
```bash
docker exec tickertracker-db psql -U tickertracker -d tickertracker_dev -c "\dt"
```

### Creating New Migrations

After modifying SQLAlchemy models:

```bash
cd backend

# Generate migration (auto-detect model changes)
alembic revision --autogenerate -m "description of changes"

# Review generated migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Migration History

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic upgrade head --sql  # Preview SQL without executing
```

**Complete Migration Guide:** See [backend/ALEMBIC_SETUP_COMPLETED.md](../backend/ALEMBIC_SETUP_COMPLETED.md)

---

## 📊 Performance Best Practices

### For Queries

1. **Use the Materialized View for Dashboard Queries**
   - Always prefer `estimate_summary_view` over direct `estimates` table for list/aggregate queries
   - View has pre-computed joins and metrics

2. **Index Usage**
   - Ensure queries use WHERE clauses on indexed columns (status, ticker_id, date)
   - Use `EXPLAIN ANALYZE` to verify index usage

3. **Pagination**
   - Always paginate large result sets
   - Use `LIMIT` and `OFFSET` with ORDER BY on indexed columns

### For Writes

1. **Batch Inserts**
   - Use SQLAlchemy `bulk_insert_mappings` for large market_data imports
   - Commit in batches of 1000-5000 rows

2. **Event Sourcing**
   - Always create an `estimate_events` record when modifying `estimates`
   - Use transactions to ensure consistency

3. **Materialized View Refresh**
   - Use concurrent refresh in production (no locking)
   - Trigger refresh after data changes, not on every query
   - Consider async refresh in background jobs

### Connection Pooling

SQLAlchemy async pool configuration (from `backend/src/infra/config.py`):

```python
pool_size=5,          # Max concurrent connections
max_overflow=10,      # Additional connections on high load
pool_timeout=30,      # Wait timeout for connection
pool_recycle=3600,    # Recycle connections after 1h
```

---

## 🔍 Monitoring & Troubleshooting

### Check Database Health

```bash
# Container health
docker ps | grep tickertracker-db

# Database connection
docker exec tickertracker-db pg_isready -U tickertracker

# Table sizes
docker exec tickertracker-db psql -U tickertracker -d tickertracker_dev -c "
  SELECT 
    tablename, 
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
  FROM pg_tables 
  WHERE schemaname = 'public'
  ORDER BY pg_total_relation_size(tablename::regclass) DESC;
"
```

### Check Materialized View Stats

```bash
# View size and last refresh
docker exec tickertracker-db psql -U tickertracker -d tickertracker_dev -c "
  SELECT 
    schemaname,
    matviewname,
    pg_size_pretty(pg_total_relation_size(matviewname::regclass)) as size,
    (SELECT COUNT(*) FROM estimate_summary_view) as rows
  FROM pg_matviews 
  WHERE matviewname = 'estimate_summary_view';
"
```

### Slow Query Analysis

```bash
# Enable slow query logging (PostgreSQL config)
log_min_duration_statement = 100  # Log queries > 100ms

# Check slow queries
docker exec tickertracker-db psql -U tickertracker -d tickertracker_dev -c "
  SELECT 
    query,
    calls,
    total_time,
    mean_time
  FROM pg_stat_statements
  ORDER BY mean_time DESC
  LIMIT 10;
"
```

---

## 🔐 Security Best Practices

1. **Never log sensitive data**
   - Don't log passwords or API keys
   - Use password hashing (bcrypt) for user passwords

2. **Use parameterized queries**
   - SQLAlchemy ORM prevents SQL injection by default
   - Avoid raw SQL strings with user input

3. **Connection security**
   - Use SSL for production PostgreSQL connections
   - Rotate database credentials regularly

4. **Backup strategy**
   - Daily automated backups (see Fase 2 tasks)
   - Test restore procedure monthly
   - Keep backups encrypted

---

## 📚 Additional Resources

- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [CQRS Pattern Explained](https://martinfowler.com/bliki/CQRS.html)
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)

---

**Last Updated:** February 2026  
**Schema Version:** e97b3b8578e1 (Alembic)
