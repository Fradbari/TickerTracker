"""
Data Lineage Tracking — TASK 3.9

Provides the ``DataSource`` enum and ``LineageTracked`` SQLAlchemy mixin
for attaching data-lineage metadata to any ORM model.

Architecture
------------
- ``DataSource``     : Enum of all known data-source identifiers.
- ``LineageTracked`` : SQLAlchemy mixin; adds 4 lineage columns to any model
                       that inherits from it.

Usage
-----
.. code-block:: python

    from src.shared.domain.lineage import LineageTracked, DataSource

    class MarketData(LineageTracked, Base):
        __tablename__ = "market_data"
        # ... other columns ...

Columns added by the mixin
--------------------------
+-----------------------+---------------+------------------------------------------------------+
| Column                | Type          | Description                                          |
+=======================+===============+======================================================+
| data_source           | VARCHAR(50)   | DataSource enum value stored as string               |
| source_timestamp      | TIMESTAMPTZ   | When data was generated at the source (nullable)     |
| ingestion_timestamp   | TIMESTAMPTZ   | When data entered our system (auto set by server)    |
| quality_score         | DECIMAL(3,2)  | Quality score 0.00–1.00 (freshness + completeness)  |
+-----------------------+---------------+------------------------------------------------------+
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DECIMAL, Column, DateTime, String
from sqlalchemy.sql import func

# ---------------------------------------------------------------------------
# DataSource enum
# ---------------------------------------------------------------------------


class DataSource(str, Enum):
    """
    Enum of all recognised data sources.

    Using ``str`` as a mixin allows the enum values to be used directly
    wherever a plain string is expected (e.g. SQLAlchemy column default).
    """

    YAHOO_FINANCE = "yahoo_finance"
    FINNHUB = "finnhub"
    MANUAL_ENTRY = "manual_entry"
    DRIVE_SYNC = "drive_sync"
    CALCULATED = "calculated"

    @classmethod
    def from_legacy(cls, value: str) -> DataSource:
        """
        Convert legacy ``data_source`` string values to the current enum.

        Legacy values (e.g. "yahoo") originate from early versions of the
        system that used plain strings instead of the enum.  Unknown values
        default to ``YAHOO_FINANCE``.

        Args:
            value: Legacy string from the ``data_source`` column.

        Returns:
            The matching ``DataSource`` member.

        Examples:
            >>> DataSource.from_legacy("yahoo")
            <DataSource.YAHOO_FINANCE: 'yahoo_finance'>
            >>> DataSource.from_legacy("unknown_source")
            <DataSource.YAHOO_FINANCE: 'yahoo_finance'>
        """
        mapping: dict[str, DataSource] = {
            "yahoo": cls.YAHOO_FINANCE,
            "yahoo_finance": cls.YAHOO_FINANCE,
            "finnhub": cls.FINNHUB,
            "manual": cls.MANUAL_ENTRY,
            "manual_entry": cls.MANUAL_ENTRY,
            "drive_sync": cls.DRIVE_SYNC,
            "calculated": cls.CALCULATED,
        }
        return mapping.get(value.lower(), cls.YAHOO_FINANCE)


# ---------------------------------------------------------------------------
# LineageTracked mixin
# ---------------------------------------------------------------------------


class LineageTracked:
    """
    SQLAlchemy mixin that adds data lineage fields to any ORM model.

    Add this mixin *before* the declarative ``Base`` in the inheritance list::

        class MarketData(LineageTracked, Base):
            ...

    Fields
    ------
    data_source
        DataSource enum value stored as a VARCHAR(50) string.
        Defaults to ``DataSource.YAHOO_FINANCE.value`` (``"yahoo_finance"``).
    source_timestamp
        UTC timestamp when the data was generated **at the source** (nullable).
        Yahoo Finance does not provide a precise source timestamp; in that
        case the ingestion time is used as a proxy.
    ingestion_timestamp
        UTC timestamp when data entered *our* system.  Set automatically by
        the database server via ``server_default=func.now()``.
    quality_score
        Float in ``[0.00, 1.00]`` computed from freshness and completeness.
        ``1.00`` = highest quality; ``None`` = not yet computed.
    """

    data_source = Column(
        String(50),
        nullable=False,
        default=DataSource.YAHOO_FINANCE.value,
        doc="Source of the data (DataSource enum value)",
    )
    source_timestamp = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when data was generated at the source",
    )
    ingestion_timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp when data was ingested into the system",
    )
    quality_score = Column(
        DECIMAL(3, 2),
        nullable=True,
        default=Decimal("0.80"),
        doc="Data quality score 0.00–1.00 (freshness + completeness)",
    )

    # ------------------------------------------------------------------
    # Quality score computation
    # ------------------------------------------------------------------

    def compute_quality_score(
        self,
        source_ts: datetime | None = None,
        has_volume: bool = True,
        has_ohlc: bool = True,
    ) -> Decimal:
        """
        Compute quality score based on freshness and completeness.

        Scoring formula (weighted average):
        - **Freshness** (weight 0.6):
          - ``source_ts`` within 24 h → 1.00
          - ``source_ts`` within 7 days → 0.80
          - older or missing → 0.50
        - **Completeness** (weight 0.4):
          - base score 0.80
          - missing OHLC ``has_ohlc=False`` → −0.40
          - missing volume ``has_volume=False`` → −0.10

        The result is clamped to ``[0.00, 1.00]``.

        Args:
            source_ts:  UTC datetime when data was generated at the source.
                        Pass ``None`` if unknown.
            has_volume: Whether volume data is present and positive.
            has_ohlc:   Whether all four OHLC price fields are present.

        Returns:
            Computed quality score as a ``Decimal``.

        Examples:
            >>> # Fresh complete data
            >>> score = obj.compute_quality_score(source_ts=datetime.utcnow())
            >>> assert score >= Decimal("0.80")
        """
        # --- Freshness sub-score ---
        freshness = Decimal("0.50")
        if source_ts is not None:
            delta = datetime.utcnow() - source_ts.replace(tzinfo=None)
            if delta.total_seconds() < 86_400:      # < 24 h
                freshness = Decimal("1.00")
            elif delta.days < 7:                    # < 7 days
                freshness = Decimal("0.80")

        # --- Completeness sub-score ---
        completeness = Decimal("0.80")
        if not has_ohlc:
            completeness -= Decimal("0.40")
        if not has_volume:
            completeness -= Decimal("0.10")

        score = freshness * Decimal("0.6") + completeness * Decimal("0.4")
        return min(max(score, Decimal("0.00")), Decimal("1.00"))
