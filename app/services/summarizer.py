"""Service for summarizing transcripts using Gemini."""

import asyncio
from google.genai import types, Client

from dotenv import load_dotenv
from os import getenv

load_dotenv()
api_key = getenv("GEMINI_API_KEY")


class SummarizerService:
    """Service for summarizing text using Gemini API."""

    @staticmethod
    async def summarize_request(content: str, system_instruction: str) -> str:
        """Submitting a summarization request to Gemini."""
        try:
            def _generate():
                with Client(api_key=api_key) as client:
                    return client.models.generate_content(
                        model="gemini-2.5-flash",
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

    @staticmethod
    async def summarize_and_translate_request(
    content: str,
    system_instruction: str,
    preferred_translate_language: str) -> str:
        """Summarize and translate trascript with Gemini."""
        try:
            def _generate():
                with Client() as client:
                    return client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        config=types.GenerateContentConfig(
                            system_instruction=[
                                (f"You can use only this language to answer: {preferred_translate_language}"),
                                "Output format: text without markdown formatting",
                                system_instruction,
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
