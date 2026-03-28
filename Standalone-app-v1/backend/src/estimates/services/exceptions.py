"""
Business exceptions for Estimate operations.

These custom exceptions represent domain-specific error conditions.
"""

from typing import Any
from uuid import UUID


class EstimateServiceError(Exception):
    """Base exception for all estimate service errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class EstimateNotFoundError(EstimateServiceError):
    """Raised when an estimate cannot be found."""

    def __init__(self, estimate_id: UUID):
        super().__init__(
            f"Estimate not found: {estimate_id}",
            {"estimate_id": str(estimate_id)}
        )
        self.estimate_id = estimate_id


class TickerNotFoundError(EstimateServiceError):
    """Raised when a ticker cannot be found."""

    def __init__(self, ticker_id: UUID):
        super().__init__(
            f"Ticker not found: {ticker_id}",
            {"ticker_id": str(ticker_id)}
        )
        self.ticker_id = ticker_id


class MarketDataNotAvailableError(EstimateServiceError):
    """Raised when market data is not available for a ticker."""

    def __init__(self, ticker_id: UUID, reason: str = "No market data available"):
        super().__init__(
            f"Market data not available for ticker {ticker_id}: {reason}",
            {"ticker_id": str(ticker_id), "reason": reason}
        )
        self.ticker_id = ticker_id
        self.reason = reason


class EstimateAlreadyClosedError(EstimateServiceError):
    """Raised when attempting to modify a closed estimate."""

    def __init__(self, estimate_id: UUID, current_status: str):
        super().__init__(
            f"Cannot modify estimate {estimate_id}: already closed with status {current_status}",
            {"estimate_id": str(estimate_id), "current_status": current_status}
        )
        self.estimate_id = estimate_id
        self.current_status = current_status


class InvalidEstimateStateError(EstimateServiceError):
    """Raised when an estimate is in an invalid state for the requested operation."""

    def __init__(self, estimate_id: UUID, operation: str, reason: str):
        super().__init__(
            f"Cannot perform '{operation}' on estimate {estimate_id}: {reason}",
            {
                "estimate_id": str(estimate_id),
                "operation": operation,
                "reason": reason
            }
        )
        self.estimate_id = estimate_id
        self.operation = operation
        self.reason = reason


class InvalidPriceError(EstimateServiceError):
    """Raised when price data is invalid or illogical."""

    def __init__(self, message: str, price_details: dict[str, Any] | None = None):
        super().__init__(
            f"Invalid price: {message}",
            price_details or {}
        )


class ValidationError(EstimateServiceError):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str):
        super().__init__(
            f"Validation failed for '{field}': {message}",
            {"field": field, "validation_error": message}
        )
        self.field = field

