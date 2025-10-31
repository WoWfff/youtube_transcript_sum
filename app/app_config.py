"""Application configuration."""

import json
from pathlib import Path
from functools import lru_cache
from enum import Enum

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

YOUTUBE_URL_TYPES: dict[str, str] = {"long": r"youtube\.com/\w", "short": r"youtu\.be/\w"}


class Modes(Enum):
    TRANSLATING = "translating"
    SUMMARIZING = "summarizing"


@lru_cache
def get_system_instructions(mode: str) -> str:
    """Reading system instructions from the config."""
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
        raise ValueError(f"Error reading config file: {str(err)}") from err
