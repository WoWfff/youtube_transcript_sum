"""Service for fetching and processing YouTube transcripts."""

import re
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import formatters
from youtube_transcript_api import _errors as youtube_transcript_api_errors
from youtube_transcript_api._api import FetchedTranscript

from app.app_config import YOUTUBE_URL_TYPES


class TranscriptService:
    """Service for handling YouTube transcripts."""

    def __init__(self):
        self.ytt_api = YouTubeTranscriptApi()
        self.formatter = formatters.TextFormatter()

    @staticmethod
    def get_url_type(url: str) -> str:
        """Determining the type of YouTube URL."""
        for key, value in YOUTUBE_URL_TYPES.items():
            if bool(re.search(value, url, re.IGNORECASE)):
                return str(key)
        raise ValueError("Invalid YouTube URL")

    @staticmethod
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

    async def fetch_transcripts(self, video_id: str) -> FetchedTranscript:
        """Obtaining a video transcript."""
        try:

            def fetch():
                list_of_transcripts = self.ytt_api.list(video_id=video_id)
                if list_of_transcripts._manually_created_transcripts:
                    for transcript in list_of_transcripts._manually_created_transcripts:
                        return self.ytt_api.fetch(video_id=video_id, languages=[str(transcript)])

                elif list_of_transcripts._generated_transcripts:
                    for transcript in list_of_transcripts._generated_transcripts:
                        return self.ytt_api.fetch(video_id=video_id, languages=[str(transcript)])

            return await asyncio.to_thread(fetch)

        except youtube_transcript_api_errors.TranscriptsDisabled as err:
            raise ValueError("Transcripts for this video are disabled") from err
        except Exception as err:
            raise ValueError(f"Error fetching transcript: {str(err)}") from err

    def format_transcripts(self, transcript: FetchedTranscript) -> str:
        """Formatting the transcript into text."""
        try:
            return " ".join(line.text for line in transcript)
            # return self.formatter.format_transcript(transcript)

        except Exception as err:
            raise ValueError("Error while formatting transcript") from err
