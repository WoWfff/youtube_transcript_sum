"""Router for YouTube-related endpoints."""

import logging
from typing import Annotated
from fastapi import APIRouter, Request, HTTPException, Depends, Response
from pydantic import BaseModel

from app.models import Url, SummaryResponse, UserUrlResponse, HealthResponse
from app.dependencies import get_user_id, get_user_url_storage
from app.config import get_system_instructions, Modes
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


# Combined model for translate endpoint
class TranslateRequest(BaseModel):
    """Combined request model for translation."""
    name: str
    language: str


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
        system_instruction = get_system_instructions(Modes.SUMMARIZING.value)

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


@router.post("/url/translate")
async def translate(
    request: Request,
    translate_request: TranslateRequest,
    user_id: Annotated[str, Depends(get_user_id)],
    user_urls: Annotated[dict, Depends(get_user_url_storage)],
    ):
    """Process the video URL and translate the transcript."""
    try:
        # Saving the user's URL
        user_urls[user_id] = translate_request.name

        # Determine the URL type
        url_type = transcript_service.get_url_type(translate_request.name)
        logger.info(f"URL type detected: {url_type}")

        # Extract video ID
        video_id = transcript_service.fetch_video_id(url=translate_request.name, url_type=url_type)
        logger.info(f"Video ID extracted: {video_id}")

        # We receive a transcript
        transcript = await transcript_service.fetch_transcripts(video_id=video_id)
        logger.info("Transcript fetched successfully")

        # Format the transcript
        formatted_transcript = transcript_service.format_transcripts(transcript=transcript)
        logger.info(f"Transcript formatted, length: {len(formatted_transcript)}")

        # Receiving system instructions for summarizing
        system_instruction = get_system_instructions(Modes.SUMMARIZING.value)

        # Summarize
        summary = await summarizer_service.summarize_request(
            content=formatted_transcript, system_instruction=system_instruction
        )
        logger.info("Summary generated successfully")

        # Receiving system instructions for translating
        system_instruction = get_system_instructions(Modes.TRANSLATING.value)

        # Translating transcript
        translated_transcript = await translate_service.translate_text(
            content=summary,
            system_instruction=system_instruction,
            preferred_translate_language=translate_request.language
        )
        logger.info("Transcript translated successfully.")

        return Response(content=translated_transcript, media_type="text/plain")

    except ValueError as err:
        logger.error(f"Validation error: {str(err)}")
        raise HTTPException(status_code=400, detail=str(err)) from err

    except Exception as err:
        logger.error(f"Unexpected error: {str(err)}")
        raise HTTPException(status_code=500, detail="Internal server error") from err


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