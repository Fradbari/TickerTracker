"""
Unit tests for src/infra/logging/config.py  (Task 3.5).

Strategy
--------
- Middleware tests use a minimal FastAPI TestClient to verify header
  reading, UUID generation, response propagation and ContextVar injection.
- Processor tests call ``add_correlation_id`` directly with a controlled
  ContextVar state.
- ``configure_logging`` idempotency is verified by resetting the private
  ``_configured`` flag via ``monkeypatch`` and checking structlog config.
- JSON output is verified by invoking ``JSONRenderer`` in isolation.
- No real Redis, DB, or .env required.

Coverage
--------
  TestCorrelationIDMiddleware  – header read / UUID fallback / response header / ContextVar
  TestAddCorrelationIdProcessor – processor injects / omits field
  TestConfigureLogging          – idempotency / wrapping class / JSON renderer
  TestLogLevel                  – INFO / DEBUG level accepted correctly
"""

import json
import logging
from uuid import UUID

import pytest
import structlog
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.infra.logging.config import (
    CorrelationIDMiddleware,
    add_correlation_id,
    configure_logging,
    correlation_id,
)
import src.infra.logging.config as logging_config_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_app() -> FastAPI:
    """Minimal app that exposes the ContextVar value via /ping."""
    app = FastAPI()
    app.add_middleware(CorrelationIDMiddleware)

    @app.get("/ping")
    async def ping():
        return {"cid": correlation_id.get()}

    return app


# ---------------------------------------------------------------------------
# Middleware tests
# ---------------------------------------------------------------------------

class TestCorrelationIDMiddleware:
    """Tests for CorrelationIDMiddleware header management."""

    def setup_method(self):
        self.client = TestClient(_make_test_app(), raise_server_exceptions=True)

    # -- ContextVar set correctly ----------------------------------------

    def test_correlation_id_set_in_contextvar(self):
        """Endpoint reads the injected ContextVar value correctly."""
        resp = self.client.get("/ping", headers={"X-Correlation-ID": "ctx-check-123"})
        assert resp.status_code == 200
        assert resp.json()["cid"] == "ctx-check-123"

    # -- Read from header -------------------------------------------------

    def test_correlation_id_from_header(self):
        """When X-Correlation-ID is present, that value is used."""
        resp = self.client.get("/ping", headers={"X-Correlation-ID": "provided-id"})
        assert resp.json()["cid"] == "provided-id"

    # -- UUID generated when header absent --------------------------------

    def test_correlation_id_generated_if_missing(self):
        """When X-Correlation-ID header is absent a UUID4 is generated."""
        resp = self.client.get("/ping")
        cid: str = resp.json()["cid"]
        # Validate it is a valid UUID4
        parsed = UUID(cid, version=4)
        assert str(parsed) == cid

    def test_generated_ids_are_unique(self):
        """Two requests without the header must receive different IDs."""
        cid1 = self.client.get("/ping").json()["cid"]
        cid2 = self.client.get("/ping").json()["cid"]
        assert cid1 != cid2

    # -- Response header propagation ------------------------------------

    def test_correlation_id_in_response_header_from_request(self):
        """Provided ID is echoed back in the X-Correlation-ID response header."""
        resp = self.client.get("/ping", headers={"X-Correlation-ID": "echo-me"})
        assert resp.headers["X-Correlation-ID"] == "echo-me"

    def test_correlation_id_in_response_header_generated(self):
        """Generated UUID is present in X-Correlation-ID response header."""
        resp = self.client.get("/ping")
        assert "X-Correlation-ID" in resp.headers
        cid = resp.headers["X-Correlation-ID"]
        # Must be a valid UUID4
        UUID(cid, version=4)

    def test_response_header_matches_contextvar(self):
        """Response header and ContextVar value must be the same ID."""
        resp = self.client.get("/ping")
        header_cid = resp.headers["X-Correlation-ID"]
        body_cid = resp.json()["cid"]
        assert header_cid == body_cid


# ---------------------------------------------------------------------------
# Processor tests
# ---------------------------------------------------------------------------

class TestAddCorrelationIdProcessor:
    """Tests for the add_correlation_id structlog processor."""

    def test_adds_correlation_id_when_set(self):
        """Processor injects correlation_id field when ContextVar is non-empty."""
        token = correlation_id.set("proc-test-id")
        try:
            result = add_correlation_id(None, None, {"event": "test"})
            assert result["correlation_id"] == "proc-test-id"
        finally:
            correlation_id.reset(token)

    def test_omits_correlation_id_when_empty(self):
        """Processor does NOT add correlation_id field when ContextVar is empty."""
        token = correlation_id.set("")
        try:
            result = add_correlation_id(None, None, {"event": "test"})
            assert "correlation_id" not in result
        finally:
            correlation_id.reset(token)

    def test_returns_event_dict_unchanged_structure(self):
        """Existing keys in event_dict are preserved."""
        token = correlation_id.set("keep-keys")
        try:
            result = add_correlation_id(None, None, {"event": "e", "extra": 42})
            assert result["extra"] == 42
            assert result["event"] == "e"
        finally:
            correlation_id.reset(token)


# ---------------------------------------------------------------------------
# configure_logging tests
# ---------------------------------------------------------------------------

class TestConfigureLogging:
    """Tests for the configure_logging() function."""

    def _reset(self, monkeypatch):
        """Reset _configured flag and structlog to a clean state."""
        monkeypatch.setattr(logging_config_module, "_configured", False)

    def test_configure_logging_idempotent(self, monkeypatch):
        """Calling configure_logging twice does not duplicate processors."""
        self._reset(monkeypatch)
        configure_logging("INFO")
        count_after_first = len(structlog.get_config()["processors"])

        # Second call must be a no-op because _configured is now True
        configure_logging("INFO")
        count_after_second = len(structlog.get_config()["processors"])

        assert count_after_first == count_after_second

    def test_configured_flag_set_after_call(self, monkeypatch):
        """_configured flag becomes True after first call."""
        self._reset(monkeypatch)
        configure_logging("INFO")
        assert logging_config_module._configured is True

    def test_second_call_skipped_when_configured(self, monkeypatch):
        """When _configured is already True, configure_logging returns immediately."""
        monkeypatch.setattr(logging_config_module, "_configured", True)
        # Patch structlog.configure to verify it is NOT called
        with pytest.MonkeyPatch().context() as mp:
            called = []
            mp.setattr(structlog, "configure", lambda **kw: called.append(kw))
            configure_logging("INFO")
        assert called == [], "structlog.configure must not be called again"

    def test_wrapper_class_is_bound_logger(self, monkeypatch):
        """After configure_logging, structlog wraps with BoundLogger."""
        self._reset(monkeypatch)
        configure_logging("INFO")
        cfg = structlog.get_config()
        assert cfg["wrapper_class"] is structlog.stdlib.BoundLogger

    def test_json_output(self, monkeypatch):
        """JSONRenderer processor produces valid JSON from an event_dict."""
        # Test the renderer in isolation without needing a live logger
        renderer = structlog.processors.JSONRenderer()
        event_dict = {"event": "hello", "level": "info", "logger": "test_module"}
        json_str = renderer(None, None, event_dict)
        data = json.loads(json_str)
        assert data["event"] == "hello"
        assert data["level"] == "info"


# ---------------------------------------------------------------------------
# Log level tests
# ---------------------------------------------------------------------------

class TestLogLevel:
    """Tests for log level propagation inside configure_logging."""

    def _reset(self, monkeypatch):
        monkeypatch.setattr(logging_config_module, "_configured", False)

    def test_info_level_accepted(self, monkeypatch):
        """configure_logging('INFO') runs without raising."""
        self._reset(monkeypatch)
        # Clear root handlers so basicConfig is effective
        root = logging.getLogger()
        saved = root.handlers[:]
        root.handlers.clear()
        try:
            configure_logging("INFO")
            assert root.level == logging.INFO
        finally:
            root.handlers = saved

    def test_debug_level_accepted(self, monkeypatch):
        """configure_logging('DEBUG') runs without raising."""
        self._reset(monkeypatch)
        root = logging.getLogger()
        saved = root.handlers[:]
        root.handlers.clear()
        try:
            configure_logging("DEBUG")
            assert root.level == logging.DEBUG
        finally:
            root.handlers = saved

    def test_invalid_level_falls_back_to_info(self, monkeypatch):
        """Unknown level name falls back to INFO without raising."""
        self._reset(monkeypatch)
        root = logging.getLogger()
        saved = root.handlers[:]
        root.handlers.clear()
        try:
            configure_logging("NOTEXISTENT")
            # getattr(logging, "NOTEXISTENT", logging.INFO) → INFO
            assert root.level == logging.INFO
        finally:
            root.handlers = saved
