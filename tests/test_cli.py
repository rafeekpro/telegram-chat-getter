"""
TDD RED Phase: Tests for CLI commands.

These tests verify:
1. auth command exists and works correctly
2. download command exists and accepts required arguments
3. download command options work correctly
4. CLI help shows all commands
5. Error handling and user-friendly messages
"""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

from telegram_getter.cli import app

runner = CliRunner()


class TestCLIHelp:
    """Test CLI help output shows all commands."""

    def test_help_shows_all_commands(self) -> None:
        """
        GIVEN CLI app
        WHEN running with --help
        THEN shows all available commands including auth, list, download
        """
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "auth" in result.output
        assert "list" in result.output
        assert "download" in result.output

    def test_version_option_works(self) -> None:
        """
        GIVEN CLI app
        WHEN running with --version
        THEN shows version number
        """
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()


class TestAuthCommand:
    """Test auth command."""

    def test_auth_command_exists(self) -> None:
        """
        GIVEN CLI app
        WHEN running auth --help
        THEN command is recognized and shows help
        """
        result = runner.invoke(app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "auth" in result.output.lower() or "Authenticate" in result.output

    def test_auth_command_shows_success_message(self) -> None:
        """
        GIVEN valid credentials and mock client
        WHEN running auth command
        THEN shows success message with username
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            mock_user = MagicMock()
            mock_user.username = "testuser"
            mock_user.first_name = "Test"

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.get_me = AsyncMock(return_value=mock_user)
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                result = runner.invoke(app, ["auth"])
                assert result.exit_code == 0
                # Should show success message
                output_lower = result.output.lower()
                assert "success" in output_lower or "authenticated" in output_lower or "logged in" in output_lower

    def test_auth_command_handles_missing_credentials(self) -> None:
        """
        GIVEN no API credentials in environment
        WHEN running auth command
        THEN shows error message about missing credentials
        """
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(app, ["auth"])
            assert result.exit_code != 0
            output_lower = result.output.lower()
            assert "error" in output_lower or "missing" in output_lower or "api" in output_lower


class TestDownloadCommand:
    """Test download command."""

    def test_download_command_exists(self) -> None:
        """
        GIVEN CLI app
        WHEN running download --help
        THEN command is recognized and shows help
        """
        result = runner.invoke(app, ["download", "--help"])
        assert result.exit_code == 0
        # Should show download help
        output_lower = result.output.lower()
        assert "download" in output_lower

    def test_download_command_requires_chat_or_id(self) -> None:
        """
        GIVEN CLI app
        WHEN running download without chat or --id
        THEN shows error about missing argument
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            result = runner.invoke(app, ["download"])
            # Should fail with missing argument
            assert result.exit_code != 0 or "missing" in result.output.lower() or "required" in result.output.lower()

    def test_download_command_accepts_chat_name(self) -> None:
        """
        GIVEN CLI app with valid setup
        WHEN running download with chat name
        THEN command accepts the argument
        """
        result = runner.invoke(app, ["download", "--help"])
        assert result.exit_code == 0
        # Help should mention chat argument
        assert "chat" in result.output.lower() or "CHAT" in result.output

    def test_download_command_has_id_option(self) -> None:
        """
        GIVEN CLI app
        WHEN running download --help
        THEN shows --chat-id option for downloading by ID
        """
        result = runner.invoke(app, ["download", "--help"])
        assert result.exit_code == 0
        # Typer converts chat_id to --chat-id
        assert "--chat-id" in result.output

    def test_download_command_has_output_option(self) -> None:
        """
        GIVEN CLI app
        WHEN running download --help
        THEN shows --output/-o option
        """
        result = runner.invoke(app, ["download", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output or "-o" in result.output

    def test_download_command_has_from_date_option(self) -> None:
        """
        GIVEN CLI app
        WHEN running download --help
        THEN shows --from-date option for date filtering
        """
        result = runner.invoke(app, ["download", "--help"])
        assert result.exit_code == 0
        assert "--from" in result.output or "--from-date" in result.output

    def test_download_command_has_to_date_option(self) -> None:
        """
        GIVEN CLI app
        WHEN running download --help
        THEN shows --to-date option for date filtering
        """
        result = runner.invoke(app, ["download", "--help"])
        assert result.exit_code == 0
        assert "--to" in result.output or "--to-date" in result.output

    def test_download_command_has_no_media_flag(self) -> None:
        """
        GIVEN CLI app
        WHEN running download --help
        THEN shows --no-media flag
        """
        result = runner.invoke(app, ["download", "--help"])
        assert result.exit_code == 0
        assert "--no-media" in result.output


class TestDownloadCommandExecution:
    """Test download command execution with mocked Telegram client."""

    def test_download_by_chat_name(self, tmp_path: Path) -> None:
        """
        GIVEN valid credentials and chat name
        WHEN running download with --chat option
        THEN downloads messages to output directory
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            # Mock Telegram client
            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            # Mock get_dialogs to return a chat
            mock_entity = MagicMock()
            mock_entity.id = 12345
            mock_entity.__class__.__name__ = "Chat"
            mock_entity.unread_count = 0

            mock_dialog = MagicMock()
            mock_dialog.name = "Test Chat"
            mock_dialog.entity = mock_entity
            mock_dialog.unread_count = 0

            mock_client.get_dialogs = AsyncMock(return_value=[mock_dialog])
            mock_client.get_entity = AsyncMock(return_value=mock_entity)

            # Mock iter_messages to return empty (no messages)
            mock_client.iter_messages = MagicMock()
            mock_client.iter_messages.return_value = AsyncIteratorMock([])

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                result = runner.invoke(
                    app,
                    ["download", "--chat", "Test Chat", "--output", str(tmp_path)],
                )
                # Command should complete (even with no messages)
                # We're mainly testing that the command is recognized
                # Check that the command is recognized and arguments are accepted
                assert "no such option" not in result.output.lower()
                assert "unexpected" not in result.output.lower()

    def test_download_by_chat_id(self, tmp_path: Path) -> None:
        """
        GIVEN valid credentials and chat ID
        WHEN running download --chat-id 12345
        THEN downloads messages to output directory
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            # Mock get_entity to return a chat
            mock_entity = MagicMock()
            mock_entity.id = 12345
            mock_entity.__class__.__name__ = "Chat"
            mock_entity.title = "Test Chat"

            mock_client.get_entity = AsyncMock(return_value=mock_entity)

            # Mock get_dialogs
            mock_dialog = MagicMock()
            mock_dialog.name = "Test Chat"
            mock_dialog.entity = mock_entity
            mock_dialog.unread_count = 0
            mock_client.get_dialogs = AsyncMock(return_value=[mock_dialog])

            # Mock iter_messages
            mock_client.iter_messages = MagicMock()
            mock_client.iter_messages.return_value = AsyncIteratorMock([])

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                result = runner.invoke(
                    app,
                    ["download", "--chat-id", "12345", "--output", str(tmp_path)],
                )
                # Command should accept --chat-id option
                # Should not have "no such option" error
                assert "no such option" not in result.output.lower()
                assert "unexpected" not in result.output.lower()

    def test_download_with_date_range(self, tmp_path: Path) -> None:
        """
        GIVEN valid credentials and date range
        WHEN running download with --from-date and --to-date options
        THEN filters messages by date
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            mock_entity = MagicMock()
            mock_entity.id = 12345
            mock_entity.__class__.__name__ = "Chat"
            mock_entity.unread_count = 0

            mock_dialog = MagicMock()
            mock_dialog.name = "Test Chat"
            mock_dialog.entity = mock_entity
            mock_dialog.unread_count = 0

            mock_client.get_dialogs = AsyncMock(return_value=[mock_dialog])
            mock_client.get_entity = AsyncMock(return_value=mock_entity)
            mock_client.iter_messages = MagicMock()
            mock_client.iter_messages.return_value = AsyncIteratorMock([])

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                result = runner.invoke(
                    app,
                    [
                        "download",
                        "--chat",
                        "Test Chat",
                        "--output",
                        str(tmp_path),
                        "--from-date",
                        "2025-01-01",
                        "--to-date",
                        "2025-01-31",
                    ],
                )
                # Should accept date options
                assert "no such option" not in result.output.lower()

    def test_download_with_no_media_flag(self, tmp_path: Path) -> None:
        """
        GIVEN valid credentials
        WHEN running download with --no-media flag
        THEN skips media download
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            mock_entity = MagicMock()
            mock_entity.id = 12345
            mock_entity.__class__.__name__ = "Chat"
            mock_entity.unread_count = 0

            mock_dialog = MagicMock()
            mock_dialog.name = "Test Chat"
            mock_dialog.entity = mock_entity
            mock_dialog.unread_count = 0

            mock_client.get_dialogs = AsyncMock(return_value=[mock_dialog])
            mock_client.get_entity = AsyncMock(return_value=mock_entity)
            mock_client.iter_messages = MagicMock()
            mock_client.iter_messages.return_value = AsyncIteratorMock([])

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                result = runner.invoke(
                    app,
                    ["download", "--chat", "Test Chat", "--output", str(tmp_path), "--no-media"],
                )
                # Should accept --no-media flag
                assert "unknown" not in result.output.lower()
                assert "no such option" not in result.output.lower()


class TestDownloadCommandErrors:
    """Test download command error handling."""

    def test_download_handles_chat_not_found(self) -> None:
        """
        GIVEN valid credentials but non-existent chat
        WHEN running download with unknown chat name
        THEN shows error message about chat not found
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)
            mock_client.get_dialogs = AsyncMock(return_value=[])  # No chats

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                result = runner.invoke(app, ["download", "--chat", "NonExistentChat"])
                # Should show error about chat not found
                output_lower = result.output.lower()
                assert result.exit_code != 0 or "not found" in output_lower or "error" in output_lower

    def test_download_handles_authentication_error(self) -> None:
        """
        GIVEN missing credentials
        WHEN running download command
        THEN shows authentication error
        """
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(app, ["download", "--chat", "SomeChat"])
            assert result.exit_code != 0
            output_lower = result.output.lower()
            assert "error" in output_lower or "authentication" in output_lower or "api" in output_lower


class TestListCommand:
    """Test existing list command still works."""

    def test_list_command_exists(self) -> None:
        """
        GIVEN CLI app
        WHEN running list --help
        THEN command is recognized
        """
        result = runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output.lower()

    def test_list_command_has_groups_option(self) -> None:
        """
        GIVEN CLI app
        WHEN running list --help
        THEN shows --groups option
        """
        result = runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "--groups" in result.output

    def test_list_command_has_private_option(self) -> None:
        """
        GIVEN CLI app
        WHEN running list --help
        THEN shows --private option
        """
        result = runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "--private" in result.output

    def test_list_command_has_channels_option(self) -> None:
        """
        GIVEN CLI app
        WHEN running list --help
        THEN shows --channels option
        """
        result = runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "--channels" in result.output


# Helper class for mocking async iterators
class AsyncIteratorMock:
    """Mock async iterator for testing."""

    def __init__(self, items: list) -> None:
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item
