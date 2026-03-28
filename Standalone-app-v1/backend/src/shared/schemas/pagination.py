"""
Pagination schemas for cursor-based pagination.

Used by repositories to implement efficient pagination without OFFSET.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Pagination(BaseModel):
    """
    Cursor-based pagination parameters.

    Attributes:
        limit: Maximum number of results to return (default: 20, max: 100)
        cursor: Cursor for next page (opaque string from previous response)
    """

    limit: int = Field(default=20, ge=1, le=100, description="Results per page")
    cursor: str | None = Field(default=None, description="Cursor for next page")

    class Config:
        json_schema_extra = {
            "example": {
                "limit": 20,
                "cursor": "eyJpZCI6IjEyMzQ1Njc4LTEyMzQtMTIzNC0xMjM0LTEyMzQ1Njc4OTBhYiJ9"
            }
        }


class PageInfo(BaseModel):
    """
    Pagination metadata for cursor-based pagination.

    Attributes:
        has_next_page: Whether there are more results available
        has_previous_page: Whether there is a previous page
        next_cursor: Cursor for the next page (None if no more results)
        previous_cursor: Cursor for the previous page (None if first page)
        total_count: Total number of results (optional, expensive to compute)
    """

    has_next_page: bool = Field(description="More results available")
    has_previous_page: bool = Field(default=False, description="Previous page exists")
    next_cursor: str | None = Field(default=None, description="Next page cursor")
    previous_cursor: str | None = Field(default=None, description="Previous page cursor")
    total_count: int | None = Field(default=None, description="Total result count")


class PaginatedResult(BaseModel, Generic[T]):
    """
    Generic paginated result container.

    Type Parameters:
        T: Type of items in the result

    Attributes:
        items: List of result items
        page_info: Pagination metadata
    """

    items: list[T] = Field(description="Result items")
    page_info: PageInfo = Field(description="Pagination info")

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "items": [{"id": "123...", "name": "Example"}],
                "page_info": {
                    "has_next_page": True,
                    "has_previous_page": False,
                    "next_cursor": "eyJpZCI6IjEyMy4uLiJ9",
                    "previous_cursor": None,
                    "total_count": 42
                }
            }
        }
