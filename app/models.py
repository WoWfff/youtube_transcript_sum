"""Pydantic models for request/response validation."""

from pydantic import BaseModel


class Url(BaseModel):
    """YouTube URL model."""
    name: str


class SummaryResponse(BaseModel):
    """Summary response model."""
    message: str


class UserUrlResponse(BaseModel):
    """User URL response model."""
    user_id: str
    url: str | None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str


class PreferredLanguage(BaseModel):
    """Preferred user translating language response model."""
    language: str
