# Legacy CSV Column Mapping Documentation

This document describes the column structure and mapping for legacy TickerTracker CSV files.

## Estimates CSV Format (120+ columns)

### Core Estimate Fields (Required)
| Legacy Column | Internal Field | Type | Description |
|--------------|----------------|------|-------------|
| Ticker | ticker | string | Stock ticker symbol (e.g., "AAPL") |
| Start Date | start_date | date | Date when estimate was created |
| Start Price | start_price | Decimal | Entry price for the estimate |
| Target Price | target_price | Decimal | Target price for profit |
| Stop Loss | stop_loss_price | Decimal | Stop loss price |
| Target % | target_profit_percent | Decimal | Target profit percentage |
| Stop Loss % | stop_loss_percent | Decimal | Stop loss percentage |
| Direction | direction | enum | "LONG" or "SHORT" |
| Status | status | enum | "OPEN", "CLOSED_WIN", "CLOSED_LOSS", "CLOSED_MANUAL", "EXPIRED" |

### Closure Fields (Optional)
| Legacy Column | Internal Field | Type | Description |
|--------------|----------------|------|-------------|
| Close Date | close_date | date | Date when estimate was closed (nullable) |
| Exit Price | exit_price | Decimal | Actual exit price (nullable) |
| Realized P/L | realized_pnl | Decimal | Realized profit/loss in currency (nullable) |
| Realized P/L % | realized_pnl_percent | Decimal | Realized profit/loss percentage (nullable) |

### AI Prediction Fields (Optional)
| Legacy Column | Internal Field | Type | Description |
|--------------|----------------|------|-------------|
| AI Model | ai_model | string | Name of AI model used (e.g., "gpt-4", "gemini) |
| AI Confidence | ai_confidence | Decimal | Confidence score 0-100 |
| AI Reasoning | ai_reasoning | text | AI reasoning/explanation for prediction |

### Market Data Snapshot (Optional)
| Legacy Column | Internal Field | Type | Description |
|--------------|----------------|------|-------------|
| Current Price | current_price | Decimal | Current market price at estimate creation |
| Day Change | day_change | Decimal | Price change from previous close |
| Day Change % | day_change_percent | Decimal | Day change as percentage |
| Volume | volume | int | Trading volume |
| Avg Volume | avg_volume | int | Average volume (typically 30-day) |
| Market Cap | market_cap | Decimal | Market capitalization |

### Fundamentals Snapshot (Optional)
| Legacy Column | Internal Field | Type | Description |
|--------------|----------------|------|-------------|
| P/E Ratio | pe_ratio | Decimal | Price-to-Earnings ratio |
| EPS | eps | Decimal | Earnings Per Share |
| Dividend Yield | dividend_yield | Decimal | Dividend yield percentage |
| Dividend Rate | dividend_rate | Decimal | Annual dividend rate |
| Beta | beta | Decimal | Stock beta (volatility measure) |
| 52W High | week_52_high | Decimal | 52-week high price |
| 52W Low | week_52_low | Decimal | 52-week low price |
| 52W Change % | week_52_change_percent | Decimal | 52-week change percentage |

### Technical Indicators Snapshot (Optional)
| Legacy Column | Internal Field | Type | Description |
|--------------|----------------|------|-------------|
| RSI(14) | rsi_14 | Decimal | Relative Strength Index (14-period) |
| SMA(20) | sma_20 | Decimal | Simple Moving Average (20-day) |
| SMA(50) | sma_50 | Decimal | Simple Moving Average (50-day) |
| SMA(200) | sma_200 | Decimal | Simple Moving Average (200-day) |
| EMA(20) | ema_20 | Decimal | Exponential Moving Average (20-day) |
| EMA(50) | ema_50 | Decimal | Exponential Moving Average (50-day) |

### Metadata Fields (Optional)
| Legacy Column | Internal Field | Type | Description |
|--------------|----------------|------|-------------|
| User ID | user_id | string | User identifier (UUID) |
| Notes | notes | text | User notes/comments |
| Tags | tags | string | Comma-separated tags |
| Created At | created_at | datetime | Record creation timestamp (ISO format) |
| Updated At | updated_at | datetime | Last update timestamp (ISO format) |

## History CSV Format (7-8 columns)

Format: `History_{TICKER}.csv` (e.g., `History_AAPL.csv`)

| Legacy Column | Internal Field | Type | Description |
|--------------|----------------|------|-------------|
| Date | date | date | Trading date (YYYY-MM-DD) |
| Ticker | ticker | string | Stock ticker symbol |
| Open | open | Decimal | Opening price |
| High | high | Decimal | Highest price of the day |
| Low | low | Decimal | Lowest price of the day |
| Close | close | Decimal | Closing price |
| Volume | volume | int | Trading volume |
| Adj Close | adjusted_close | Decimal | Adjusted closing price (optional) |

## Encoding

Both CSV formats use **UTF-8 encoding with BOM** for compatibility with Excel and other tools.

## Missing/Empty Values

- Empty numeric fields are converted to `None` (nullable)
- Empty string fields are converted to `None` or empty string based on field type
- Missing required fields cause row to be skipped with warning log
- Default values:
  - `direction`: "LONG"
  - `status`: "OPEN"
  - `start_date`: current date (if missing)
  - `target_profit_percent`: 0
  - `stop_loss_percent`: 0

## Date Formats

Parser supports multiple date formats:
- ISO format: `YYYY-MM-DD` (preferred)
- US format: `MM/DD/YYYY`
- EU format: `DD/MM/YYYY`
- Alternative: `YYYY/MM/DD`

## Datetime Formats

Parser supports:
- ISO 8601: `YYYY-MM-DDTHH:MM:SS` or `YYYY-MM-DDTHH:MM:SS.ffffff`
- SQL format: `YYYY-MM-DD HH:MM:SS`
- With timezone: `YYYY-MM-DDTHH:MM:SSZ`

## Example CSV Row (Estimates)

```csv
Ticker,Start Date,Start Price,Target Price,Stop Loss,Target %,Stop Loss %,Direction,Status,Close Date,Exit Price,Realized P/L,Realized P/L %,AI Model,AI Confidence,AI Reasoning,Current Price,Day Change,Day Change %,Volume,Avg Volume,Market Cap,P/E Ratio,EPS,Dividend Yield,Dividend Rate,Beta,52W High,52W Low,52W Change %,RSI(14),SMA(20),SMA(50),SMA(200),EMA(20),EMA(50),User ID,Notes,Tags,Created At,Updated At
AAPL,2024-01-15,150.00,165.00,140.00,10.00,-6.67,LONG,CLOSED_WIN,2024-02-01,164.50,14.50,9.67,gpt-4,85,Strong upward momentum with positive earnings,150.50,2.30,1.55,95234567,78456123,2450000000000,28.5,5.25,0.52,0.78,1.15,175.30,125.40,18.25,65.4,148.30,145.20,142.50,149.10,146.80,a1b2c3d4-e5f6-7890-abcd-ef1234567890,Earnings play,tech;growth,2024-01-15T09:30:00,2024-02-01T16:00:00
```

## Example CSV Row (History)

```csv
Date,Ticker,Open,High,Low,Close,Volume,Adj Close
2024-01-15,AAPL,148.50,152.30,147.80,150.00,95234567,149.85
2024-01-16,AAPL,150.20,153.40,149.90,152.80,87456123,152.65
```

## Round-Trip Compatibility

The parser guarantees:
1. **Parse -> Export -> Parse** produces the same data (within floating-point precision)
2. Column order is preserved in export
3. Empty values are handled consistently
4. Encoding remains UTF-8 with BOM

## Error Handling

- **Malformed rows**: Logged as warning, row skipped, processing continues
- **Missing required fields**: Row skipped with warning
- **Type conversion errors**: Default value used, warning logged
- **Encoding errors**: Exception raised (unrecoverable)
- **Empty CSV**: Returns empty list (not an error)

## Usage in Code

```python
from src.sync.infra.csv_parser import LegacyCsvParser

# Parse estimates
parser = LegacyCsvParser()
with open('estimates.csv', 'rb') as f:
    estimates = parser.parse_estimates_csv(f.read())

# Export estimate to CSV row
csv_row = parser.export_estimate_to_csv_row(estimate, fundamentals_dict)

# Parse history
with open('History_AAPL.csv', 'rb') as f:
    history = parser.parse_history_csv(f.read())

# Export history
market_data_list = [...]  # List of MarketData entities
csv_bytes = parser.export_history_to_csv(market_data_list)
```

## Migration Notes

When migrating from legacy CSV to new database format:
1. Parse CSV files using `parse_estimates_csv()` and `parse_history_csv()`
2. Convert LegacyEstimateRow to Estimate entity
3. Convert LegacyHistoryRow to MarketData entity
4. Save to database using repositories
5. Keep original CSV as backup until migration verified

## Version History

- **v1.0** - Initial legacy format (120+ columns)
- **v2.0** - Added technical indicators (RSI, SMA, EMA)
- **v3.0** - Added AI prediction fields (current version)
