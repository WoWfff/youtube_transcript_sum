"""Application configuration."""

import json
from enum import Enum
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

YOUTUBE_URL_TYPES: dict[str, str] = {"long": r"youtube\.com/\w", "short": r"youtu\.be/\w"}

YOUTUBE_THUMBNAIL_URL = "https://img.youtube.com/vi/{}/maxresdefault.jpg"  # use .format(video_id) to enter video_id in variable  # noqa: E501


class Modes(Enum):
    SUMMARIZING = "summarizing"


@lru_cache
def get_system_instructions(mode: str) -> str:
    """Getting system instructions from config file."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            json_file = json.load(file)

        instructions = json_file.get("system_instructions")
        mode_instructions = instructions.get(mode)
        if not instructions:
            raise ValueError("system_instructions not found in config")

        return mode_instructions

    except FileNotFoundError as err:
        raise ValueError(f"Config file not found at {CONFIG_PATH}") from err
    except json.JSONDecodeError as err:
        raise ValueError("Invalid JSON in config file") from err
    except Exception as err:
        raise ValueError(f"Error reading config file: {err}") from err

@lru_cache
def get_language_name(language_code: str) -> str:
    """Getting language name from config file."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            json_file = json.load(file)

        instructions = json_file.get("languages")
        language_name = instructions.get(language_code)
        if not instructions:
            raise ValueError("system_instructions not found in config")

        return language_name

    except FileNotFoundError as err:
        raise ValueError(f"Config file not found at {CONFIG_PATH}") from err
    except json.JSONDecodeError as err:
        raise ValueError("Invalid JSON in config file") from err
    except Exception as err:
        raise ValueError(f"Error reading config file: {err}") from err
