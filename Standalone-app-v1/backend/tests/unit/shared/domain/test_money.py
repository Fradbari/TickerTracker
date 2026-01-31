"""Unit tests for Money value object."""

import pytest
from decimal import Decimal
from src.shared.domain.value_objects import Money


class TestMoneyConstruction:
    """Test Money object construction and validation."""
    
    def test_create_money_with_defaults(self):
        """Money should create with Decimal and default USD currency."""
        money = Money(amount=Decimal("100.50"))
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"
    
    def test_create_money_with_custom_currency(self):
        """Money should create with specified currency."""
        money = Money(amount=Decimal("50.00"), currency="EUR")
        assert money.amount == Decimal("50.00")
        assert money.currency == "EUR"
    
    def test_convert_int_to_decimal(self):
        """Money should convert int to Decimal."""
        money = Money(amount=100)
        assert isinstance(money.amount, Decimal)
        assert money.amount == Decimal("100")
    
    def test_convert_float_to_decimal(self):
        """Money should convert float to Decimal (via string to avoid precision loss)."""
        money = Money(amount=100.50)
        assert isinstance(money.amount, Decimal)
        assert money.amount == Decimal("100.5")
    
    def test_convert_string_to_decimal(self):
        """Money should convert string to Decimal."""
        money = Money(amount="99.99")
        assert isinstance(money.amount, Decimal)
        assert money.amount == Decimal("99.99")
    
    def test_invalid_currency_too_short(self):
        """Money should reject currency shorter than 3 characters."""
        with pytest.raises(ValueError, match="3-character"):
            Money(amount=Decimal("100"), currency="US")
    
    def test_invalid_currency_too_long(self):
        """Money should reject currency longer than 3 characters."""
        with pytest.raises(ValueError, match="3-character"):
            Money(amount=Decimal("100"), currency="USDA")
    
    def test_invalid_currency_lowercase(self):
        """Money should reject lowercase currency."""
        with pytest.raises(ValueError, match="3-character uppercase"):
            Money(amount=Decimal("100"), currency="usd")
    
    def test_invalid_currency_mixed_case(self):
        """Money should reject mixed case currency."""
        with pytest.raises(ValueError, match="3-character uppercase"):
            Money(amount=Decimal("100"), currency="Usd")
    
    def test_invalid_amount_non_numeric(self):
        """Money should reject non-numeric amounts."""
        with pytest.raises(Exception):  # decimal.InvalidOperation
            Money(amount="abc")
    
    def test_money_is_immutable(self):
        """Money should be frozen (immutable)."""
        money = Money(amount=Decimal("100"))
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            money.amount = Decimal("200")


class TestMoneyArithmetic:
    """Test Money arithmetic operations."""
    
    def test_add_same_currency(self):
        """Adding Money objects with same currency should work."""
        m1 = Money(amount=Decimal("100"), currency="USD")
        m2 = Money(amount=Decimal("50"), currency="USD")
        result = m1 + m2
        
        assert result.amount == Decimal("150")
        assert result.currency == "USD"
    
    def test_add_different_currency_raises_error(self):
        """Adding Money objects with different currencies should raise ValueError."""
        m1 = Money(amount=Decimal("100"), currency="USD")
        m2 = Money(amount=Decimal("50"), currency="EUR")
        
        with pytest.raises(ValueError, match="different currencies"):
            m1 + m2
    
    def test_add_non_money_raises_error(self):
        """Adding Money to non-Money should raise TypeError."""
        m1 = Money(amount=Decimal("100"))
        
        with pytest.raises(TypeError):
            m1 + 50
    
    def test_subtract_same_currency(self):
        """Subtracting Money objects with same currency should work."""
        m1 = Money(amount=Decimal("100"), currency="USD")
        m2 = Money(amount=Decimal("30"), currency="USD")
        result = m1 - m2
        
        assert result.amount == Decimal("70")
        assert result.currency == "USD"
    
    def test_subtract_different_currency_raises_error(self):
        """Subtracting Money objects with different currencies should raise ValueError."""
        m1 = Money(amount=Decimal("100"), currency="USD")
        m2 = Money(amount=Decimal("50"), currency="EUR")
        
        with pytest.raises(ValueError, match="different currencies"):
            m1 - m2
    
    def test_subtract_non_money_raises_error(self):
        """Subtracting non-Money from Money should raise TypeError."""
        m1 = Money(amount=Decimal("100"))
        
        with pytest.raises(TypeError):
            m1 - 30
    
    def test_multiply_by_int(self):
        """Multiplying Money by int should work."""
        m = Money(amount=Decimal("10"), currency="USD")
        result = m * 5
        
        assert result.amount == Decimal("50")
        assert result.currency == "USD"
    
    def test_multiply_by_decimal(self):
        """Multiplying Money by Decimal should work."""
        m = Money(amount=Decimal("10"), currency="USD")
        result = m * Decimal("2.5")
        
        assert result.amount == Decimal("25")
        assert result.currency == "USD"
    
    def test_multiply_by_float_raises_error(self):
        """Multiplying Money by float should raise TypeError."""
        m = Money(amount=Decimal("10"))
        
        with pytest.raises(TypeError):
            m * 2.5
    
    def test_multiply_by_string_raises_error(self):
        """Multiplying Money by string should raise TypeError."""
        m = Money(amount=Decimal("10"))
        
        with pytest.raises(TypeError):
            m * "5"
    
    def test_rmul_int(self):
        """Right multiplication by int should work (e.g., 5 * money)."""
        m = Money(amount=Decimal("10"), currency="USD")
        result = 5 * m
        
        assert result.amount == Decimal("50")
        assert result.currency == "USD"
    
    def test_negate(self):
        """Negating Money should flip the sign."""
        m = Money(amount=Decimal("100"), currency="USD")
        result = -m
        
        assert result.amount == Decimal("-100")
        assert result.currency == "USD"
    
    def test_negate_negative(self):
        """Negating negative Money should result in positive."""
        m = Money(amount=Decimal("-100"), currency="USD")
        result = -m
        
        assert result.amount == Decimal("100")
        assert result.currency == "USD"


class TestMoneyRounding:
    """Test Money rounding operations."""
    
    def test_round_down(self):
        """Rounding should use ROUND_HALF_UP strategy."""
        m = Money(amount=Decimal("10.124"), currency="USD")
        result = m.round(places=2)
        
        assert result.amount == Decimal("10.12")
        assert result.currency == "USD"
    
    def test_round_up(self):
        """Rounding .5 and above should round up with ROUND_HALF_UP."""
        m = Money(amount=Decimal("10.125"), currency="USD")
        result = m.round(places=2)
        
        assert result.amount == Decimal("10.13")
    
    def test_round_zero_places(self):
        """Rounding to 0 places should work."""
        m = Money(amount=Decimal("10.6"), currency="USD")
        result = m.round(places=0)
        
        assert result.amount == Decimal("11")
    
    def test_round_preserves_currency(self):
        """Rounding should preserve currency."""
        m = Money(amount=Decimal("10.125"), currency="EUR")
        result = m.round(places=2)
        
        assert result.currency == "EUR"


class TestMoneySerializtion:
    """Test Money serialization and deserialization."""
    
    def test_to_dict(self):
        """to_dict should serialize Money to dict with string amount."""
        m = Money(amount=Decimal("100.50"), currency="EUR")
        result = m.to_dict()
        
        assert result == {"amount": "100.50", "currency": "EUR"}
        assert isinstance(result["amount"], str)
    
    def test_from_dict(self):
        """from_dict should deserialize dict to Money."""
        data = {"amount": "100.50", "currency": "EUR"}
        m = Money.from_dict(data)
        
        assert m.amount == Decimal("100.50")
        assert m.currency == "EUR"
    
    def test_from_dict_default_currency(self):
        """from_dict should default to USD if currency not provided."""
        data = {"amount": "100"}
        m = Money.from_dict(data)
        
        assert m.amount == Decimal("100")
        assert m.currency == "USD"
    
    def test_from_dict_missing_amount(self):
        """from_dict should raise KeyError if amount is missing."""
        data = {"currency": "EUR"}
        
        with pytest.raises(KeyError):
            Money.from_dict(data)
    
    def test_roundtrip_serialization(self):
        """Serialize and deserialize should yield equal Money."""
        original = Money(amount=Decimal("99.99"), currency="GBP")
        serialized = original.to_dict()
        deserialized = Money.from_dict(serialized)
        
        assert deserialized.amount == original.amount
        assert deserialized.currency == original.currency
    
    def test_roundtrip_with_many_decimals(self):
        """Roundtrip should preserve precision with many decimal places."""
        original = Money(amount=Decimal("123.456789"), currency="JPY")
        serialized = original.to_dict()
        deserialized = Money.from_dict(serialized)
        
        assert deserialized.amount == original.amount
        assert deserialized.currency == original.currency


class TestMoneyStringRepresentation:
    """Test Money string representations."""
    
    def test_str(self):
        """str() should return formatted string."""
        m = Money(amount=Decimal("100.50"), currency="USD")
        assert str(m) == "100.50 USD"
    
    def test_repr(self):
        """repr() should return developer-friendly representation."""
        m = Money(amount=Decimal("100.50"), currency="USD")
        result = repr(m)
        
        assert "Money" in result
        assert "100.50" in result
        assert "USD" in result
