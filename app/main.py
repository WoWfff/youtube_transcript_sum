"""Main application entry point."""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(youtube.router, tags=["YouTube"])


# Root endpoint - serve the main page
@app.get("/")
async def root():
    """Serve the main HTML page."""
    html_file = static_path / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {
        "message": "YouTube Transcript Summarizer API",
        "docs": "/docs",
        "health": "/health"
    }
