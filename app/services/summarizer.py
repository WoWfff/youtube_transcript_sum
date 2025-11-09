"""Service for summarizing transcripts using Gemini."""

import asyncio
import logging
from os import getenv

from dotenv import load_dotenv
from google.genai import Client, types

load_dotenv()
api_key = getenv("GEMINI_API_KEY")
logger = logging.getLogger(__name__)


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

            logger.info(f"System instructions: {[
                                system_instruction,
                                "Output format: text without markdown formatting",
                            ]}")
            response = await asyncio.to_thread(_generate)

            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")

            return response.text

        except Exception as err:
            raise ValueError(f"Error while summarizing transcript: {err}") from err

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
                        model="gemini-2.5-flash",
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
            logger.info(f"System instructions: {[
                                (f"You can use only this language to answer: {preferred_translate_language}"),
                                "Output format: text without markdown formatting",
                                system_instruction,
                            ]}")
            response = await asyncio.to_thread(_generate)

            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")

            return response.text

        except Exception as err:
            raise ValueError(f"Error while summarizing transcript: {err}") from err
