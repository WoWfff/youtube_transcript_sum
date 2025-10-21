"""Service for getting list of available translating languages and
translating processed YouTube transcripts."""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import formatters
from youtube_transcript_api._errors import IpBlocked


class TranslateService:

    def __init__(self):
        self.ytt_api = YouTubeTranscriptApi()
        self.formatter = formatters.TextFormatter()

    async def get_available_translations(self, video_id: str) -> list:
        try:
            transcript_list = self.ytt_api.list(video_id=video_id)
            languages = [transcript.language_code for transcript in transcript_list]
            return languages
        except Exception as err:
            raise ValueError("Error while getting translations") from err

    async def translate_transcript(self, video_id: str, preferred_language: str):
        try:
            transcript_list = self.ytt_api.list(video_id=video_id)
            for transcript in transcript_list:
                if transcript.language_code == preferred_language:
                    return transcript.fetch()

        except IpBlocked as err:
            raise ValueError("""Could not retrieve a transcript for the video
            https://www.youtube.com/watch?v=o4TdHrMi6do!""") from err

        except Exception as err:
            raise ValueError("Error while translating transcript.") from err
