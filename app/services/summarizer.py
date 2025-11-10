"""
Service for summarizing transcripts using Gemini AI.

This module provides functionality to summarize and translate text
using Google's Gemini AI API. It handles both summarization and
summarization with translation in a single request.
"""

import asyncio
import logging
from os import getenv

from dotenv import load_dotenv
from google.genai import Client, types

load_dotenv()
api_key = getenv("GEMINI_API_KEY")
logger = logging.getLogger(__name__)


class SummarizerService:
    """
    Service for summarizing text using Gemini API.

    This service provides methods to:
    - Summarize transcripts using Gemini AI
    - Summarize and translate transcripts in one request
    - Handle API errors and empty responses
    """

    @staticmethod
    async def summarize_request(content: str, system_instruction: str) -> str:
        """
        Submit a summarization request to Gemini AI.

        This method sends the transcript content to Gemini AI with
        system instructions for summarization. The response is returned
        as plain text without markdown formatting.

        Args:
            content: Transcript text to summarize
            system_instruction: Instructions for the AI model on how to summarize

        Returns:
            Summarized text as string

        Raises:
            ValueError: If API response is empty or an error occurs

        Note:
            - Uses gemini-2.5-flash model for fast responses
            - Temperature set to 0.2 for more consistent outputs
            - Runs in thread pool to avoid blocking event loop
        """
        try:

            def _generate():
                """
                Internal function to generate content (runs in thread).

                This function is wrapped in asyncio.to_thread to run
                synchronously in a thread pool, preventing blocking of
                the async event loop.
                """
                with Client(api_key=api_key) as client:
                    return client.models.generate_content(
                        model="gemini-2.5-flash",  # Fast and efficient model
                        config=types.GenerateContentConfig(
                            system_instruction=[
                                system_instruction,
                                "Output format: text without markdown formatting",
                            ],
                            temperature=0.2,  # Lower temperature for more consistent outputs
                        ),
                        contents=content,
                    )

            logger.info(
                f"System instructions: {
                    [
                        system_instruction,
                        'Output format: text without markdown formatting',
                    ]
                }"
            )
            # Run the synchronous API call in a thread pool
            # This prevents blocking the async event loop
            response = await asyncio.to_thread(_generate)

            # Validate response
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")

            return response.text

        except Exception as err:
            raise ValueError(f"Error while summarizing transcript: {err}") from err

    @staticmethod
    async def summarize_and_translate_request(
        content: str, system_instruction: str, preferred_translate_language: str
    ) -> str:
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

            logger.info(
                f"System instructions: {
                    [
                        (f'You can use only this language to answer: {preferred_translate_language}'),
                        'Output format: text without markdown formatting',
                        system_instruction,
                    ]
                }"
            )
            response = await asyncio.to_thread(_generate)

            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")

            return response.text

        except Exception as err:
            raise ValueError(f"Error while summarizing transcript: {err}") from err
