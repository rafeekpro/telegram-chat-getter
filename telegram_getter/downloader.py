"""
Message and media downloader for Telegram chats.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from telethon import TelegramClient
from telethon.tl.types import Message


@dataclass
class DownloadProgress:
    """Progress information for downloads."""

    current: int
    total: int
    filename: str


@dataclass
class ChatMessage:
    """Represents a downloaded chat message."""

    id: int
    date: datetime
    sender_id: int | None
    sender_name: str
    text: str
    media_path: Path | None = None


async def get_chat_messages(
    client: TelegramClient,
    chat_id: int | str,
    limit: int | None = None,
    offset_date: datetime | None = None,
) -> AsyncIterator[Message]:
    """
    Iterate over messages in a chat.

    Args:
        client: Authenticated TelegramClient
        chat_id: Chat ID or username
        limit: Maximum number of messages to fetch
        offset_date: Only fetch messages before this date

    Yields:
        Message objects from the chat
    """
    async for message in client.iter_messages(
        chat_id,
        limit=limit,
        offset_date=offset_date,
    ):
        yield message


async def download_media(
    client: TelegramClient,
    message: Message,
    output_dir: Path,
    progress_callback: Any | None = None,
) -> Path | None:
    """
    Download media from a message.

    Args:
        client: Authenticated TelegramClient
        message: Message containing media
        output_dir: Directory to save downloaded files
        progress_callback: Optional callback for download progress

    Returns:
        Path to downloaded file, or None if no media
    """
    if not message.media:
        return None

    output_dir.mkdir(parents=True, exist_ok=True)

    path = await client.download_media(
        message,
        file=output_dir,
        progress_callback=progress_callback,
    )

    return Path(path) if path else None
