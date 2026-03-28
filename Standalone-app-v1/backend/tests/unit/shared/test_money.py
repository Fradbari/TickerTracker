from decimal import Decimal

import pytest

from src.shared.domain.value_objects.money import Money


class TestMoney:
    def test_money_creation_valid(self):
        m1 = Money(amount=Decimal("100.50"), currency="USD")
        assert m1.amount == Decimal("100.50")
        assert m1.currency == "USD"

        m2 = Money(amount=100)
        assert m2.amount == Decimal("100")

        m3 = Money(amount=100.50)
        assert m3.amount == Decimal("100.5")  # Float conversion logic

        m4 = Money(amount="100.50")
        assert m4.amount == Decimal("100.50")

    def test_money_creation_invalid_currency(self):
        with pytest.raises(ValueError, match="Currency must be a 3-character uppercase string"):
            Money(amount=10, currency="us")
        with pytest.raises(ValueError, match="Currency must be a 3-character uppercase string"):
            Money(amount=10, currency="USDD")
        with pytest.raises(ValueError, match="Currency must be a 3-character uppercase string"):
            Money(amount=10, currency="usd")
        with pytest.raises(ValueError, match="Currency must be a 3-character uppercase string"):
            Money(amount=10, currency=123)

    def test_money_creation_invalid_amount(self):
        with pytest.raises(TypeError, match="Cannot convert amount to Decimal"):
            Money(amount="invalid")
        with pytest.raises(TypeError, match="Cannot convert amount to Decimal"):
            Money(amount=[1, 2, 3])

    def test_money_addition(self):
        m1 = Money("10.50")
        m2 = Money("20.00")
        m3 = m1 + m2
        assert m3.amount == Decimal("30.50")
        assert m3.currency == "USD"

        with pytest.raises(ValueError, match="Cannot add amounts in different currencies"):
            m1 + Money("5", currency="EUR")

        with pytest.raises(TypeError, match="Cannot add Money and int"):
            m1 + 5

    def test_money_subtraction(self):
        m1 = Money("30.50")
        m2 = Money("20.00")
        m3 = m1 - m2
        assert m3.amount == Decimal("10.50")
        assert m3.currency == "USD"

        with pytest.raises(ValueError, match="Cannot subtract amounts in different currencies"):
            m1 - Money("5", currency="EUR")

        with pytest.raises(TypeError, match="Cannot subtract int from Money"):
            m1 - 5

    def test_money_multiplication(self):
        m1 = Money("10.50")
        m2 = m1 * 2
        assert m2.amount == Decimal("21.00")

        m3 = 2 * m1
        assert m3.amount == Decimal("21.00")

        m4 = m1 * Decimal("1.5")
        assert m4.amount == Decimal("15.75")

        with pytest.raises(TypeError, match="Can only multiply Money by Decimal or int"):
            m1 * "2"

    def test_money_negation(self):
        m1 = Money("10.50")
        m2 = -m1
        assert m2.amount == Decimal("-10.50")

    def test_money_rounding(self):
        m1 = Money("2.345")
        m2 = m1.round(2)
        assert m2.amount == Decimal("2.35")  # ROUND_HALF_UP behavior

        m3 = Money("2.344")
        m4 = m3.round(2)
        assert m4.amount == Decimal("2.34")

    def test_serialization_deserialization(self):
        m1 = Money("100.50", "EUR")
        data = m1.to_dict()
        assert data == {"amount": "100.50", "currency": "EUR"}

        m2 = Money.from_dict(data)
        assert m2.amount == Decimal("100.50")
        assert m2.currency == "EUR"

        # Test Default USD fallback if missing
        m3 = Money.from_dict({"amount": "50.0"})
        assert m3.amount == Decimal("50.0")
        assert m3.currency == "USD"

        with pytest.raises(KeyError, match="Dictionary must contain 'amount' key"):
            Money.from_dict({"currency": "EUR"})

    def test_string_representation(self):
        m1 = Money("10.50", "USD")
        assert str(m1) == "10.50 USD"
        assert repr(m1) == "Money(amount=Decimal('10.50'), currency='USD')"
