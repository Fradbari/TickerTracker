
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from src.sync.infra.csv_parser import LegacyCsvParser
from src.sync.infra.json_parser import LegacyJsonParser
from src.sync.infra.legacy_models import LegacyEstimateRow, LegacyHistoryRow

# Path to fixtures provided by USER
FIXTURES_DIR = Path(os.getcwd()) / "tests" / "fixtures" / "legacy"
HISTORY_SAP_FILE = FIXTURES_DIR / "History_SAP.csv"
BACKUP_JSON_FILE = FIXTURES_DIR / "TickerTracker_1771064737397.json"

class TestProvidedLegacyFiles:
    """
    Validation tests for specific legacy files provided by USER.
    Ensures 'full retro compatibility' as requested.
    """

    def test_history_sap_csv_compatibility(self):
        """Test parsing of History_SAP.csv with various column names and formats."""
        parser = LegacyCsvParser()

        assert HISTORY_SAP_FILE.exists(), f"File not found: {HISTORY_SAP_FILE}"

        with open(HISTORY_SAP_FILE, 'rb') as f:
            content = f.read()

        # Ticker inferred from filename
        ticker = "SAP"
        rows = parser.parse_history_csv(content, default_ticker=ticker)

        assert len(rows) > 0, "No rows parsed from History_SAP.csv"
        assert rows[0].ticker == "SAP"
        assert isinstance(rows[0].date, date)
        assert rows[0].open > 0
        assert rows[0].volume > 0
        assert rows[0].adjusted_close is not None

        print(f"Successfully validated {len(rows)} rows from History_SAP.csv")

    def test_ticker_tracker_json_v4_compatibility(self):
        """Test parsing of TickerTracker version 4.0 JSON backup."""
        parser = LegacyJsonParser()

        assert BACKUP_JSON_FILE.exists(), f"File not found: {BACKUP_JSON_FILE}"

        with open(BACKUP_JSON_FILE, encoding='utf-8') as f:
            content = f.read()

        estimates = parser.parse_backup_json(content)

        assert len(estimates) > 0, "No estimates parsed from backup JSON"

        # Verify first estimate (ORCL as seen in previous steps)
        orcl = next((e for e in estimates if e.ticker == "ORCL"), None)
        assert orcl is not None
        assert orcl.start_price == Decimal("214.33")
        assert orcl.status == "CLOSED_LOSS"  # completed-negative -> CLOSED_LOSS
        assert orcl.ai_model == "Copilot"

        # Verify diversity
        tickers = {e.ticker for e in estimates}
        assert "PLTR" in tickers
        assert "GOOGL" in tickers
        assert "AMZN" in tickers

        print(f"Successfully validated {len(estimates)} estimates from TickerTracker_1771064737397.json")

    def test_legacy_data_conversions(self):
        """Test that legacy models can be converted back to dictionaries for export."""
        LegacyCsvParser()

        # Sample history row
        h_row = LegacyHistoryRow(
            date=date(2024, 1, 1),
            ticker="TEST",
            open=Decimal("100.00"),
            high=Decimal("105.00"),
            low=Decimal("95.00"),
            close=Decimal("102.00"),
            volume=1000,
            adjusted_close=Decimal("101.50")
        )

        d = h_row.to_dict()
        assert d["Date"] == "2024-01-01"
        assert d["Ticker"] == "TEST"
        assert d["Adj Close"] == "101.50"

        # Sample estimate row
        e_row = LegacyEstimateRow(
            ticker="AAPL",
            start_date=date(2024, 1, 1),
            start_price=Decimal("180.00"),
            target_price=Decimal("200.00"),
            stop_loss_price=Decimal("170.00"),
            target_profit_percent=Decimal("11.1"),
            stop_loss_percent=Decimal("-5.5"),
            direction="LONG",
            status="OPEN"
        )

        d_est = e_row.to_dict()
        assert d_est["Ticker"] == "AAPL"
        assert d_est["Status"] == "OPEN"
        assert d_est["Target %"] == "11.1"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
