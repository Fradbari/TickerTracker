"""
Legacy data models for CSV parsing.

Defines dataclasses representing rows in legacy CSV format.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


@dataclass
class LegacyEstimateRow:
    """
    Represents a single row from the legacy estimates CSV file.
    
    The legacy format contains 120+ columns including estimate data,
    market data, fundamentals, and AI predictions.
    
    Core estimate fields come first, followed by market data and fundamentals.
    """
    
    # Core estimate fields
    ticker: str
    start_date: date
    start_price: Decimal
    target_price: Decimal
    stop_loss_price: Decimal
    target_profit_percent: Decimal
    stop_loss_percent: Decimal
    direction: str  # "LONG" or "SHORT"
    status: str  # "OPEN", "CLOSED_WIN", "CLOSED_LOSS", etc.
    
    # Closure fields (nullable)
    close_date: Optional[date] = None
    exit_price: Optional[Decimal] = None
    realized_pnl: Optional[Decimal] = None
    realized_pnl_percent: Optional[Decimal] = None
    
    # AI fields
    ai_model: Optional[str] = None
    ai_confidence: Optional[Decimal] = None
    ai_reasoning: Optional[str] = None
    
    # Market data at start (snapshot)
    current_price: Optional[Decimal] = None
    day_change: Optional[Decimal] = None
    day_change_percent: Optional[Decimal] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    market_cap: Optional[Decimal] = None
    
    # Fundamentals (snapshot)
    pe_ratio: Optional[Decimal] = None
    eps: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    dividend_rate: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    week_52_high: Optional[Decimal] = None
    week_52_low: Optional[Decimal] = None
    week_52_change_percent: Optional[Decimal] = None
    
    # Technical indicators (snapshot)
    rsi_14: Optional[Decimal] = None
    sma_20: Optional[Decimal] = None
    sma_50: Optional[Decimal] = None
    sma_200: Optional[Decimal] = None
    ema_20: Optional[Decimal] = None
    ema_50: Optional[Decimal] = None
    
    # Additional metadata
    user_id: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None  # Comma-separated
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV export."""
        return {
            "Ticker": self.ticker,
            "Start Date": self.start_date.isoformat() if self.start_date else "",
            "Start Price": str(self.start_price),
            "Target Price": str(self.target_price),
            "Stop Loss": str(self.stop_loss_price),
            "Target %": str(self.target_profit_percent),
            "Stop Loss %": str(self.stop_loss_percent),
            "Direction": self.direction,
            "Status": self.status,
            "Close Date": self.close_date.isoformat() if self.close_date else "",
            "Exit Price": str(self.exit_price) if self.exit_price else "",
            "Realized P/L": str(self.realized_pnl) if self.realized_pnl else "",
            "Realized P/L %": str(self.realized_pnl_percent) if self.realized_pnl_percent else "",
            "AI Model": self.ai_model or "",
            "AI Confidence": str(self.ai_confidence) if self.ai_confidence else "",
            "AI Reasoning": self.ai_reasoning or "",
            "Current Price": str(self.current_price) if self.current_price else "",
            "Day Change": str(self.day_change) if self.day_change else "",
            "Day Change %": str(self.day_change_percent) if self.day_change_percent else "",
            "Volume": str(self.volume) if self.volume else "",
            "Avg Volume": str(self.avg_volume) if self.avg_volume else "",
            "Market Cap": str(self.market_cap) if self.market_cap else "",
            "P/E Ratio": str(self.pe_ratio) if self.pe_ratio else "",
            "EPS": str(self.eps) if self.eps else "",
            "Dividend Yield": str(self.dividend_yield) if self.dividend_yield else "",
            "Dividend Rate": str(self.dividend_rate) if self.dividend_rate else "",
            "Beta": str(self.beta) if self.beta else "",
            "52W High": str(self.week_52_high) if self.week_52_high else "",
            "52W Low": str(self.week_52_low) if self.week_52_low else "",
            "52W Change %": str(self.week_52_change_percent) if self.week_52_change_percent else "",
            "RSI(14)": str(self.rsi_14) if self.rsi_14 else "",
            "SMA(20)": str(self.sma_20) if self.sma_20 else "",
            "SMA(50)": str(self.sma_50) if self.sma_50 else "",
            "SMA(200)": str(self.sma_200) if self.sma_200 else "",
            "EMA(20)": str(self.ema_20) if self.ema_20 else "",
            "EMA(50)": str(self.ema_50) if self.ema_50 else "",
            "User ID": self.user_id or "",
            "Notes": self.notes or "",
            "Tags": self.tags or "",
            "Created At": self.created_at.isoformat() if self.created_at else "",
            "Updated At": self.updated_at.isoformat() if self.updated_at else "",
        }


@dataclass
class LegacyHistoryRow:
    """
    Represents a single row from the legacy History_*.csv files.
    
    These files contain daily market data snapshots for tracked tickers.
    Format: Date, Ticker, Open, High, Low, Close, Volume
    """
    
    date: date
    ticker: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    adjusted_close: Optional[Decimal] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV export."""
        return {
            "Date": self.date.isoformat(),
            "Ticker": self.ticker,
            "Open": str(self.open),
            "High": str(self.high),
            "Low": str(self.low),
            "Close": str(self.close),
            "Volume": str(self.volume),
            "Adj Close": str(self.adjusted_close) if self.adjusted_close else "",
        }
