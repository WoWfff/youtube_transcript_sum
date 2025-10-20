import re
import asyncio
import uuid
import logging
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import formatters
from youtube_transcript_api import _errors as youtube_transcript_api_errors
from youtube_transcript_api._api import FetchedTranscript

from google.genai import types, Client

import json

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

# Logger settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "config.json"

youtube_url_types: dict[str, str] = {"long": r"youtube\.com/\w", "short": r"youtu\.be/\w"}

ytt_api = YouTubeTranscriptApi()
formatter = formatters.TextFormatter()
app = FastAPI()
user_urls: dict[str, str] = {}


class Url(BaseModel):
    name: str


def get_url_type(url: str) -> str:
    """Determining the type of YouTube URL."""
    for key, value in youtube_url_types.items():
        if bool(re.search(value, url, re.IGNORECASE)):
            return str(key)
    raise ValueError("Invalid YouTube URL")


def fetch_video_id(url: str, url_type: str) -> str:
    """Extract video ID from URL."""
    if url_type == "long":
        match = re.search(r"watch\?v=([\w-]+)", url)
    elif url_type == "short":
        match = re.search(r"youtu\.be\/([\w-]+)(?=\?|$)", url)
    else:
        raise ValueError("Unknown URL type")

    if match:
        return match.group(1)
    else:
        raise ValueError("Can't extract video ID from URL")


async def fetch_transcripts(video_id: str) -> FetchedTranscript:
    """Obtaining a video transcript."""
    try:

        def fetch():
            return ytt_api.fetch(video_id=video_id, languages=["en"])

        return await asyncio.to_thread(fetch)

    except youtube_transcript_api_errors.CouldNotRetrieveTranscript:
        transcript_list = ytt_api.list(video_id=video_id)
        for transcript in transcript_list:
            data = transcript.translate('en').fetch()
        return data

    except youtube_transcript_api_errors.TranscriptsDisabled as err:
        raise ValueError("Transcripts for this video are disabled") from err
    except Exception as err:
        raise ValueError(f"Error fetching transcript: {str(err)}") from err


def format_transcripts(transcript: FetchedTranscript) -> str:
    """Formatting the transcript into text."""
    try:
        return formatter.format_transcript(transcript)
    except Exception as err:
        raise ValueError("Error while formatting transcript") from err


def get_system_instructions() -> str:
    """Reading system instructions from the config."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            json_file = json.load(file)

        instructions = json_file.get("system_instructions")
        if not instructions:
            raise ValueError("system_instructions not found in config")

        return instructions

    except FileNotFoundError as err:
        raise ValueError(f"Config file not found at {CONFIG_PATH}") from err
    except json.JSONDecodeError as err:
        raise ValueError("Invalid JSON in config file") from err
    except Exception as err:
        raise ValueError(f"Error reading config file: {str(err)}") from err


async def summarize_request(content: str, system_instruction: str) -> str:
    """Submitting a summarization request to Gemini."""
    try:

        def _generate():
            with Client() as client:
                return client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    config=types.GenerateContentConfig(
                        system_instruction=[
                            system_instruction,
                            "Output format: text without markdown formatting",
                        ],
                        temperature=0.2,
                    ),
                    contents=content,
                )

        response = await asyncio.to_thread(_generate)

        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")

        return response.text

    except Exception as err:
        raise ValueError(f"Error while summarizing transcript: {str(err)}") from err


@app.middleware("http")
async def add_user_id(request: Request, call_next):
    """Middleware for managing user_id via cookies."""
    user_id = request.cookies.get("user_id")

    if not user_id:
        user_id = str(uuid.uuid4())
        request.state.user_id = user_id

    response = await call_next(request)

    if not request.cookies.get("user_id"):
        response.set_cookie(
            key="user_id",
            value=user_id,
            httponly=True,
            max_age=31536000,  # 1 year
        )

    return response


@app.post("/url/")
async def get_url(request: Request, url: Url):
    """Process the video URL and return the summarization."""
    user_id = request.cookies.get("user_id") or getattr(request.state, "user_id", None)

    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID not found")

    try:
        # Saving the user's URL
        user_urls[user_id] = url.name

        # Determine the URL type
        url_type = get_url_type(url.name)
        logger.info(f"URL type detected: {url_type}")

        # Extracting video ID
        video_id = fetch_video_id(url=url.name, url_type=url_type)
        logger.info(f"Video ID extracted: {video_id}")

        # We receive a transcript
        transcript = await fetch_transcripts(video_id=video_id)
        logger.info("Transcript fetched successfully")

        # Format the transcript
        formatted_transcript = format_transcripts(transcript=transcript)
        logger.info(f"Transcript formatted, length: {len(formatted_transcript)}")

        # Receiving system instructions
        system_instruction = get_system_instructions()

        # Summarize
        summary = await summarize_request(
            content=formatted_transcript, system_instruction=system_instruction
        )
        logger.info("Summary generated successfully")

        return {"message": summary}

    except ValueError as err:
        logger.error(f"Validation error: {str(err)}")
        raise HTTPException(status_code=400, detail=str(err)) from err

    except Exception as err:
        logger.error(f"Unexpected error: {str(err)}")
        raise HTTPException(status_code=500, detail="Internal server error") from err


@app.get("/my_url/")
async def my_url(request: Request):
    """Returns the user's saved URL."""
    user_id = request.cookies.get("user_id") or getattr(request.state, "user_id", None)

    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID not found")

    url = user_urls.get(user_id)

    return {"user_id": user_id, "url": url or None}


@app.get("/health")
async def health_check():
    """Checking the service's functionality."""
    return {"status": "ok"}
