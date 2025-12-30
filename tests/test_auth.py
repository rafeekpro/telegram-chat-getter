"""
TDD RED Phase: Tests for Telegram authentication module.

These tests verify:
1. TelegramAuth class can be instantiated
2. API credentials are loaded from environment
3. connect() returns a TelegramClient
4. disconnect() works gracefully
5. Error handling for missing credentials
6. Session persistence logic
7. 2FA password handling
"""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_getter.auth import AuthenticationError, TelegramAuth


class TestTelegramAuthInstantiation:
    """Test TelegramAuth class instantiation."""

    def test_can_instantiate_telegram_auth(self) -> None:
        """
        GIVEN valid environment variables
        WHEN creating TelegramAuth instance
        THEN instance is created successfully
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()
            assert auth is not None
            assert isinstance(auth, TelegramAuth)

    def test_default_session_name(self) -> None:
        """
        GIVEN no session_file parameter
        WHEN creating TelegramAuth instance
        THEN default session name is used
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()
            assert auth.session_file == "telegram_getter"

    def test_custom_session_name(self) -> None:
        """
        GIVEN custom session_file parameter
        WHEN creating TelegramAuth instance
        THEN custom session name is used
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth(session_file="my_custom_session")
            assert auth.session_file == "my_custom_session"

    def test_custom_session_path(self) -> None:
        """
        GIVEN custom session_path parameter
        WHEN creating TelegramAuth instance
        THEN custom session path is used
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            custom_path = Path("/tmp/telegram_sessions")
            auth = TelegramAuth(session_path=custom_path)
            assert auth.session_path == custom_path

    def test_client_initially_none(self) -> None:
        """
        GIVEN a new TelegramAuth instance
        WHEN checking client attribute
        THEN client is None before connect()
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()
            assert auth.client is None


class TestCredentialLoading:
    """Test that API credentials are loaded correctly from environment."""

    def test_loads_api_id_from_environment(self) -> None:
        """
        GIVEN API_ID in environment
        WHEN creating TelegramAuth instance
        THEN api_id is loaded correctly
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()
            assert auth.api_id == "12345"

    def test_loads_api_hash_from_environment(self) -> None:
        """
        GIVEN API_HASH in environment
        WHEN creating TelegramAuth instance
        THEN api_hash is loaded correctly
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()
            assert auth.api_hash == "abc123hash"

    def test_raises_error_when_api_id_missing(self) -> None:
        """
        GIVEN API_ID not in environment
        WHEN creating TelegramAuth instance
        THEN AuthenticationError is raised
        """
        with patch.dict(os.environ, {"API_HASH": "abc123hash"}, clear=True):
            with pytest.raises(AuthenticationError) as exc_info:
                TelegramAuth()
            assert "API_ID" in str(exc_info.value)

    def test_raises_error_when_api_hash_missing(self) -> None:
        """
        GIVEN API_HASH not in environment
        WHEN creating TelegramAuth instance
        THEN AuthenticationError is raised
        """
        with patch.dict(os.environ, {"API_ID": "12345"}, clear=True):
            with pytest.raises(AuthenticationError) as exc_info:
                TelegramAuth()
            assert "API_HASH" in str(exc_info.value)

    def test_raises_error_with_friendly_message_for_missing_credentials(self) -> None:
        """
        GIVEN no credentials in environment
        WHEN creating TelegramAuth instance
        THEN error message is user-friendly
        """
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError) as exc_info:
                TelegramAuth()
            error_msg = str(exc_info.value)
            assert "API_ID" in error_msg or "API_HASH" in error_msg
            # Should suggest how to fix
            assert ".env" in error_msg.lower() or "environment" in error_msg.lower()


class TestConnect:
    """Test connect() method returns TelegramClient."""

    @pytest.mark.asyncio
    async def test_connect_returns_telegram_client(self) -> None:
        """
        GIVEN valid credentials
        WHEN calling connect()
        THEN returns TelegramClient instance
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            # Mock TelegramClient
            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                client = await auth.connect()
                assert client is not None
                assert auth.client is client

    @pytest.mark.asyncio
    async def test_connect_calls_client_start(self) -> None:
        """
        GIVEN valid credentials
        WHEN calling connect()
        THEN client.start() is called
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                await auth.connect()
                mock_client.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_creates_client_with_correct_params(self) -> None:
        """
        GIVEN valid credentials and session file
        WHEN calling connect()
        THEN TelegramClient is created with correct parameters
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth(session_file="test_session")

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client) as mock_cls:
                await auth.connect()
                # Check that TelegramClient was called with session file, api_id, api_hash
                call_args = mock_cls.call_args
                assert call_args is not None
                # First positional arg should contain session file name
                assert "test_session" in str(call_args[0][0])
                # api_id should be int
                assert call_args[0][1] == 12345
                # api_hash should be string
                assert call_args[0][2] == "abc123hash"

    @pytest.mark.asyncio
    async def test_connect_uses_session_path_if_provided(self) -> None:
        """
        GIVEN custom session_path
        WHEN calling connect()
        THEN session file is created in that path
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            custom_path = Path("/custom/sessions")
            auth = TelegramAuth(session_file="my_session", session_path=custom_path)

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client) as mock_cls:
                await auth.connect()
                call_args = mock_cls.call_args
                session_arg = str(call_args[0][0])
                assert "custom/sessions" in session_arg
                assert "my_session" in session_arg


class TestDisconnect:
    """Test disconnect() method."""

    @pytest.mark.asyncio
    async def test_disconnect_calls_client_disconnect(self) -> None:
        """
        GIVEN connected TelegramAuth
        WHEN calling disconnect()
        THEN client.disconnect() is called
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                await auth.connect()
                await auth.disconnect()
                mock_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_works_when_not_connected(self) -> None:
        """
        GIVEN TelegramAuth not connected
        WHEN calling disconnect()
        THEN no error is raised
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()
            # Should not raise
            await auth.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect_sets_client_to_none(self) -> None:
        """
        GIVEN connected TelegramAuth
        WHEN calling disconnect()
        THEN client is set to None
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                await auth.connect()
                assert auth.client is not None
                await auth.disconnect()
                assert auth.client is None


class TestSessionPersistence:
    """Test session file persistence."""

    def test_session_file_path_is_deterministic(self) -> None:
        """
        GIVEN same session_file name
        WHEN creating TelegramAuth multiple times
        THEN session path is the same
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth1 = TelegramAuth(session_file="persistent_session")
            auth2 = TelegramAuth(session_file="persistent_session")
            assert auth1.get_session_path() == auth2.get_session_path()

    @pytest.mark.asyncio
    async def test_existing_session_is_reused(self) -> None:
        """
        GIVEN existing session file
        WHEN calling connect()
        THEN session is reused (no re-authentication needed)
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                await auth.connect()
                # If session exists and is valid, is_user_authorized returns True
                is_authorized = await auth.is_authorized()
                assert is_authorized is True


class TestAuthorizationStatus:
    """Test authorization status checking."""

    @pytest.mark.asyncio
    async def test_is_authorized_returns_true_when_authorized(self) -> None:
        """
        GIVEN connected and authorized client
        WHEN calling is_authorized()
        THEN returns True
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                await auth.connect()
                assert await auth.is_authorized() is True

    @pytest.mark.asyncio
    async def test_is_authorized_returns_false_when_not_connected(self) -> None:
        """
        GIVEN TelegramAuth not connected
        WHEN calling is_authorized()
        THEN returns False
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()
            assert await auth.is_authorized() is False


class TestTwoFactorAuth:
    """Test 2FA password handling."""

    @pytest.mark.asyncio
    async def test_connect_with_2fa_password(self) -> None:
        """
        GIVEN 2FA is enabled on account
        WHEN calling connect() with password callback
        THEN password is requested and used
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            # The password callback should be passable to start()
            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):

                def password_callback() -> str:
                    return "my2fapassword"

                await auth.connect(password=password_callback)
                # Verify start was called (password handling is internal to telethon)
                mock_client.start.assert_called_once()


class TestContextManager:
    """Test async context manager support."""

    @pytest.mark.asyncio
    async def test_can_use_as_async_context_manager(self) -> None:
        """
        GIVEN TelegramAuth instance
        WHEN using as async context manager
        THEN connect is called on enter and disconnect on exit
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                async with auth as client:
                    assert client is not None
                    mock_client.start.assert_called_once()

                mock_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_disconnects_on_exception(self) -> None:
        """
        GIVEN TelegramAuth as context manager
        WHEN exception occurs inside context
        THEN disconnect is still called
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                test_error_msg = "Test error"
                with pytest.raises(ValueError, match=test_error_msg):
                    async with auth:
                        raise ValueError(test_error_msg)

                mock_client.disconnect.assert_called_once()


class TestGetCurrentUser:
    """Test getting current user information."""

    @pytest.mark.asyncio
    async def test_get_me_returns_user_info(self) -> None:
        """
        GIVEN connected and authorized client
        WHEN calling get_me()
        THEN returns user information
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_user = MagicMock()
            mock_user.id = 123456789
            mock_user.username = "testuser"
            mock_user.first_name = "Test"

            mock_client = MagicMock()
            mock_client.start = AsyncMock()
            mock_client.get_me = AsyncMock(return_value=mock_user)
            mock_client.is_user_authorized = AsyncMock(return_value=True)

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                await auth.connect()
                user = await auth.get_me()
                assert user is not None
                assert user.id == 123456789
                assert user.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_me_raises_when_not_connected(self) -> None:
        """
        GIVEN TelegramAuth not connected
        WHEN calling get_me()
        THEN raises AuthenticationError
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()
            with pytest.raises(AuthenticationError) as exc_info:
                await auth.get_me()
            assert "not connected" in str(exc_info.value).lower()


class TestErrorHandling:
    """Test error handling for various failure scenarios."""

    @pytest.mark.asyncio
    async def test_connect_handles_network_error(self) -> None:
        """
        GIVEN network is unavailable
        WHEN calling connect()
        THEN raises AuthenticationError with helpful message
        """
        with patch.dict(os.environ, {"API_ID": "12345", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock(side_effect=ConnectionError("Network unreachable"))

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                with pytest.raises(AuthenticationError) as exc_info:
                    await auth.connect()
                error_msg = str(exc_info.value).lower()
                assert "network" in error_msg or "connection" in error_msg

    @pytest.mark.asyncio
    async def test_connect_handles_invalid_credentials(self) -> None:
        """
        GIVEN invalid API credentials
        WHEN calling connect()
        THEN raises AuthenticationError with helpful message
        """
        with patch.dict(os.environ, {"API_ID": "invalid", "API_HASH": "abc123hash"}):
            auth = TelegramAuth()

            mock_client = MagicMock()
            mock_client.start = AsyncMock(side_effect=ValueError("Invalid API ID"))

            with patch("telegram_getter.auth.TelegramClient", return_value=mock_client):
                with pytest.raises(AuthenticationError) as exc_info:
                    await auth.connect()
                error_msg = str(exc_info.value).lower()
                assert "invalid" in error_msg or "credentials" in error_msg
