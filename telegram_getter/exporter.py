"""
Export functionality for chat messages.

Provides functionality to:
- Format individual messages as markdown
- Export messages to markdown files with date grouping
- Generate metadata JSON files with statistics
- Load existing messages for incremental sync
- Convert message dicts back to Message dataclass
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiofiles

from telegram_getter.downloader import ChatMessage, Message

if TYPE_CHECKING:
    from collections.abc import Sequence


async def load_existing_messages(output_dir: Path) -> tuple[list[dict[str, Any]], int]:
    """
    Load existing messages from messages.json.

    Reads the messages.json file from the output directory and returns
    both the list of message dictionaries and the highest message ID.
    This is used for incremental sync to download only new messages.

    Args:
        output_dir: Directory containing messages.json

    Returns:
        Tuple of (list of message dicts, highest message ID).
        Returns ([], 0) if file doesn't exist or is empty.
    """
    json_path = output_dir / "messages.json"
    if not json_path.exists():
        return [], 0

    async with aiofiles.open(json_path, encoding="utf-8") as f:
        content = await f.read()
        data = json.loads(content)
        messages = data.get("messages", [])
        if not messages:
            return [], 0
        highest_id = max(m["id"] for m in messages)
        return messages, highest_id


def dict_to_message(d: dict[str, Any]) -> Message:
    """
    Convert a dictionary back to Message dataclass.

    Used for loading existing messages from JSON and converting them
    back to Message objects for merging with newly downloaded messages.

    Args:
        d: Dictionary with message fields (as stored in messages.json)

    Returns:
        Message dataclass with all fields populated from the dict
    """
    return Message(
        id=d["id"],
        date=datetime.fromisoformat(d["date"]),
        sender_id=d["sender_id"],
        sender_name=d["sender_name"],
        text=d["text"],
        reply_to=d.get("reply_to"),
        media_type=d.get("media_type"),
        media_path=d.get("media_path"),
        transcription=d.get("transcription"),
    )


def format_message(msg: Message) -> str:
    """
    Format a single message as markdown.

    Creates a markdown block with:
    - Header: ### HH:MM - Sender Name
    - Reply indicator (if replying to another message)
    - Message text (if present)
    - Media link (if media attached)

    Args:
        msg: Message object to format

    Returns:
        Formatted markdown string
    """
    lines: list[str] = []

    # Header with time and sender name
    time_str = msg.date.strftime("%H:%M")
    lines.append(f"### {time_str} - {msg.sender_name}")

    # Reply indicator
    if msg.reply_to is not None:
        lines.append(f"> Replying to message #{msg.reply_to}")
        lines.append("")  # Empty line after blockquote

    # Message text
    if msg.text:
        lines.append(msg.text)

    # Media link
    if msg.media_type and msg.media_path:
        media_line = _format_media_link(msg.media_type, msg.media_path)
        if media_line:
            lines.append(media_line)

    # Transcription (for voice messages)
    if msg.transcription:
        lines.append(f"> Transcription: {msg.transcription}")

    return "\n".join(lines)


def _format_media_link(media_type: str, media_path: str) -> str:
    """
    Format a media link based on media type.

    Args:
        media_type: Type of media (photo, audio, video, document)
        media_path: Relative path to the media file

    Returns:
        Formatted markdown link
    """
    if media_type == "photo":
        return f"![image]({media_path})"
    if media_type == "audio":
        return f"[Voice message]({media_path})"
    if media_type == "video":
        return f"[Video]({media_path})"
    if media_type == "document":
        filename = Path(media_path).name
        return f"[Document: {filename}]({media_path})"
    return ""


async def export_to_markdown(
    messages: Sequence[Message],
    chat_name: str,
    output_dir: Path,
) -> Path:
    """
    Export messages to a markdown file.

    Creates a messages.md file with:
    - Header with chat name, download date, counts
    - Messages grouped by date (newest first)
    - Messages sorted by time within each date

    Args:
        messages: List of Message objects to export
        chat_name: Name of the chat being exported
        output_dir: Directory where the file will be created

    Returns:
        Path to the created markdown file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "messages.md"

    # Count media files
    media_count = sum(1 for msg in messages if msg.media_type and msg.media_path)

    # Build header
    lines: list[str] = []
    lines.append(f"# Chat: {chat_name}")
    lines.append(f"Downloaded: {datetime.now(UTC).isoformat()}")
    lines.append(f"Total messages: {len(messages)}")
    lines.append(f"Media files: {media_count}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Group messages by date
    messages_by_date: dict[str, list[Message]] = defaultdict(list)
    for msg in messages:
        date_key = msg.date.strftime("%Y-%m-%d")
        messages_by_date[date_key].append(msg)

    # Sort dates (oldest first for chronological order) and messages within each date (oldest first)
    sorted_dates = sorted(messages_by_date.keys())

    for i, date_key in enumerate(sorted_dates):
        # Date header
        lines.append(f"## {date_key}")
        lines.append("")

        # Sort messages by time (oldest first within the day)
        day_messages = sorted(messages_by_date[date_key], key=lambda m: m.date)

        for msg in day_messages:
            lines.append(format_message(msg))
            lines.append("")

        # Add separator between dates (not after the last one)
        if i < len(sorted_dates) - 1:
            lines.append("---")
            lines.append("")

    content = "\n".join(lines)

    async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
        await f.write(content)

    return output_path


async def generate_metadata(
    messages: Sequence[Message],
    chat_name: str,
    chat_id: int,
    chat_type: str,
    output_dir: Path,
) -> Path:
    """
    Generate a metadata.json file with chat statistics.

    Creates a JSON file containing:
    - Chat info (name, id, type)
    - Download timestamp
    - Message count
    - Media counts by type
    - Date range

    Args:
        messages: List of Message objects
        chat_name: Name of the chat
        chat_id: Telegram chat ID
        chat_type: Type of chat (group, channel, etc.)
        output_dir: Directory where the file will be created

    Returns:
        Path to the created metadata file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "metadata.json"

    # Count media by type
    media_counts = {
        "images": 0,
        "audio": 0,
        "video": 0,
        "documents": 0,
    }

    for msg in messages:
        if msg.media_type and msg.media_path:
            if msg.media_type == "photo":
                media_counts["images"] += 1
            elif msg.media_type == "audio":
                media_counts["audio"] += 1
            elif msg.media_type == "video":
                media_counts["video"] += 1
            elif msg.media_type == "document":
                media_counts["documents"] += 1

    # Calculate date range
    if messages:
        dates = [msg.date for msg in messages]
        min_date = min(dates).strftime("%Y-%m-%d")
        max_date = max(dates).strftime("%Y-%m-%d")
    else:
        min_date = None
        max_date = None

    metadata = {
        "chat_name": chat_name,
        "chat_id": chat_id,
        "chat_type": chat_type,
        "downloaded_at": datetime.now(UTC).isoformat(),
        "total_messages": len(messages),
        "media_files": media_counts,
        "date_range": {
            "from": min_date,
            "to": max_date,
        },
    }

    async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))

    return output_path


async def export_messages_to_json(
    messages: Sequence[Message],
    output_dir: Path,
) -> Path:
    """
    Export all messages to a JSON file in chronological order.

    Creates a messages.json file containing:
    - Export timestamp
    - Message count
    - All messages sorted oldest first with all fields

    Args:
        messages: List of Message objects to export
        output_dir: Directory where the file will be created

    Returns:
        Path to the created JSON file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "messages.json"

    # Sort messages by date (oldest first for chronological order)
    sorted_messages = sorted(messages, key=lambda m: m.date)

    def message_to_dict(msg: Message) -> dict[str, Any]:
        """Convert Message to dictionary for JSON serialization."""
        return {
            "id": msg.id,
            "date": msg.date.isoformat(),
            "sender_id": msg.sender_id,
            "sender_name": msg.sender_name,
            "text": msg.text,
            "reply_to": msg.reply_to,
            "media_type": msg.media_type,
            "media_path": msg.media_path,
            "transcription": msg.transcription,
        }

    data = {
        "exported_at": datetime.now(UTC).isoformat(),
        "message_count": len(messages),
        "messages": [message_to_dict(msg) for msg in sorted_messages],
    }

    async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    return output_path


class ChatExporter:
    """Export chat messages to various formats (legacy class)."""

    def __init__(self, output_dir: Path) -> None:
        """
        Initialize exporter with output directory.

        Args:
            output_dir: Directory where exports will be saved
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def export_to_json(
        self,
        messages: list[ChatMessage],
        filename: str = "chat_export.json",
    ) -> Path:
        """
        Export messages to JSON format.

        Args:
            messages: List of ChatMessage objects to export
            filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename

        data = {
            "exported_at": datetime.now(UTC).isoformat(),
            "message_count": len(messages),
            "messages": [self._message_to_dict(msg) for msg in messages],
        }

        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

        return output_path

    async def export_to_txt(
        self,
        messages: list[ChatMessage],
        filename: str = "chat_export.txt",
    ) -> Path:
        """
        Export messages to plain text format.

        Args:
            messages: List of ChatMessage objects to export
            filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename

        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            for msg in messages:
                line = f"[{msg.date.isoformat()}] {msg.sender_name}: {msg.text}\n"
                await f.write(line)

        return output_path

    def _message_to_dict(self, message: ChatMessage) -> dict[str, Any]:
        """Convert ChatMessage to dictionary for JSON serialization."""
        return {
            "id": message.id,
            "date": message.date.isoformat(),
            "sender_id": message.sender_id,
            "sender_name": message.sender_name,
            "text": message.text,
            "media_path": str(message.media_path) if message.media_path else None,
        }
