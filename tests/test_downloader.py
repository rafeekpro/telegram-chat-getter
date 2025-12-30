"""
TDD RED Phase: Tests for Telegram message downloader module.

These tests verify:
1. Message dataclass with all required fields
2. download_messages function with pagination
3. Rate limiting to prevent API errors
4. Media type detection
5. Progress tracking during download
6. Date range filtering
"""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from telegram_getter.downloader import (
    Message,
    MessageDownloader,
    parse_message,
)


class TestMessageDataclass:
    """Test Message dataclass structure and fields."""

    def test_message_has_required_id_field(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance
        THEN id field is required and stored correctly
        """
        msg = Message(
            id=12345,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test User",
            text="Hello world",
        )
        assert msg.id == 12345

    def test_message_has_required_date_field(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance
        THEN date field is required and stored correctly
        """
        now = datetime.now(UTC)
        msg = Message(
            id=1,
            date=now,
            sender_id=1001,
            sender_name="Test",
            text="Hello",
        )
        assert msg.date == now

    def test_message_has_required_sender_id_field(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance
        THEN sender_id field is required and stored correctly
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=999888777,
            sender_name="Test",
            text="Hello",
        )
        assert msg.sender_id == 999888777

    def test_message_has_required_sender_name_field(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance
        THEN sender_name field is required and stored correctly
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="John Doe",
            text="Hello",
        )
        assert msg.sender_name == "John Doe"

    def test_message_has_required_text_field(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance
        THEN text field is required and stored correctly
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test",
            text="This is the message content",
        )
        assert msg.text == "This is the message content"

    def test_message_has_optional_reply_to_field(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance with reply_to
        THEN reply_to field is stored correctly
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test",
            text="Hello",
            reply_to=456,
        )
        assert msg.reply_to == 456

    def test_message_reply_to_defaults_to_none(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance without reply_to
        THEN reply_to defaults to None
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test",
            text="Hello",
        )
        assert msg.reply_to is None

    def test_message_has_optional_media_type_field(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance with media_type
        THEN media_type field is stored correctly
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test",
            text="Hello",
            media_type="photo",
        )
        assert msg.media_type == "photo"

    def test_message_media_type_defaults_to_none(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance without media_type
        THEN media_type defaults to None
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test",
            text="Hello",
        )
        assert msg.media_type is None

    def test_message_has_optional_media_path_field(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance with media_path
        THEN media_path field is stored correctly
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test",
            text="Hello",
            media_path="/downloads/photo.jpg",
        )
        assert msg.media_path == "/downloads/photo.jpg"

    def test_message_media_path_defaults_to_none(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance without media_path
        THEN media_path defaults to None
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test",
            text="Hello",
        )
        assert msg.media_path is None

    def test_message_supports_all_media_types(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating instances with different media types
        THEN all standard media types are accepted
        """
        media_types = ["photo", "audio", "video", "document"]
        for media_type in media_types:
            msg = Message(
                id=1,
                date=datetime.now(UTC),
                sender_id=1001,
                sender_name="Test",
                text="Hello",
                media_type=media_type,
            )
            assert msg.media_type == media_type

    def test_message_has_optional_transcription_field(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance with transcription
        THEN transcription field is stored correctly
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test",
            text="",
            media_type="audio",
            transcription="This is the transcribed voice message",
        )
        assert msg.transcription == "This is the transcribed voice message"

    def test_message_transcription_defaults_to_none(self) -> None:
        """
        GIVEN Message dataclass
        WHEN creating an instance without transcription
        THEN transcription defaults to None
        """
        msg = Message(
            id=1,
            date=datetime.now(UTC),
            sender_id=1001,
            sender_name="Test",
            text="Hello",
        )
        assert msg.transcription is None


class TestParseMessage:
    """Test parse_message function that converts Telegram messages to Message dataclass."""

    def test_parse_message_extracts_id(self) -> None:
        """
        GIVEN a Telegram message object
        WHEN calling parse_message
        THEN message id is correctly extracted
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 12345
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "Hello"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.media = None

        result = parse_message(telegram_msg)
        assert result.id == 12345

    def test_parse_message_extracts_date(self) -> None:
        """
        GIVEN a Telegram message object
        WHEN calling parse_message
        THEN message date is correctly extracted
        """
        now = datetime.now(UTC)
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = now
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "Hello"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.media = None

        result = parse_message(telegram_msg)
        assert result.date == now

    def test_parse_message_extracts_sender_id(self) -> None:
        """
        GIVEN a Telegram message object
        WHEN calling parse_message
        THEN sender_id is correctly extracted
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 999888777
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "Hello"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.media = None

        result = parse_message(telegram_msg)
        assert result.sender_id == 999888777

    def test_parse_message_extracts_sender_name_from_first_name(self) -> None:
        """
        GIVEN a Telegram message with sender first name
        WHEN calling parse_message
        THEN sender_name contains the first name
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "John"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "Hello"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.media = None

        result = parse_message(telegram_msg)
        assert result.sender_name == "John"

    def test_parse_message_extracts_full_name(self) -> None:
        """
        GIVEN a Telegram message with sender first and last name
        WHEN calling parse_message
        THEN sender_name contains full name
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "John"
        telegram_msg.sender.last_name = "Doe"
        telegram_msg.text = "Hello"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.media = None

        result = parse_message(telegram_msg)
        assert result.sender_name == "John Doe"

    def test_parse_message_handles_no_sender(self) -> None:
        """
        GIVEN a Telegram message with no sender
        WHEN calling parse_message
        THEN sender_name is set to "Unknown"
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = None
        telegram_msg.sender = None
        telegram_msg.text = "Hello"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.media = None

        result = parse_message(telegram_msg)
        assert result.sender_name == "Unknown"
        assert result.sender_id == 0

    def test_parse_message_extracts_text(self) -> None:
        """
        GIVEN a Telegram message with text
        WHEN calling parse_message
        THEN text is correctly extracted
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "This is the message content"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.media = None

        result = parse_message(telegram_msg)
        assert result.text == "This is the message content"

    def test_parse_message_handles_empty_text(self) -> None:
        """
        GIVEN a Telegram message with no text (media only)
        WHEN calling parse_message
        THEN text is empty string
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = None
        telegram_msg.reply_to_msg_id = None
        telegram_msg.media = None

        result = parse_message(telegram_msg)
        assert result.text == ""

    def test_parse_message_extracts_reply_to(self) -> None:
        """
        GIVEN a Telegram message that is a reply
        WHEN calling parse_message
        THEN reply_to contains the original message ID
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "Hello"
        telegram_msg.reply_to_msg_id = 456
        telegram_msg.media = None

        result = parse_message(telegram_msg)
        assert result.reply_to == 456

    def test_parse_message_detects_photo_media(self) -> None:
        """
        GIVEN a Telegram message with photo
        WHEN calling parse_message
        THEN media_type is "photo"
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "Check this photo"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.photo = MagicMock()  # Has photo attribute
        telegram_msg.media = MagicMock()

        result = parse_message(telegram_msg)
        assert result.media_type == "photo"

    def test_parse_message_detects_video_media(self) -> None:
        """
        GIVEN a Telegram message with video
        WHEN calling parse_message
        THEN media_type is "video"
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "Check this video"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.photo = None
        telegram_msg.video = MagicMock()  # Has video attribute
        telegram_msg.media = MagicMock()

        result = parse_message(telegram_msg)
        assert result.media_type == "video"

    def test_parse_message_detects_audio_media(self) -> None:
        """
        GIVEN a Telegram message with audio
        WHEN calling parse_message
        THEN media_type is "audio"
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "Check this audio"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.photo = None
        telegram_msg.video = None
        telegram_msg.audio = MagicMock()  # Has audio attribute
        telegram_msg.media = MagicMock()

        result = parse_message(telegram_msg)
        assert result.media_type == "audio"

    def test_parse_message_detects_document_media(self) -> None:
        """
        GIVEN a Telegram message with document
        WHEN calling parse_message
        THEN media_type is "document"
        """
        telegram_msg = MagicMock()
        telegram_msg.id = 1
        telegram_msg.date = datetime.now(UTC)
        telegram_msg.sender_id = 1001
        telegram_msg.sender = MagicMock()
        telegram_msg.sender.first_name = "Test"
        telegram_msg.sender.last_name = None
        telegram_msg.text = "Check this file"
        telegram_msg.reply_to_msg_id = None
        telegram_msg.photo = None
        telegram_msg.video = None
        telegram_msg.audio = None
        telegram_msg.document = MagicMock()  # Has document attribute
        telegram_msg.media = MagicMock()

        result = parse_message(telegram_msg)
        assert result.media_type == "document"


class TestMessageDownloader:
    """Test MessageDownloader class for downloading messages from chats."""

    def test_can_instantiate_downloader(self) -> None:
        """
        GIVEN a TelegramClient
        WHEN creating MessageDownloader instance
        THEN instance is created successfully
        """
        mock_client = MagicMock()
        downloader = MessageDownloader(client=mock_client)
        assert downloader is not None
        assert downloader.client is mock_client

    def test_downloader_has_default_batch_size(self) -> None:
        """
        GIVEN MessageDownloader instance
        WHEN checking batch_size
        THEN default batch_size is 100
        """
        mock_client = MagicMock()
        downloader = MessageDownloader(client=mock_client)
        assert downloader.batch_size == 100

    def test_downloader_has_configurable_batch_size(self) -> None:
        """
        GIVEN custom batch_size parameter
        WHEN creating MessageDownloader instance
        THEN batch_size is set correctly
        """
        mock_client = MagicMock()
        downloader = MessageDownloader(client=mock_client, batch_size=500)
        assert downloader.batch_size == 500

    def test_downloader_has_default_delay(self) -> None:
        """
        GIVEN MessageDownloader instance
        WHEN checking delay_seconds
        THEN default delay is 0.5 seconds
        """
        mock_client = MagicMock()
        downloader = MessageDownloader(client=mock_client)
        assert downloader.delay_seconds == 0.5

    def test_downloader_has_configurable_delay(self) -> None:
        """
        GIVEN custom delay_seconds parameter
        WHEN creating MessageDownloader instance
        THEN delay_seconds is set correctly
        """
        mock_client = MagicMock()
        downloader = MessageDownloader(client=mock_client, delay_seconds=1.0)
        assert downloader.delay_seconds == 1.0


class TestDownloadMessages:
    """Test download_messages method for iterating through chat messages."""

    @pytest.mark.asyncio
    async def test_download_messages_yields_messages(self) -> None:
        """
        GIVEN a chat with messages
        WHEN calling download_messages
        THEN Message objects are yielded
        """
        mock_client = MagicMock()

        # Create mock Telegram messages
        mock_telegram_msg = MagicMock()
        mock_telegram_msg.id = 1
        mock_telegram_msg.date = datetime.now(UTC)
        mock_telegram_msg.sender_id = 1001
        mock_telegram_msg.sender = MagicMock()
        mock_telegram_msg.sender.first_name = "Test"
        mock_telegram_msg.sender.last_name = None
        mock_telegram_msg.text = "Hello"
        mock_telegram_msg.reply_to_msg_id = None
        mock_telegram_msg.media = None
        mock_telegram_msg.photo = None
        mock_telegram_msg.video = None
        mock_telegram_msg.audio = None
        mock_telegram_msg.document = None

        async def mock_iter_messages(*_args, **_kwargs):
            yield mock_telegram_msg

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        messages = []
        async for msg in downloader.download_messages(chat="test_chat"):
            messages.append(msg)

        assert len(messages) == 1
        assert isinstance(messages[0], Message)
        assert messages[0].id == 1

    @pytest.mark.asyncio
    async def test_download_messages_accepts_chat_name(self) -> None:
        """
        GIVEN a chat name string
        WHEN calling download_messages
        THEN messages from that chat are downloaded
        """
        mock_client = MagicMock()

        captured_chat = None

        async def mock_iter_messages(chat, **_kwargs):
            nonlocal captured_chat
            captured_chat = chat
            return
            yield  # Make it an async generator

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        async for _ in downloader.download_messages(chat="my_channel"):
            pass

        assert captured_chat == "my_channel"

    @pytest.mark.asyncio
    async def test_download_messages_accepts_chat_id(self) -> None:
        """
        GIVEN a chat ID integer
        WHEN calling download_messages
        THEN messages from that chat are downloaded
        """
        mock_client = MagicMock()

        captured_chat = None

        async def mock_iter_messages(chat, **_kwargs):
            nonlocal captured_chat
            captured_chat = chat
            return
            yield

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        async for _ in downloader.download_messages(chat=-1001234567890):
            pass

        assert captured_chat == -1001234567890

    @pytest.mark.asyncio
    async def test_download_messages_respects_from_date(self) -> None:
        """
        GIVEN a from_date parameter
        WHEN calling download_messages
        THEN only messages after from_date are yielded
        """
        mock_client = MagicMock()

        from_date = datetime(2024, 1, 15, tzinfo=UTC)

        # Create messages with different dates
        old_msg = MagicMock()
        old_msg.id = 1
        old_msg.date = datetime(2024, 1, 10, tzinfo=UTC)  # Before from_date
        old_msg.sender_id = 1001
        old_msg.sender = MagicMock()
        old_msg.sender.first_name = "Test"
        old_msg.sender.last_name = None
        old_msg.text = "Old message"
        old_msg.reply_to_msg_id = None
        old_msg.media = None
        old_msg.photo = None
        old_msg.video = None
        old_msg.audio = None
        old_msg.document = None

        new_msg = MagicMock()
        new_msg.id = 2
        new_msg.date = datetime(2024, 1, 20, tzinfo=UTC)  # After from_date
        new_msg.sender_id = 1001
        new_msg.sender = MagicMock()
        new_msg.sender.first_name = "Test"
        new_msg.sender.last_name = None
        new_msg.text = "New message"
        new_msg.reply_to_msg_id = None
        new_msg.media = None
        new_msg.photo = None
        new_msg.video = None
        new_msg.audio = None
        new_msg.document = None

        async def mock_iter_messages(_chat, **_kwargs):
            # Telethon returns newest first by default
            yield new_msg
            yield old_msg

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        messages = []
        async for msg in downloader.download_messages(chat="test", from_date=from_date):
            messages.append(msg)

        assert len(messages) == 1
        assert messages[0].id == 2

    @pytest.mark.asyncio
    async def test_download_messages_respects_to_date(self) -> None:
        """
        GIVEN a to_date parameter
        WHEN calling download_messages
        THEN only messages before to_date are yielded
        """
        mock_client = MagicMock()

        to_date = datetime(2024, 1, 15, tzinfo=UTC)

        # Create messages with different dates
        old_msg = MagicMock()
        old_msg.id = 1
        old_msg.date = datetime(2024, 1, 10, tzinfo=UTC)  # Before to_date
        old_msg.sender_id = 1001
        old_msg.sender = MagicMock()
        old_msg.sender.first_name = "Test"
        old_msg.sender.last_name = None
        old_msg.text = "Old message"
        old_msg.reply_to_msg_id = None
        old_msg.media = None
        old_msg.photo = None
        old_msg.video = None
        old_msg.audio = None
        old_msg.document = None

        new_msg = MagicMock()
        new_msg.id = 2
        new_msg.date = datetime(2024, 1, 20, tzinfo=UTC)  # After to_date
        new_msg.sender_id = 1001
        new_msg.sender = MagicMock()
        new_msg.sender.first_name = "Test"
        new_msg.sender.last_name = None
        new_msg.text = "New message"
        new_msg.reply_to_msg_id = None
        new_msg.media = None
        new_msg.photo = None
        new_msg.video = None
        new_msg.audio = None
        new_msg.document = None

        captured_offset_date = None

        async def mock_iter_messages(_chat, **kwargs):
            nonlocal captured_offset_date
            captured_offset_date = kwargs.get("offset_date")
            yield old_msg

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        messages = []
        async for msg in downloader.download_messages(chat="test", to_date=to_date):
            messages.append(msg)

        assert captured_offset_date == to_date
        assert len(messages) == 1

    @pytest.mark.asyncio
    async def test_download_messages_respects_limit(self) -> None:
        """
        GIVEN a limit parameter
        WHEN calling download_messages
        THEN at most limit messages are yielded
        """
        mock_client = MagicMock()

        def create_mock_msg(msg_id: int):
            msg = MagicMock()
            msg.id = msg_id
            msg.date = datetime.now(UTC)
            msg.sender_id = 1001
            msg.sender = MagicMock()
            msg.sender.first_name = "Test"
            msg.sender.last_name = None
            msg.text = f"Message {msg_id}"
            msg.reply_to_msg_id = None
            msg.media = None
            msg.photo = None
            msg.video = None
            msg.audio = None
            msg.document = None
            return msg

        captured_limit = None

        async def mock_iter_messages(_chat, **kwargs):
            nonlocal captured_limit
            captured_limit = kwargs.get("limit")
            for i in range(5):
                yield create_mock_msg(i)

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        messages = []
        async for msg in downloader.download_messages(chat="test", limit=3):
            messages.append(msg)
            if len(messages) >= 3:
                break

        assert captured_limit == 3

    @pytest.mark.asyncio
    async def test_download_messages_adds_delay_between_batches(self) -> None:
        """
        GIVEN a configured delay_seconds
        WHEN downloading multiple batches
        THEN delay is added between batches to respect rate limits
        """
        mock_client = MagicMock()

        def create_mock_msg(msg_id: int):
            msg = MagicMock()
            msg.id = msg_id
            msg.date = datetime.now(UTC)
            msg.sender_id = 1001
            msg.sender = MagicMock()
            msg.sender.first_name = "Test"
            msg.sender.last_name = None
            msg.text = f"Message {msg_id}"
            msg.reply_to_msg_id = None
            msg.media = None
            msg.photo = None
            msg.video = None
            msg.audio = None
            msg.document = None
            return msg

        async def mock_iter_messages(_chat, **_kwargs):
            # Return 25 messages - will trigger 2 delays with batch_size=10
            for i in range(25):
                yield create_mock_msg(i)

        mock_client.iter_messages = mock_iter_messages

        # batch_size=10 means delay every 10 messages
        # With 25 messages: delay after msg 10, delay after msg 20
        # That's 2 delays of 0.05s each
        downloader = MessageDownloader(client=mock_client, batch_size=10, delay_seconds=0.05)

        start_time = asyncio.get_event_loop().time()
        messages = []
        async for msg in downloader.download_messages(chat="test"):
            messages.append(msg)

        elapsed = asyncio.get_event_loop().time() - start_time

        # We should have processed 25 messages with 2 delays
        assert len(messages) == 25
        # At least some delay was added (2 * 0.05 = 0.1s minimum)
        assert elapsed >= 0.08  # Give some tolerance


class TestProgressTracking:
    """Test progress tracking during download."""

    @pytest.mark.asyncio
    async def test_download_messages_calls_progress_callback(self) -> None:
        """
        GIVEN a progress_callback parameter
        WHEN downloading messages
        THEN progress_callback is called with current progress
        """
        mock_client = MagicMock()

        def create_mock_msg(msg_id: int):
            msg = MagicMock()
            msg.id = msg_id
            msg.date = datetime.now(UTC)
            msg.sender_id = 1001
            msg.sender = MagicMock()
            msg.sender.first_name = "Test"
            msg.sender.last_name = None
            msg.text = f"Message {msg_id}"
            msg.reply_to_msg_id = None
            msg.media = None
            msg.photo = None
            msg.video = None
            msg.audio = None
            msg.document = None
            return msg

        async def mock_iter_messages(_chat, **_kwargs):
            for i in range(5):
                yield create_mock_msg(i)

        mock_client.iter_messages = mock_iter_messages

        progress_calls = []

        def progress_callback(current: int, total: int | None) -> None:
            progress_calls.append((current, total))

        downloader = MessageDownloader(client=mock_client)
        messages = []
        async for msg in downloader.download_messages(
            chat="test", progress_callback=progress_callback
        ):
            messages.append(msg)

        assert len(progress_calls) > 0
        # Last call should have the final count
        assert progress_calls[-1][0] == 5

    @pytest.mark.asyncio
    async def test_progress_callback_receives_total_when_known(self) -> None:
        """
        GIVEN a chat with known message count
        WHEN downloading with progress callback
        THEN total is passed to callback
        """
        mock_client = MagicMock()

        # Mock get_messages to get total count
        mock_client.get_messages = AsyncMock(return_value=MagicMock(total=100))

        def create_mock_msg(msg_id: int):
            msg = MagicMock()
            msg.id = msg_id
            msg.date = datetime.now(UTC)
            msg.sender_id = 1001
            msg.sender = MagicMock()
            msg.sender.first_name = "Test"
            msg.sender.last_name = None
            msg.text = f"Message {msg_id}"
            msg.reply_to_msg_id = None
            msg.media = None
            msg.photo = None
            msg.video = None
            msg.audio = None
            msg.document = None
            return msg

        async def mock_iter_messages(_chat, **_kwargs):
            for i in range(5):
                yield create_mock_msg(i)

        mock_client.iter_messages = mock_iter_messages

        progress_calls = []

        def progress_callback(current: int, total: int | None) -> None:
            progress_calls.append((current, total))

        downloader = MessageDownloader(client=mock_client)
        messages = []
        async for msg in downloader.download_messages(
            chat="test", progress_callback=progress_callback, fetch_total=True
        ):
            messages.append(msg)

        # Check that total was passed
        assert any(call[1] == 100 for call in progress_calls)


class TestReverseAndMinId:
    """Test reverse and min_id parameters for chronological download."""

    @pytest.mark.asyncio
    async def test_download_messages_with_reverse_true_passes_reverse_to_client(self) -> None:
        """
        GIVEN reverse=True parameter
        WHEN calling download_messages
        THEN reverse=True is passed to iter_messages
        """
        mock_client = MagicMock()

        captured_reverse = None

        async def mock_iter_messages(_chat, **kwargs):
            nonlocal captured_reverse
            captured_reverse = kwargs.get("reverse")
            return
            yield  # Make it an async generator

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        async for _ in downloader.download_messages(chat="test", reverse=True):
            pass

        assert captured_reverse is True

    @pytest.mark.asyncio
    async def test_download_messages_with_reverse_false_does_not_pass_reverse(self) -> None:
        """
        GIVEN reverse=False parameter (default)
        WHEN calling download_messages
        THEN reverse is not passed to iter_messages (default behavior)
        """
        mock_client = MagicMock()

        captured_kwargs = {}

        async def mock_iter_messages(_chat, **kwargs):
            nonlocal captured_kwargs
            captured_kwargs = kwargs
            return
            yield

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        async for _ in downloader.download_messages(chat="test", reverse=False):
            pass

        # reverse should not be passed when False (default behavior)
        assert captured_kwargs.get("reverse") is None or captured_kwargs.get("reverse") is False

    @pytest.mark.asyncio
    async def test_download_messages_with_min_id_passes_min_id_to_client(self) -> None:
        """
        GIVEN min_id=0 parameter
        WHEN calling download_messages
        THEN min_id=0 is passed to iter_messages
        """
        mock_client = MagicMock()

        captured_min_id = None

        async def mock_iter_messages(_chat, **kwargs):
            nonlocal captured_min_id
            captured_min_id = kwargs.get("min_id")
            return
            yield

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        async for _ in downloader.download_messages(chat="test", min_id=0):
            pass

        assert captured_min_id == 0

    @pytest.mark.asyncio
    async def test_download_messages_default_min_id_is_none(self) -> None:
        """
        GIVEN no min_id parameter
        WHEN calling download_messages
        THEN min_id is not passed to iter_messages
        """
        mock_client = MagicMock()

        captured_kwargs = {}

        async def mock_iter_messages(_chat, **kwargs):
            nonlocal captured_kwargs
            captured_kwargs = kwargs
            return
            yield

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        async for _ in downloader.download_messages(chat="test"):
            pass

        assert "min_id" not in captured_kwargs or captured_kwargs.get("min_id") is None

    @pytest.mark.asyncio
    async def test_download_messages_reverse_and_min_id_together(self) -> None:
        """
        GIVEN reverse=True and min_id=0 parameters
        WHEN calling download_messages
        THEN both are passed to iter_messages for chronological download
        """
        mock_client = MagicMock()

        captured_reverse = None
        captured_min_id = None

        async def mock_iter_messages(_chat, **kwargs):
            nonlocal captured_reverse, captured_min_id
            captured_reverse = kwargs.get("reverse")
            captured_min_id = kwargs.get("min_id")
            return
            yield

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        async for _ in downloader.download_messages(chat="test", reverse=True, min_id=0):
            pass

        assert captured_reverse is True
        assert captured_min_id == 0


class TestMessageStorage:
    """Test message metadata storage for later processing."""

    @pytest.mark.asyncio
    async def test_downloader_can_store_messages(self) -> None:
        """
        GIVEN a MessageDownloader
        WHEN downloading messages with store=True
        THEN messages are stored in internal list
        """
        mock_client = MagicMock()

        def create_mock_msg(msg_id: int):
            msg = MagicMock()
            msg.id = msg_id
            msg.date = datetime.now(UTC)
            msg.sender_id = 1001
            msg.sender = MagicMock()
            msg.sender.first_name = "Test"
            msg.sender.last_name = None
            msg.text = f"Message {msg_id}"
            msg.reply_to_msg_id = None
            msg.media = None
            msg.photo = None
            msg.video = None
            msg.audio = None
            msg.document = None
            return msg

        async def mock_iter_messages(_chat, **_kwargs):
            for i in range(3):
                yield create_mock_msg(i)

        mock_client.iter_messages = mock_iter_messages

        downloader = MessageDownloader(client=mock_client)
        async for _ in downloader.download_messages(chat="test", store=True):
            pass

        assert len(downloader.messages) == 3
        assert all(isinstance(m, Message) for m in downloader.messages)

    def test_downloader_messages_initially_empty(self) -> None:
        """
        GIVEN a new MessageDownloader
        WHEN checking messages attribute
        THEN it is an empty list
        """
        mock_client = MagicMock()
        downloader = MessageDownloader(client=mock_client)
        assert downloader.messages == []

    def test_downloader_can_clear_stored_messages(self) -> None:
        """
        GIVEN a MessageDownloader with stored messages
        WHEN calling clear_messages()
        THEN stored messages are cleared
        """
        mock_client = MagicMock()
        downloader = MessageDownloader(client=mock_client)

        # Manually add some messages
        downloader.messages.append(
            Message(
                id=1,
                date=datetime.now(UTC),
                sender_id=1001,
                sender_name="Test",
                text="Hello",
            )
        )

        assert len(downloader.messages) == 1
        downloader.clear_messages()
        assert len(downloader.messages) == 0
