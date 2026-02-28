from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

# Generic type for the data field
T = TypeVar("T")


class ApiError(BaseModel):
    """
    Standard API error schema.

    Attributes:
        code (str): Internal error code for machine readability.
        message (str): Human-readable error message.
        details (Optional[Dict[str, Any]]): Additional error context.
    """

    code: str
    message: str
    details: dict[str, Any] | None = None


class ApiResponse(BaseModel, Generic[T]):
    """
    Uniform API response model used by all endpoints.

    Attributes:
        success (bool): Indicates if the operation was successful.
        data (Optional[T]): The response payload.
        error (Optional[ApiError]): Error details if success is False.
        trace_id: Unique identifier for request tracing.

    Class helpers
    -------------
    Use :func:`make_success` / :func:`make_error` class-methods to build
    response objects without constructing the model manually.  These names
    avoid the conflict with the ``success: bool`` field.
    """

    success: bool
    data: Optional[T] = None
    error: Optional[ApiError] = None
    trace_id: str = ""

    @classmethod
    def make_success(cls, data: Any = None, message: str = "", trace_id: str = "") -> "ApiResponse":
        """
        Create a successful API response.

        Note: use this instead of the non-existent ``ApiResponse.success()``
        which conflicts with the ``success: bool`` Pydantic field.

        Args:
            data:     The payload to wrap.
            message:  Human-readable description (ignored, for documentation
                      purposes only — ``ApiResponse`` has no message field).
            trace_id: Optional request trace ID.

        Returns:
            ``ApiResponse`` with ``success=True``.
        """
        return cls(success=True, data=data, error=None, trace_id=trace_id)


def success_response(data: Any, trace_id: str) -> ApiResponse[Any]:
    """
    Creates a standardized successful API response.

    Use this helper when an operation has completed successfully and you need to
    return data to the client.

    Args:
        data: The payload to include in the response.
        trace_id: Unique identifier for the request.

    Returns:
        ApiResponse: A success response instance.
    """
    return ApiResponse(success=True, data=data, error=None, trace_id=trace_id)


def error_response(
    code: str, message: str, details: dict[str, Any] | None = None, trace_id: str = ""
) -> ApiResponse[None]:
    """
    Creates a standardized error API response.

    Use this helper when an operation has failed and you need to return
    error details to the client.

    Args:
        code: Machine-readable error code.
        message: Human-readable error description.
        details: Optional dictionary with extra error info.
        trace_id: Unique identifier for the request.

    Returns:
        ApiResponse: An error response instance.
    """
    return ApiResponse(
        success=False,
        data=None,
        error=ApiError(code=code, message=message, details=details),
        trace_id=trace_id,
    )
