"""
Authentication module for Telegram API.
"""

from pathlib import Path
from typing import Any

from telethon import TelegramClient

DEFAULT_SESSION_NAME = "telegram_getter_session"


async def create_client(
    api_id: str,
    api_hash: str,
    session_name: str = DEFAULT_SESSION_NAME,
    session_path: Path | None = None,
) -> TelegramClient:
    """
    Create and return a TelegramClient instance.

    Args:
        api_id: Telegram API ID
        api_hash: Telegram API Hash
        session_name: Name for the session file
        session_path: Optional path for session storage

    Returns:
        Configured TelegramClient instance
    """
    session_file = session_path / session_name if session_path else Path.cwd() / session_name
    return TelegramClient(str(session_file), int(api_id), api_hash)


async def authenticate(client: TelegramClient) -> bool:
    """
    Authenticate the client with Telegram.

    Args:
        client: TelegramClient instance to authenticate

    Returns:
        True if authentication successful, False otherwise
    """
    await client.start()
    return await client.is_user_authorized()


async def get_me(client: TelegramClient) -> Any:
    """
    Get information about the authenticated user.

    Args:
        client: Authenticated TelegramClient instance

    Returns:
        User object with information about current user
    """
    return await client.get_me()
