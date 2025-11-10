"""
Service for fetching and processing YouTube transcripts.

This module provides functionality to extract video IDs from various
YouTube URL formats and fetch transcripts using the youtube-transcript-api.
It handles different URL types (long, short, shorts) and prioritizes
manually created transcripts over auto-generated ones.
"""

import asyncio
import logging
import re

from youtube_transcript_api import YouTubeTranscriptApi, formatters
from youtube_transcript_api import _errors as youtube_transcript_api_errors
from youtube_transcript_api._api import FetchedTranscript

from app.configs.app_config import YOUTUBE_URL_TYPES

logger = logging.getLogger(__name__)


class TranscriptService:
    """
    Service for handling YouTube transcripts.

    This service provides methods to:
    - Identify YouTube URL types (long, short, shorts)
    - Extract video IDs from URLs
    - Fetch transcripts with language preference
    - Format transcripts for processing
    """

    def __init__(self):
        """Initialize the transcript service with YouTube API client."""
        self.ytt_api = YouTubeTranscriptApi()
        self.formatter = formatters.TextFormatter()

    @staticmethod
    def get_url_type(url: str) -> str:
        """
        Determine the type of YouTube URL.

        Checks URL patterns in order of specificity:
        1. Shorts (most specific pattern)
        2. Long URLs (watch?v=)
        3. Short URLs (youtu.be/)

        This order ensures shorts URLs are detected correctly before
        long URLs, which is important because shorts URLs contain
        "youtube.com" which could match the long URL pattern.

        Args:
            url: YouTube URL string

        Returns:
            URL type as string: "shorts", "long", or "short"

        Raises:
            ValueError: If URL doesn't match any known pattern
        """
        # Check in order: shorts (most specific), then long, then short
        # This ensures shorts URLs are detected correctly before long URLs
        for key, value in YOUTUBE_URL_TYPES.items():
            if bool(re.search(value, url, re.IGNORECASE)):
                return str(key)
        raise ValueError("Invalid YouTube URL")

    @staticmethod
    def fetch_video_id(url: str, url_type: str) -> str:
        """
        Extract video ID from YouTube URL.

        Uses regex patterns specific to each URL type to extract
        the video ID. Handles URL fragments and query parameters.

        Args:
            url: YouTube URL string
            url_type: Type of URL ("long", "short", or "shorts")

        Returns:
            Video ID as string

        Raises:
            ValueError: If URL type is unknown or video ID cannot be extracted
        """
        if url_type == "long":
            # Pattern for: youtube.com/watch?v=VIDEO_ID
            match = re.search(r"watch\?v=([\w-]+)", url)
        elif url_type == "short":
            # Pattern for: youtu.be/VIDEO_ID
            # (?=\?|$) ensures we stop at query params or end of string
            match = re.search(r"youtu\.be\/([\w-]+)(?=\?|$)", url)
        elif url_type == "shorts":
            # Pattern for: youtube.com/shorts/VIDEO_ID or www.youtube.com/shorts/VIDEO_ID
            # Handles optional www. and stops at query params, fragments, or end
            match = re.search(r"(?:www\.)?youtube\.com/shorts/([\w-]+)(?=\?|$|#)", url, re.IGNORECASE)
        else:
            raise ValueError("Unknown URL type")

        if match:
            return match.group(1)  # Return the captured video ID
        else:
            raise ValueError("Can't extract video ID from URL")

    async def fetch_transcripts(self, video_id: str) -> tuple[FetchedTranscript, str]:
        """
        Obtain a video transcript with language preference.

        This method fetches transcripts with the following priority:
        1. Manually created transcripts (more accurate)
        2. Auto-generated transcripts (fallback)
        3. English variants are preferred (en, en-US, en-GB, etc.)
        4. Other languages as fallback

        The method runs in a separate thread to avoid blocking the event loop.

        Args:
            video_id: YouTube video ID

        Returns:
            Tuple of (FetchedTranscript object, language code string)

        Raises:
            ValueError: If transcripts are disabled or unavailable
        """
        try:

            def fetch():
                """
                Internal function to fetch transcripts (runs in thread).

                This function is wrapped in asyncio.to_thread to run
                synchronously in a thread pool, preventing blocking of
                the async event loop.
                """
                # Get list of available transcripts for the video
                list_of_transcripts = self.ytt_api.list(video_id=video_id)

                # English language variants to check (in priority order)
                # Standard English is preferred, then regional variants
                english_variants = ["en", "en-US", "en-GB", "en-AU", "en-CA", "en-IN", "en-IE"]

                # Prefer manually created transcripts (more accurate than auto-generated)
                if list_of_transcripts._manually_created_transcripts:
                    # Check for English variants first
                    for lang in english_variants:
                        if lang in list_of_transcripts._manually_created_transcripts:
                            return (self.ytt_api.fetch(video_id=video_id, languages=[lang]), lang)

                    # If no English variant found, use the first available manually created transcript
                    for transcript in list_of_transcripts._manually_created_transcripts:
                        return (self.ytt_api.fetch(video_id=video_id, languages=[str(transcript)]), str(transcript))

                # Fall back to auto-generated transcripts if no manual transcripts available
                if list_of_transcripts._generated_transcripts:
                    # Check for English variants first
                    for lang in english_variants:
                        if lang in list_of_transcripts._generated_transcripts:
                            return (self.ytt_api.fetch(video_id=video_id, languages=[lang]), lang)

                    # If no English variant found, use the first available generated transcript
                    for transcript in list_of_transcripts._generated_transcripts:
                        return (self.ytt_api.fetch(video_id=video_id, languages=[str(transcript)]), str(transcript))

                # No transcripts available for this video
                raise ValueError("No transcripts available for this video")

            # Run the synchronous fetch function in a thread pool
            # This prevents blocking the async event loop
            return await asyncio.to_thread(fetch)

        except youtube_transcript_api_errors.TranscriptsDisabled as err:
            raise ValueError("Transcripts for this video are disabled") from err
        except Exception as err:
            raise ValueError(f"Error fetching transcript: {err}") from err

    def format_transcripts(self, transcript: FetchedTranscript) -> str:
        """Formatting the transcript into text."""
        try:
            return " ".join(line.text for line in transcript)

        except Exception as err:
            raise ValueError("Error while formatting transcript") from err
