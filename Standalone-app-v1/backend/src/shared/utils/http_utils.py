import logging
from httpx import TimeoutException, HTTPStatusError

logger = logging.getLogger(__name__)


def is_retryable_http_error(exc: Exception) -> bool:
    """Return True if the HTTP exception is worth retrying (timeout, 429, 5xx)."""
    if isinstance(exc, TimeoutException):
        return True
    if isinstance(exc, HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    return False