"""
Media downloader for Telegram chats.

Provides functionality to:
- Detect media types from Telegram media objects
- Generate filenames based on message date and sequence
- Download media files with proper folder structure
- Handle duplicate file detection
- Support progress callbacks during download
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from telethon import TelegramClient

if TYPE_CHECKING:
    pass


def get_media_type(media: Any) -> str:
    """
    Detect media type from Telegram media object.

    Args:
        media: Telegram media object (MessageMediaPhoto, MessageMediaDocument, etc.)

    Returns:
        Media type category:
        - "images" for MessageMediaPhoto
        - "audio" for audio/* MIME types
        - "video" for video/* MIME types
        - "documents" for other documents
        - "other" for unknown types
    """
    class_name = media.__class__.__name__

    if class_name == "MessageMediaPhoto":
        return "images"

    if class_name == "MessageMediaDocument":
        document = getattr(media, "document", None)
        if document is None:
            return "other"

        mime_type = getattr(document, "mime_type", None)
        if mime_type is None:
            return "other"

        if mime_type.startswith("audio/"):
            return "audio"
        if mime_type.startswith("video/"):
            return "video"

        return "documents"

    return "other"


def generate_filename(message: Any, extension: str, sequence: int = 1) -> str:
    """
    Generate filename from message date and sequence number.

    Args:
        message: Telegram message object with date attribute
        extension: File extension (without dot)
        sequence: Sequence number for this date (default 1)

    Returns:
        Filename in format: YYYY-MM-DD_NNN.extension
        where NNN is zero-padded sequence number
    """
    date_str = message.date.strftime("%Y-%m-%d")
    return f"{date_str}_{sequence:03d}.{extension}"


def get_extension_from_media(media: Any) -> str:
    """
    Extract file extension from media object.

    Args:
        media: Telegram media object

    Returns:
        File extension (without dot)
    """
    class_name = media.__class__.__name__

    if class_name == "MessageMediaPhoto":
        return "jpg"

    if class_name == "MessageMediaDocument":
        document = getattr(media, "document", None)
        if document is not None:
            # Try to get extension from filename attribute
            attributes = getattr(document, "attributes", [])
            for attr in attributes:
                file_name = getattr(attr, "file_name", None)
                if file_name:
                    ext = Path(file_name).suffix.lstrip(".")
                    if ext:
                        return ext

            # Fallback to MIME type
            mime_type = getattr(document, "mime_type", None)
            if mime_type:
                if mime_type == "audio/ogg":
                    return "ogg"
                if mime_type == "audio/mpeg":
                    return "mp3"
                if mime_type.startswith("audio/"):
                    return mime_type.split("/")[1]
                if mime_type == "video/mp4":
                    return "mp4"
                if mime_type.startswith("video/"):
                    return mime_type.split("/")[1]
                if mime_type == "application/pdf":
                    return "pdf"

    return "bin"


@dataclass
class MediaDownloader:
    """
    Downloads media files from Telegram messages.

    Handles:
    - Creating proper folder structure (media/images/, media/audio/, etc.)
    - Generating filenames based on message date
    - Tracking sequence numbers per date
    - Skipping existing files
    - Progress callback support

    Usage:
        downloader = MediaDownloader(client=client, output_dir=Path("output/chat"))
        path = await downloader.download_media(message)
        if path:
            print(f"Downloaded to: {path}")
    """

    client: TelegramClient
    output_dir: Path
    _sequence_counters: dict[tuple[str, str], int] = field(
        default_factory=lambda: defaultdict(int)
    )

    async def download_media(
        self,
        message: Any,
        progress_callback: Any | None = None,
    ) -> str | None:
        """
        Download media from a message.

        Args:
            message: Telegram message object with media attribute
            progress_callback: Optional callback for download progress

        Returns:
            Relative path to downloaded file from output_dir, or None if:
            - Message has no media
            - Download failed
        """
        if message.media is None:
            return None

        # Detect media type and create folder
        media_type = get_media_type(message.media)
        media_dir = self.output_dir / "media" / media_type
        media_dir.mkdir(parents=True, exist_ok=True)

        # Get extension
        extension = get_extension_from_media(message.media)

        # Get date key for sequence tracking
        date_key = message.date.strftime("%Y-%m-%d")
        sequence_key = (date_key, media_type)

        # Increment sequence counter
        self._sequence_counters[sequence_key] += 1
        sequence = self._sequence_counters[sequence_key]

        # Generate filename
        filename = generate_filename(message, extension, sequence)
        file_path = media_dir / filename
        relative_path = f"media/{media_type}/{filename}"

        # Check if file already exists (duplicate handling)
        if file_path.exists():
            return relative_path

        # Download the media
        result = await self.client.download_media(
            message,
            file=str(file_path),
            progress_callback=progress_callback,
        )

        if result is None:
            return None

        return relative_path
