"""Service for summarizing transcripts using Gemini."""

import asyncio
from google.genai import types, Client


class SummarizerService:
    """Service for summarizing text using Gemini API."""

    @staticmethod
    async def summarize_request(content: str, system_instruction: str) -> str:
        """Submitting a summarization request to Gemini."""
        try:
            def _generate():
                with Client() as client:
                    return client.models.generate_content(
                        model="gemini-2.5-flash-lite",
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
