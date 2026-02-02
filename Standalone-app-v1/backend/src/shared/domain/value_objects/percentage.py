from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .money import Money


@dataclass(frozen=True)
class Percentage:
    """
    Immutable value object for handling percentage values with decimal precision.

    This class represents percentages as Decimal values. For example:
    - 10% is stored as Decimal("0.10")
    - 0.5% is stored as Decimal("0.005")
    - 100% is stored as Decimal("1.00")

    Attributes:
        value (Decimal): The percentage value as a fraction (e.g., 0.10 for 10%).

    Raises:
        TypeError: If value cannot be converted to Decimal.
    """

    value: Decimal

    def __post_init__(self) -> None:
        """
        Convert value to Decimal if needed.

        Raises:
            TypeError: If value cannot be converted to Decimal.
        """
        if not isinstance(self.value, Decimal):
            try:
                from decimal import DecimalException

                object.__setattr__(self, "value", Decimal(str(self.value)))
            except (ValueError, TypeError, DecimalException) as e:
                raise TypeError(f"Cannot convert percentage value to Decimal: {e}") from e

    @classmethod
    def from_basis_points(cls, bps: int) -> "Percentage":
        """
        Create a Percentage from basis points.

        Basis points (bps) are a unit equal to 1/100th of a percent.
        For example:
        - 100 bps = 1% = 0.01
        - 50 bps = 0.5% = 0.005
        - 1 bps = 0.01% = 0.0001

        Args:
            bps: Basis points value (integer).

        Returns:
            Percentage: A new Percentage instance.

        Raises:
            TypeError: If bps is not an integer.
        """
        if not isinstance(bps, int):
            raise TypeError(f"Basis points must be an integer, got {type(bps).__name__}")

        # 100 bps = 1% = 0.01
        # So value = bps / 10000
        value = Decimal(bps) / Decimal(10000)
        return cls(value=value)

    def apply_to(self, money: "Money") -> "Money":
        """
        Apply this percentage to a Money amount.

        Returns a new Money with the amount increased by this percentage.
        For example: 10% applied to 100 USD returns 110 USD.

        Args:
            money: Money instance to apply percentage to.

        Returns:
            Money: A new Money instance with the adjusted amount.

        Raises:
            TypeError: If money is not a Money instance.
        """
        from .money import Money

        if not isinstance(money, Money):
            raise TypeError(f"Can only apply Percentage to Money, got {type(money).__name__}")

        adjusted_amount = money.amount * (Decimal(1) + self.value)
        return Money(amount=adjusted_amount, currency=money.currency)

    def as_multiplier(self) -> Decimal:
        """
        Convert percentage to a multiplier for direct use in calculations.

        Returns 1 + value, which can be used to multiply amounts directly.
        For example: 10% returns 1.10, so amount * multiplier gives amount + 10%.

        Returns:
            Decimal: The multiplier (1 + percentage value).
        """
        return Decimal(1) + self.value

    def __add__(self, other: "Percentage") -> "Percentage":
        """
        Add two Percentage objects.

        Args:
            other: Another Percentage instance to add.

        Returns:
            Percentage: A new Percentage with the sum.

        Raises:
            TypeError: If other is not a Percentage instance.
        """
        if not isinstance(other, Percentage):
            raise TypeError(f"Cannot add Percentage and {type(other).__name__}")

        return Percentage(value=self.value + other.value)

    def __sub__(self, other: "Percentage") -> "Percentage":
        """
        Subtract two Percentage objects.

        Args:
            other: Another Percentage instance to subtract.

        Returns:
            Percentage: A new Percentage with the difference.

        Raises:
            TypeError: If other is not a Percentage instance.
        """
        if not isinstance(other, Percentage):
            raise TypeError(f"Cannot subtract {type(other).__name__} from Percentage")

        return Percentage(value=self.value - other.value)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize Percentage to a dictionary.

        Returns:
            Dict with "value" (as string) key.
        """
        return {"value": str(self.value)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Percentage":
        """
        Deserialize Percentage from a dictionary.

        Args:
            data: Dictionary with "value" key.

        Returns:
            Percentage: A new Percentage instance.

        Raises:
            KeyError: If "value" key is missing.
            TypeError: If value cannot be converted to Decimal.
        """
        if "value" not in data:
            raise KeyError("Dictionary must contain 'value' key")

        value = Decimal(str(data["value"]))
        return cls(value=value)

    def __str__(self) -> str:
        """String representation as percentage (e.g., '10.50%')"""
        percentage = self.value * Decimal(100)
        return f"{percentage}%"

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"Percentage(value={self.value!r})"
