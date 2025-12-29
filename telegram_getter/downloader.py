"""
Message and media downloader for Telegram chats.

Provides functionality to:
- Download messages by chat name or ID
- Handle pagination for chats with 100K+ messages
- Respect Telegram rate limits with configurable delays
- Extract message metadata including text, sender, timestamp
- Identify messages with media attachments
- Store message metadata for later processing
- Show progress during download via callbacks
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from telethon import TelegramClient
from telethon.tl.types import Message as TelegramMessage

if TYPE_CHECKING:
    pass


@dataclass
class DownloadProgress:
    """Progress information for downloads."""

    current: int
    total: int
    filename: str


@dataclass
class ChatMessage:
    """Represents a downloaded chat message (legacy class)."""

    id: int
    date: datetime
    sender_id: int | None
    sender_name: str
    text: str
    media_path: Path | None = None


@dataclass
class Message:
    """
    Represents a downloaded chat message with full metadata.

    Attributes:
        id: Unique message ID within the chat
        date: Timestamp when the message was sent
        sender_id: Telegram user ID of the sender (0 if unknown)
        sender_name: Display name of the sender
        text: Message text content (empty string if no text)
        reply_to: ID of the message this is replying to (None if not a reply)
        media_type: Type of media attachment (photo, audio, video, document, or None)
        media_path: Local path to downloaded media file (filled after download)
    """

    id: int
    date: datetime
    sender_id: int
    sender_name: str
    text: str
    reply_to: int | None = None
    media_type: str | None = None
    media_path: str | None = None


def parse_message(telegram_msg: TelegramMessage) -> Message:
    """
    Convert a Telegram message object to our Message dataclass.

    Extracts all relevant fields from the Telegram message including:
    - Basic fields: id, date, text
    - Sender information: sender_id, sender_name (handles missing sender)
    - Reply context: reply_to message ID
    - Media type detection: photo, video, audio, document

    Args:
        telegram_msg: Telegram message object from Telethon

    Returns:
        Message dataclass with extracted data
    """
    # Extract sender information
    sender_id = 0
    sender_name = "Unknown"

    if telegram_msg.sender_id is not None:
        sender_id = telegram_msg.sender_id

    if telegram_msg.sender is not None:
        first_name = getattr(telegram_msg.sender, "first_name", None) or ""
        last_name = getattr(telegram_msg.sender, "last_name", None) or ""
        sender_name = f"{first_name} {last_name}".strip() or "Unknown"

    # Extract text (default to empty string)
    text = telegram_msg.text or ""

    # Extract reply_to
    reply_to = telegram_msg.reply_to_msg_id

    # Detect media type
    media_type: str | None = None
    if telegram_msg.media is not None:
        if getattr(telegram_msg, "photo", None) is not None:
            media_type = "photo"
        elif getattr(telegram_msg, "video", None) is not None:
            media_type = "video"
        elif getattr(telegram_msg, "audio", None) is not None:
            media_type = "audio"
        elif getattr(telegram_msg, "document", None) is not None:
            media_type = "document"

    return Message(
        id=telegram_msg.id,
        date=telegram_msg.date,
        sender_id=sender_id,
        sender_name=sender_name,
        text=text,
        reply_to=reply_to,
        media_type=media_type,
        media_path=None,  # Filled later when media is downloaded
    )


# Type alias for progress callback
ProgressCallback = Callable[[int, int | None], None]


@dataclass
class MessageDownloader:
    """
    Downloads messages from Telegram chats with pagination and rate limiting.

    Handles:
    - Downloading messages by chat name or ID
    - Pagination for large chats (100K+ messages)
    - Rate limiting to prevent API errors
    - Progress tracking via callbacks
    - Message storage for later processing

    Usage:
        downloader = MessageDownloader(client)
        async for message in downloader.download_messages("my_channel"):
            print(message.text)

    Or with storage:
        downloader = MessageDownloader(client)
        async for _ in downloader.download_messages("my_channel", store=True):
            pass
        # Access all messages later
        for msg in downloader.messages:
            process(msg)
    """

    client: TelegramClient
    batch_size: int = 100
    delay_seconds: float = 0.5
    messages: list[Message] = field(default_factory=list)

    async def download_messages(
        self,
        chat: str | int,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int | None = None,
        progress_callback: ProgressCallback | None = None,
        store: bool = False,
        fetch_total: bool = False,
    ) -> AsyncIterator[Message]:
        """
        Iterate through all messages in a chat.

        Handles pagination automatically and respects rate limits by adding
        delays between batches.

        Args:
            chat: Chat username or ID to download from
            from_date: Only yield messages after this date
            to_date: Only yield messages before this date
            limit: Maximum number of messages to yield
            progress_callback: Callback called with (current_count, total)
            store: If True, store messages in self.messages
            fetch_total: If True, fetch total message count before iterating

        Yields:
            Message objects from the chat
        """
        total: int | None = None

        # Fetch total count if requested
        if fetch_total:
            try:
                result = await self.client.get_messages(chat, limit=0)
                total = getattr(result, "total", None)
            except Exception:
                # If we can't get total, continue without it
                pass

        count = 0
        batch_count = 0

        async for telegram_msg in self.client.iter_messages(
            chat,
            offset_date=to_date,
            limit=limit,
        ):
            # Filter by from_date if specified
            if from_date is not None and telegram_msg.date < from_date:
                continue

            message = parse_message(telegram_msg)
            count += 1

            # Store if requested
            if store:
                self.messages.append(message)

            # Call progress callback
            if progress_callback is not None:
                progress_callback(count, total)

            yield message

            # Add delay between batches for rate limiting
            batch_count += 1
            if batch_count >= self.batch_size:
                batch_count = 0
                await asyncio.sleep(self.delay_seconds)

    def clear_messages(self) -> None:
        """Clear all stored messages."""
        self.messages.clear()


# Legacy function-based API for backwards compatibility
async def get_chat_messages(
    client: TelegramClient,
    chat_id: int | str,
    limit: int | None = None,
    offset_date: datetime | None = None,
) -> AsyncIterator[TelegramMessage]:
    """
    Iterate over messages in a chat.

    This is a legacy function. Consider using MessageDownloader class instead.

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
    message: TelegramMessage,
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
