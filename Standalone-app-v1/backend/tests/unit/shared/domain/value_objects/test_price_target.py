"""Unit tests for PriceTarget value object."""

from decimal import Decimal

import pytest

from src.shared.domain.value_objects import Money, PriceTarget


class TestPriceTargetConstructionLONG:
    """Test PriceTarget construction with LONG direction."""

    def test_create_valid_long_price_target(self):
        """Should create valid LONG PriceTarget with stop_loss < entry < take_profit."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        assert target.entry_price.amount == Decimal("100")
        assert target.stop_loss.amount == Decimal("90")
        assert target.take_profit.amount == Decimal("120")
        assert target.direction == "LONG"

    def test_long_invalid_stop_loss_above_entry(self):
        """LONG should reject stop_loss >= entry_price."""
        with pytest.raises(ValueError, match="stop_loss.*<.*entry_price"):
            PriceTarget(
                entry_price=Money(Decimal("100"), "USD"),
                stop_loss=Money(Decimal("100"), "USD"),  # Invalid: equal to entry
                take_profit=Money(Decimal("120"), "USD"),
                direction="LONG",
            )

    def test_long_invalid_take_profit_below_entry(self):
        """LONG should reject take_profit <= entry_price."""
        with pytest.raises(ValueError, match="entry_price.*<.*take_profit"):
            PriceTarget(
                entry_price=Money(Decimal("100"), "USD"),
                stop_loss=Money(Decimal("90"), "USD"),
                take_profit=Money(Decimal("100"), "USD"),  # Invalid: equal to entry
                direction="LONG",
            )

    def test_long_invalid_stop_loss_above_take_profit(self):
        """LONG should reject inverted prices."""
        with pytest.raises(ValueError):
            PriceTarget(
                entry_price=Money(Decimal("100"), "USD"),
                stop_loss=Money(Decimal("110"), "USD"),  # Invalid: above entry
                take_profit=Money(Decimal("120"), "USD"),
                direction="LONG",
            )


class TestPriceTargetConstructionSHORT:
    """Test PriceTarget construction with SHORT direction."""

    def test_create_valid_short_price_target(self):
        """Should create valid SHORT PriceTarget with take_profit < entry < stop_loss."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        assert target.entry_price.amount == Decimal("100")
        assert target.stop_loss.amount == Decimal("110")
        assert target.take_profit.amount == Decimal("80")
        assert target.direction == "SHORT"

    def test_short_invalid_take_profit_above_entry(self):
        """SHORT should reject take_profit >= entry_price."""
        with pytest.raises(ValueError, match="take_profit.*<.*entry_price"):
            PriceTarget(
                entry_price=Money(Decimal("100"), "USD"),
                stop_loss=Money(Decimal("110"), "USD"),
                take_profit=Money(Decimal("100"), "USD"),  # Invalid: equal to entry
                direction="SHORT",
            )

    def test_short_invalid_stop_loss_below_entry(self):
        """SHORT should reject stop_loss <= entry_price."""
        with pytest.raises(ValueError, match="entry_price.*<.*stop_loss"):
            PriceTarget(
                entry_price=Money(Decimal("100"), "USD"),
                stop_loss=Money(Decimal("100"), "USD"),  # Invalid: equal to entry
                take_profit=Money(Decimal("80"), "USD"),
                direction="SHORT",
            )

    def test_short_invalid_stop_loss_below_take_profit(self):
        """SHORT should reject inverted prices."""
        with pytest.raises(ValueError):
            PriceTarget(
                entry_price=Money(Decimal("100"), "USD"),
                stop_loss=Money(Decimal("90"), "USD"),  # Invalid: below entry
                take_profit=Money(Decimal("80"), "USD"),
                direction="SHORT",
            )


class TestPriceTargetValidation:
    """Test validation logic."""

    def test_currency_mismatch_raises_error(self):
        """Should reject prices with different currencies."""
        with pytest.raises(ValueError, match="same currency"):
            PriceTarget(
                entry_price=Money(Decimal("100"), "USD"),
                stop_loss=Money(Decimal("90"), "EUR"),  # Different currency
                take_profit=Money(Decimal("120"), "USD"),
                direction="LONG",
            )

    def test_invalid_direction_raises_error(self):
        """Should reject invalid direction."""
        with pytest.raises(ValueError, match="Direction must be"):
            PriceTarget(
                entry_price=Money(Decimal("100"), "USD"),
                stop_loss=Money(Decimal("90"), "USD"),
                take_profit=Money(Decimal("120"), "USD"),
                direction="INVALID",
            )

    def test_non_money_prices_raise_error(self):
        """Should reject non-Money prices."""
        with pytest.raises(ValueError, match="Money instances"):
            PriceTarget(
                entry_price=100,  # Not Money
                stop_loss=Money(Decimal("90"), "USD"),
                take_profit=Money(Decimal("120"), "USD"),
                direction="LONG",
            )


class TestRiskRewardRatio:
    """Test risk/reward ratio calculation."""

    def test_long_risk_reward_ratio(self):
        """LONG risk/reward should be (TP - Entry) / (Entry - SL)."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        # Reward = 120 - 100 = 20
        # Risk = 100 - 90 = 10
        # Ratio = 20 / 10 = 2
        assert target.risk_reward_ratio() == Decimal("2")

    def test_short_risk_reward_ratio(self):
        """SHORT risk/reward should be (Entry - TP) / (SL - Entry)."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        # Reward = 100 - 80 = 20
        # Risk = 110 - 100 = 10
        # Ratio = 20 / 10 = 2
        assert target.risk_reward_ratio() == Decimal("2")

    def test_1_to_1_risk_reward_ratio(self):
        """Risk/reward ratio of 1:1."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("95"), "USD"),
            take_profit=Money(Decimal("105"), "USD"),
            direction="LONG",
        )

        # Reward = 105 - 100 = 5
        # Risk = 100 - 95 = 5
        # Ratio = 5 / 5 = 1
        assert target.risk_reward_ratio() == Decimal("1")

    def test_3_to_1_risk_reward_ratio(self):
        """Risk/reward ratio of 3:1."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("99"), "USD"),
            take_profit=Money(Decimal("103"), "USD"),
            direction="LONG",
        )

        # Reward = 103 - 100 = 3
        # Risk = 100 - 99 = 1
        # Ratio = 3 / 1 = 3
        assert target.risk_reward_ratio() == Decimal("3")


class TestIsTargetHit:
    """Test target hit detection."""

    def test_long_target_not_hit_below(self):
        """LONG target not hit when current < take_profit."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        assert not target.is_target_hit(Money(Decimal("110"), "USD"))

    def test_long_target_hit_at_target(self):
        """LONG target hit when current == take_profit."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        assert target.is_target_hit(Money(Decimal("120"), "USD"))

    def test_long_target_hit_above_target(self):
        """LONG target hit when current > take_profit."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        assert target.is_target_hit(Money(Decimal("130"), "USD"))

    def test_short_target_not_hit_above(self):
        """SHORT target not hit when current > take_profit."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        assert not target.is_target_hit(Money(Decimal("90"), "USD"))

    def test_short_target_hit_at_target(self):
        """SHORT target hit when current == take_profit."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        assert target.is_target_hit(Money(Decimal("80"), "USD"))

    def test_short_target_hit_below_target(self):
        """SHORT target hit when current < take_profit."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        assert target.is_target_hit(Money(Decimal("70"), "USD"))

    def test_target_hit_currency_mismatch_raises_error(self):
        """Target hit check should reject different currency."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        with pytest.raises(ValueError, match="currency"):
            target.is_target_hit(Money(Decimal("110"), "EUR"))

    def test_target_hit_non_money_raises_error(self):
        """Target hit check should reject non-Money."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        with pytest.raises(ValueError, match="Money"):
            target.is_target_hit(110)


class TestIsStopHit:
    """Test stop loss hit detection."""

    def test_long_stop_not_hit_above(self):
        """LONG stop not hit when current > stop_loss."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        assert not target.is_stop_hit(Money(Decimal("95"), "USD"))

    def test_long_stop_hit_at_stop(self):
        """LONG stop hit when current == stop_loss."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        assert target.is_stop_hit(Money(Decimal("90"), "USD"))

    def test_long_stop_hit_below_stop(self):
        """LONG stop hit when current < stop_loss."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        assert target.is_stop_hit(Money(Decimal("80"), "USD"))

    def test_short_stop_not_hit_below(self):
        """SHORT stop not hit when current < stop_loss."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        assert not target.is_stop_hit(Money(Decimal("105"), "USD"))

    def test_short_stop_hit_at_stop(self):
        """SHORT stop hit when current == stop_loss."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        assert target.is_stop_hit(Money(Decimal("110"), "USD"))

    def test_short_stop_hit_above_stop(self):
        """SHORT stop hit when current > stop_loss."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        assert target.is_stop_hit(Money(Decimal("120"), "USD"))

    def test_stop_hit_currency_mismatch_raises_error(self):
        """Stop hit check should reject different currency."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        with pytest.raises(ValueError, match="currency"):
            target.is_stop_hit(Money(Decimal("85"), "EUR"))

    def test_stop_hit_non_money_raises_error(self):
        """Stop hit check should reject non-Money."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        with pytest.raises(ValueError, match="Money"):
            target.is_stop_hit(85)


class TestPriceTargetSerialization:
    """Test serialization and deserialization."""

    def test_to_dict_long(self):
        """to_dict should serialize LONG PriceTarget correctly."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        data = target.to_dict()

        assert data["entry_price"] == {"amount": "100", "currency": "USD"}
        assert data["stop_loss"] == {"amount": "90", "currency": "USD"}
        assert data["take_profit"] == {"amount": "120", "currency": "USD"}
        assert data["direction"] == "LONG"

    def test_to_dict_short(self):
        """to_dict should serialize SHORT PriceTarget correctly."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        data = target.to_dict()

        assert data["direction"] == "SHORT"

    def test_from_dict_long(self):
        """from_dict should deserialize LONG PriceTarget correctly."""
        data = {
            "entry_price": {"amount": "100", "currency": "USD"},
            "stop_loss": {"amount": "90", "currency": "USD"},
            "take_profit": {"amount": "120", "currency": "USD"},
            "direction": "LONG",
        }

        target = PriceTarget.from_dict(data)

        assert target.entry_price.amount == Decimal("100")
        assert target.stop_loss.amount == Decimal("90")
        assert target.take_profit.amount == Decimal("120")
        assert target.direction == "LONG"

    def test_from_dict_missing_key_raises_error(self):
        """from_dict should raise KeyError if required key is missing."""
        data = {
            "entry_price": {"amount": "100", "currency": "USD"},
            "stop_loss": {"amount": "90", "currency": "USD"},
            # Missing take_profit and direction
        }

        with pytest.raises(KeyError):
            PriceTarget.from_dict(data)

    def test_roundtrip_serialization_long(self):
        """Serialize and deserialize LONG PriceTarget should yield equal object."""
        original = PriceTarget(
            entry_price=Money(Decimal("100.50"), "EUR"),
            stop_loss=Money(Decimal("95.75"), "EUR"),
            take_profit=Money(Decimal("115.25"), "EUR"),
            direction="LONG",
        )

        serialized = original.to_dict()
        restored = PriceTarget.from_dict(serialized)

        assert restored.entry_price.amount == original.entry_price.amount
        assert restored.stop_loss.amount == original.stop_loss.amount
        assert restored.take_profit.amount == original.take_profit.amount
        assert restored.direction == original.direction

    def test_roundtrip_serialization_short(self):
        """Serialize and deserialize SHORT PriceTarget should yield equal object."""
        original = PriceTarget(
            entry_price=Money(Decimal("1000"), "GBP"),
            stop_loss=Money(Decimal("1050"), "GBP"),
            take_profit=Money(Decimal("950"), "GBP"),
            direction="SHORT",
        )

        serialized = original.to_dict()
        restored = PriceTarget.from_dict(serialized)

        assert restored.entry_price.amount == original.entry_price.amount
        assert restored.direction == "SHORT"


class TestPriceTargetStringRepresentation:
    """Test string representations."""

    def test_str_long(self):
        """str() should show LONG prices in correct order."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("90"), "USD"),
            take_profit=Money(Decimal("120"), "USD"),
            direction="LONG",
        )

        result = str(target)
        assert "LONG" in result
        assert "90" in result
        assert "100" in result
        assert "120" in result

    def test_str_short(self):
        """str() should show SHORT prices in correct order."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("110"), "USD"),
            take_profit=Money(Decimal("80"), "USD"),
            direction="SHORT",
        )

        result = str(target)
        assert "SHORT" in result
        assert "80" in result
        assert "100" in result
        assert "110" in result


class TestPriceTargetIntegration:
    """Integration tests combining multiple operations."""

    def test_long_trade_scenario(self):
        """Test complete LONG trade scenario."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("95"), "USD"),
            take_profit=Money(Decimal("110"), "USD"),
            direction="LONG",
        )

        # Risk/reward: (110-100)/(100-95) = 10/5 = 2
        assert target.risk_reward_ratio() == Decimal("2")

        # Price rises to 105 - no stop hit, no target hit
        assert not target.is_stop_hit(Money(Decimal("105"), "USD"))
        assert not target.is_target_hit(Money(Decimal("105"), "USD"))

        # Price reaches take profit
        assert target.is_target_hit(Money(Decimal("110"), "USD"))

        # Serialize and deserialize
        data = target.to_dict()
        restored = PriceTarget.from_dict(data)
        assert restored.risk_reward_ratio() == Decimal("2")

    def test_short_trade_scenario(self):
        """Test complete SHORT trade scenario."""
        target = PriceTarget(
            entry_price=Money(Decimal("100"), "USD"),
            stop_loss=Money(Decimal("105"), "USD"),
            take_profit=Money(Decimal("90"), "USD"),
            direction="SHORT",
        )

        # Risk/reward: (100-90)/(105-100) = 10/5 = 2
        assert target.risk_reward_ratio() == Decimal("2")

        # Price drops to 95 - no stop hit, no target hit
        assert not target.is_stop_hit(Money(Decimal("95"), "USD"))
        assert not target.is_target_hit(Money(Decimal("95"), "USD"))

        # Price reaches take profit
        assert target.is_target_hit(Money(Decimal("90"), "USD"))

        # Price hits stop loss
        assert target.is_stop_hit(Money(Decimal("105"), "USD"))
