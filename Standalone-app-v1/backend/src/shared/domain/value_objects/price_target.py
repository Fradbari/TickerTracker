from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from .money import Money


@dataclass(frozen=True)
class PriceTarget:
    """
    Immutable value object for managing price targets with stop loss and take profit.

    Encapsulates the relationship between entry price, stop loss, and take profit for
    a trade, with direction-aware validation and risk/reward calculations.

    For LONG positions:
    - stop_loss < entry_price < take_profit

    For SHORT positions:
    - take_profit < entry_price < stop_loss

    All prices must have the same currency.

    Attributes:
        entry_price (Money): The entry price for the trade.
        stop_loss (Money): The stop loss price.
        take_profit (Money): The take profit price.
        direction (Literal["LONG", "SHORT"]): Trade direction.

    Raises:
        ValueError: If prices don't follow direction rules or currencies don't match.
    """

    entry_price: "Money"
    stop_loss: "Money"
    take_profit: "Money"
    direction: Literal["LONG", "SHORT"]

    def __post_init__(self) -> None:
        """
        Validate price relationships and currency consistency.

        For LONG: stop_loss < entry_price < take_profit
        For SHORT: take_profit < entry_price < stop_loss
        All prices must have the same currency.

        Raises:
            ValueError: If validation fails.
        """
        from .money import Money

        # Verify all are Money instances
        if not all(
            isinstance(p, Money) for p in [self.entry_price, self.stop_loss, self.take_profit]
        ):
            raise ValueError("All prices must be Money instances")

        # Verify all currencies match
        currencies = {self.entry_price.currency, self.stop_loss.currency, self.take_profit.currency}
        if len(currencies) > 1:
            raise ValueError(f"All prices must have the same currency, got: {currencies}")

        # Validate direction
        if self.direction not in ("LONG", "SHORT"):
            raise ValueError(f"Direction must be 'LONG' or 'SHORT', got: {self.direction}")

        # Direction-specific validation
        if self.direction == "LONG":
            # For LONG: stop_loss < entry_price < take_profit
            if not (self.stop_loss.amount < self.entry_price.amount < self.take_profit.amount):
                raise ValueError(
                    f"For LONG: stop_loss ({self.stop_loss.amount}) < "
                    f"entry_price ({self.entry_price.amount}) < "
                    f"take_profit ({self.take_profit.amount})"
                )
        else:  # SHORT
            # For SHORT: take_profit < entry_price < stop_loss
            if not (self.take_profit.amount < self.entry_price.amount < self.stop_loss.amount):
                raise ValueError(
                    f"For SHORT: take_profit ({self.take_profit.amount}) < "
                    f"entry_price ({self.entry_price.amount}) < "
                    f"stop_loss ({self.stop_loss.amount})"
                )

    def risk_reward_ratio(self) -> Decimal:
        """
        Calculate the risk/reward ratio for the trade.

        Risk = distance from entry to stop loss
        Reward = distance from entry to take profit

        Ratio = Reward / Risk (always positive)

        Returns:
            Decimal: The risk/reward ratio.

        Raises:
            ValueError: If risk is zero (shouldn't happen with valid data).
        """
        if self.direction == "LONG":
            risk = self.entry_price.amount - self.stop_loss.amount
            reward = self.take_profit.amount - self.entry_price.amount
        else:  # SHORT
            risk = self.stop_loss.amount - self.entry_price.amount
            reward = self.entry_price.amount - self.take_profit.amount

        if risk <= 0:
            raise ValueError(f"Risk must be positive, got: {risk}")

        return reward / risk

    def is_target_hit(self, current_price: "Money") -> bool:
        """
        Check if the take profit target has been hit.

        Args:
            current_price: Current market price.

        Returns:
            bool: True if take profit has been reached, False otherwise.

        Raises:
            ValueError: If current_price has different currency or is not Money.
        """
        from .money import Money

        if not isinstance(current_price, Money):
            raise ValueError(f"current_price must be Money, got {type(current_price)}")

        if current_price.currency != self.entry_price.currency:
            raise ValueError(
                f"current_price currency ({current_price.currency}) doesn't match "
                f"entry_price currency ({self.entry_price.currency})"
            )

        if self.direction == "LONG":
            # For LONG, target is hit when current >= take_profit
            return current_price.amount >= self.take_profit.amount
        else:  # SHORT
            # For SHORT, target is hit when current <= take_profit
            return current_price.amount <= self.take_profit.amount

    def is_stop_hit(self, current_price: "Money") -> bool:
        """
        Check if the stop loss has been triggered.

        Args:
            current_price: Current market price.

        Returns:
            bool: True if stop loss has been triggered, False otherwise.

        Raises:
            ValueError: If current_price has different currency or is not Money.
        """
        from .money import Money

        if not isinstance(current_price, Money):
            raise ValueError(f"current_price must be Money, got {type(current_price)}")

        if current_price.currency != self.entry_price.currency:
            raise ValueError(
                f"current_price currency ({current_price.currency}) doesn't match "
                f"entry_price currency ({self.entry_price.currency})"
            )

        if self.direction == "LONG":
            # For LONG, stop is hit when current <= stop_loss
            return current_price.amount <= self.stop_loss.amount
        else:  # SHORT
            # For SHORT, stop is hit when current >= stop_loss
            return current_price.amount >= self.stop_loss.amount

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize PriceTarget to a dictionary.

        Returns:
            Dict with entry_price, stop_loss, take_profit (as dicts) and direction.
        """
        return {
            "entry_price": self.entry_price.to_dict(),
            "stop_loss": self.stop_loss.to_dict(),
            "take_profit": self.take_profit.to_dict(),
            "direction": self.direction,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PriceTarget":
        """
        Deserialize PriceTarget from a dictionary.

        Args:
            data: Dictionary with entry_price, stop_loss, take_profit (as dicts) and direction.

        Returns:
            PriceTarget: A new PriceTarget instance.

        Raises:
            KeyError: If required keys are missing.
            ValueError: If prices are invalid or direction is invalid.
        """
        from .money import Money

        required_keys = {"entry_price", "stop_loss", "take_profit", "direction"}
        if not required_keys.issubset(data.keys()):
            raise KeyError(f"Missing required keys: {required_keys - set(data.keys())}")

        entry_price = Money.from_dict(data["entry_price"])
        stop_loss = Money.from_dict(data["stop_loss"])
        take_profit = Money.from_dict(data["take_profit"])
        direction = data["direction"]

        return cls(
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            direction=direction,
        )

    def __str__(self) -> str:
        """String representation showing direction and prices."""
        return (
            f"PriceTarget({self.direction} | "
            f"SL:{self.stop_loss.amount} < "
            f"Entry:{self.entry_price.amount} "
            f"{'<' if self.direction == 'LONG' else '>'} "
            f"TP:{self.take_profit.amount})"
        )

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"PriceTarget(entry_price={self.entry_price!r}, "
            f"stop_loss={self.stop_loss!r}, "
            f"take_profit={self.take_profit!r}, "
            f"direction={self.direction!r})"
        )
