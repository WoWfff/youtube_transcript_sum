import re
from os import chdir

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import formatters
from youtube_transcript_api import _errors as youtube_transcript_api_errors
from youtube_transcript_api._api import FetchedTranscript

from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse

import json

import fastapi
import uvicorn

# To remove
url = test_url = "https://www.youtube.com/watch?v=NTc9wE191jo"
chdir("/home/user/Python/Own/youtube_transcript_sum")

youtube_url_types: dict[str, str] = {
    "long": r"youtube\.com/\w",
    "short": r"youtu\.be/\w"
    }

ytt_api = YouTubeTranscriptApi()
formatter = formatters.TextFormatter()
Client = genai.Client()


def get_url_type(url) -> str:
    for key, value in youtube_url_types.items():
        if bool(re.search(value, url, re.IGNORECASE)):
            return str(key)
    else:
        raise ValueError("Invalid url")


def fetch_video_id(url: str, url_type: str) -> str:
    if url_type == "long":
        match = re.search(r"watch\?v=([\w-]+)", url)
    elif url_type == "short":
        match = re.search(r"youtu\.be\/([\w-]+)(?=\?|$)", url)
    else:
        raise ValueError("Can't find URL type")

    if match:
        return match.group(1)
    else:
        raise ValueError("Can't extract video ID")


def fetch_transcripts(video_id) -> FetchedTranscript:
    try:
        return ytt_api.fetch(video_id=video_id, languages=["en"])

    except youtube_transcript_api_errors.TranscriptsDisabled as err:
        raise ValueError("Transcripts for this video are disabled.") from err


def format_transcripts(transcript) -> str:
    return formatter.format_transcript(transcript)


def save_data_to_file(filename, data) -> None:
    with open(filename, "w") as file:
        file.write(data)


def get_system_instructions() -> str:
    try:
        with open("config.json", "r") as file:
            json_file = json.load(file)
        return json_file.get("system_instructions", None)
    except Exception as err:
        raise ValueError("Error while reading config file...") from err


def sumarize_request(content, system_instruction) -> GenerateContentResponse:
    try:
        with Client as client:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=[
                        system_instruction,
                        "Output format: text without markdown formating"
                    ],
                    temperature=0.2,
                    ),
                contents=content,
            )
            return response
    except Exception as err:
        raise ValueError("Error while sumarizing transcript!") from err


def main() -> None:
    url_type = get_url_type(url)
    video_id = fetch_video_id(url=url, url_type=url_type)
    transcript = fetch_transcripts(video_id=video_id)
    formatted_transcript = format_transcripts(transcript=transcript)
    sumarized_data = sumarize_request(
        content=formatted_transcript,
        system_instruction=get_system_instructions())
    save_data_to_file(filename="transcript.txt", data=formatted_transcript)
    save_data_to_file(filename="summarized_transcript.txt", data=sumarized_data.text)


if __name__ == "__main__":
    main()
