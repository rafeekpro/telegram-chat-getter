"""
Utility functions for telegram_getter.
"""

import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def load_config() -> dict[str, Any]:
    """
    Load configuration from environment variables and .env file.

    Returns:
        dict with configuration values (api_id, api_hash, etc.)
    """
    # Load .env file if it exists
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    return {
        "api_id": os.getenv("API_ID"),
        "api_hash": os.getenv("API_HASH"),
    }


def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filename to make it safe for filesystem.

    Args:
        filename: Original filename that may contain invalid characters

    Returns:
        Sanitized filename safe for use on most filesystems
    """
    if not filename:
        return "unnamed"

    # Remove or replace invalid characters
    # Invalid on Windows: < > : " / \ | ? *
    # Invalid on Unix: / and null
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, "_", filename)

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(". ")

    # Ensure we have something left
    if not sanitized:
        return "unnamed"

    return sanitized


def format_size(size_bytes: int) -> str:
    """
    Format a size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"

    return f"{size:.1f} {units[unit_index]}"
