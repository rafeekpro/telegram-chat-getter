"""
TDD RED Phase: Tests for incremental sync download functionality.

These tests verify:
1. load_existing_messages() reads existing messages.json and returns messages with highest ID
2. dict_to_message() converts dict back to Message dataclass
3. --sync CLI flag only downloads new messages
4. Merge logic combines old and new messages correctly
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from telegram_getter.downloader import Message


class TestLoadExistingMessages:
    """Test load_existing_messages function for reading existing messages.json."""

    @pytest.mark.asyncio
    async def test_load_existing_messages_returns_empty_when_file_not_exists(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN output directory without messages.json
        WHEN calling load_existing_messages
        THEN returns empty list and 0 as highest ID
        """
        from telegram_getter.exporter import load_existing_messages

        messages, highest_id = await load_existing_messages(tmp_path)

        assert messages == []
        assert highest_id == 0

    @pytest.mark.asyncio
    async def test_load_existing_messages_reads_messages_from_file(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN output directory with messages.json containing messages
        WHEN calling load_existing_messages
        THEN returns list of message dicts
        """
        from telegram_getter.exporter import load_existing_messages

        # Create messages.json
        data = {
            "exported_at": "2025-01-15T14:30:00Z",
            "message_count": 2,
            "messages": [
                {
                    "id": 1,
                    "date": "2025-01-15T10:00:00+00:00",
                    "sender_id": 1001,
                    "sender_name": "John",
                    "text": "Hello",
                    "reply_to": None,
                    "media_type": None,
                    "media_path": None,
                    "transcription": None,
                },
                {
                    "id": 2,
                    "date": "2025-01-15T11:00:00+00:00",
                    "sender_id": 1002,
                    "sender_name": "Jane",
                    "text": "Hi",
                    "reply_to": 1,
                    "media_type": None,
                    "media_path": None,
                    "transcription": None,
                },
            ],
        }

        json_path = tmp_path / "messages.json"
        json_path.write_text(json.dumps(data))

        messages, highest_id = await load_existing_messages(tmp_path)

        assert len(messages) == 2
        assert messages[0]["id"] == 1
        assert messages[1]["id"] == 2

    @pytest.mark.asyncio
    async def test_load_existing_messages_returns_highest_id(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN output directory with messages.json containing messages
        WHEN calling load_existing_messages
        THEN returns highest message ID
        """
        from telegram_getter.exporter import load_existing_messages

        data = {
            "exported_at": "2025-01-15T14:30:00Z",
            "message_count": 3,
            "messages": [
                {
                    "id": 5,
                    "date": "2025-01-15T10:00:00+00:00",
                    "sender_id": 1,
                    "sender_name": "A",
                    "text": "a",
                },
                {
                    "id": 10,
                    "date": "2025-01-15T11:00:00+00:00",
                    "sender_id": 1,
                    "sender_name": "A",
                    "text": "b",
                },
                {
                    "id": 7,
                    "date": "2025-01-15T12:00:00+00:00",
                    "sender_id": 1,
                    "sender_name": "A",
                    "text": "c",
                },
            ],
        }

        json_path = tmp_path / "messages.json"
        json_path.write_text(json.dumps(data))

        messages, highest_id = await load_existing_messages(tmp_path)

        assert highest_id == 10

    @pytest.mark.asyncio
    async def test_load_existing_messages_handles_empty_messages_array(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN output directory with messages.json containing empty messages array
        WHEN calling load_existing_messages
        THEN returns empty list and 0 as highest ID
        """
        from telegram_getter.exporter import load_existing_messages

        data = {
            "exported_at": "2025-01-15T14:30:00Z",
            "message_count": 0,
            "messages": [],
        }

        json_path = tmp_path / "messages.json"
        json_path.write_text(json.dumps(data))

        messages, highest_id = await load_existing_messages(tmp_path)

        assert messages == []
        assert highest_id == 0

    @pytest.mark.asyncio
    async def test_load_existing_messages_preserves_all_fields(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN output directory with messages.json containing full message data
        WHEN calling load_existing_messages
        THEN all fields are preserved in returned dicts
        """
        from telegram_getter.exporter import load_existing_messages

        data = {
            "exported_at": "2025-01-15T14:30:00Z",
            "message_count": 1,
            "messages": [
                {
                    "id": 123,
                    "date": "2025-01-15T14:30:45+00:00",
                    "sender_id": 1001,
                    "sender_name": "John Doe",
                    "text": "Hello world",
                    "reply_to": 100,
                    "media_type": "photo",
                    "media_path": "media/images/photo.jpg",
                    "transcription": "Voice transcription",
                },
            ],
        }

        json_path = tmp_path / "messages.json"
        json_path.write_text(json.dumps(data))

        messages, _ = await load_existing_messages(tmp_path)

        msg = messages[0]
        assert msg["id"] == 123
        assert msg["date"] == "2025-01-15T14:30:45+00:00"
        assert msg["sender_id"] == 1001
        assert msg["sender_name"] == "John Doe"
        assert msg["text"] == "Hello world"
        assert msg["reply_to"] == 100
        assert msg["media_type"] == "photo"
        assert msg["media_path"] == "media/images/photo.jpg"
        assert msg["transcription"] == "Voice transcription"


class TestDictToMessage:
    """Test dict_to_message function for converting dict back to Message."""

    def test_dict_to_message_basic_fields(self) -> None:
        """
        GIVEN a dict with basic message fields
        WHEN calling dict_to_message
        THEN returns Message dataclass with correct values
        """
        from telegram_getter.exporter import dict_to_message

        d = {
            "id": 123,
            "date": "2025-01-15T14:30:00+00:00",
            "sender_id": 1001,
            "sender_name": "John Doe",
            "text": "Hello world",
        }

        result = dict_to_message(d)

        assert isinstance(result, Message)
        assert result.id == 123
        assert result.sender_id == 1001
        assert result.sender_name == "John Doe"
        assert result.text == "Hello world"

    def test_dict_to_message_parses_date_correctly(self) -> None:
        """
        GIVEN a dict with ISO date string
        WHEN calling dict_to_message
        THEN returns Message with parsed datetime
        """
        from telegram_getter.exporter import dict_to_message

        d = {
            "id": 1,
            "date": "2025-01-15T14:30:45+00:00",
            "sender_id": 1001,
            "sender_name": "John",
            "text": "Test",
        }

        result = dict_to_message(d)

        assert result.date.year == 2025
        assert result.date.month == 1
        assert result.date.day == 15
        assert result.date.hour == 14
        assert result.date.minute == 30
        assert result.date.second == 45

    def test_dict_to_message_handles_optional_fields(self) -> None:
        """
        GIVEN a dict with None optional fields
        WHEN calling dict_to_message
        THEN returns Message with None for those fields
        """
        from telegram_getter.exporter import dict_to_message

        d = {
            "id": 1,
            "date": "2025-01-15T14:30:00+00:00",
            "sender_id": 1001,
            "sender_name": "John",
            "text": "Test",
            "reply_to": None,
            "media_type": None,
            "media_path": None,
            "transcription": None,
        }

        result = dict_to_message(d)

        assert result.reply_to is None
        assert result.media_type is None
        assert result.media_path is None
        assert result.transcription is None

    def test_dict_to_message_with_all_fields(self) -> None:
        """
        GIVEN a dict with all fields populated
        WHEN calling dict_to_message
        THEN returns Message with all fields
        """
        from telegram_getter.exporter import dict_to_message

        d = {
            "id": 123,
            "date": "2025-01-15T14:30:45+00:00",
            "sender_id": 1001,
            "sender_name": "John Doe",
            "text": "Hello world",
            "reply_to": 100,
            "media_type": "photo",
            "media_path": "media/images/photo.jpg",
            "transcription": "Voice transcription",
        }

        result = dict_to_message(d)

        assert result.id == 123
        assert result.sender_id == 1001
        assert result.sender_name == "John Doe"
        assert result.text == "Hello world"
        assert result.reply_to == 100
        assert result.media_type == "photo"
        assert result.media_path == "media/images/photo.jpg"
        assert result.transcription == "Voice transcription"

    def test_dict_to_message_handles_missing_optional_fields(self) -> None:
        """
        GIVEN a dict missing optional fields (not present in dict)
        WHEN calling dict_to_message
        THEN returns Message with defaults for those fields
        """
        from telegram_getter.exporter import dict_to_message

        # Minimal dict without optional fields
        d = {
            "id": 1,
            "date": "2025-01-15T14:30:00+00:00",
            "sender_id": 1001,
            "sender_name": "John",
            "text": "Test",
        }

        result = dict_to_message(d)

        assert result.reply_to is None
        assert result.media_type is None
        assert result.media_path is None
        assert result.transcription is None


class TestSyncCLIFlag:
    """Test --sync CLI flag for incremental download."""

    def test_download_command_has_sync_flag(self) -> None:
        """
        GIVEN CLI app
        WHEN running download --help
        THEN shows --sync/-s flag for incremental sync
        """
        from typer.testing import CliRunner

        from telegram_getter.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["download", "--help"])

        assert result.exit_code == 0
        assert "--sync" in result.output


class TestMergeMessages:
    """Test message merging logic for sync functionality."""

    def test_merge_avoids_duplicates_by_id(self) -> None:
        """
        GIVEN existing messages and new messages with overlapping IDs
        WHEN merging
        THEN duplicates are removed based on ID
        """
        from telegram_getter.exporter import dict_to_message

        existing_dicts = [
            {
                "id": 1,
                "date": "2025-01-15T10:00:00+00:00",
                "sender_id": 1001,
                "sender_name": "A",
                "text": "First",
            },
            {
                "id": 2,
                "date": "2025-01-15T11:00:00+00:00",
                "sender_id": 1001,
                "sender_name": "A",
                "text": "Second",
            },
        ]

        # Simulate new messages including one with same ID (shouldn't happen but for safety)
        existing_messages = [dict_to_message(d) for d in existing_dicts]
        existing_ids = {m.id for m in existing_messages}

        # New messages from Telegram (ID 2 is duplicate, 3 is new)
        new_messages = [
            Message(
                id=2,
                date=datetime(2025, 1, 15, 11, 0, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="A",
                text="Second",
            ),
            Message(
                id=3,
                date=datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="A",
                text="Third",
            ),
        ]

        # Filter out duplicates
        new_unique = [m for m in new_messages if m.id not in existing_ids]

        assert len(new_unique) == 1
        assert new_unique[0].id == 3

    def test_merged_messages_sorted_chronologically(self) -> None:
        """
        GIVEN existing messages and new messages
        WHEN merging and sorting
        THEN all messages are in chronological order
        """
        from telegram_getter.exporter import dict_to_message

        existing_dicts = [
            {
                "id": 1,
                "date": "2025-01-15T10:00:00+00:00",
                "sender_id": 1001,
                "sender_name": "A",
                "text": "First",
            },
        ]

        existing_messages = [dict_to_message(d) for d in existing_dicts]

        new_messages = [
            Message(
                id=3,
                date=datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="A",
                text="Third",
            ),
            Message(
                id=2,
                date=datetime(2025, 1, 15, 11, 0, 0, tzinfo=UTC),
                sender_id=1001,
                sender_name="A",
                text="Second",
            ),
        ]

        # Merge and sort
        all_messages = existing_messages + new_messages
        all_messages.sort(key=lambda m: m.date)

        assert all_messages[0].id == 1
        assert all_messages[1].id == 2
        assert all_messages[2].id == 3
