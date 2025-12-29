"""
Export functionality for chat messages.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiofiles

from telegram_getter.downloader import ChatMessage


class ChatExporter:
    """Export chat messages to various formats."""

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
