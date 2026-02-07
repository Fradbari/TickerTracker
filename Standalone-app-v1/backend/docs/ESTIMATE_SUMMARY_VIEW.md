# Estimate Summary View - Materialized View (CQRS Pattern)

## 📋 Overview

The `estimate_summary_view` is a PostgreSQL materialized view that implements the CQRS (Command Query Responsibility Segregation) pattern for optimized dashboard queries. It combines data from `estimates` and `market_data` tables with computed metrics for fast read access.

## 🎯 Purpose

- **Performance Optimization**: Pre-computed aggregations and joins for sub-50ms query times
- **Simplified Queries**: Single view instead of complex joins
- **Real-time Metrics**: Current PnL, days open, risk level calculated automatically
- **Dashboard Optimization**: Designed specifically for dashboard list/aggregate queries

## 📊 Schema

### Base Fields (from `estimates` table)

All fields from the `estimates` table are included:
- `id` - UUID primary key
- `ticker_id` - Reference to ticker
- `user_id` - Reference to user (nullable)
- `start_price`, `target_price`, `stop_loss_price`
- `target_profit_percent`, `stop_loss_percent`
- `status` - OPEN, CLOSED_WIN, CLOSED_LOSS, etc.
- `direction` - LONG or SHORT
- `ai_model`, `ai_confidence`, `ai_reasoning`
- `created_at`, `updated_at`, `closed_at`
- `exit_price`, `realized_pnl`

### Computed Fields

#### `current_price` (DECIMAL)
Latest closing price from `market_data` for the ticker.
- Falls back to `start_price` if no market data available
- Uses `LATERAL JOIN` for optimal performance

#### `current_pnl` (DECIMAL)
Unrealized profit/loss calculated based on direction:
- **For OPEN estimates:**
  - LONG: `(current_price - start_price) × 100`
  - SHORT: `(start_price - current_price) × 100`
- **For CLOSED estimates:** Uses `realized_pnl`

#### `current_pnl_percent` (DECIMAL)
PnL as percentage:
- **For OPEN estimates:**
  - LONG: `((current_price - start_price) / start_price) × 100`
  - SHORT: `((start_price - current_price) / start_price) × 100`
- **For CLOSED estimates:** Calculated from `realized_pnl`

#### `days_open` (INTEGER)
Days since estimate was created:
- **For OPEN:** `current_timestamp - created_at`
- **For CLOSED:** `closed_at - created_at`

#### `risk_level` (TEXT)
Risk categorization based on `stop_loss_percent`:
- **LOW**: stop_loss_percent ≤ 2.0%
- **MEDIUM**: stop_loss_percent ≤ 5.0%
- **HIGH**: stop_loss_percent > 5.0%

## 🔍 Indexes

The materialized view has the following indexes for optimal query performance:

1. **`ix_estimate_summary_view_id`** (UNIQUE)
   - Required for `REFRESH MATERIALIZED VIEW CONCURRENTLY`
   - Allows concurrent refresh without locking the view

2. **`ix_estimate_summary_view_status`**
   - Index on `status` field
   - Optimizes filtering by OPEN/CLOSED estimates

3. **`ix_estimate_summary_view_ticker_id`**
   - Index on `ticker_id` field
   - Optimizes filtering estimates by ticker

4. **`ix_estimate_summary_view_status_created_at`**
   - Composite index on `(status, created_at DESC)`
   - Optimizes sorting open estimates by date

## 🔄 Refreshing the View

### Manual Refresh

#### Standard Refresh (with lock)
```sql
REFRESH MATERIALIZED VIEW estimate_summary_view;
```
- **Pros:** Faster refresh
- **Cons:** Locks the view during refresh (no concurrent reads)

#### Concurrent Refresh (no lock)
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY estimate_summary_view;
```
- **Pros:** Allows concurrent reads during refresh
- **Cons:** Slightly slower, requires unique index on `id`
- **Recommended** for production use

### Using the Refresh Script

```bash
# Concurrent refresh (default, recommended)
python scripts/refresh_estimate_summary_view.py

# Standard refresh (faster but locks view)
python scripts/refresh_estimate_summary_view.py --no-concurrent

# Show statistics after refresh
python scripts/refresh_estimate_summary_view.py --stats
```

### Automated Refresh

For production, set up automated refresh using:

1. **Cron Job** (Linux/macOS)
   ```bash
   # Refresh every 5 minutes
   */5 * * * * cd /path/to/backend && python scripts/refresh_estimate_summary_view.py
   ```

2. **Task Scheduler** (Windows)
   - Create a scheduled task to run the refresh script every 5 minutes

3. **Application-Level Trigger**
   - Refresh after estimate create/update/close operations
   - Refresh after market data ingestion

## 📈 Performance

### Target Metrics
- ✅ **Query Time**: < 50ms (actual: 3-5ms average)
- ✅ **Refresh Time**: < 50ms for concurrent refresh
- ✅ **Concurrent Refresh**: No locking, zero downtime

### Test Results
```
📊 Test 1: Query all estimates
   Query time: 5.44 ms ✅

📊 Test 2: Query OPEN estimates only
   Query time: 3.01 ms ✅

📊 Test 3: Aggregation queries
   Query time: 3.00 ms ✅

🔄 Concurrent refresh
   Refresh time: 12.15 ms ✅
```

## 💡 Usage Examples

### Get All Open Estimates with Metrics
```sql
SELECT *
FROM estimate_summary_view
WHERE status = 'OPEN'
ORDER BY created_at DESC;
```

### Get Estimates by Risk Level
```sql
SELECT *
FROM estimate_summary_view
WHERE risk_level = 'HIGH'
  AND status = 'OPEN';
```

### Dashboard Summary Statistics
```sql
SELECT 
    status,
    COUNT(*) as count,
    AVG(current_pnl_percent) as avg_pnl_percent,
    SUM(current_pnl) as total_pnl
FROM estimate_summary_view
GROUP BY status;
```

### Top Performing Estimates
```sql
SELECT *
FROM estimate_summary_view
ORDER BY current_pnl_percent DESC
LIMIT 10;
```

## ⚠️ Important Notes

1. **Unique Index Requirement**
   - The unique index on `id` is **required** for concurrent refresh
   - Do not drop this index

2. **Refresh Strategy**
   - Use concurrent refresh in production to avoid locking
   - Refresh frequency depends on your use case (recommended: every 5-15 minutes)
   - Can also trigger refresh on data changes (estimates, market_data)

3. **Data Freshness**
   - Materialized view data is a snapshot from last refresh
   - Not real-time unless refreshed frequently
   - Consider application-level caching for very frequent reads

4. **Migration Management**
   - View definition is in Alembic migration `e97b3b8578e1`
   - To modify view, create a new migration with `DROP` and `CREATE`

## 🔧 Troubleshooting

### "cannot refresh materialized view concurrently"
- **Cause:** Missing unique index on `id`
- **Fix:** Run migration again or manually create the unique index

### Slow Query Performance
- **Check:** Ensure all indexes exist (use `\d estimate_summary_view` in psql)
- **Check:** Run `ANALYZE estimate_summary_view` to update statistics
- **Check:** Consider refresh frequency (stale statistics can slow queries)

### Refresh Takes Too Long
- **Use:** Standard refresh instead of concurrent if acceptable
- **Optimize:** Ensure source tables (`estimates`, `market_data`) have proper indexes
- **Monitor:** Check `estimates` and `market_data` table sizes

## 📚 Related Documentation

- [Alembic Migrations](./ALEMBIC_SETUP_COMPLETED.md)
- [Database Schema](./README.md#database-schema)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
- [PostgreSQL Materialized Views](https://www.postgresql.org/docs/current/rules-materializedviews.html)
