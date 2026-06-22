# Data Quality Monitor — Task 3.8

`DataQualityMonitor` esegue controlli automatici sui dati `market_data` e segnala anomalie via `structlog` + Prometheus.

## Check disponibili

| Check | Cosa rileva |
|---|---|
| `positive_prices` | `open > 0`, `high > 0`, `low > 0`, `close > 0` |
| `positive_volume` | `volume > 0` per ogni riga |
| `no_large_gaps` | Nessun gap > N giorni tra date consecutive per ticker (configurabile) |
| `daily_change_lt50` | `\|((close - prev_close) / prev_close) × 100\| < 50` su base daily |

## API

```python
from src.market_data.quality import DataQualityMonitor, DataQualityConfig

config = DataQualityConfig(large_gap_days=7, max_daily_change_pct=50.0)

report = await DataQualityMonitor(session).run_all_checks(
    ticker_id=ticker.id,
    lookback_days=90,
    config=config,
)
# report = {"checks": [...], "critical": [...], "summary": {...}}
```

## Scheduling

Job APScheduler `data_quality_daily` — ogni giorno alle **06:00 UTC**. Su critical findings logga ERROR via `structlog` con `alert_event` placeholder (integrazione Slack/Email da Fase 2).

## Critical findings

Se uno o più critical check falliscono, `summary.critical_count > 0`. Il job non blocca l'app: marca e va avanti.

## Test Coverage

26 test in `backend/tests/market_data/test_data_quality.py` (Task 3.8).

## Metriche Prometheus

| Metrica | Tipo | Note |
|---|---|---|
| `data_quality_checks_total` | Counter | Per check type e verdict (pass/fail) |
| `data_quality_critical_total` | Counter | Per ticker |
| `data_quality_run_duration_seconds` | Histogram | Latenza complessiva del run |

## File chiave

`src/market_data/quality/data_quality_monitor.py`
