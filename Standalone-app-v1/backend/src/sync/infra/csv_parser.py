"""
CSV Parser for legacy TickerTracker format.

Provides bidirectional parsing and export for legacy CSV files:
- Estimates CSV (120+ columns with comprehensive data)
- History CSV (daily market data)
"""

import csv
import io
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Dict, Any

from src.sync.infra.legacy_models import LegacyEstimateRow, LegacyHistoryRow
from src.estimates.domain.entities import Estimate
from src.market_data.domain.market_data import MarketData

logger = logging.getLogger(__name__)


# Column mapping for estimates CSV
ESTIMATES_COLUMN_MAP = {
    "Ticker": "ticker",
    "Start Date": "start_date",
    "Start Price": "start_price",
    "Target Price": "target_price",
    "Stop Loss": "stop_loss_price",
    "Target %": "target_profit_percent",
    "Stop Loss %": "stop_loss_percent",
    "Direction": "direction",
    "Status": "status",
    "Close Date": "close_date",
    "Exit Price": "exit_price",
    "Realized P/L": "realized_pnl",
    "Realized P/L %": "realized_pnl_percent",
    "AI Model": "ai_model",
    "AI Confidence": "ai_confidence",
    "AI Reasoning": "ai_reasoning",
    "Current Price": "current_price",
    "Day Change": "day_change",
    "Day Change %": "day_change_percent",
    "Volume": "volume",
    "Avg Volume": "avg_volume",
    "Market Cap": "market_cap",
    "P/E Ratio": "pe_ratio",
    "EPS": "eps",
    "Dividend Yield": "dividend_yield",
    "Dividend Rate": "dividend_rate",
    "Beta": "beta",
    "52W High": "week_52_high",
    "52W Low": "week_52_low",
    "52W Change %": "week_52_change_percent",
    "RSI(14)": "rsi_14",
    "SMA(20)": "sma_20",
    "SMA(50)": "sma_50",
    "SMA(200)": "sma_200",
    "EMA(20)": "ema_20",
    "EMA(50)": "ema_50",
    "User ID": "user_id",
    "Notes": "notes",
    "Tags": "tags",
    "Created At": "created_at",
    "Updated At": "updated_at",
}

# Column mapping for history CSV
HISTORY_COLUMN_MAP = {
    "Date": "date",
    "Ticker": "ticker",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume",
    "Adj Close": "adjusted_close",
}


class LegacyCsvParser:
    """
    Parser for legacy TickerTracker CSV formats.
    
    Handles:
    - UTF-8 encoding with BOM
    - Missing/empty columns
    - Type conversions with fallbacks
    - Bidirectional parse/export
    
    Example:
        ```python
        parser = LegacyCsvParser()
        
        # Parse estimates
        with open('estimates.csv', 'rb') as f:
            content = f.read()
            estimates = parser.parse_estimates_csv(content)
        
        # Export estimate
        csv_row = parser.export_estimate_to_csv_row(estimate, fundamentals)
        ```
    """
    
    def __init__(self):
        """Initialize parser with column mappings."""
        self.estimates_map = ESTIMATES_COLUMN_MAP
        self.history_map = HISTORY_COLUMN_MAP
    
    @staticmethod
    def _safe_decimal(value: str, default: Optional[Decimal] = None) -> Optional[Decimal]:
        """
        Safely convert string to Decimal.
        
        Args:
            value: String value to convert
            default: Default value if conversion fails
            
        Returns:
            Decimal value or default
        """
        if not value or value.strip() == "":
            return default
        
        try:
            # Remove any currency symbols, commas, etc.
            cleaned = value.strip().replace(",", "").replace("$", "").replace("%", "")
            return Decimal(cleaned)
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"Failed to convert '{value}' to Decimal: {e}")
            return default
    
    @staticmethod
    def _safe_int(value: str, default: Optional[int] = None) -> Optional[int]:
        """
        Safely convert string to int.
        
        Args:
            value: String value to convert
            default: Default value if conversion fails
            
        Returns:
            Int value or default
        """
        if not value or value.strip() == "":
            return default
        
        try:
            # Remove any commas
            cleaned = value.strip().replace(",", "")
            return int(float(cleaned))  # Handle scientific notation
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to convert '{value}' to int: {e}")
            return default
    
    @staticmethod
    def _safe_date(value: str, default: Optional[date] = None) -> Optional[date]:
        """
        Safely convert string to date.
        
        Supports formats:
        - YYYY-MM-DD (ISO)
        - MM/DD/YYYY
        - DD/MM/YYYY
        
        Args:
            value: String value to convert
            default: Default value if conversion fails
            
        Returns:
            Date value or default
        """
        if not value or value.strip() == "":
            return default
        
        value = value.strip()
        
        # Try different date formats
        formats = [
            "%Y-%m-%d",        # ISO format
            "%m/%d/%Y",        # US format
            "%d/%m/%Y",        # EU format
            "%Y/%m/%d",        # Alternative ISO
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Failed to parse date '{value}'")
        return default
    
    @staticmethod
    def _safe_datetime(value: str, default: Optional[datetime] = None) -> Optional[datetime]:
        """
        Safely convert string to datetime.
        
        Args:
            value: String value to convert
            default: Default value if conversion fails
            
        Returns:
            Datetime value or default
        """
        if not value or value.strip() == "":
            return default
        
        value = value.strip()
        
        # Try ISO format
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
        
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%m/%d/%Y %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Failed to parse datetime '{value}'")
        return default
    
    def parse_estimates_csv(self, content: bytes) -> List[LegacyEstimateRow]:
        """
        Parse estimates CSV file into LegacyEstimateRow objects.
        
        Handles:
        - UTF-8 encoding with BOM
        - Missing columns (uses defaults)
        - Empty values (converts to None)
        - Type conversions with error handling
        
        Args:
            content: Raw CSV content as bytes
            
        Returns:
            List of LegacyEstimateRow objects
            
        Raises:
            ValueError: If CSV is malformed or required columns missing
            
        Example:
            >>> with open('estimates.csv', 'rb') as f:
            ...     rows = parser.parse_estimates_csv(f.read())
            >>> print(f"Parsed {len(rows)} estimates")
        """
        logger.info("Parsing estimates CSV")
        
        # Decode with UTF-8, handling BOM
        try:
            text = content.decode('utf-8-sig')  # Removes BOM if present
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode CSV: {e}")
            raise ValueError(f"Invalid UTF-8 encoding: {e}")
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(text))
        rows = []
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
            try:
                # Required fields
                ticker = row.get("Ticker", "").strip()
                if not ticker:
                    logger.warning(f"Row {row_num}: Missing ticker, skipping")
                    continue
                
                start_price = self._safe_decimal(row.get("Start Price", ""))
                target_price = self._safe_decimal(row.get("Target Price", ""))
                stop_loss_price = self._safe_decimal(row.get("Stop Loss", ""))
                
                if not all([start_price, target_price, stop_loss_price]):
                    logger.warning(f"Row {row_num}: Missing required price fields, skipping")
                    continue
                
                # Build LegacyEstimateRow
                legacy_row = LegacyEstimateRow(
                    ticker=ticker,
                    start_date=self._safe_date(row.get("Start Date", ""), date.today()),
                    start_price=start_price,
                    target_price=target_price,
                    stop_loss_price=stop_loss_price,
                    target_profit_percent=self._safe_decimal(row.get("Target %", ""), Decimal("0")),
                    stop_loss_percent=self._safe_decimal(row.get("Stop Loss %", ""), Decimal("0")),
                    direction=row.get("Direction", "LONG").strip().upper(),
                    status=row.get("Status", "OPEN").strip().upper(),
                    
                    # Optional closure fields
                    close_date=self._safe_date(row.get("Close Date", "")),
                    exit_price=self._safe_decimal(row.get("Exit Price", "")),
                    realized_pnl=self._safe_decimal(row.get("Realized P/L", "")),
                    realized_pnl_percent=self._safe_decimal(row.get("Realized P/L %", "")),
                    
                    # AI fields
                    ai_model=row.get("AI Model", "").strip() or None,
                    ai_confidence=self._safe_decimal(row.get("AI Confidence", "")),
                    ai_reasoning=row.get("AI Reasoning", "").strip() or None,
                    
                    # Market data
                    current_price=self._safe_decimal(row.get("Current Price", "")),
                    day_change=self._safe_decimal(row.get("Day Change", "")),
                    day_change_percent=self._safe_decimal(row.get("Day Change %", "")),
                    volume=self._safe_int(row.get("Volume", "")),
                    avg_volume=self._safe_int(row.get("Avg Volume", "")),
                    market_cap=self._safe_decimal(row.get("Market Cap", "")),
                    
                    # Fundamentals
                    pe_ratio=self._safe_decimal(row.get("P/E Ratio", "")),
                    eps=self._safe_decimal(row.get("EPS", "")),
                    dividend_yield=self._safe_decimal(row.get("Dividend Yield", "")),
                    dividend_rate=self._safe_decimal(row.get("Dividend Rate", "")),
                    beta=self._safe_decimal(row.get("Beta", "")),
                    week_52_high=self._safe_decimal(row.get("52W High", "")),
                    week_52_low=self._safe_decimal(row.get("52W Low", "")),
                    week_52_change_percent=self._safe_decimal(row.get("52W Change %", "")),
                    
                    # Technical indicators
                    rsi_14=self._safe_decimal(row.get("RSI(14)", "")),
                    sma_20=self._safe_decimal(row.get("SMA(20)", "")),
                    sma_50=self._safe_decimal(row.get("SMA(50)", "")),
                    sma_200=self._safe_decimal(row.get("SMA(200)", "")),
                    ema_20=self._safe_decimal(row.get("EMA(20)", "")),
                    ema_50=self._safe_decimal(row.get("EMA(50)", "")),
                    
                    # Metadata
                    user_id=row.get("User ID", "").strip() or None,
                    notes=row.get("Notes", "").strip() or None,
                    tags=row.get("Tags", "").strip() or None,
                    created_at=self._safe_datetime(row.get("Created At", "")),
                    updated_at=self._safe_datetime(row.get("Updated At", "")),
                )
                
                rows.append(legacy_row)
                
            except Exception as e:
                logger.error(f"Row {row_num}: Failed to parse: {e}", exc_info=True)
                continue
        
        logger.info(f"Parsed {len(rows)} estimate rows from CSV")
        return rows
    
    def export_estimate_to_csv_row(
        self,
        estimate: Estimate,
        fundamentals: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export an Estimate entity to CSV row format.
        
        Args:
            estimate: Estimate entity to export
            fundamentals: Optional dict with market data and fundamentals
            
        Returns:
            CSV row string (single line with values)
            
        Example:
            >>> row = parser.export_estimate_to_csv_row(estimate, fundamentals)
            >>> print(row)
            "AAPL,2024-01-01,150.00,165.00,140.00,..."
        """
        # Extract fundamentals if provided
        fund = fundamentals or {}
        
        # Build legacy row from estimate
        legacy_row = LegacyEstimateRow(
            ticker=estimate.ticker.symbol if hasattr(estimate, 'ticker') else "UNKNOWN",
            start_date=estimate.created_at.date() if estimate.created_at else date.today(),
            start_price=estimate.start_price,
            target_price=estimate.target_price,
            stop_loss_price=estimate.stop_loss_price,
            target_profit_percent=estimate.target_profit_percent,
            stop_loss_percent=estimate.stop_loss_percent,
            direction=estimate.direction.value if hasattr(estimate.direction, 'value') else str(estimate.direction),
            status=estimate.status.value if hasattr(estimate.status, 'value') else str(estimate.status),
            
            # Closure fields
            close_date=estimate.closed_at.date() if estimate.closed_at else None,
            exit_price=estimate.exit_price,
            realized_pnl=estimate.realized_pnl,
            realized_pnl_percent=estimate.realized_pnl / estimate.start_price * 100 if estimate.realized_pnl and estimate.start_price else None,
            
            # AI fields
            ai_model=estimate.ai_model,
            ai_confidence=estimate.ai_confidence,
            ai_reasoning=estimate.ai_reasoning,
            
            # Fundamentals from dict
            current_price=self._safe_decimal(str(fund.get("current_price", ""))),
            day_change=self._safe_decimal(str(fund.get("day_change", ""))),
            day_change_percent=self._safe_decimal(str(fund.get("day_change_percent", ""))),
            volume=self._safe_int(str(fund.get("volume", ""))),
            avg_volume=self._safe_int(str(fund.get("avg_volume", ""))),
            market_cap=self._safe_decimal(str(fund.get("market_cap", ""))),
            pe_ratio=self._safe_decimal(str(fund.get("pe_ratio", ""))),
            eps=self._safe_decimal(str(fund.get("eps", ""))),
            dividend_yield=self._safe_decimal(str(fund.get("dividend_yield", ""))),
            dividend_rate=self._safe_decimal(str(fund.get("dividend_rate", ""))),
            beta=self._safe_decimal(str(fund.get("beta", ""))),
            week_52_high=self._safe_decimal(str(fund.get("week_52_high", ""))),
            week_52_low=self._safe_decimal(str(fund.get("week_52_low", ""))),
            week_52_change_percent=self._safe_decimal(str(fund.get("week_52_change_percent", ""))),
            rsi_14=self._safe_decimal(str(fund.get("rsi_14", ""))),
            sma_20=self._safe_decimal(str(fund.get("sma_20", ""))),
            sma_50=self._safe_decimal(str(fund.get("sma_50", ""))),
            sma_200=self._safe_decimal(str(fund.get("sma_200", ""))),
            ema_20=self._safe_decimal(str(fund.get("ema_20", ""))),
            ema_50=self._safe_decimal(str(fund.get("ema_50", ""))),
            
            # Metadata
            user_id=str(estimate.user_id) if estimate.user_id else None,
            notes=None,  # Not in Estimate model
            tags=None,  # Not in Estimate model
            created_at=estimate.created_at,
            updated_at=estimate.updated_at,
        )
        
        # Convert to dict and build CSV row
        row_dict = legacy_row.to_dict()
        
        # Create CSV string with proper quoting
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=row_dict.keys(), quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row_dict)
        
        return output.getvalue().strip()
    
    def parse_history_csv(self, content: bytes) -> List[LegacyHistoryRow]:
        """
        Parse history CSV file into LegacyHistoryRow objects.
        
        Format: Date,Ticker,Open,High,Low,Close,Volume,Adj Close
        
        Args:
            content: Raw CSV content as bytes
            
        Returns:
            List of LegacyHistoryRow objects
            
        Raises:
            ValueError: If CSV is malformed
            
        Example:
            >>> with open('History_AAPL.csv', 'rb') as f:
            ...     rows = parser.parse_history_csv(f.read())
            >>> print(f"Parsed {len(rows)} history rows")
        """
        logger.info("Parsing history CSV")
        
        # Decode with UTF-8, handling BOM
        try:
            text = content.decode('utf-8-sig')
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode CSV: {e}")
            raise ValueError(f"Invalid UTF-8 encoding: {e}")
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(text))
        rows = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Required fields
                date_val = self._safe_date(row.get("Date", ""))
                ticker = row.get("Ticker", "").strip()
                open_price = self._safe_decimal(row.get("Open", ""))
                high = self._safe_decimal(row.get("High", ""))
                low = self._safe_decimal(row.get("Low", ""))
                close = self._safe_decimal(row.get("Close", ""))
                volume = self._safe_int(row.get("Volume", ""))
                
                if not all([date_val, ticker, open_price, high, low, close, volume]):
                    logger.warning(f"Row {row_num}: Missing required fields, skipping")
                    continue
                
                legacy_row = LegacyHistoryRow(
                    date=date_val,
                    ticker=ticker,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,
                    adjusted_close=self._safe_decimal(row.get("Adj Close", "")),
                )
                
                rows.append(legacy_row)
                
            except Exception as e:
                logger.error(f"Row {row_num}: Failed to parse: {e}", exc_info=True)
                continue
        
        logger.info(f"Parsed {len(rows)} history rows from CSV")
        return rows
    
    def export_history_to_csv(self, data: List[MarketData]) -> bytes:
        """
        Export list of MarketData to history CSV format.
        
        Args:
            data: List of MarketData entities
            
        Returns:
            CSV content as bytes (UTF-8 encoded with BOM)
            
        Example:
            >>> market_data = [...] # List of MarketData
            >>> csv_bytes = parser.export_history_to_csv(market_data)
            >>> with open('History_AAPL.csv', 'wb') as f:
            ...     f.write(csv_bytes)
        """
        logger.info(f"Exporting {len(data)} market data records to CSV")
        
        # Create history rows from MarketData
        rows = []
        for md in data:
            legacy_row = LegacyHistoryRow(
                date=md.date,
                ticker=md.ticker.symbol if hasattr(md, 'ticker') and md.ticker else "UNKNOWN",
                open=md.open,
                high=md.high,
                low=md.low,
                close=md.close,
                volume=md.volume,
                adjusted_close=md.adjusted_close,
            )
            rows.append(legacy_row.to_dict())
        
        # Write to CSV
        output = io.StringIO()
        if rows:
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(rows)
        
        # Encode to bytes with BOM
        csv_text = output.getvalue()
        return csv_text.encode('utf-8-sig')
