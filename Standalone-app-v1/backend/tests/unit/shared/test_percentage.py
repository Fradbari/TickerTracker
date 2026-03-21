import pytest
from decimal import Decimal
from src.shared.domain.value_objects.money import Money
from src.shared.domain.value_objects.percentage import Percentage

class TestPercentage:
    def test_percentage_creation(self):
        p1 = Percentage(Decimal("0.10"))
        assert p1.value == Decimal("0.10")
        
        p2 = Percentage(0.10)
        assert p2.value == Decimal("0.1")
        
        p3 = Percentage("0.10")
        assert p3.value == Decimal("0.10")

    def test_percentage_invalid_creation(self):
        with pytest.raises(TypeError, match="Cannot convert percentage value to Decimal"):
            Percentage("invalid")
            
        with pytest.raises(TypeError, match="Cannot convert percentage value to Decimal"):
            Percentage([1, 2])

    def test_from_basis_points(self):
        p1 = Percentage.from_basis_points(100)
        assert p1.value == Decimal("0.01")
        
        p2 = Percentage.from_basis_points(50)
        assert p2.value == Decimal("0.005")
        
        with pytest.raises(TypeError, match="Basis points must be an integer, got str"):
            Percentage.from_basis_points("100")

    def test_apply_to_money(self):
        p1 = Percentage("0.10")
        m1 = Money("100.00", "USD")
        
        m2 = p1.apply_to(m1)
        assert m2.amount == Decimal("110.00")
        assert m2.currency == "USD"
        
        with pytest.raises(TypeError, match="Can only apply Percentage to Money"):
            p1.apply_to("not money")

    def test_as_multiplier(self):
        p1 = Percentage("0.10")
        assert p1.as_multiplier() == Decimal("1.10")
        
        p2 = Percentage("-0.05")
        assert p2.as_multiplier() == Decimal("0.95")

    def test_addition(self):
        p1 = Percentage("0.10")
        p2 = Percentage("0.05")
        p3 = p1 + p2
        assert p3.value == Decimal("0.15")
        
        with pytest.raises(TypeError, match="Cannot add Percentage and int"):
            p1 + 5

    def test_subtraction(self):
        p1 = Percentage("0.10")
        p2 = Percentage("0.05")
        p3 = p1 - p2
        assert p3.value == Decimal("0.05")
        
        with pytest.raises(TypeError, match="Cannot subtract int from Percentage"):
            p1 - 5

    def test_serialization(self):
        p1 = Percentage("0.15")
        data = p1.to_dict()
        assert data == {"value": "0.15"}
        
        p2 = Percentage.from_dict(data)
        assert p2.value == Decimal("0.15")
        
        with pytest.raises(KeyError, match="Dictionary must contain 'value' key"):
            Percentage.from_dict({})

    def test_string_representation(self):
        p1 = Percentage("0.105")
        assert str(p1) == "10.500%"
        assert repr(p1) == "Percentage(value=Decimal('0.105'))"
