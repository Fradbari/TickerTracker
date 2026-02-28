"""
Prometheus metrics endpoint  (Task 3.6).

Exposes ``GET /metrics`` in the standard Prometheus text exposition format
(text/plain; version=0.0.4).

The route is intentionally kept separate from the application business routers
and placed in ``src/infra/metrics/`` alongside the metric definitions.

Security note
-------------
``/metrics`` is added to ``API_KEY_EXEMPT_PATHS`` in ``config.py`` so that
Prometheus scrapers can reach it without an API key.  In production you should
protect this endpoint at the network/proxy level (e.g. allow only the
Prometheus server IP).
"""

from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.infra.metrics.metrics import update_pool_metrics

router = APIRouter(tags=["metrics"])


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description=(
        "Exposes all registered Prometheus metrics in the standard text "
        "exposition format.  Meant to be scraped by a Prometheus server."
    ),
    response_class=Response,
    include_in_schema=False,  # hide from Swagger — monitoring-only endpoint
)
def metrics_endpoint() -> Response:
    """Return all Prometheus metrics in text/plain; version=0.0.4 format."""
    # Refresh pool gauges before scrape (Task 3.10)
    update_pool_metrics()
    data: bytes = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
