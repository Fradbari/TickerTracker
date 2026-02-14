"""
Unit tests for Legacy CSV Parser.

Tests parsing and export of legacy CSV formats with various edge cases.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO

from src.sync.infra.csv_parser import LegacyCsvParser
from src.sync.infra.legacy_models import LegacyEstimateRow, LegacyHistoryRow


@pytest.fixture
def parser():
    """Create parser instance."""
    return LegacyCsvParser()


@pytest.fixture
def sample_estimates_csv():
    """Sample estimates CSV content."""
    csv_content = """Ticker,Start Date,Start Price,Target Price,Stop Loss,Target %,Stop Loss %,Direction,Status,Close Date,Exit Price,Realized P/L,Realized P/L %,AI Model,AI Confidence,AI Reasoning,Current Price,Day Change,Day Change %,Volume,Avg Volume,Market Cap,P/E Ratio,EPS,Dividend Yield,Dividend Rate,Beta,52W High,52W Low,52W Change %,RSI(14),SMA(20),SMA(50),SMA(200),EMA(20),EMA(50),User ID,Notes,Tags,Created At,Updated At
AAPL,2024-01-15,150.00,165.00,140.00,10.00,-6.67,LONG,CLOSED_WIN,2024-02-01,164.50,14.50,9.67,gpt-4,85,Strong upward momentum,150.50,2.30,1.55,95234567,78456123,2450000000000,28.5,5.25,0.52,0.78,1.15,175.30,125.40,18.25,65.4,148.30,145.20,142.50,149.10,146.80,a1b2c3d4,Good trade,tech;growth,2024-01-15T09:30:00,2024-02-01T16:00:00
MSFT,2024-01-20,380.00,400.00,360.00,5.26,-5.26,LONG,OPEN,,,,,gemini,75,Positive cloud growth,381.50,1.50,0.39,45678912,52345678,2850000000000,32.1,11.85,0.75,2.85,0.92,420.50,320.10,15.40,58.2,378.50,375.20,370.00,379.30,376.40,a1b2c3d4,Cloud play,tech;enterprise,2024-01-20T10:15:00,2024-01-20T10:15:00
"""
    return csv_content.encode('utf-8-sig')


@pytest.fixture
def sample_history_csv():
    """Sample history CSV content."""
    csv_content = """Date,Ticker,Open,High,Low,Close,Volume,Adj Close
2024-01-15,AAPL,148.50,152.30,147.80,150.00,95234567,149.85
2024-01-16,AAPL,150.20,153.40,149.90,152.80,87456123,152.65
2024-01-17,AAPL,152.00,154.20,151.50,153.50,92345678,153.35
"""
    return csv_content.encode('utf-8-sig')


class TestLegacyCsvParserInit:
    """Test parser initialization."""
    
    def test_init(self, parser):
        """Test parser initializes with mappings."""
        assert parser.estimates_map is not None
        assert parser.history_map is not None
        assert len(parser.estimates_map) > 0
        assert len(parser.history_map) > 0


class TestSafeConversions:
    """Test safe type conversion methods."""
    
    def test_safe_decimal_valid(self, parser):
        """Test safe_decimal with valid input."""
        result = parser._safe_decimal("150.00")
        assert result == Decimal("150.00")
    
    def test_safe_decimal_with_comma(self, parser):
        """Test safe_decimal removes commas."""
        result = parser._safe_decimal("1,234.56")
        assert result == Decimal("1234.56")
    
    def test_safe_decimal_with_currency(self, parser):
        """Test safe_decimal removes currency symbols."""
        result = parser._safe_decimal("$150.00")
        assert result == Decimal("150.00")
    
    def test_safe_decimal_empty(self, parser):
        """Test safe_decimal with empty string."""
        result = parser._safe_decimal("")
        assert result is None
    
    def test_safe_decimal_invalid(self, parser):
        """Test safe_decimal with invalid input."""
        result = parser._safe_decimal("invalid")
        assert result is None
    
    def test_safe_decimal_with_default(self, parser):
        """Test safe_decimal with default value."""
        result = parser._safe_decimal("", Decimal("0"))
        assert result == Decimal("0")
    
    def test_safe_int_valid(self, parser):
        """Test safe_int with valid input."""
        result = parser._safe_int("12345")
        assert result == 12345
    
    def test_safe_int_with_comma(self, parser):
        """Test safe_int removes commas."""
        result = parser._safe_int("1,234,567")
        assert result == 1234567
    
    def test_safe_int_empty(self, parser):
        """Test safe_int with empty string."""
        result = parser._safe_int("")
        assert result is None
    
    def test_safe_date_iso(self, parser):
        """Test safe_date with ISO format."""
        result = parser._safe_date("2024-01-15")
        assert result == date(2024, 1, 15)
    
    def test_safe_date_us_format(self, parser):
        """Test safe_date with US format."""
        result = parser._safe_date("01/15/2024")
        assert result == date(2024, 1, 15)
    
    def test_safe_date_empty(self, parser):
        """Test safe_date with empty string."""
        result = parser._safe_date("")
        assert result is None
    
    def test_safe_datetime_iso(self, parser):
        """Test safe_datetime with ISO format."""
        result = parser._safe_datetime("2024-01-15T09:30:00")
        assert result == datetime(2024, 1, 15, 9, 30, 0)


class TestParseEstimatesCsv:
    """Test parse_estimates_csv method."""
    
    def test_parse_valid_csv(self, parser, sample_estimates_csv):
        """Test parsing valid estimates CSV."""
        rows = parser.parse_estimates_csv(sample_estimates_csv)
        
        assert len(rows) == 2
        
        # Check first row (AAPL CLOSED_WIN)
        aapl = rows[0]
        assert aapl.ticker == "AAPL"
        assert aapl.start_price == Decimal("150.00")
        assert aapl.target_price == Decimal("165.00")
        assert aapl.stop_loss_price == Decimal("140.00")
        assert aapl.direction == "LONG"
        assert aapl.status == "CLOSED_WIN"
        assert aapl.exit_price == Decimal("164.50")
        assert aapl.ai_model == "gpt-4"
        assert aapl.ai_confidence == Decimal("85")
        
        # Check second row (MSFT OPEN)
        msft = rows[1]
        assert msft.ticker == "MSFT"
        assert msft.start_price == Decimal("380.00")
        assert msft.status == "OPEN"
        assert msft.exit_price is None
        assert msft.ai_model == "gemini"
    
    def test_parse_empty_csv(self, parser):
        """Test parsing empty CSV."""
        csv_content = b"Ticker,Start Date,Start Price,Target Price,Stop Loss,Target %,Stop Loss %,Direction,Status\n"
        rows = parser.parse_estimates_csv(csv_content)
        assert len(rows) == 0
    
    def test_parse_missing_required_fields(self, parser):
        """Test parsing CSV with missing required fields."""
        csv_content = """Ticker,Start Date,Start Price,Target Price,Stop Loss
AAPL,2024-01-15,,,
""".encode('utf-8')
        rows = parser.parse_estimates_csv(csv_content)
        assert len(rows) == 0  # Row should be skipped
    
    def test_parse_utf8_bom(self, parser):
        """Test parsing CSV with UTF-8 BOM."""
        csv_content = b'\xef\xbb\xbf' + b"Ticker,Start Date,Start Price,Target Price,Stop Loss,Target %,Stop Loss %,Direction,Status\nAAPL,2024-01-15,150.00,165.00,140.00,10.00,-6.67,LONG,OPEN\n"
        rows = parser.parse_estimates_csv(csv_content)
        assert len(rows) == 1
        assert rows[0].ticker == "AAPL"
    
    def test_parse_invalid_encoding(self, parser):
        """Test parsing CSV with invalid encoding."""
        csv_content = b'\xff\xfe'  # UTF-16 BOM
        with pytest.raises(ValueError, match="Invalid UTF-8 encoding"):
            parser.parse_estimates_csv(csv_content)


class TestExportEstimateToCsvRow:
    """Test export_estimate_to_csv_row method."""
    
    def test_export_basic_estimate(self, parser):
        """Test exporting basic estimate without fundamentals."""
        from unittest.mock import Mock
        
        # Create mock estimate
        estimate = Mock()
        estimate.ticker = Mock(symbol="AAPL")
        estimate.created_at = datetime(2024, 1, 15, 9, 30, 0)
        estimate.start_price = Decimal("150.00")
        estimate.target_price = Decimal("165.00")
        estimate.stop_loss_price = Decimal("140.00")
        estimate.target_profit_percent = Decimal("10.00")
        estimate.stop_loss_percent = Decimal("-6.67")
        estimate.direction = Mock(value="LONG")
        estimate.status = Mock(value="OPEN")
        estimate.closed_at = None
        estimate.exit_price = None
        estimate.realized_pnl = None
        estimate.ai_model = "gpt-4"
        estimate.ai_confidence = Decimal("85")
        estimate.ai_reasoning = "Strong upward momentum"
        estimate.user_id = "a1b2c3d4"
        estimate.updated_at = datetime(2024, 1, 15, 9, 30, 0)
        
        # Export to CSV row
        csv_row = parser.export_estimate_to_csv_row(estimate)
        
        # Verify content
        assert "AAPL" in csv_row
        assert "150.00" in csv_row
        assert "165.00" in csv_row
        assert "LONG" in csv_row
        assert "OPEN" in csv_row


class TestParseHistoryCsv:
    """Test parse_history_csv method."""
    
    def test_parse_valid_history(self, parser, sample_history_csv):
        """Test parsing valid history CSV."""
        rows = parser.parse_history_csv(sample_history_csv)
        
        assert len(rows) == 3
        
        # Check first row
        row1 = rows[0]
        assert row1.date == date(2024, 1, 15)
        assert row1.ticker == "AAPL"
        assert row1.open == Decimal("148.50")
        assert row1.high == Decimal("152.30")
        assert row1.low == Decimal("147.80")
        assert row1.close == Decimal("150.00")
        assert row1.volume == 95234567
        assert row1.adjusted_close == Decimal("149.85")
    
    def test_parse_empty_history(self, parser):
        """Test parsing empty history CSV."""
        csv_content = b"Date,Ticker,Open,High,Low,Close,Volume\n"
        rows = parser.parse_history_csv(csv_content)
        assert len(rows) == 0
    
    def test_parse_history_missing_fields(self, parser):
        """Test parsing history CSV with missing fields."""
        csv_content = """Date,Ticker,Open,High,Low,Close,Volume
2024-01-15,AAPL,,,,,
""".encode('utf-8')
        rows = parser.parse_history_csv(csv_content)
        assert len(rows) == 0  # Row should be skipped


class TestExportHistoryToCsv:
    """Test export_history_to_csv method."""
    
    def test_export_empty_list(self, parser):
        """Test exporting empty list."""
        csv_bytes = parser.export_history_to_csv([])
        
        # Should contain BOM + empty CSV
        assert csv_bytes.startswith(b'\xef\xbb\xbf')
    
    def test_export_market_data(self, parser):
        """Test exporting market data list."""
        from unittest.mock import Mock
        
        # Create mock market data
        md1 = Mock()
        md1.date = date(2024, 1, 15)
        md1.ticker = Mock(symbol="AAPL")
        md1.open = Decimal("148.50")
        md1.high = Decimal("152.30")
        md1.low = Decimal("147.80")
        md1.close = Decimal("150.00")
        md1.volume = 95234567
        md1.adjusted_close = Decimal("149.85")
        
        csv_bytes = parser.export_history_to_csv([md1])
        
        # Verify content
        csv_text = csv_bytes.decode('utf-8-sig')
        assert "Date,Ticker,Open,High,Low,Close,Volume,Adj Close" in csv_text
        assert "2024-01-15" in csv_text
        assert "AAPL" in csv_text
        assert "150.00" in csv_text


class TestRoundTrip:
    """Test round-trip parsing and export."""
    
    def test_estimates_round_trip(self, parser, sample_estimates_csv):
        """Test parse -> export -> parse produces same data."""
        # First parse
        rows1 = parser.parse_estimates_csv(sample_estimates_csv)
        
        # Export to CSV
        csv_lines = []
        # Add header (assuming same order as LegacyEstimateRow.to_dict())
        header = rows1[0].to_dict().keys()
        csv_lines.append(",".join(header))
        
        # Add rows
        for row in rows1:
            row_dict = row.to_dict()
            csv_lines.append(",".join(str(v) for v in row_dict.values()))
        
        csv_content = "\n".join(csv_lines).encode('utf-8')
        
        # Second parse
        rows2 = parser.parse_estimates_csv(csv_content)
        
        # Compare
        assert len(rows1) == len(rows2)
        for r1, r2 in zip(rows1, rows2):
            assert r1.ticker == r2.ticker
            assert r1.start_price == r2.start_price
            assert r1.target_price == r2.target_price
            assert r1.status == r2.status
    
    def test_history_round_trip(self, parser, sample_history_csv):
        """Test parse -> export -> parse produces same data for history."""
        # First parse
        rows1 = parser.parse_history_csv(sample_history_csv)
        
        # Mock MarketData entities
        from unittest.mock import Mock
        market_data = []
        for row in rows1:
            md = Mock()
            md.date = row.date
            md.ticker = Mock(symbol=row.ticker)
            md.open = row.open
            md.high = row.high
            md.low = row.low
            md.close = row.close
            md.volume = row.volume
            md.adjusted_close = row.adjusted_close
            market_data.append(md)
        
        # Export
        csv_bytes = parser.export_history_to_csv(market_data)
        
        # Second parse
        rows2 = parser.parse_history_csv(csv_bytes)
        
        # Compare
        assert len(rows1) == len(rows2)
        for r1, r2 in zip(rows1, rows2):
            assert r1.date == r2.date
            assert r1.ticker == r2.ticker
            assert r1.open == r2.open
            assert r1.close == r2.close


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_parse_very_long_reasoning(self, parser):
        """Test parsing with very long AI reasoning text."""
        csv_content = """Ticker,Start Date,Start Price,Target Price,Stop Loss,Target %,Stop Loss %,Direction,Status,AI Reasoning
AAPL,2024-01-15,150.00,165.00,140.00,10.00,-6.67,LONG,OPEN,""" + "A" * 10000 + "\n"
        rows = parser.parse_estimates_csv(csv_content.encode('utf-8'))
        assert len(rows) == 1
        assert len(rows[0].ai_reasoning) == 10000
    
    def test_parse_special_characters(self, parser):
        """Test parsing with special characters in text fields."""
        csv_content = """Ticker,Start Date,Start Price,Target Price,Stop Loss,Target %,Stop Loss %,Direction,Status,Notes
AAPL,2024-01-15,150.00,165.00,140.00,10.00,-6.67,LONG,OPEN,"Quote with ""nested"" quotes and, commas"
""".encode('utf-8')
        rows = parser.parse_estimates_csv(csv_content)
        assert len(rows) == 1
    
    def test_parse_negative_values(self, parser):
        """Test parsing with negative price values."""
        csv_content = """Ticker,Start Date,Start Price,Target Price,Stop Loss,Target %,Stop Loss %,Direction,Status
AAPL,2024-01-15,150.00,165.00,140.00,-10.00,-6.67,LONG,OPEN
""".encode('utf-8')
        rows = parser.parse_estimates_csv(csv_content)
        assert len(rows) == 1
        assert rows[0].target_profit_percent == Decimal("-10.00")
