"""
Health Service for TickerTracker backend (Task 3.7).

Provides comprehensive health checks for all system components:
- Database (PostgreSQL via AsyncSession)
- Redis (via redis.asyncio)
- Yahoo Finance (via yfinance fast_info)
- Google Drive (via GoogleDriveClient)

All checks run IN PARALLEL via asyncio.gather(return_exceptions=True) so a
slow or failing dependency never blocks the others.

Status semantics
----------------
- HEALTHY  : Component is working normally.
- DEGRADED : Component is reachable but behaving sub-optimally, OR a
             non-critical component failed / is not configured.
- UNHEALTHY: Component is completely unavailable (DB only triggers this).

System status rules
-------------------
- UNHEALTHY if database status == UNHEALTHY
- DEGRADED  if any non-DB component is DEGRADED or UNHEALTHY
- HEALTHY   otherwise
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Literal

import redis.asyncio as aioredis  # type: ignore[import]
import structlog
import yfinance as yf  # type: ignore[import]
from sqlalchemy import text

from src.infra.drive.client import GoogleDriveClient
from src.shared.infra.config import get_settings
from src.shared.infra.database import AsyncSessionLocal

_logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ComponentHealth:
    """Health status of a single system component."""

    name: str
    status: Literal["HEALTHY", "DEGRADED", "UNHEALTHY"]
    latency_ms: float
    message: str = ""


@dataclass
class SystemHealth:
    """Aggregated health status of the entire system."""

    status: Literal["HEALTHY", "DEGRADED", "UNHEALTHY"]
    version: str
    uptime_seconds: float
    components: list[ComponentHealth] = field(default_factory=list)

    @property
    def is_ready(self) -> bool:
        """
        True when the database component is HEALTHY.

        Kubernetes readiness probe: only the database is critical.  Redis,
        Yahoo, and Drive are non-critical and their degradation does NOT
        block traffic.
        """
        db = next((c for c in self.components if c.name == "database"), None)
        return db is not None and db.status == "HEALTHY"


# ---------------------------------------------------------------------------
# Health service
# ---------------------------------------------------------------------------


class HealthService:
    """
    Runs health checks for all system components.

    Class-level ``_start_time`` is set at first import and used to compute
    uptime for every subsequent call to ``check_all()``.
    """

    _start_time: float = time.monotonic()
    _VERSION: str = "3.0.0"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    async def check_database(self) -> ComponentHealth:
        """
        Execute ``SELECT 1`` on the database to verify connectivity.

        Timeout: 3 s.  Any exception → UNHEALTHY.
        """


        t0 = time.perf_counter()
        try:
            async def _check() -> None:
                async with AsyncSessionLocal() as session:
                    await session.execute(text("SELECT 1"))

            await asyncio.wait_for(_check(), timeout=3.0)  # noqa: RUF006
            latency_ms = (time.perf_counter() - t0) * 1000

            _logger.info(
                "health_check",
                component="database",
                status="HEALTHY",
                latency_ms=round(latency_ms, 2),
            )
            return ComponentHealth(
                name="database",
                status="HEALTHY",
                latency_ms=round(latency_ms, 2),
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - t0) * 1000
            msg = str(exc)[:200]
            _logger.warning(
                "health_check",
                component="database",
                status="UNHEALTHY",
                latency_ms=round(latency_ms, 2),
                error=msg,
            )
            return ComponentHealth(
                name="database",
                status="UNHEALTHY",
                latency_ms=round(latency_ms, 2),
                message=msg,
            )

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    async def check_redis(self) -> ComponentHealth:
        """
        Ping Redis to verify connectivity.

        Timeout: 2 s.  Any exception → DEGRADED (non-critical).
        """
        settings = get_settings()
        t0 = time.perf_counter()
        client = None
        try:
            async def _check() -> None:
                nonlocal client
                client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
                await client.ping()

            await asyncio.wait_for(_check(), timeout=2.0)
            latency_ms = (time.perf_counter() - t0) * 1000

            _logger.info(
                "health_check",
                component="redis",
                status="HEALTHY",
                latency_ms=round(latency_ms, 2),
            )
            return ComponentHealth(
                name="redis",
                status="HEALTHY",
                latency_ms=round(latency_ms, 2),
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - t0) * 1000
            msg = str(exc)[:200]
            _logger.warning(
                "health_check",
                component="redis",
                status="DEGRADED",
                latency_ms=round(latency_ms, 2),
                error=msg,
            )
            return ComponentHealth(
                name="redis",
                status="DEGRADED",
                latency_ms=round(latency_ms, 2),
                message=msg,
            )
        finally:
            if client is not None:
                try:
                    await client.aclose()
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # Yahoo Finance
    # ------------------------------------------------------------------

    async def check_yahoo(self) -> ComponentHealth:
        """
        Fetch AAPL last price to verify Yahoo Finance connectivity.

        Timeout: 5 s.  Any exception → DEGRADED (non-critical).
        Price == 0 → DEGRADED (data quality issue).
        """
        t0 = time.perf_counter()
        try:
            async def _check() -> float:
                loop = asyncio.get_event_loop()
                # yfinance is synchronous — run in a thread so we don't block
                price: float = await loop.run_in_executor(
                    None,
                    lambda: float(yf.Ticker("AAPL").fast_info.get("lastPrice", 0) or 0),
                )
                return price

            price = await asyncio.wait_for(_check(), timeout=5.0)
            latency_ms = (time.perf_counter() - t0) * 1000

            if price > 0:
                status: Literal["HEALTHY", "DEGRADED", "UNHEALTHY"] = "HEALTHY"
            else:
                status = "DEGRADED"

            _logger.info(
                "health_check",
                component="yahoo_finance",
                status=status,
                latency_ms=round(latency_ms, 2),
                price=price,
            )
            return ComponentHealth(
                name="yahoo_finance",
                status=status,
                latency_ms=round(latency_ms, 2),
                message="" if price > 0 else "AAPL price returned 0 or None",
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - t0) * 1000
            msg = str(exc)[:200]
            _logger.warning(
                "health_check",
                component="yahoo_finance",
                status="DEGRADED",
                latency_ms=round(latency_ms, 2),
                error=msg,
            )
            return ComponentHealth(
                name="yahoo_finance",
                status="DEGRADED",
                latency_ms=round(latency_ms, 2),
                message=msg,
            )

    # ------------------------------------------------------------------
    # Google Drive
    # ------------------------------------------------------------------

    async def check_drive(self) -> ComponentHealth:
        """
        List ≤ 1 file in DRIVE_FOLDER_ID to verify Drive connectivity.

        - DRIVE_FOLDER_ID == "" → DEGRADED + "not configured" message.
        - Timeout: 5 s.  Any exception → DEGRADED (non-critical).
        """
        settings = get_settings()
        t0 = time.perf_counter()

        if not settings.DRIVE_FOLDER_ID:
            return ComponentHealth(
                name="google_drive",
                status="DEGRADED",
                latency_ms=0.0,
                message="DRIVE_FOLDER_ID not configured",
            )

        try:
            async def _check() -> None:
                client = GoogleDriveClient(
                    service_account_json=settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value(),
                )
                await client.list_files(settings.DRIVE_FOLDER_ID, page_size=1)

            await asyncio.wait_for(_check(), timeout=5.0)
            latency_ms = (time.perf_counter() - t0) * 1000

            _logger.info(
                "health_check",
                component="google_drive",
                status="HEALTHY",
                latency_ms=round(latency_ms, 2),
            )
            return ComponentHealth(
                name="google_drive",
                status="HEALTHY",
                latency_ms=round(latency_ms, 2),
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - t0) * 1000
            msg = str(exc)[:200]
            _logger.warning(
                "health_check",
                component="google_drive",
                status="DEGRADED",
                latency_ms=round(latency_ms, 2),
                error=msg,
            )
            return ComponentHealth(
                name="google_drive",
                status="DEGRADED",
                latency_ms=round(latency_ms, 2),
                message=msg,
            )

    # ------------------------------------------------------------------
    # Aggregate
    # ------------------------------------------------------------------

    async def check_all(self) -> SystemHealth:
        """
        Run all component checks IN PARALLEL and aggregate the results.

        Uses ``asyncio.gather(return_exceptions=True)`` so a failing check
        never prevents the others from running.

        Returns:
            SystemHealth with aggregated status, uptime, and per-component details.
        """
        results = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_yahoo(),
            self.check_drive(),
            return_exceptions=True,
        )

        components: list[ComponentHealth] = []
        _names = ["database", "redis", "yahoo_finance", "google_drive"]
        for name, result in zip(_names, results, strict=False):
            if isinstance(result, ComponentHealth):
                components.append(result)
            else:
                # Unexpected exception from the check itself (bug in check code)
                components.append(
                    ComponentHealth(
                        name=name,
                        status="UNHEALTHY",
                        latency_ms=0.0,
                        message=str(result)[:200],
                    )
                )

        # Determine overall system status
        db_comp = next((c for c in components if c.name == "database"), None)
        if db_comp is not None and db_comp.status == "UNHEALTHY":
            system_status: Literal["HEALTHY", "DEGRADED", "UNHEALTHY"] = "UNHEALTHY"
        elif any(
            c.status in ("UNHEALTHY", "DEGRADED")
            for c in components
            if c.name != "database"
        ):
            system_status = "DEGRADED"
        else:
            system_status = "HEALTHY"

        uptime_seconds = time.monotonic() - HealthService._start_time

        health = SystemHealth(
            status=system_status,
            version=self._VERSION,
            uptime_seconds=round(uptime_seconds, 2),
            components=components,
        )

        _logger.info(
            "health_check_all",
            status=system_status,
            uptime_seconds=health.uptime_seconds,
            components=[
                {"name": c.name, "status": c.status, "latency_ms": c.latency_ms}
                for c in components
            ],
        )
        return health
