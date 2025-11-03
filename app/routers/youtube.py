"""Router for YouTube-related endpoints."""

import logging
from typing import Annotated
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from youtube_transcript_api._errors import CouldNotRetrieveTranscript

from app.models.pydantic_models import Url, SummaryResponse, UserUrlResponse, HealthResponse, TranslateRequest  # noqa: E501
from app.dependencies import get_user_id
from app.configs.app_config import get_system_instructions, Modes
from app.services.transcript import TranscriptService
from app.services.summarizer import SummarizerService
from app.models.db_models import UserBase, UrlBase, SumBase
from app.database.methods import engine, Select, Insert, Update
from app.services.sum_methods import File


# Logger settings
logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
transcript_service = TranscriptService()
summarizer_service = SummarizerService()


@router.post("/url/")
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
        url_instance = Insert(model=UrlBase, engine=engine).one(owner_id=db_user.id, url=url.name)

        # Determine the URL type
        url_type = transcript_service.get_url_type(url.name)
        logger.info(f"URL type detected: {url_type}")

        # Extracting video ID
        video_id = transcript_service.fetch_video_id(url=url.name, url_type=url_type)
        logger.info(f"Video ID extracted: {video_id}")

        # Updating video_shortcode in database
        Update(model=UrlBase, engine=engine).by_id(url_instance.id, url_shortcode=video_id)

        # We receive a transcript
        transcript, language_code = await transcript_service.fetch_transcripts(video_id=video_id)
        logger.info("Transcript fetched successfully")

        # Updating status of transcript_accessibility in database
        Update(model=UrlBase, engine=engine).by_id(url_instance.id, transcript_accessibility=True)

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

        # Writing summarization to file
        path_to_sum_file = File(file_name=video_id, text=summary).save()
        logger.info("Summary writed into file successfully")

        # Adding summarization into database
        Insert(model=SumBase, engine=engine).one(
            user_owner_id=db_user.id,
            url_owner_id=url_instance.id,
            url_shortcode=video_id,
            path_to_sum_file=str(path_to_sum_file),
            language_code=language_code
            )
        logger.info("Summary writed into db successfully")

        return PlainTextResponse(summary)

    except ValueError as err:
        if str(err) == "Transcripts for this video are disabled":
            # Updating status of transcript_accessibility in database
            Update(model=UrlBase, engine=engine).by_id(url_instance.id,
            transcript_accessibility=False)
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
async def summarize_and_translate(
    user_id: Annotated[str, Depends(get_user_id)],
    translate_request: TranslateRequest,
    ):
    """Process the video URL and translate the transcript."""
    try:
        # Saving the user's URL
        db_user = Select(model=UserBase, engine=engine).by_filter(cookies=user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        url_instance = Insert(model=UrlBase, engine=engine).one(owner_id=db_user.id, url=translate_request.name)

        # Determine the URL type
        url_type = transcript_service.get_url_type(translate_request.name)
        logger.info(f"URL type detected: {url_type}")

        # Extracting video ID
        video_id = transcript_service.fetch_video_id(url=translate_request.name, url_type=url_type)
        logger.info(f"Video ID extracted: {video_id}")

        # Updating video_shortcode in database
        Update(model=UrlBase, engine=engine).by_id(url_instance.id, url_shortcode=video_id)

        # We receive a transcript
        transcript, language_code = await transcript_service.fetch_transcripts(video_id=video_id)
        logger.info("Transcript fetched successfully")

        # Updating status of transcript_accessibility in database
        Update(model=UrlBase, engine=engine).by_id(url_instance.id, transcript_accessibility=True)

        # Format the transcript
        formatted_transcript = transcript_service.format_transcripts(transcript=transcript)
        logger.info(f"Transcript formatted, length: {len(formatted_transcript)}")

        # Receiving system instructions for summarizing and translating
        system_instruction = get_system_instructions(Modes.SUMMARIZING_AND_TRANSLATING.value)

        # Translating transcript
        summary = await summarizer_service.summarize_and_translate_request(
            content=formatted_transcript,
            system_instruction=system_instruction,
            preferred_translate_language=translate_request.language
        )
        logger.info("Transcript summarized and translated successfully.")

        # Writing summarization to file
        path_to_sum_file = File(file_name=video_id, text=summary).save()
        logger.info("Summary writed into file successfully")

        # Adding summarization into database
        Insert(model=SumBase, engine=engine).one(
            user_owner_id=db_user.id,
            url_owner_id=url_instance.id,
            url_shortcode=video_id,
            path_to_sum_file=str(path_to_sum_file),
            language_code=language_code
            )
        logger.info("Summary writed into db successfully")

        return PlainTextResponse(summary)

    except ValueError as err:
        if str(err) == "Transcripts for this video are disabled":
            # Updating status of transcript_accessibility in database
            Update(model=UrlBase, engine=engine).by_id(url_instance.id,
            transcript_accessibility=False)
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

    return {
    "user_id": cookies_user_id,
    "url": url.url if url else None
    }


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
