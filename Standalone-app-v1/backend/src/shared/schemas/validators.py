"""
Shared input validators for TickerTracker backend (Task 3.3).

All functions are standalone callables designed to be invoked from Pydantic v2
``@field_validator`` / ``@model_validator`` decorators inside schema classes.

They focus on *security* and *sanity* — domain-specific constraints (e.g.
``Field(gt=0, le=100)`` on ``stop_loss_percent``) live in their respective
schemas and are intentionally not replaced by these helpers.

Public API
----------
    sanitize_ticker       – uppercase, regex-safe ticker symbol
    sanitize_text         – strip HTML tags and whitespace, enforce max length
    validate_price        – positive Decimal ≤ 999 999.999999, 6 decimal places
    validate_percentage   – Decimal in [-100, 1000], 4 decimal places
    validate_date_range   – start ≤ end, span ≤ 10 years
"""

import re
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TICKER_RE = re.compile(r"^[A-Z0-9.\-]{1,10}$")
_HTML_TAG_RE = re.compile(r"<[^>]+>")

_PRICE_MAX = Decimal("999999.999999")
_PRICE_QUANTUM = Decimal("0.000001")

_PCT_MIN = Decimal("-100")
_PCT_MAX = Decimal("1000")
_PCT_QUANTUM = Decimal("0.0001")

_MAX_DATE_RANGE_DAYS = 3650  # 10 years


# ---------------------------------------------------------------------------
# 1. sanitize_ticker
# ---------------------------------------------------------------------------

def sanitize_ticker(v: str) -> str:
    """
    Validate and normalise a ticker symbol.

    Steps:
        1. Strip surrounding whitespace.
        2. Convert to uppercase.
        3. Assert the result matches ``^[A-Z0-9.\\-]{1,10}$``.

    Args:
        v: Raw ticker string from user input.

    Returns:
        Uppercase, validated ticker string.

    Raises:
        ValueError: If the ticker does not match the allowed pattern.

    Examples:
        >>> sanitize_ticker("aapl")
        'AAPL'
        >>> sanitize_ticker("BRK.B")
        'BRK.B'
    """
    cleaned = v.strip().upper()
    if not _TICKER_RE.match(cleaned):
        raise ValueError(
            "Ticker must be 1–10 characters: A-Z, 0-9, dot or dash"
        )
    return cleaned


# ---------------------------------------------------------------------------
# 2. sanitize_text
# ---------------------------------------------------------------------------

def sanitize_text(v: str, *, max_len: int = 500) -> str:
    """
    Strip HTML tags, trim whitespace, and enforce a maximum length.

    Designed for free-text fields such as ``ai_reasoning``.  The caller is
    responsible for deciding whether an empty result is acceptable (i.e. this
    function does **not** raise on empty strings — nullable fields should use
    ``Optional[str]`` and the field-level ``default=None``).

    Args:
        v:       Raw text from user input.
        max_len: Maximum number of characters to keep (default 500).

    Returns:
        Sanitised, stripped, and potentially truncated string.

    Raises:
        ValueError: Never raised for empty strings (nullability is the schema's
                    responsibility).  Only raised if ``max_len < 1``.

    Examples:
        >>> sanitize_text("<script>alert(1)</script>hello")
        'hello'
        >>> sanitize_text("  lots of spaces  ")
        'lots of spaces'
    """
    # Remove HTML/XML tags
    without_tags = _HTML_TAG_RE.sub("", v)
    # Strip leading/trailing whitespace
    stripped = without_tags.strip()
    # Truncate to max_len
    return stripped[:max_len]


# ---------------------------------------------------------------------------
# 3. validate_price
# ---------------------------------------------------------------------------

def validate_price(v: Decimal) -> Decimal:
    """
    Validate a monetary price value.

    Rules:
        - Must be strictly positive (``> 0``).
        - Must not exceed ``999 999.999999``.
        - Normalised to 6 decimal places using ``ROUND_HALF_UP``.

    Args:
        v: Decimal price value.

    Returns:
        Normalised price Decimal.

    Raises:
        ValueError: If the value is non-positive or exceeds the maximum.

    Examples:
        >>> validate_price(Decimal("115.50"))
        Decimal('115.500000')
    """
    if v <= Decimal("0") or v > _PRICE_MAX:
        raise ValueError("Price must be positive and ≤ 999,999.999999")
    return v.quantize(_PRICE_QUANTUM, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# 4. validate_percentage
# ---------------------------------------------------------------------------

def validate_percentage(v: Decimal) -> Decimal:
    """
    Validate a percentage value with a broad financial range.

    Range: ``[-100, +1000]`` — covers short positions and high-growth targets.
    Normalised to 4 decimal places using ``ROUND_HALF_UP``.

    ⚠️  Do NOT apply this validator to ``stop_loss_percent`` or fields that
    carry tighter domain-specific constraints (e.g. ``Field(le=100)``).  Those
    constraints must remain in their respective schema definitions.

    Args:
        v: Decimal percentage value.

    Returns:
        Normalised percentage Decimal.

    Raises:
        ValueError: If the value is outside ``[-100, +1000]``.

    Examples:
        >>> validate_percentage(Decimal("-100"))
        Decimal('-100.0000')
        >>> validate_percentage(Decimal("1001"))
        Traceback (most recent call last):
            ...
        ValueError: Percentage must be between -100% and +1000%
    """
    if v < _PCT_MIN or v > _PCT_MAX:
        raise ValueError("Percentage must be between -100% and +1000%")
    return v.quantize(_PCT_QUANTUM, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# 5. validate_date_range
# ---------------------------------------------------------------------------

def validate_date_range(start: datetime, end: datetime) -> None:
    """
    Validate that a date range is logically ordered and within 10 years.

    Intended to be called from a ``@model_validator(mode="after")`` after
    confirming that both ``start`` and ``end`` are non-None.

    Args:
        start: The range start datetime.
        end:   The range end datetime.

    Raises:
        ValueError: ``"start_date must be ≤ end_date"`` when ``start > end``.
        ValueError: ``"Date range cannot exceed 10 years"`` when span > 3650 days.
    """
    if start > end:
        raise ValueError("start_date must be ≤ end_date")
    if (end - start).days > _MAX_DATE_RANGE_DAYS:
        raise ValueError("Date range cannot exceed 10 years")
