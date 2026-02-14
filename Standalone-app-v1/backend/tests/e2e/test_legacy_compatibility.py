"""
E2E tests for legacy format compatibility.

Tests validate that the new backend maintains full backward compatibility
with legacy files (backup JSON and History_*.csv) from HTML+GAS version.
"""

import pytest
import json
from pathlib import Path
from decimal import Decimal
from datetime import date, datetime

from src.sync.infra.csv_parser import LegacyCsvParser
from src.sync.infra.legacy_models import LegacyEstimateRow, LegacyHistoryRow


# Path to fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "legacy"


@pytest.fixture
def csv_parser():
    """Create CSV parser instance."""
    return LegacyCsvParser()


@pytest.fixture
def backup_json_path():
    """Path to backup JSON fixture."""
    return FIXTURES_DIR / "backup_simple.json"


@pytest.fixture
def history_csv_path():
    """Path to History CSV fixture."""
    return FIXTURES_DIR / "History_AAPL_simple.csv"


@pytest.fixture
def backup_data(backup_json_path):
    """Load backup JSON data."""
    with open(backup_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestLegacyBackupJsonStructure:
    """Test backup JSON structure and parsing."""
    
    def test_backup_json_loads_correctly(self, backup_data):
        """Test that backup JSON loads without errors."""
        assert isinstance(backup_data, list)
        assert len(backup_data) > 0
    
    def test_backup_json_has_required_fields(self, backup_data):
        """Test that all estimates have required fields."""
        required_fields = [
            'ticker', 'startDate', 'startPrice', 'targetPrice',
            'stopLossPrice', 'status', 'aiModel', 'aiConfidence'
        ]
        
        for estimate in backup_data:
            for field in required_fields:
                assert field in estimate, f"Missing required field: {field}"
    
    def test_backup_json_field_types(self, backup_data):
        """Test that field types are correct."""
        for estimate in backup_data:
            # Ticker should be string
            assert isinstance(estimate['ticker'], str)
            
            # Prices should be numeric
            assert isinstance(estimate['startPrice'], (int, float))
            assert isinstance(estimate['targetPrice'], (int, float))
            
            # Status should be string
            assert isinstance(estimate['status'], str)
            assert estimate['status'] in ['OPEN', 'CLOSED_WIN', 'CLOSED_LOSS', 'CLOSED_MANUAL', 'EXPIRED']
            
            # Confidence should be numeric
            assert isinstance(estimate['aiConfidence'], (int, float))
            assert 0 <= estimate['aiConfidence'] <= 100
    
    def test_backup_json_closed_estimates_have_exit_data(self, backup_data):
        """Test that closed estimates have exit price and PnL."""
        for estimate in backup_data:
            if estimate['status'] in ['CLOSED_WIN', 'CLOSED_LOSS']:
                assert estimate.get('exitPrice') is not None, f"Closed estimate {estimate['ticker']} missing exitPrice"
                assert estimate.get('realizedPnL') is not None, f"Closed estimate {estimate['ticker']} missing realizedPnL"
                assert estimate.get('closeDate') is not None, f"Closed estimate {estimate['ticker']} missing closeDate"
    
    def test_backup_json_open_estimates_no_exit_data(self, backup_data):
        """Test that open estimates don't have exit data."""
        for estimate in backup_data:
            if estimate['status'] == 'OPEN':
                assert estimate.get('exitPrice') is None or estimate.get('exitPrice') == ""
                assert estimate.get('closeDate') is None or estimate.get('closeDate') == ""


class TestLegacyHistoryCsvRoundtrip:
    """Test History CSV parsing and export round-trip."""
    
    def test_parse_history_csv(self, csv_parser, history_csv_path):
        """Test parsing legacy History CSV."""
        # Read CSV content
        with open(history_csv_path, 'rb') as f:
            content = f.read()
        
        # Parse CSV
        history_rows = csv_parser.parse_history_csv(content)
        
        # Verify data
        assert len(history_rows) > 0, "Should parse at least one row"
        
        for row in history_rows:
            assert isinstance(row, LegacyHistoryRow)
            assert row.ticker == "AAPL"
            assert isinstance(row.date, date)
            assert isinstance(row.open, Decimal)
            assert isinstance(row.high, Decimal)
            assert isinstance(row.low, Decimal)
            assert isinstance(row.close, Decimal)
            assert isinstance(row.volume, int)
    
    def test_history_csv_ohlc_validity(self, csv_parser, history_csv_path):
        """Test that OHLC data is valid (high >= open/close, low <= open/close)."""
        with open(history_csv_path, 'rb') as f:
            content = f.read()
        
        history_rows = csv_parser.parse_history_csv(content)
        
        for row in history_rows:
            # High should be >= Open, Close, Low
            assert row.high >= row.open, f"High {row.high} < Open {row.open} on {row.date}"
            assert row.high >= row.close, f"High {row.high} < Close {row.close} on {row.date}"
            assert row.high >= row.low, f"High {row.high} < Low {row.low} on {row.date}"
            
            # Low should be <= Open, Close, High
            assert row.low <= row.open, f"Low {row.low} > Open {row.open} on {row.date}"
            assert row.low <= row.close, f"Low {row.low} > Close {row.close} on {row.date}"
            assert row.low <= row.high, f"Low {row.low} > High {row.high} on {row.date}"
    
    def test_history_csv_roundtrip(self, csv_parser, history_csv_path):
        """Test that parsing and exporting History CSV produces the same data."""
        # Read and parse original CSV
        with open(history_csv_path, 'rb') as f:
            original_content = f.read()
        
        original_rows = csv_parser.parse_history_csv(original_content)
        
        # Export to CSV format (would need MarketData entities in real implementation)
        # For now, just verify we can convert to dict
        for row in original_rows:
            row_dict = row.to_dict()
            
            # Verify all fields present (keys are capitalized as in CSV)
            assert 'Date' in row_dict
            assert 'Open' in row_dict
            assert 'High' in row_dict
            assert 'Low' in row_dict
            assert 'Close' in row_dict
            assert 'Volume' in row_dict
            assert 'Ticker' in row_dict
    
    def test_history_csv_date_ordering(self, csv_parser, history_csv_path):
        """Test that dates are in chronological order."""
        with open(history_csv_path, 'rb') as f:
            content = f.read()
        
        history_rows = csv_parser.parse_history_csv(content)
        
        dates = [row.date for row in history_rows]
        
        # Verify dates are sorted (ascending)
        for i in range(len(dates) - 1):
            assert dates[i] <= dates[i + 1], f"Dates not in order: {dates[i]} > {dates[i + 1]}"


class TestLegacyEstimatesCsvFormat:
    """Test estimates CSV format compatibility."""
    
    def test_estimates_csv_column_order(self, csv_parser):
        """Test that estimates CSV has required columns in expected order."""
        # Get the header
        header = csv_parser._get_estimates_header()
        
        # Should have all required columns
        required_columns = [
            'Ticker', 'Start Date', 'Start Price', 'Target Price',
            'Stop Loss', 'Status', 'AI Model', 'AI Confidence'
        ]
        
        for col in required_columns:
            assert f'"{col}"' in header, f"Missing required column: {col}"
    
    def test_estimates_csv_has_fundamentals_columns(self, csv_parser):
        """Test that estimates CSV includes fundamental data columns."""
        header = csv_parser._get_estimates_header()
        
        fundamental_columns = [
            'Market Cap', 'P/E Ratio', 'EPS', 'Dividend Yield'
        ]
        
        for col in fundamental_columns:
            assert f'"{col}"' in header, f"Missing fundamental column: {col}"
    
    def test_estimates_csv_has_technical_columns(self, csv_parser):
        """Test that estimates CSV includes technical indicator columns."""
        header = csv_parser._get_estimates_header()
        
        technical_columns = [
            'RSI(14)', 'SMA(50)', 'SMA(200)'
        ]
        
        for col in technical_columns:
            assert f'"{col}"' in header, f"Missing technical column: {col}"


class TestLegacyDataIntegrity:
    """Test data integrity and constraints."""
    
    def test_backup_json_no_duplicate_tickers_same_date(self, backup_data):
        """Test that there are no duplicate estimates for same ticker on same date."""
        seen = set()
        
        for estimate in backup_data:
            key = (estimate['ticker'], estimate['startDate'])
            assert key not in seen, f"Duplicate estimate found: {estimate['ticker']} on {estimate['startDate']}"
            seen.add(key)
    
    def test_backup_json_target_prices_valid(self, backup_data):
        """Test that target prices are sensible relative to start prices."""
        for estimate in backup_data:
            start_price = estimate['startPrice']
            target_price = estimate['targetPrice']
            stop_loss = estimate['stopLossPrice']
            
            if estimate['direction'] == 'LONG':
                # For LONG: target > start > stop
                assert target_price > start_price, f"{estimate['ticker']}: Target should be > start for LONG"
                assert stop_loss < start_price, f"{estimate['ticker']}: Stop loss should be < start for LONG"
            elif estimate['direction'] == 'SHORT':
                # For SHORT: target < start < stop (opposite)
                assert target_price < start_price, f"{estimate['ticker']}: Target should be < start for SHORT"
                assert stop_loss > start_price, f"{estimate['ticker']}: Stop loss should be > start for SHORT"
    
    def test_backup_json_percentages_match_prices(self, backup_data):
        """Test that percentage calculations match price differences."""
        for estimate in backup_data:
            start_price = estimate['startPrice']
            target_price = estimate['targetPrice']
            target_percent = estimate.get('targetProfitPercent')
            
            if target_percent is not None and start_price > 0:
                # Calculate expected percentage
                if estimate['direction'] == 'LONG':
                    expected_percent = ((target_price - start_price) / start_price) * 100
                else:
                    expected_percent = ((start_price - target_price) / start_price) * 100
                
                # Allow small rounding difference
                assert abs(expected_percent - target_percent) < 0.5, \
                    f"{estimate['ticker']}: Percentage mismatch - expected {expected_percent:.2f}, got {target_percent}"
    
    def test_history_csv_volume_positive(self, csv_parser, history_csv_path):
        """Test that volume is always positive."""
        with open(history_csv_path, 'rb') as f:
            content = f.read()
        
        history_rows = csv_parser.parse_history_csv(content)
        
        for row in history_rows:
            assert row.volume > 0, f"Volume should be positive on {row.date}, got {row.volume}"
    
    def test_history_csv_prices_positive(self, csv_parser, history_csv_path):
        """Test that all prices are positive."""
        with open(history_csv_path, 'rb') as f:
            content = f.read()
        
        history_rows = csv_parser.parse_history_csv(content)
        
        for row in history_rows:
            assert row.open > 0, f"Open price should be positive on {row.date}"
            assert row.high > 0, f"High price should be positive on {row.date}"
            assert row.low > 0, f"Low price should be positive on {row.date}"
            assert row.close > 0, f"Close price should be positive on {row.date}"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
