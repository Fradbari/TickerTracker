"""
Unit tests for standard API response models.
"""

from src.shared.schemas.api_response import ApiError, ApiResponse, error_response, success_response


class TestApiResponse:
    """Tests for ApiResponse and ApiError schemas."""

    def test_api_error_creation(self):
        """Test creation of ApiError model."""
        error = ApiError(code="TEST_ERROR", message="Test error message", details={"key": "value"})
        assert error.code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.details == {"key": "value"}

    def test_api_response_success(self):
        """Test creation of successful ApiResponse."""
        response = ApiResponse(success=True, data={"foo": "bar"}, trace_id="test-trace-id")
        assert response.success is True
        assert response.data == {"foo": "bar"}
        assert response.error is None
        assert response.trace_id == "test-trace-id"

    def test_api_response_error(self):
        """Test creation of error ApiResponse."""
        error = ApiError(code="ERR", message="Msg")
        response = ApiResponse(success=False, error=error, trace_id="trace-id")
        assert response.success is False
        assert response.data is None
        assert response.error.code == "ERR"
        assert response.trace_id == "trace-id"


class TestApiResponseHelpers:
    """Tests for success_response and error_response helper functions."""

    def test_success_response_helper(self):
        """Test success_response helper function."""
        data = {"id": 1}
        trace_id = "trace-123"
        response = success_response(data, trace_id)

        assert isinstance(response, ApiResponse)
        assert response.success is True
        assert response.data == data
        assert response.trace_id == trace_id
        assert response.error is None

    def test_error_response_helper(self):
        """Test error_response helper function."""
        code = "NOT_FOUND"
        message = "Item not found"
        details = {"id": 999}
        trace_id = "trace-456"

        response = error_response(code, message, details, trace_id)

        assert isinstance(response, ApiResponse)
        assert response.success is False
        assert response.data is None
        assert response.trace_id == trace_id
        assert response.error.code == code
        assert response.error.message == message
        assert response.error.details == details

    def test_error_response_helper_no_details(self):
        """Test error_response helper function without details."""
        response = error_response("ERR", "Msg", trace_id="tid")
        assert response.error.details is None
