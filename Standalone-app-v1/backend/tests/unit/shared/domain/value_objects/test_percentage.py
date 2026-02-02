"""Unit tests for Percentage value object."""

from decimal import Decimal

import pytest

from src.shared.domain.value_objects import Money, Percentage


class TestPercentageConstruction:
    """Test Percentage object construction and validation."""

    def test_create_percentage_with_decimal(self):
        """Percentage should create with Decimal value."""
        pct = Percentage(value=Decimal("0.10"))
        assert pct.value == Decimal("0.10")

    def test_create_percentage_with_int(self):
        """Percentage should convert int to Decimal."""
        pct = Percentage(value=0)
        assert isinstance(pct.value, Decimal)
        assert pct.value == Decimal("0")

    def test_create_percentage_with_float(self):
        """Percentage should convert float to Decimal."""
        pct = Percentage(value=0.10)
        assert isinstance(pct.value, Decimal)
        assert pct.value == Decimal("0.1")

    def test_create_percentage_with_string(self):
        """Percentage should convert string to Decimal."""
        pct = Percentage(value="0.15")
        assert isinstance(pct.value, Decimal)
        assert pct.value == Decimal("0.15")

    def test_invalid_percentage_non_numeric(self):
        """Percentage should reject non-numeric values."""
        with pytest.raises(TypeError):  # Converted to TypeError in __post_init__
            Percentage(value="abc")

    def test_percentage_is_immutable(self):
        """Percentage should be frozen (immutable)."""
        pct = Percentage(value=Decimal("0.10"))
        from dataclasses import FrozenInstanceError

        with pytest.raises(FrozenInstanceError):
            pct.value = Decimal("0.20")  # type: ignore


class TestPercentageBasisPoints:
    """Test conversion between basis points and percentages."""

    def test_100_basis_points_equals_1_percent(self):
        """100 basis points should equal 1% (0.01)."""
        pct = Percentage.from_basis_points(100)
        assert pct.value == Decimal("0.01")

    def test_50_basis_points_equals_0_5_percent(self):
        """50 basis points should equal 0.5% (0.005)."""
        pct = Percentage.from_basis_points(50)
        assert pct.value == Decimal("0.005")

    def test_1_basis_point_equals_0_01_percent(self):
        """1 basis point should equal 0.01% (0.0001)."""
        pct = Percentage.from_basis_points(1)
        assert pct.value == Decimal("0.0001")

    def test_1000_basis_points_equals_10_percent(self):
        """1000 basis points should equal 10% (0.10)."""
        pct = Percentage.from_basis_points(1000)
        assert pct.value == Decimal("0.10")

    def test_zero_basis_points(self):
        """0 basis points should equal 0%."""
        pct = Percentage.from_basis_points(0)
        assert pct.value == Decimal("0")

    def test_negative_basis_points(self):
        """Negative basis points should work (for discounts)."""
        pct = Percentage.from_basis_points(-100)
        assert pct.value == Decimal("-0.01")

    def test_basis_points_non_integer_raises_error(self):
        """Basis points must be an integer."""
        with pytest.raises(TypeError):
            Percentage.from_basis_points(100.5)


class TestPercentageApplyTo:
    """Test applying percentage to Money amounts."""

    def test_apply_10_percent_to_100_usd(self):
        """10% applied to 100 USD should return 110 USD."""
        pct = Percentage(value=Decimal("0.10"))
        money = Money(amount=Decimal("100"), currency="USD")
        result = pct.apply_to(money)

        assert result.amount == Decimal("110")
        assert result.currency == "USD"

    def test_apply_5_percent_to_200_eur(self):
        """5% applied to 200 EUR should return 210 EUR."""
        pct = Percentage(value=Decimal("0.05"))
        money = Money(amount=Decimal("200"), currency="EUR")
        result = pct.apply_to(money)

        assert result.amount == Decimal("210")
        assert result.currency == "EUR"

    def test_apply_negative_percentage(self):
        """Negative percentage should reduce amount."""
        pct = Percentage(value=Decimal("-0.20"))
        money = Money(amount=Decimal("100"), currency="USD")
        result = pct.apply_to(money)

        assert result.amount == Decimal("80")

    def test_apply_percentage_to_non_money_raises_error(self):
        """apply_to should only work with Money objects."""
        pct = Percentage(value=Decimal("0.10"))

        with pytest.raises(TypeError):
            pct.apply_to(100)

    def test_apply_percentage_preserves_precision(self):
        """apply_to should preserve decimal precision."""
        pct = Percentage(value=Decimal("0.015"))
        money = Money(amount=Decimal("333.33"), currency="USD")
        result = pct.apply_to(money)

        expected = Decimal("333.33") * (Decimal(1) + Decimal("0.015"))
        assert result.amount == expected


class TestPercentageAsMultiplier:
    """Test conversion to multiplier format."""

    def test_10_percent_as_multiplier(self):
        """10% should return 1.10 as multiplier."""
        pct = Percentage(value=Decimal("0.10"))
        multiplier = pct.as_multiplier()

        assert multiplier == Decimal("1.10")

    def test_zero_percent_as_multiplier(self):
        """0% should return 1.00 as multiplier."""
        pct = Percentage(value=Decimal("0"))
        multiplier = pct.as_multiplier()

        assert multiplier == Decimal("1")

    def test_negative_10_percent_as_multiplier(self):
        """-10% should return 0.90 as multiplier."""
        pct = Percentage(value=Decimal("-0.10"))
        multiplier = pct.as_multiplier()

        assert multiplier == Decimal("0.90")

    def test_multiplier_with_decimal_places(self):
        """Multiplier should preserve decimal places."""
        pct = Percentage(value=Decimal("0.015"))
        multiplier = pct.as_multiplier()

        assert multiplier == Decimal("1.015")


class TestPercentageArithmetic:
    """Test arithmetic operations on percentages."""

    def test_add_percentages(self):
        """Adding two percentages should sum their values."""
        pct1 = Percentage(value=Decimal("0.10"))
        pct2 = Percentage(value=Decimal("0.05"))
        result = pct1 + pct2

        assert result.value == Decimal("0.15")

    def test_add_negative_percentage(self):
        """Adding negative percentage should reduce value."""
        pct1 = Percentage(value=Decimal("0.20"))
        pct2 = Percentage(value=Decimal("-0.05"))
        result = pct1 + pct2

        assert result.value == Decimal("0.15")

    def test_add_non_percentage_raises_error(self):
        """Adding Percentage to non-Percentage should raise TypeError."""
        pct = Percentage(value=Decimal("0.10"))

        with pytest.raises(TypeError):
            pct + 0.05

    def test_subtract_percentages(self):
        """Subtracting two percentages should find difference."""
        pct1 = Percentage(value=Decimal("0.20"))
        pct2 = Percentage(value=Decimal("0.05"))
        result = pct1 - pct2

        assert result.value == Decimal("0.15")

    def test_subtract_non_percentage_raises_error(self):
        """Subtracting non-Percentage from Percentage should raise TypeError."""
        pct = Percentage(value=Decimal("0.10"))

        with pytest.raises(TypeError):
            pct - 0.05


class TestPercentageSerialization:
    """Test serialization and deserialization of percentages."""

    def test_to_dict(self):
        """to_dict should serialize Percentage to dict with string value."""
        pct = Percentage(value=Decimal("0.10"))
        result = pct.to_dict()

        assert result == {"value": "0.10"}
        assert isinstance(result["value"], str)

    def test_from_dict(self):
        """from_dict should deserialize dict to Percentage."""
        data = {"value": "0.10"}
        pct = Percentage.from_dict(data)

        assert pct.value == Decimal("0.10")

    def test_from_dict_missing_value(self):
        """from_dict should raise KeyError if value is missing."""
        data = {}

        with pytest.raises(KeyError):
            Percentage.from_dict(data)

    def test_roundtrip_serialization(self):
        """Serialize and deserialize should yield equal Percentage."""
        original = Percentage(value=Decimal("0.125"))
        serialized = original.to_dict()
        deserialized = Percentage.from_dict(serialized)

        assert deserialized.value == original.value

    def test_roundtrip_with_basis_points(self):
        """Roundtrip should preserve basis points precision."""
        original = Percentage.from_basis_points(150)
        serialized = original.to_dict()
        deserialized = Percentage.from_dict(serialized)

        assert deserialized.value == original.value
        assert deserialized.value == Decimal("0.015")


class TestPercentageStringRepresentation:
    """Test string representations of percentages."""

    def test_str_10_percent(self):
        """str() should return '10%' for 0.10."""
        pct = Percentage(value=Decimal("0.10"))
        assert str(pct) == "10.00%"

    def test_str_0_5_percent(self):
        """str() should return '0.500%' for 0.005."""
        pct = Percentage(value=Decimal("0.005"))
        assert str(pct) == "0.500%"

    def test_str_negative_percent(self):
        """str() should show negative percentage."""
        pct = Percentage(value=Decimal("-0.15"))
        assert str(pct) == "-15.00%"

    def test_repr(self):
        """repr() should return developer-friendly representation."""
        pct = Percentage(value=Decimal("0.10"))
        result = repr(pct)

        assert "Percentage" in result
        assert "0.10" in result


class TestPercentageIntegration:
    """Integration tests combining multiple operations."""

    def test_apply_basis_points_to_money(self):
        """Should be able to create percentage from basis points and apply to Money."""
        pct = Percentage.from_basis_points(500)  # 5%
        money = Money(amount=Decimal("1000"), currency="USD")
        result = pct.apply_to(money)

        assert result.amount == Decimal("1050")

    def test_add_percentages_then_apply(self):
        """Should be able to add percentages and apply result to Money."""
        pct1 = Percentage(value=Decimal("0.10"))
        pct2 = Percentage(value=Decimal("0.05"))
        combined = pct1 + pct2

        money = Money(amount=Decimal("100"), currency="EUR")
        result = combined.apply_to(money)

        assert result.amount == Decimal("115")

    def test_percentage_roundtrip_then_apply(self):
        """Should be able to serialize, deserialize, and apply percentage."""
        original = Percentage.from_basis_points(250)  # 2.5%
        serialized = original.to_dict()
        restored = Percentage.from_dict(serialized)

        money = Money(amount=Decimal("400"), currency="GBP")
        result = restored.apply_to(money)

        assert result.amount == Decimal("410")
