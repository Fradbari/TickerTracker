"""
Unit tests for src/infra/metrics/metrics.py and src/infra/metrics/routes.py
(Task 3.6).

Strategy
--------
- Metric unit tests (Counter, Gauge, Histogram) use **isolated** registries
  via ``CollectorRegistry()`` so tests cannot pollute each other.
- ``track_duration`` tests patch the histogram ``observe`` method to verify it
  is called with a non-negative elapsed time — both async and sync code paths.
- Endpoint tests use a **minimal** FastAPI TestClient (only the metrics router)
  to avoid dragging in the scheduler, database, and other app infrastructure.
- The ``API_KEY_EXEMPT_PATHS`` test reads the Pydantic field default directly
  without instantiating ``Settings`` (which would require a valid ``.env``).

Coverage
--------
  TestCounterBehaviour      – prometheus Counter increments
  TestGaugeBehaviour        – prometheus Gauge set/inc/dec
  TestHistogramBehaviour    – observe lands in the correct bucket
  TestTrackDurationDecorator – sync and async route handler coverage
  TestMetricsEndpoint       – 200 / Content-Type / text format
  TestMetricsExemptPath     – /metrics in API_KEY_EXEMPT_PATHS
"""

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

from src.infra.metrics.metrics import track_duration
from src.infra.metrics.routes import router as metrics_router

# ---------------------------------------------------------------------------
# Minimal test app (metrics router only)
# ---------------------------------------------------------------------------

def _make_metrics_app() -> FastAPI:
    app = FastAPI()
    app.include_router(metrics_router)
    return app


# ---------------------------------------------------------------------------
# Counter tests
# ---------------------------------------------------------------------------

class TestCounterBehaviour:
    """Verifies basic Counter semantics with an isolated registry."""

    def setup_method(self):
        self._registry = CollectorRegistry()
        self._counter = Counter(
            "test_counter_total",
            "Test counter",
            labelnames=["env"],
            registry=self._registry,
        )

    def test_counter_starts_at_zero(self):
        self._counter.labels(env="test")
        {
            s.name: s.value
            for s in self._registry.get_sample_value.__self__  # pragma: no cover
        } if False else {}
        # Use direct sample value query
        val = self._registry.get_sample_value(
            "test_counter_total", {"env": "test"}
        )
        assert val == 0.0 or val is None  # None before first observation

    def test_counter_increments(self):
        self._counter.labels(env="prod").inc()
        val = self._registry.get_sample_value(
            "test_counter_total", {"env": "prod"}
        )
        assert val == 1.0

    def test_counter_increments_by_amount(self):
        self._counter.labels(env="dev").inc(5)
        val = self._registry.get_sample_value(
            "test_counter_total", {"env": "dev"}
        )
        assert val == 5.0

    def test_counter_accumulates(self):
        self._counter.labels(env="stg").inc()
        self._counter.labels(env="stg").inc(3)
        val = self._registry.get_sample_value(
            "test_counter_total", {"env": "stg"}
        )
        assert val == 4.0


# ---------------------------------------------------------------------------
# Gauge tests
# ---------------------------------------------------------------------------

class TestGaugeBehaviour:
    """Verifies basic Gauge semantics with an isolated registry."""

    def setup_method(self):
        self._registry = CollectorRegistry()
        self._gauge = Gauge(
            "test_gauge",
            "Test gauge",
            registry=self._registry,
        )

    def test_gauge_set(self):
        self._gauge.set(42.0)
        val = self._registry.get_sample_value("test_gauge")
        assert val == 42.0

    def test_gauge_inc(self):
        self._gauge.set(10.0)
        self._gauge.inc(5.0)
        val = self._registry.get_sample_value("test_gauge")
        assert val == 15.0

    def test_gauge_dec(self):
        self._gauge.set(10.0)
        self._gauge.dec(3.0)
        val = self._registry.get_sample_value("test_gauge")
        assert val == 7.0

    def test_gauge_can_go_negative(self):
        self._gauge.set(-5.0)
        val = self._registry.get_sample_value("test_gauge")
        assert val == -5.0


# ---------------------------------------------------------------------------
# Histogram tests
# ---------------------------------------------------------------------------

class TestHistogramBehaviour:
    """Verifies Histogram observe and bucket accumulation."""

    def _make_hist(self, name: str, buckets=None):
        registry = CollectorRegistry()
        kwargs = {"registry": registry}
        if buckets:
            kwargs["buckets"] = buckets
        h = Histogram(name, "test histogram", **kwargs)
        return h, registry

    def test_histogram_observe_increments_count(self):
        h, reg = self._make_hist("h_count")
        h.observe(0.05)
        val = reg.get_sample_value("h_count_count")
        assert val == 1.0

    def test_histogram_observe_accumulates_sum(self):
        h, reg = self._make_hist("h_sum")
        h.observe(0.1)
        h.observe(0.2)
        val = reg.get_sample_value("h_sum_sum")
        assert abs(val - 0.3) < 1e-9

    def test_histogram_observe_correct_bucket(self):
        """Value of 0.05 must land in bucket le=0.05 and not in smaller buckets."""
        h, reg = self._make_hist("h_bucket", buckets=[0.01, 0.05, 0.1, 1.0])
        h.observe(0.05)
        # Bucket le="0.05" should be 1
        val_05 = reg.get_sample_value("h_bucket_bucket", {"le": "0.05"})
        # Bucket le="0.01" should be 0 (0.05 > 0.01)
        val_01 = reg.get_sample_value("h_bucket_bucket", {"le": "0.01"})
        assert val_05 == 1.0
        assert val_01 == 0.0

    def test_histogram_inf_bucket_always_counts(self):
        h, reg = self._make_hist("h_inf", buckets=[0.001])
        h.observe(9999.0)
        val_inf = reg.get_sample_value("h_inf_bucket", {"le": "+Inf"})
        assert val_inf == 1.0

    def test_histogram_custom_buckets(self):
        """api_request_duration_seconds-style buckets accept a 5s observation."""
        buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
        h, reg = self._make_hist("h_api", buckets=buckets)
        h.observe(5.0)
        val = reg.get_sample_value("h_api_bucket", {"le": "5.0"})
        assert val == 1.0


# ---------------------------------------------------------------------------
# @track_duration decorator tests
# ---------------------------------------------------------------------------

class TestTrackDurationDecorator:
    """Verifies that @track_duration calls histogram.observe with elapsed time."""

    def _isolated_hist(self, name: str, labelnames=None) -> Histogram:
        registry = CollectorRegistry()
        kw = {"registry": registry}
        if labelnames:
            kw["labelnames"] = labelnames
        return Histogram(name, "test", **kw)

    # -- Sync function ---------------------------------------------------

    def test_sync_observe_called(self):
        hist = self._isolated_hist("td_sync")
        mock_observe = MagicMock()
        with patch.object(hist, "observe", mock_observe):
            @track_duration(hist)
            def fn():
                return 99

            result = fn()
        assert result == 99
        mock_observe.assert_called_once()
        elapsed = mock_observe.call_args[0][0]
        assert 0.0 <= elapsed < 5.0  # sanity bound

    def test_sync_with_labels(self):
        hist = self._isolated_hist("td_sync_lbl", labelnames=["method"])
        mock_child = MagicMock()
        with patch.object(hist, "labels", return_value=mock_child) as mock_labels:
            @track_duration(hist, method="GET")
            def fn():
                return "ok"

            result = fn()
            # Assertions inside the with block (before patch is restored)
            mock_labels.assert_called_once_with(method="GET")
            mock_child.observe.assert_called_once()
            elapsed = mock_child.observe.call_args[0][0]
            assert elapsed >= 0
        assert result == "ok"

    def test_sync_still_records_on_exception(self):
        """observe() must be called even when the wrapped function raises."""
        hist = self._isolated_hist("td_exc")
        mock_observe = MagicMock()
        with patch.object(hist, "observe", mock_observe):
            @track_duration(hist)
            def failing():
                raise ValueError("boom")

            with pytest.raises(ValueError):
                failing()
        mock_observe.assert_called_once()

    # -- Async function --------------------------------------------------

    def test_async_observe_called(self):
        hist = self._isolated_hist("td_async")
        mock_observe = MagicMock()
        with patch.object(hist, "observe", mock_observe):
            @track_duration(hist)
            async def afn():
                return "async-result"

            result = asyncio.run(afn())
            mock_observe.assert_called_once()
        assert result == "async-result"

    def test_async_with_labels(self):
        hist = self._isolated_hist("td_async_lbl", labelnames=["endpoint"])
        mock_child = MagicMock()
        with patch.object(hist, "labels", return_value=mock_child) as mock_labels:
            @track_duration(hist, endpoint="/test")
            async def afn():
                return None

            asyncio.run(afn())
            # Assertions inside the with block (before patch is restored)
            mock_labels.assert_called_once_with(endpoint="/test")
            mock_child.observe.assert_called_once()

    def test_preserves_function_name(self):
        hist = self._isolated_hist("td_name")
        @track_duration(hist)
        def my_named_fn():
            pass

        assert my_named_fn.__name__ == "my_named_fn"


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------

class TestMetricsEndpoint:
    """Integration tests for the GET /metrics route."""

    def setup_method(self):
        self.client = TestClient(_make_metrics_app(), raise_server_exceptions=True)

    def test_metrics_endpoint_returns_200(self):
        resp = self.client.get("/metrics")
        assert resp.status_code == 200

    def test_metrics_endpoint_content_type(self):
        """Response must carry the Prometheus text exposition content type."""
        resp = self.client.get("/metrics")
        ct = resp.headers.get("content-type", "")
        assert "text/plain" in ct
        assert "0.0.4" in ct

    def test_metrics_endpoint_format(self):
        """Body must include standard Prometheus # HELP and # TYPE lines."""
        resp = self.client.get("/metrics")
        body = resp.text
        assert "# HELP" in body
        assert "# TYPE" in body

    def test_metrics_endpoint_not_json(self):
        """The response body must not be JSON-parseable (it is plain text)."""
        resp = self.client.get("/metrics")
        with pytest.raises(Exception):
            json.loads(resp.text)


# ---------------------------------------------------------------------------
# API_KEY_EXEMPT_PATHS test
# ---------------------------------------------------------------------------

class TestMetricsExemptPath:
    """Verifies that /metrics is included in the default exempt path list."""

    def test_metrics_exempt_from_api_key(self):
        import src.shared.infra.config as cfg_module
        field = cfg_module.Settings.model_fields["API_KEY_EXEMPT_PATHS"]
        exempt_paths = field.default
        assert "/metrics" in exempt_paths
