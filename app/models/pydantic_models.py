"""Pydantic models for request/response validation."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class UrlData(BaseModel):
    """UrlData model."""
    created_at: datetime
    url: str
    thumbnail_url: str | None = None
    transcipt: str | None = None


class SummarizesResponse(BaseModel):
    """All user summarizes response model."""
    cookies_user_id: str
    user_urls: dict[int, UrlData]


class PureState(BaseModel):
    """State for pure request."""
    state: bool = False


class SumRequest(BaseModel):
    """YouTube URL model."""
    name: str
    pure_state: PureState


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


class FileResponse(BaseModel):
    text: str


class SumAndTranslateRequest(BaseModel):
    """Combined request model for translation."""
    name: str
    language: str
    pure_state: PureState
