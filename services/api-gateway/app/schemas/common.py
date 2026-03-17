"""Shared response schemas."""
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str
    detail: str | None = None


class StatsResponse(BaseModel):
    total_systems: int
    by_eu_tier: dict[str, int]
    by_us_designation: dict[str, int]
    by_status: dict[str, int]
    by_sector: dict[str, int]
    pending_approvals: int
