"""
TDD RED Phase: Tests for Telegram markdown exporter module.

These tests verify:
1. format_message() formats individual messages correctly
2. export_to_markdown() creates proper markdown files
3. generate_metadata() creates valid JSON metadata
4. Proper date grouping and sorting
5. Media linking with relative paths
6. Reply-to message handling
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from telegram_getter.downloader import Message
from telegram_getter.exporter import (
    export_to_markdown,
    format_message,
    generate_metadata,
)


class TestFormatMessageTextOnly:
    """Test format_message function with text-only messages."""

    def test_format_message_includes_time(self) -> None:
        """
        GIVEN a message with a specific time
        WHEN calling format_message
        THEN output includes time in HH:MM format
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="Hello world",
        )

        result = format_message(msg)

        assert "14:30" in result

    def test_format_message_includes_sender_name(self) -> None:
        """
        GIVEN a message with sender name
        WHEN calling format_message
        THEN output includes sender name
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="Hello world",
        )

        result = format_message(msg)

        assert "John Doe" in result

    def test_format_message_includes_text(self) -> None:
        """
        GIVEN a message with text content
        WHEN calling format_message
        THEN output includes the message text
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="This is my message content",
        )

        result = format_message(msg)

        assert "This is my message content" in result

    def test_format_message_creates_header_with_time_and_name(self) -> None:
        """
        GIVEN a message
        WHEN calling format_message
        THEN output has header format "### HH:MM - Sender Name"
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="Hello",
        )

        result = format_message(msg)

        assert "### 14:30 - John Doe" in result

    def test_format_message_handles_empty_text(self) -> None:
        """
        GIVEN a message with empty text
        WHEN calling format_message
        THEN output contains header but no extra content lines
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="",
        )

        result = format_message(msg)

        # Should have header
        assert "### 14:30 - John Doe" in result
        # Should not have content beyond header
        lines = [line for line in result.strip().split("\n") if line.strip()]
        assert len(lines) == 1


class TestFormatMessageWithMedia:
    """Test format_message function with media attachments."""

    def test_format_message_with_image_media(self) -> None:
        """
        GIVEN a message with image media
        WHEN calling format_message
        THEN output includes markdown image link
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="Check this out",
            media_type="photo",
            media_path="media/images/2025-01-15_001.jpg",
        )

        result = format_message(msg)

        assert "![image](media/images/2025-01-15_001.jpg)" in result

    def test_format_message_with_audio_media(self) -> None:
        """
        GIVEN a message with audio media
        WHEN calling format_message
        THEN output includes audio link
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="Listen to this",
            media_type="audio",
            media_path="media/audio/2025-01-15_001.ogg",
        )

        result = format_message(msg)

        assert "[Voice message](media/audio/2025-01-15_001.ogg)" in result

    def test_format_message_with_video_media(self) -> None:
        """
        GIVEN a message with video media
        WHEN calling format_message
        THEN output includes video link
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="Watch this",
            media_type="video",
            media_path="media/video/2025-01-15_001.mp4",
        )

        result = format_message(msg)

        assert "[Video](media/video/2025-01-15_001.mp4)" in result

    def test_format_message_with_document_media(self) -> None:
        """
        GIVEN a message with document media
        WHEN calling format_message
        THEN output includes document link with filename
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="Here's the file",
            media_type="document",
            media_path="media/documents/2025-01-15_001.pdf",
        )

        result = format_message(msg)

        assert "[Document: 2025-01-15_001.pdf](media/documents/2025-01-15_001.pdf)" in result

    def test_format_message_media_only_no_text(self) -> None:
        """
        GIVEN a message with media but no text
        WHEN calling format_message
        THEN output includes header and media link
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="",
            media_type="photo",
            media_path="media/images/2025-01-15_001.jpg",
        )

        result = format_message(msg)

        assert "### 14:30 - John Doe" in result
        assert "![image](media/images/2025-01-15_001.jpg)" in result


class TestFormatMessageWithReply:
    """Test format_message function with reply_to field."""

    def test_format_message_with_reply_to(self) -> None:
        """
        GIVEN a message that is a reply
        WHEN calling format_message
        THEN output includes "Replying to message #ID"
        """
        msg = Message(
            id=2,
            date=datetime(2025, 1, 15, 14, 31, 0, tzinfo=UTC),
            sender_id=1002,
            sender_name="Jane Smith",
            text="Thanks for sharing!",
            reply_to=1,
        )

        result = format_message(msg)

        assert "> Replying to message #1" in result

    def test_format_message_reply_appears_before_text(self) -> None:
        """
        GIVEN a message that is a reply with text
        WHEN calling format_message
        THEN reply indicator appears before the message text
        """
        msg = Message(
            id=2,
            date=datetime(2025, 1, 15, 14, 31, 0, tzinfo=UTC),
            sender_id=1002,
            sender_name="Jane Smith",
            text="Thanks!",
            reply_to=1,
        )

        result = format_message(msg)

        reply_pos = result.find("> Replying to message #1")
        text_pos = result.find("Thanks!")

        assert reply_pos < text_pos

    def test_format_message_without_reply(self) -> None:
        """
        GIVEN a message that is not a reply
        WHEN calling format_message
        THEN output does not include reply indicator
        """
        msg = Message(
            id=1,
            date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="Hello",
        )

        result = format_message(msg)

        assert "Replying to" not in result


class TestExportToMarkdown:
    """Test export_to_markdown function for creating markdown files."""

    @pytest.mark.asyncio
    async def test_export_to_markdown_creates_file(self, tmp_path: Path) -> None:
        """
        GIVEN a list of messages
        WHEN calling export_to_markdown
        THEN creates messages.md file in output directory
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            )
        ]

        result = await export_to_markdown(messages, "Test Chat", tmp_path)

        assert result.exists()
        assert result.name == "messages.md"

    @pytest.mark.asyncio
    async def test_export_to_markdown_includes_chat_name(self, tmp_path: Path) -> None:
        """
        GIVEN a chat name
        WHEN calling export_to_markdown
        THEN output includes "# Chat: {name}" header
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            )
        ]

        result = await export_to_markdown(messages, "Work Team", tmp_path)

        content = result.read_text()
        assert "# Chat: Work Team" in content

    @pytest.mark.asyncio
    async def test_export_to_markdown_includes_download_date(self, tmp_path: Path) -> None:
        """
        GIVEN messages to export
        WHEN calling export_to_markdown
        THEN output includes download timestamp
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            )
        ]

        result = await export_to_markdown(messages, "Test Chat", tmp_path)

        content = result.read_text()
        assert "Downloaded:" in content

    @pytest.mark.asyncio
    async def test_export_to_markdown_includes_total_messages(self, tmp_path: Path) -> None:
        """
        GIVEN multiple messages
        WHEN calling export_to_markdown
        THEN output includes total message count
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            ),
            Message(
                id=2,
                date=datetime(2025, 1, 15, 14, 31, 0, tzinfo=UTC),
                sender_id=1002,
                sender_name="Jane Smith",
                text="Hi",
            ),
        ]

        result = await export_to_markdown(messages, "Test Chat", tmp_path)

        content = result.read_text()
        assert "Total messages: 2" in content

    @pytest.mark.asyncio
    async def test_export_to_markdown_includes_media_count(self, tmp_path: Path) -> None:
        """
        GIVEN messages with media
        WHEN calling export_to_markdown
        THEN output includes media file count
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Photo",
                media_type="photo",
                media_path="media/images/2025-01-15_001.jpg",
            ),
            Message(
                id=2,
                date=datetime(2025, 1, 15, 14, 31, 0, tzinfo=UTC),
                sender_id=1002,
                sender_name="Jane Smith",
                text="Hi",
            ),
        ]

        result = await export_to_markdown(messages, "Test Chat", tmp_path)

        content = result.read_text()
        assert "Media files: 1" in content

    @pytest.mark.asyncio
    async def test_export_to_markdown_groups_by_date(self, tmp_path: Path) -> None:
        """
        GIVEN messages from different dates
        WHEN calling export_to_markdown
        THEN output groups messages by date with "## YYYY-MM-DD" headers
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Day 1",
            ),
            Message(
                id=2,
                date=datetime(2025, 1, 14, 10, 0, 0, tzinfo=UTC),
                sender_id=1002,
                sender_name="Jane Smith",
                text="Day 2",
            ),
        ]

        result = await export_to_markdown(messages, "Test Chat", tmp_path)

        content = result.read_text()
        assert "## 2025-01-15" in content
        assert "## 2025-01-14" in content

    @pytest.mark.asyncio
    async def test_export_to_markdown_sorts_dates_newest_first(self, tmp_path: Path) -> None:
        """
        GIVEN messages from different dates
        WHEN calling export_to_markdown
        THEN dates are sorted newest first
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 14, 10, 0, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Old",
            ),
            Message(
                id=2,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1002,
                sender_name="Jane Smith",
                text="New",
            ),
        ]

        result = await export_to_markdown(messages, "Test Chat", tmp_path)

        content = result.read_text()
        pos_jan_15 = content.find("## 2025-01-15")
        pos_jan_14 = content.find("## 2025-01-14")

        assert pos_jan_15 < pos_jan_14

    @pytest.mark.asyncio
    async def test_export_to_markdown_sorts_messages_by_time_within_date(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN multiple messages on same date
        WHEN calling export_to_markdown
        THEN messages are sorted by time (earliest first)
        """
        messages = [
            Message(
                id=2,
                date=datetime(2025, 1, 15, 16, 0, 0, tzinfo=UTC),
                sender_id=1002,
                sender_name="Jane",
                text="Later",
            ),
            Message(
                id=1,
                date=datetime(2025, 1, 15, 10, 0, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John",
                text="Earlier",
            ),
        ]

        result = await export_to_markdown(messages, "Test Chat", tmp_path)

        content = result.read_text()
        pos_earlier = content.find("Earlier")
        pos_later = content.find("Later")

        assert pos_earlier < pos_later

    @pytest.mark.asyncio
    async def test_export_to_markdown_includes_separator_between_dates(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN messages from multiple dates
        WHEN calling export_to_markdown
        THEN dates are separated by horizontal rules
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Day 1",
            ),
            Message(
                id=2,
                date=datetime(2025, 1, 14, 10, 0, 0, tzinfo=UTC),
                sender_id=1002,
                sender_name="Jane Smith",
                text="Day 2",
            ),
        ]

        result = await export_to_markdown(messages, "Test Chat", tmp_path)

        content = result.read_text()
        assert "---" in content

    @pytest.mark.asyncio
    async def test_export_to_markdown_empty_messages(self, tmp_path: Path) -> None:
        """
        GIVEN an empty message list
        WHEN calling export_to_markdown
        THEN creates file with header only
        """
        messages: list[Message] = []

        result = await export_to_markdown(messages, "Empty Chat", tmp_path)

        assert result.exists()
        content = result.read_text()
        assert "# Chat: Empty Chat" in content
        assert "Total messages: 0" in content


class TestGenerateMetadata:
    """Test generate_metadata function for creating metadata.json."""

    @pytest.mark.asyncio
    async def test_generate_metadata_creates_file(self, tmp_path: Path) -> None:
        """
        GIVEN messages and chat info
        WHEN calling generate_metadata
        THEN creates metadata.json file
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            )
        ]

        result = await generate_metadata(
            messages, "Work Team", 123456789, "group", tmp_path
        )

        assert result.exists()
        assert result.name == "metadata.json"

    @pytest.mark.asyncio
    async def test_generate_metadata_includes_chat_name(self, tmp_path: Path) -> None:
        """
        GIVEN a chat name
        WHEN calling generate_metadata
        THEN JSON includes chat_name field
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            )
        ]

        result = await generate_metadata(
            messages, "Work Team", 123456789, "group", tmp_path
        )

        data = json.loads(result.read_text())
        assert data["chat_name"] == "Work Team"

    @pytest.mark.asyncio
    async def test_generate_metadata_includes_chat_id(self, tmp_path: Path) -> None:
        """
        GIVEN a chat id
        WHEN calling generate_metadata
        THEN JSON includes chat_id field
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            )
        ]

        result = await generate_metadata(
            messages, "Work Team", 123456789, "group", tmp_path
        )

        data = json.loads(result.read_text())
        assert data["chat_id"] == 123456789

    @pytest.mark.asyncio
    async def test_generate_metadata_includes_chat_type(self, tmp_path: Path) -> None:
        """
        GIVEN a chat type
        WHEN calling generate_metadata
        THEN JSON includes chat_type field
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            )
        ]

        result = await generate_metadata(
            messages, "Work Team", 123456789, "channel", tmp_path
        )

        data = json.loads(result.read_text())
        assert data["chat_type"] == "channel"

    @pytest.mark.asyncio
    async def test_generate_metadata_includes_download_timestamp(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN messages to export
        WHEN calling generate_metadata
        THEN JSON includes downloaded_at timestamp
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            )
        ]

        result = await generate_metadata(
            messages, "Work Team", 123456789, "group", tmp_path
        )

        data = json.loads(result.read_text())
        assert "downloaded_at" in data
        # Should be ISO format
        assert "T" in data["downloaded_at"]

    @pytest.mark.asyncio
    async def test_generate_metadata_includes_total_messages(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN multiple messages
        WHEN calling generate_metadata
        THEN JSON includes total_messages count
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            ),
            Message(
                id=2,
                date=datetime(2025, 1, 15, 14, 31, 0, tzinfo=UTC),
                sender_id=1002,
                sender_name="Jane Smith",
                text="Hi",
            ),
        ]

        result = await generate_metadata(
            messages, "Work Team", 123456789, "group", tmp_path
        )

        data = json.loads(result.read_text())
        assert data["total_messages"] == 2

    @pytest.mark.asyncio
    async def test_generate_metadata_counts_media_by_type(self, tmp_path: Path) -> None:
        """
        GIVEN messages with different media types
        WHEN calling generate_metadata
        THEN JSON includes media_files breakdown by type
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John",
                text="Photo",
                media_type="photo",
                media_path="media/images/2025-01-15_001.jpg",
            ),
            Message(
                id=2,
                date=datetime(2025, 1, 15, 14, 31, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John",
                text="Audio",
                media_type="audio",
                media_path="media/audio/2025-01-15_001.ogg",
            ),
            Message(
                id=3,
                date=datetime(2025, 1, 15, 14, 32, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John",
                text="Video",
                media_type="video",
                media_path="media/video/2025-01-15_001.mp4",
            ),
            Message(
                id=4,
                date=datetime(2025, 1, 15, 14, 33, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John",
                text="Doc",
                media_type="document",
                media_path="media/documents/2025-01-15_001.pdf",
            ),
            Message(
                id=5,
                date=datetime(2025, 1, 15, 14, 34, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John",
                text="Another photo",
                media_type="photo",
                media_path="media/images/2025-01-15_002.jpg",
            ),
        ]

        result = await generate_metadata(
            messages, "Work Team", 123456789, "group", tmp_path
        )

        data = json.loads(result.read_text())
        assert data["media_files"]["images"] == 2
        assert data["media_files"]["audio"] == 1
        assert data["media_files"]["video"] == 1
        assert data["media_files"]["documents"] == 1

    @pytest.mark.asyncio
    async def test_generate_metadata_includes_date_range(self, tmp_path: Path) -> None:
        """
        GIVEN messages spanning multiple dates
        WHEN calling generate_metadata
        THEN JSON includes date_range with from and to
        """
        messages = [
            Message(
                id=1,
                date=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John",
                text="Start",
            ),
            Message(
                id=2,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John",
                text="End",
            ),
        ]

        result = await generate_metadata(
            messages, "Work Team", 123456789, "group", tmp_path
        )

        data = json.loads(result.read_text())
        assert data["date_range"]["from"] == "2024-01-01"
        assert data["date_range"]["to"] == "2025-01-15"

    @pytest.mark.asyncio
    async def test_generate_metadata_handles_empty_messages(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN an empty message list
        WHEN calling generate_metadata
        THEN creates valid JSON with zero counts
        """
        messages: list[Message] = []

        result = await generate_metadata(
            messages, "Empty Chat", 123456789, "group", tmp_path
        )

        data = json.loads(result.read_text())
        assert data["total_messages"] == 0
        assert data["media_files"]["images"] == 0
        assert data["media_files"]["audio"] == 0
        assert data["media_files"]["video"] == 0
        assert data["media_files"]["documents"] == 0
        assert data["date_range"]["from"] is None
        assert data["date_range"]["to"] is None

    @pytest.mark.asyncio
    async def test_generate_metadata_is_valid_json(self, tmp_path: Path) -> None:
        """
        GIVEN messages
        WHEN calling generate_metadata
        THEN output file is valid JSON
        """
        messages = [
            Message(
                id=1,
                date=datetime(2025, 1, 15, 14, 30, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="John Doe",
                text="Hello",
            )
        ]

        result = await generate_metadata(
            messages, "Work Team", 123456789, "group", tmp_path
        )

        # Should not raise
        data = json.loads(result.read_text())
        assert isinstance(data, dict)
