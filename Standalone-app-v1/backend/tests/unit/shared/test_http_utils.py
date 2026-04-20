import pytest
import httpx
from unittest.mock import MagicMock
from src.shared.utils.http_utils import is_retryable_http_error


def test_timeout_is_retryable():
    assert is_retryable_http_error(httpx.TimeoutException("timeout")) is True


def test_429_is_retryable():
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    exc = httpx.HTTPStatusError("rate limit", request=MagicMock(), response=mock_resp)
    assert is_retryable_http_error(exc) is True


def test_500_is_retryable():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    exc = httpx.HTTPStatusError("server error", request=MagicMock(), response=mock_resp)
    assert is_retryable_http_error(exc) is True


def test_400_is_not_retryable():
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    exc = httpx.HTTPStatusError("bad request", request=MagicMock(), response=mock_resp)
    assert is_retryable_http_error(exc) is False


def test_generic_exception_is_not_retryable():
    assert is_retryable_http_error(ValueError("oops")) is False