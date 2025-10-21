"""Main application entry point."""

import logging
from fastapi import FastAPI

from app.routers import youtube
from app.middleware.user_tracking import add_user_id


# Logger settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="YouTube Transcript Summarizer",
    description="API for summarizing YouTube video transcripts using Gemini AI",
    version="1.0.0"
)

# Add middleware
app.middleware("http")(add_user_id)

# Include routers
app.include_router(youtube.router, tags=["YouTube"])


# Optional: Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "YouTube Transcript Summarizer API",
        "docs": "/docs",
        "health": "/health"
    }
