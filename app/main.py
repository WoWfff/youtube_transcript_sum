"""
Main application entry point.

This module initializes the FastAPI application, configures middleware,
mounts static files, and includes all API routers.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.middleware.user_tracking import add_user_id
from app.routers import auth, summarizes, youtube

# Configure logging for the application
# Set to INFO level to capture important application events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with metadata
# This metadata is used in the auto-generated API documentation
app = FastAPI(
    title="YouTube Transcript Summarizer",
    description="API for summarizing YouTube video transcripts using Gemini AI",
    version="1.0.0"
)

# Add custom middleware for user tracking
# This middleware adds user identification to requests (legacy support)
app.middleware("http")(add_user_id)

# Configure static file serving
# Static files (HTML, CSS, JS) are served from the /static directory
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)  # Create directory if it doesn't exist
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Register API routers
# Each router handles a specific set of endpoints
app.include_router(auth.router, tags=["Authentication"])  # User authentication endpoints
app.include_router(youtube.router, tags=["YouTube"])  # YouTube video processing endpoints
app.include_router(summarizes.router, tags=["Summarizes"])  # User history endpoints


# Root endpoint - serve the main page
@app.get("/")
async def root():
    """
    Serve the main HTML page.

    Returns the index.html file if it exists, otherwise returns
    a JSON response with API information.
    """
    html_file = static_path / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {
        "message": "YouTube Transcript Summarizer API",
        "docs": "/docs",
        "health": "/health"
    }


# History page endpoint - serves HTML page only
@app.get("/summarizes/")
async def history_page():
    """
    Serve the history HTML page.

    This endpoint serves the history.html file for displaying
    user's video summarization history. Note: The API endpoint
    for JSON data is /summarizes/api (handled by summarizes router).
    """
    html_file = static_path / "history.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"error": "History page not found"}
