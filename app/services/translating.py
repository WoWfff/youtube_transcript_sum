"""Service for getting list of available translating languages and
translating processed YouTube transcripts."""

import asyncio
from google.genai import types, Client


class TranslateService:

    @staticmethod
    async def translate_text(
    content: str,
    system_instruction: str,
    preferred_translate_language: str | None = None) -> str:
        """Translating trascript with Gemini."""
        try:
            def _generate():
                with Client() as client:
                    return client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        config=types.GenerateContentConfig(
                            system_instruction=[
                                system_instruction,
                                "Output format: text without markdown formatting",
                                (f"preferred language: {preferred_translate_language}"
                                if preferred_translate_language else None),
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
