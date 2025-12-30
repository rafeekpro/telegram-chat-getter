"""
TDD RED Phase: Tests for Telegram media downloader module.

These tests verify:
1. get_media_type() detects media types correctly
2. generate_filename() creates proper filenames from message dates
3. MediaDownloader class for downloading media files
4. Proper folder structure creation
5. Duplicate file handling
6. Progress callback support
"""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from telegram_getter.media import (
    MediaDownloader,
    generate_filename,
    get_media_type,
)


class TestGetMediaType:
    """Test get_media_type function that detects media type from Telegram media."""

    def test_get_media_type_returns_images_for_photo(self) -> None:
        """
        GIVEN a MessageMediaPhoto object
        WHEN calling get_media_type
        THEN returns "images"
        """
        # Create mock MessageMediaPhoto
        media = MagicMock()
        media.__class__.__name__ = "MessageMediaPhoto"

        result = get_media_type(media)
        assert result == "images"

    def test_get_media_type_returns_audio_for_audio_mime(self) -> None:
        """
        GIVEN a MessageMediaDocument with audio/* MIME type
        WHEN calling get_media_type
        THEN returns "audio"
        """
        media = MagicMock()
        media.__class__.__name__ = "MessageMediaDocument"
        media.document = MagicMock()
        media.document.mime_type = "audio/ogg"

        result = get_media_type(media)
        assert result == "audio"

    def test_get_media_type_returns_audio_for_mp3(self) -> None:
        """
        GIVEN a MessageMediaDocument with audio/mpeg MIME type
        WHEN calling get_media_type
        THEN returns "audio"
        """
        media = MagicMock()
        media.__class__.__name__ = "MessageMediaDocument"
        media.document = MagicMock()
        media.document.mime_type = "audio/mpeg"

        result = get_media_type(media)
        assert result == "audio"

    def test_get_media_type_returns_video_for_video_mime(self) -> None:
        """
        GIVEN a MessageMediaDocument with video/* MIME type
        WHEN calling get_media_type
        THEN returns "video"
        """
        media = MagicMock()
        media.__class__.__name__ = "MessageMediaDocument"
        media.document = MagicMock()
        media.document.mime_type = "video/mp4"

        result = get_media_type(media)
        assert result == "video"

    def test_get_media_type_returns_video_for_webm(self) -> None:
        """
        GIVEN a MessageMediaDocument with video/webm MIME type
        WHEN calling get_media_type
        THEN returns "video"
        """
        media = MagicMock()
        media.__class__.__name__ = "MessageMediaDocument"
        media.document = MagicMock()
        media.document.mime_type = "video/webm"

        result = get_media_type(media)
        assert result == "video"

    def test_get_media_type_returns_documents_for_pdf(self) -> None:
        """
        GIVEN a MessageMediaDocument with application/pdf MIME type
        WHEN calling get_media_type
        THEN returns "documents"
        """
        media = MagicMock()
        media.__class__.__name__ = "MessageMediaDocument"
        media.document = MagicMock()
        media.document.mime_type = "application/pdf"

        result = get_media_type(media)
        assert result == "documents"

    def test_get_media_type_returns_documents_for_xlsx(self) -> None:
        """
        GIVEN a MessageMediaDocument with spreadsheet MIME type
        WHEN calling get_media_type
        THEN returns "documents"
        """
        media = MagicMock()
        media.__class__.__name__ = "MessageMediaDocument"
        media.document = MagicMock()
        media.document.mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        result = get_media_type(media)
        assert result == "documents"

    def test_get_media_type_returns_other_for_unknown_media(self) -> None:
        """
        GIVEN an unknown media type
        WHEN calling get_media_type
        THEN returns "other"
        """
        media = MagicMock()
        media.__class__.__name__ = "UnknownMediaType"

        result = get_media_type(media)
        assert result == "other"

    def test_get_media_type_returns_other_for_none_document(self) -> None:
        """
        GIVEN a MessageMediaDocument with no document attribute
        WHEN calling get_media_type
        THEN returns "other"
        """
        media = MagicMock()
        media.__class__.__name__ = "MessageMediaDocument"
        media.document = None

        result = get_media_type(media)
        assert result == "other"

    def test_get_media_type_returns_other_for_none_mime_type(self) -> None:
        """
        GIVEN a MessageMediaDocument with no MIME type
        WHEN calling get_media_type
        THEN returns "other"
        """
        media = MagicMock()
        media.__class__.__name__ = "MessageMediaDocument"
        media.document = MagicMock()
        media.document.mime_type = None

        result = get_media_type(media)
        assert result == "other"


class TestGenerateFilename:
    """Test generate_filename function that creates filenames from message date."""

    def test_generate_filename_uses_message_date(self) -> None:
        """
        GIVEN a message with a specific date
        WHEN calling generate_filename
        THEN filename contains the date in YYYY-MM-DD format
        """
        message = MagicMock()
        message.date = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)

        result = generate_filename(message, "jpg")
        assert result.startswith("2025-01-15_")

    def test_generate_filename_includes_sequence_number(self) -> None:
        """
        GIVEN a message
        WHEN calling generate_filename with sequence
        THEN filename contains 3-digit zero-padded sequence
        """
        message = MagicMock()
        message.date = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)

        result = generate_filename(message, "jpg", sequence=1)
        assert result == "2025-01-15_001.jpg"

    def test_generate_filename_with_larger_sequence(self) -> None:
        """
        GIVEN a message with sequence > 99
        WHEN calling generate_filename
        THEN filename contains properly formatted sequence
        """
        message = MagicMock()
        message.date = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)

        result = generate_filename(message, "mp4", sequence=123)
        assert result == "2025-01-15_123.mp4"

    def test_generate_filename_with_different_extensions(self) -> None:
        """
        GIVEN different file extensions
        WHEN calling generate_filename
        THEN correct extension is used
        """
        message = MagicMock()
        message.date = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)

        assert generate_filename(message, "png", sequence=1).endswith(".png")
        assert generate_filename(message, "mp3", sequence=1).endswith(".mp3")
        assert generate_filename(message, "pdf", sequence=1).endswith(".pdf")

    def test_generate_filename_defaults_sequence_to_one(self) -> None:
        """
        GIVEN a message without sequence parameter
        WHEN calling generate_filename
        THEN sequence defaults to 1
        """
        message = MagicMock()
        message.date = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)

        result = generate_filename(message, "jpg")
        assert result == "2025-01-15_001.jpg"

    def test_generate_filename_with_different_dates(self) -> None:
        """
        GIVEN messages with different dates
        WHEN calling generate_filename
        THEN each produces unique date prefix
        """
        message1 = MagicMock()
        message1.date = datetime(2025, 1, 15, tzinfo=UTC)

        message2 = MagicMock()
        message2.date = datetime(2024, 12, 25, tzinfo=UTC)

        result1 = generate_filename(message1, "jpg", sequence=1)
        result2 = generate_filename(message2, "jpg", sequence=1)

        assert result1 == "2025-01-15_001.jpg"
        assert result2 == "2024-12-25_001.jpg"


class TestMediaDownloaderInit:
    """Test MediaDownloader class initialization."""

    def test_media_downloader_requires_client(self) -> None:
        """
        GIVEN a TelegramClient
        WHEN creating MediaDownloader instance
        THEN client is stored correctly
        """
        mock_client = MagicMock()
        output_dir = Path("/tmp/test")

        downloader = MediaDownloader(client=mock_client, output_dir=output_dir)

        assert downloader.client is mock_client

    def test_media_downloader_requires_output_dir(self) -> None:
        """
        GIVEN an output directory path
        WHEN creating MediaDownloader instance
        THEN output_dir is stored correctly
        """
        mock_client = MagicMock()
        output_dir = Path("/tmp/test/output")

        downloader = MediaDownloader(client=mock_client, output_dir=output_dir)

        assert downloader.output_dir == output_dir

    def test_media_downloader_accepts_path_object(self) -> None:
        """
        GIVEN a Path object for output_dir
        WHEN creating MediaDownloader instance
        THEN it is accepted
        """
        mock_client = MagicMock()
        output_dir = Path("/tmp/test/output")

        downloader = MediaDownloader(client=mock_client, output_dir=output_dir)

        assert isinstance(downloader.output_dir, Path)


class TestMediaDownloaderDownload:
    """Test MediaDownloader.download_media method."""

    @pytest.mark.asyncio
    async def test_download_media_skips_message_without_media(self) -> None:
        """
        GIVEN a message without media
        WHEN calling download_media
        THEN returns None
        """
        mock_client = MagicMock()
        output_dir = Path("/tmp/test")
        downloader = MediaDownloader(client=mock_client, output_dir=output_dir)

        message = MagicMock()
        message.media = None

        result = await downloader.download_media(message)

        assert result is None

    @pytest.mark.asyncio
    async def test_download_media_creates_media_subfolder(self, tmp_path: Path) -> None:
        """
        GIVEN a message with photo media
        WHEN calling download_media
        THEN creates media/images/ subfolder
        """
        mock_client = MagicMock()
        mock_client.download_media = AsyncMock(return_value=str(tmp_path / "photo.jpg"))

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaPhoto"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        await downloader.download_media(message)

        # Check that media/images folder was created
        assert (tmp_path / "media" / "images").exists()

    @pytest.mark.asyncio
    async def test_download_media_returns_relative_path(self, tmp_path: Path) -> None:
        """
        GIVEN a message with media
        WHEN download_media succeeds
        THEN returns relative path from output_dir
        """
        mock_client = MagicMock()
        expected_path = tmp_path / "media" / "images" / "2025-01-15_001.jpg"
        mock_client.download_media = AsyncMock(return_value=str(expected_path))

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaPhoto"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        result = await downloader.download_media(message)

        assert result is not None
        assert result.startswith("media/images/")

    @pytest.mark.asyncio
    async def test_download_media_skips_existing_files(self, tmp_path: Path) -> None:
        """
        GIVEN a file that already exists
        WHEN calling download_media for same message
        THEN skips download and returns existing path
        """
        mock_client = MagicMock()

        # Create existing file
        media_dir = tmp_path / "media" / "images"
        media_dir.mkdir(parents=True)
        existing_file = media_dir / "2025-01-15_001.jpg"
        existing_file.write_text("existing content")

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaPhoto"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        result = await downloader.download_media(message)

        # Should not call download_media on client
        mock_client.download_media.assert_not_called()
        # Should return existing path
        assert result == "media/images/2025-01-15_001.jpg"

    @pytest.mark.asyncio
    async def test_download_media_with_progress_callback(self, tmp_path: Path) -> None:
        """
        GIVEN a progress callback
        WHEN downloading media
        THEN progress callback is passed to client
        """
        mock_client = MagicMock()
        expected_path = tmp_path / "media" / "images" / "2025-01-15_001.jpg"
        mock_client.download_media = AsyncMock(return_value=str(expected_path))

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaPhoto"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        progress_callback = MagicMock()
        await downloader.download_media(message, progress_callback=progress_callback)

        # Verify download_media was called with progress_callback
        mock_client.download_media.assert_called_once()
        call_kwargs = mock_client.download_media.call_args[1]
        assert "progress_callback" in call_kwargs

    @pytest.mark.asyncio
    async def test_download_media_creates_audio_folder(self, tmp_path: Path) -> None:
        """
        GIVEN a message with audio media
        WHEN calling download_media
        THEN creates media/audio/ subfolder
        """
        mock_client = MagicMock()
        expected_path = tmp_path / "media" / "audio" / "2025-01-15_001.ogg"
        mock_client.download_media = AsyncMock(return_value=str(expected_path))

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaDocument"
        message.media.document = MagicMock()
        message.media.document.mime_type = "audio/ogg"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        await downloader.download_media(message)

        assert (tmp_path / "media" / "audio").exists()

    @pytest.mark.asyncio
    async def test_download_media_creates_video_folder(self, tmp_path: Path) -> None:
        """
        GIVEN a message with video media
        WHEN calling download_media
        THEN creates media/video/ subfolder
        """
        mock_client = MagicMock()
        expected_path = tmp_path / "media" / "video" / "2025-01-15_001.mp4"
        mock_client.download_media = AsyncMock(return_value=str(expected_path))

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaDocument"
        message.media.document = MagicMock()
        message.media.document.mime_type = "video/mp4"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        await downloader.download_media(message)

        assert (tmp_path / "media" / "video").exists()

    @pytest.mark.asyncio
    async def test_download_media_creates_documents_folder(self, tmp_path: Path) -> None:
        """
        GIVEN a message with document media
        WHEN calling download_media
        THEN creates media/documents/ subfolder
        """
        mock_client = MagicMock()
        expected_path = tmp_path / "media" / "documents" / "2025-01-15_001.pdf"
        mock_client.download_media = AsyncMock(return_value=str(expected_path))

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaDocument"
        message.media.document = MagicMock()
        message.media.document.mime_type = "application/pdf"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        await downloader.download_media(message)

        assert (tmp_path / "media" / "documents").exists()

    @pytest.mark.asyncio
    async def test_download_media_returns_none_on_download_failure(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN a download that fails
        WHEN calling download_media
        THEN returns None
        """
        mock_client = MagicMock()
        mock_client.download_media = AsyncMock(return_value=None)

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaPhoto"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        result = await downloader.download_media(message)

        assert result is None

    @pytest.mark.asyncio
    async def test_download_media_tracks_sequence_per_date(self, tmp_path: Path) -> None:
        """
        GIVEN multiple messages on same date
        WHEN downloading each
        THEN sequence numbers increment correctly
        """
        mock_client = MagicMock()

        call_count = 0

        async def mock_download(*_args, **kwargs):
            nonlocal call_count
            call_count += 1
            file_path = kwargs.get("file")
            if file_path:
                return str(file_path)
            return None

        mock_client.download_media = mock_download

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        # First message
        message1 = MagicMock()
        message1.media = MagicMock()
        message1.media.__class__.__name__ = "MessageMediaPhoto"
        message1.date = datetime(2025, 1, 15, tzinfo=UTC)
        message1.id = 1

        # Second message same date
        message2 = MagicMock()
        message2.media = MagicMock()
        message2.media.__class__.__name__ = "MessageMediaPhoto"
        message2.date = datetime(2025, 1, 15, tzinfo=UTC)
        message2.id = 2

        result1 = await downloader.download_media(message1)
        result2 = await downloader.download_media(message2)

        # Both should have different sequence numbers
        assert result1 is not None
        assert result2 is not None
        assert "001" in result1
        assert "002" in result2


class TestMediaDownloaderExtension:
    """Test MediaDownloader extension detection and handling."""

    @pytest.mark.asyncio
    async def test_download_media_uses_jpg_for_photos(self, tmp_path: Path) -> None:
        """
        GIVEN a photo message
        WHEN downloading
        THEN uses .jpg extension
        """
        mock_client = MagicMock()
        mock_client.download_media = AsyncMock(
            return_value=str(tmp_path / "media" / "images" / "2025-01-15_001.jpg")
        )

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaPhoto"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        result = await downloader.download_media(message)

        assert result is not None
        assert result.endswith(".jpg")

    @pytest.mark.asyncio
    async def test_download_media_extracts_extension_from_filename(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN a document with filename attribute
        WHEN downloading
        THEN extracts extension from original filename
        """
        mock_client = MagicMock()
        mock_client.download_media = AsyncMock(
            return_value=str(tmp_path / "media" / "documents" / "2025-01-15_001.pdf")
        )

        downloader = MediaDownloader(client=mock_client, output_dir=tmp_path)

        message = MagicMock()
        message.media = MagicMock()
        message.media.__class__.__name__ = "MessageMediaDocument"
        message.media.document = MagicMock()
        message.media.document.mime_type = "application/pdf"
        message.media.document.attributes = [MagicMock()]
        message.media.document.attributes[0].file_name = "report.pdf"
        message.date = datetime(2025, 1, 15, tzinfo=UTC)
        message.id = 1

        result = await downloader.download_media(message)

        assert result is not None
        assert result.endswith(".pdf")
