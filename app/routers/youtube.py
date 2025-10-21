"""Router for YouTube-related endpoints."""

import logging
from typing import Annotated
from fastapi import APIRouter, Request, HTTPException, Depends, Response

from app.models import Url, SummaryResponse, UserUrlResponse, HealthResponse, PreferredLanguage
from app.dependencies import get_user_id, get_user_url_storage
from app.config import get_system_instructions
from app.services.transcript import TranscriptService
from app.services.summarizer import SummarizerService
from app.services.translating import TranslateService

# Logger settings
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
transcript_service = TranscriptService()
summarizer_service = SummarizerService()
translate_service = TranslateService()


@router.post("/url/", response_model=SummaryResponse)
async def process_url(
    request: Request,
    url: Url,
    user_id: Annotated[str, Depends(get_user_id)],
    user_urls: Annotated[dict, Depends(get_user_url_storage)],
):
    """Process the video URL and return the summarization."""
    try:
        # Saving the user's URL
        user_urls[user_id] = url.name

        # Determine the URL type
        url_type = transcript_service.get_url_type(url.name)
        logger.info(f"URL type detected: {url_type}")

        # Extracting video ID
        video_id = transcript_service.fetch_video_id(url=url.name, url_type=url_type)
        logger.info(f"Video ID extracted: {video_id}")

        # We receive a transcript
        transcript = await transcript_service.fetch_transcripts(video_id=video_id)
        logger.info("Transcript fetched successfully")

        # Format the transcript
        formatted_transcript = transcript_service.format_transcripts(transcript=transcript)
        logger.info(f"Transcript formatted, length: {len(formatted_transcript)}")

        # Receiving system instructions
        system_instruction = get_system_instructions()

        # Summarize
        summary = await summarizer_service.summarize_request(
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


@router.post("/url/translations")
async def translations(
    request: Request,
    url: Url
    ):
    """Process the video URL and returns all available translations."""
    # Determine the URL type
    url_type = transcript_service.get_url_type(url.name)
    logger.info(f"URL type detected: {url_type}")

    # Extract video ID
    video_id = transcript_service.fetch_video_id(url=url.name, url_type=url_type)
    logger.info(f"Video ID extracted: {video_id}")

    # Get list of available translating languages
    translating_languages = await translate_service.get_available_translations(video_id=video_id)
    logger.info("Translations fetched successfully")

    return {"translations": translating_languages}


@router.post("/url/translate")
async def translate(
    request: Request,
    url: Url,
    preferred_translate_language: PreferredLanguage
    ):
    """Process the video URL and returns all available translations."""
    # Determine the URL type
    url_type = transcript_service.get_url_type(url.name)
    logger.info(f"URL type detected: {url_type}")

    # Extract video ID
    video_id = transcript_service.fetch_video_id(url=url.name, url_type=url_type)
    logger.info(f"Video ID extracted: {video_id}")

    # Translate transcript
    translatted_transcript = await translate_service.translate_transcript(
        video_id=video_id,
        preferred_language=preferred_translate_language.language)

    # Format the transcript
    formatted_translatted_transcript = transcript_service.format_transcripts(
        transcript=translatted_transcript
        )
    logger.info(f"Transcript formatted, length: {len(formatted_translatted_transcript)}")

    return Response(content=formatted_translatted_transcript, media_type="text/plain")


@router.get("/my_url/", response_model=UserUrlResponse)
async def my_url(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
    user_urls: Annotated[dict, Depends(get_user_url_storage)],
):
    """Returns the user's saved URL."""
    url = user_urls.get(user_id)
    return {"user_id": user_id, "url": url or None}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Checking the service's functionality."""
    return {"status": "ok"}
