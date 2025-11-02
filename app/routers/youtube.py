"""Router for YouTube-related endpoints."""

import logging
from typing import Annotated
from fastapi import APIRouter, Request, HTTPException, Depends, Response
from pydantic import BaseModel
from youtube_transcript_api._errors import CouldNotRetrieveTranscript

from app.models import Url, SummaryResponse, UserUrlResponse, HealthResponse
from app.dependencies import get_user_id, get_user_url_storage
from app.app_config import get_system_instructions, Modes
from app.services.transcript import TranscriptService
from app.services.summarizer import SummarizerService
from app.services.translating import TranslateService
from app.db_models import UserBase, UrlBase
from app.database.methods import engine, Select, Insert

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
    url: Url,
    user_id: Annotated[str, Depends(get_user_id)],
):
    """Process the video URL and return the summarization."""
    try:
        # Saving the user's URL
        db_user = Select(model=UserBase, engine=engine).by_filter(cookies=user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        Insert(model=UrlBase, engine=engine).one(owner_id=db_user.id, url=url.name)

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

    except CouldNotRetrieveTranscript as err:
        logger.error(f"Could not retrieve a transcript for the video: {str(err)}")
        raise HTTPException(
            status_code=400,
            detail="Could not retrieve a transcript for the video.") from err

    except Exception as err:
        logger.error(f"Unexpected error: {str(err)}")
        raise HTTPException(status_code=500, detail="Internal server error") from err


@router.post("/url/translate")
async def translate(
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
    cookies_user_id: Annotated[str, Depends(get_user_id)]
    ):
    """Returns the user's last saved URL."""
    db_user = Select(model=UserBase, engine=engine).by_filter(cookies=cookies_user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    url = Select(model=UrlBase, engine=engine).by_filter(owner_id=db_user.id)

    if url:
        return {"user_id": cookies_user_id, "url": url.url}
    else:
        return None


@router.get("/my_urls/", response_model=UserUrlResponse)
async def my_urls(
    request: Request,
    cookies_user_id: Annotated[str, Depends(get_user_id)],
):
    """Returns the user's saved URL."""
    db_user = Select(model=UserBase, engine=engine).by_filter(cookies=cookies_user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    urls = Select(model=UrlBase, engine=engine).by_filter(many=True, owner_id=db_user.id)

    return {
        "user_id": cookies_user_id,
        "url": [u.url for u in urls] if urls else [],
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Checking the service's functionality."""
    return {"status": "ok"}
