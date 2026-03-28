from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any


@dataclass(frozen=True)
class Money:
    """
    Immutable value object for handling monetary amounts with decimal precision.

    This class ensures type-safe arithmetic operations on money values without
    losing precision due to float rounding errors. All calculations use Decimal.

    Attributes:
        amount (Decimal): The monetary amount.
        currency (str): ISO 4217 currency code (3 uppercase letters). Defaults to "USD".

    Raises:
        ValueError: If currency is not a 3-character uppercase string.
        TypeError: If amount cannot be converted to Decimal.
    """

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        """
        Validate and convert fields after initialization.

        - Converts amount to Decimal if needed
        - Validates currency format (3 uppercase letters)

        Raises:
            ValueError: If currency validation fails
            TypeError: If amount cannot be converted to Decimal
        """
        # Convert amount to Decimal if it's not already
        if not isinstance(self.amount, Decimal):
            try:
                from decimal import DecimalException

                object.__setattr__(self, "amount", Decimal(str(self.amount)))
            except (ValueError, TypeError, DecimalException) as e:
                raise TypeError(f"Cannot convert amount to Decimal: {e}") from e

        # Validate currency
        if (
            not isinstance(self.currency, str)
            or len(self.currency) != 3
            or not self.currency.isupper()
        ):
            raise ValueError(
                f"Currency must be a 3-character uppercase string, got: {self.currency}"
            )

    def __add__(self, other: "Money") -> "Money":
        """
        Add two Money objects.

        Args:
            other: Another Money instance to add.

        Returns:
            Money: A new Money instance with the sum.

        Raises:
            ValueError: If currencies don't match.
            TypeError: If other is not a Money instance.
        """
        if not isinstance(other, Money):
            raise TypeError(f"Cannot add Money and {type(other).__name__}")

        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add amounts in different currencies: {self.currency} + {other.currency}"
            )

        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """
        Subtract two Money objects.

        Args:
            other: Another Money instance to subtract.

        Returns:
            Money: A new Money instance with the difference.

        Raises:
            ValueError: If currencies don't match.
            TypeError: If other is not a Money instance.
        """
        if not isinstance(other, Money):
            raise TypeError(f"Cannot subtract {type(other).__name__} from Money")

        if self.currency != other.currency:
            raise ValueError(
                f"Cannot subtract amounts in different currencies: {self.currency} - {other.currency}"
            )

        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __mul__(self, factor: Decimal | int) -> "Money":
        """
        Multiply a Money amount by a scalar.

        Args:
            factor: A Decimal or int multiplier.

        Returns:
            Money: A new Money instance with the product.

        Raises:
            TypeError: If factor is not Decimal or int.
        """
        if not isinstance(factor, Decimal | int):
            raise TypeError(
                f"Can only multiply Money by Decimal or int, got {type(factor).__name__}"
            )

        factor_decimal = Decimal(factor) if isinstance(factor, int) else factor
        return Money(amount=self.amount * factor_decimal, currency=self.currency)

    def __rmul__(self, factor: Decimal | int) -> "Money":
        """Support multiplication from the left side (e.g., 2 * money_obj)."""
        return self.__mul__(factor)

    def __neg__(self) -> "Money":
        """
        Negate a Money amount.

        Returns:
            Money: A new Money instance with negated amount.
        """
        return Money(amount=-self.amount, currency=self.currency)

    def round(self, places: int) -> "Money":
        """
        Round the amount to a specified number of decimal places.

        Uses ROUND_HALF_UP strategy for consistent rounding behavior.

        Args:
            places: Number of decimal places to round to.

        Returns:
            Money: A new Money instance with rounded amount.
        """
        quantize_exp = Decimal(10) ** -places
        rounded_amount = self.amount.quantize(quantize_exp, rounding=ROUND_HALF_UP)
        return Money(amount=rounded_amount, currency=self.currency)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize Money to a dictionary.

        Returns:
            Dict with "amount" (as string) and "currency" keys.
        """
        return {"amount": str(self.amount), "currency": self.currency}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Money":
        """
        Deserialize Money from a dictionary.

        Args:
            data: Dictionary with "amount" and optionally "currency" keys.

        Returns:
            Money: A new Money instance.

        Raises:
            KeyError: If "amount" key is missing.
            ValueError: If currency is invalid.
            TypeError: If amount cannot be converted to Decimal.
        """
        if "amount" not in data:
            raise KeyError("Dictionary must contain 'amount' key")

        amount = Decimal(str(data["amount"]))
        currency = data.get("currency", "USD")

        return cls(amount=amount, currency=currency)

    def __str__(self) -> str:
        """String representation in format: {amount} {currency}"""
        return f"{self.amount} {self.currency}"

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"Money(amount={self.amount!r}, currency={self.currency!r})"
