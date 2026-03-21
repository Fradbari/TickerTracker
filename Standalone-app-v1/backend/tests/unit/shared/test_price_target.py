import pytest
from decimal import Decimal
from src.shared.domain.value_objects.money import Money
from src.shared.domain.value_objects.price_target import PriceTarget

class TestPriceTarget:
    @pytest.fixture
    def money_100(self):
        return Money("100.00", "USD")
        
    @pytest.fixture
    def money_90(self):
        return Money("90.00", "USD")
        
    @pytest.fixture
    def money_120(self):
        return Money("120.00", "USD")
        
    @pytest.fixture
    def money_110(self):
        return Money("110.00", "USD")
        
    @pytest.fixture
    def money_80(self):
        return Money("80.00", "USD")

    def test_valid_long_creation(self, money_100, money_90, money_120):
        pt = PriceTarget(
            entry_price=money_100,
            stop_loss=money_90,
            take_profit=money_120,
            direction="LONG"
        )
        assert pt.direction == "LONG"
        assert pt.entry_price == money_100
        
    def test_valid_short_creation(self, money_100, money_110, money_80):
        pt = PriceTarget(
            entry_price=money_100,
            stop_loss=money_110,
            take_profit=money_80,
            direction="SHORT"
        )
        assert pt.direction == "SHORT"
        assert pt.entry_price == money_100

    def test_invalid_types_and_currencies(self, money_100, money_90, money_120):
        with pytest.raises(ValueError, match="All prices must be Money instances"):
            PriceTarget(
                entry_price="100.00", # type: ignore
                stop_loss=money_90,
                take_profit=money_120,
                direction="LONG"
            )
            
        money_eur = Money("100.00", "EUR")
        with pytest.raises(ValueError, match="All prices must have the same currency"):
            PriceTarget(
                entry_price=money_eur,
                stop_loss=money_90,
                take_profit=money_120,
                direction="LONG"
            )
            
        with pytest.raises(ValueError, match="Direction must be 'LONG' or 'SHORT'"):
            PriceTarget(
                entry_price=money_100,
                stop_loss=money_90,
                take_profit=money_120,
                direction="INVALID" # type: ignore
            )

    def test_invalid_long_boundaries(self, money_100, money_90, money_120):
        # entry <= stop_loss
        with pytest.raises(ValueError, match="For LONG: stop_loss"):
            PriceTarget(entry_price=money_90, stop_loss=money_100, take_profit=money_120, direction="LONG")
            
        # take_profit <= entry
        with pytest.raises(ValueError, match="For LONG: stop_loss"):
            PriceTarget(entry_price=money_120, stop_loss=money_90, take_profit=money_100, direction="LONG")

    def test_invalid_short_boundaries(self, money_100, money_110, money_80):
        # stop_loss <= entry
        with pytest.raises(ValueError, match="For SHORT: take_profit"):
            PriceTarget(entry_price=money_110, stop_loss=money_100, take_profit=money_80, direction="SHORT")
            
        # entry <= take_profit
        with pytest.raises(ValueError, match="For SHORT: take_profit"):
            PriceTarget(entry_price=money_80, stop_loss=money_110, take_profit=money_100, direction="SHORT")

    def test_risk_reward_ratio(self, money_100, money_90, money_120, money_110, money_80):
        # LONG: risk = 10, reward = 20 -> RR = 2.0
        pt_long = PriceTarget(
            entry_price=money_100,
            stop_loss=money_90,
            take_profit=money_120,
            direction="LONG"
        )
        assert pt_long.risk_reward_ratio() == Decimal("2.0")
        
        # SHORT: risk = 10, reward = 20 -> RR = 2.0
        pt_short = PriceTarget(
            entry_price=money_100,
            stop_loss=money_110,
            take_profit=money_80,
            direction="SHORT"
        )
        assert pt_short.risk_reward_ratio() == Decimal("2.0")
        
    def test_risk_reward_ratio_zero_risk_fallback(self):
        # We need to bypass post_init to force a division by zero error theoretically
        pt = PriceTarget.__new__(PriceTarget)
        object.__setattr__(pt, "entry_price", Money("100.00", "USD"))
        object.__setattr__(pt, "stop_loss", Money("100.00", "USD"))
        object.__setattr__(pt, "take_profit", Money("120.00", "USD"))
        object.__setattr__(pt, "direction", "LONG")
        with pytest.raises(ValueError, match="Risk must be positive"):
            pt.risk_reward_ratio()

    def test_is_target_hit(self, money_100, money_90, money_120, money_110, money_80):
        pt_long = PriceTarget(entry_price=money_100, stop_loss=money_90, take_profit=money_120, direction="LONG")
        assert not pt_long.is_target_hit(Money("119.00", "USD"))
        assert pt_long.is_target_hit(Money("120.00", "USD"))
        assert pt_long.is_target_hit(Money("121.00", "USD"))
        
        pt_short = PriceTarget(entry_price=money_100, stop_loss=money_110, take_profit=money_80, direction="SHORT")
        assert not pt_short.is_target_hit(Money("81.00", "USD"))
        assert pt_short.is_target_hit(Money("80.00", "USD"))
        assert pt_short.is_target_hit(Money("79.00", "USD"))

        # Invalid type and currency
        with pytest.raises(ValueError, match="current_price must be Money"):
            pt_long.is_target_hit(120) # type: ignore
        with pytest.raises(ValueError, match="current_price currency"):
            pt_long.is_target_hit(Money("120.00", "EUR"))

    def test_is_stop_hit(self, money_100, money_90, money_120, money_110, money_80):
        pt_long = PriceTarget(entry_price=money_100, stop_loss=money_90, take_profit=money_120, direction="LONG")
        assert not pt_long.is_stop_hit(Money("91.00", "USD"))
        assert pt_long.is_stop_hit(Money("90.00", "USD"))
        assert pt_long.is_stop_hit(Money("89.00", "USD"))
        
        pt_short = PriceTarget(entry_price=money_100, stop_loss=money_110, take_profit=money_80, direction="SHORT")
        assert not pt_short.is_stop_hit(Money("109.00", "USD"))
        assert pt_short.is_stop_hit(Money("110.00", "USD"))
        assert pt_short.is_stop_hit(Money("111.00", "USD"))

        # Invalid type and currency
        with pytest.raises(ValueError, match="current_price must be Money"):
            pt_long.is_stop_hit(90) # type: ignore
        with pytest.raises(ValueError, match="current_price currency"):
            pt_long.is_stop_hit(Money("90.00", "EUR"))

    def test_serialization(self, money_100, money_90, money_120):
        pt = PriceTarget(entry_price=money_100, stop_loss=money_90, take_profit=money_120, direction="LONG")
        data = pt.to_dict()
        assert data == {
            "entry_price": {"amount": "100.00", "currency": "USD"},
            "stop_loss": {"amount": "90.00", "currency": "USD"},
            "take_profit": {"amount": "120.00", "currency": "USD"},
            "direction": "LONG",
        }
        
        pt_restored = PriceTarget.from_dict(data)
        assert pt_restored.entry_price == pt.entry_price
        assert pt_restored.take_profit == pt.take_profit
        assert pt_restored.direction == pt.direction
        
        # Missing keys
        with pytest.raises(KeyError, match="Missing required keys"):
            PriceTarget.from_dict({"direction": "LONG"})

    def test_string_representation(self, money_100, money_90, money_120):
        pt = PriceTarget(entry_price=money_100, stop_loss=money_90, take_profit=money_120, direction="LONG")
        assert str(pt) == "PriceTarget(LONG | SL:90.00 < Entry:100.00 < TP:120.00)"
        assert "PriceTarget" in repr(pt)
        assert "LONG" in repr(pt)
