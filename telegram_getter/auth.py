"""
Authentication module for Telegram API.

Provides TelegramAuth class for managing Telegram client authentication,
including session persistence, 2FA support, and graceful error handling.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv
from telethon import TelegramClient

if TYPE_CHECKING:
    from telethon.tl.types import User

DEFAULT_SESSION_NAME = "telegram_getter"

# Error message constants
_ERR_MISSING_CREDENTIALS = (
    "Missing required credentials: {missing}. "
    "Please set them in your .env file or environment variables. "
    "You can get these from https://my.telegram.org/apps"
)
_ERR_NETWORK_FAILED = (
    "Network connection failed: {error}. " "Please check your internet connection and try again."
)
_ERR_INVALID_CREDENTIALS = (
    "Invalid credentials: {error}. " "Please verify your API_ID and API_HASH are correct."
)
_ERR_AUTH_FAILED = "Authentication failed: {error}. " "Please try again or check your credentials."
_ERR_NOT_CONNECTED = "Not connected to Telegram. Call connect() first."


class AuthenticationError(Exception):
    """Exception raised for authentication-related errors."""


class TelegramAuth:
    """
    Manages Telegram client authentication with session persistence.

    Handles:
    - Loading API credentials from environment
    - Creating and managing TelegramClient
    - Session file persistence for reconnection
    - 2FA password support
    - Graceful error handling

    Usage:
        # Basic usage
        auth = TelegramAuth()
        client = await auth.connect()
        # ... use client ...
        await auth.disconnect()

        # As context manager
        async with TelegramAuth() as client:
            # ... use client ...
    """

    def __init__(
        self,
        session_file: str = DEFAULT_SESSION_NAME,
        session_path: Path | None = None,
    ) -> None:
        """
        Initialize TelegramAuth with credentials from environment.

        Args:
            session_file: Name for the session file (default: "telegram_getter")
            session_path: Optional directory path for session storage

        Raises:
            AuthenticationError: If API_ID or API_HASH environment variables are missing
        """
        # Load .env file if it exists
        load_dotenv()

        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")
        self.session_file = session_file
        self.session_path = session_path
        self.client: TelegramClient | None = None

        # Validate credentials
        self._validate_credentials()

    def _validate_credentials(self) -> None:
        """
        Validate that required API credentials are present.

        Raises:
            AuthenticationError: If credentials are missing
        """
        missing = []
        if not self.api_id:
            missing.append("API_ID")
        if not self.api_hash:
            missing.append("API_HASH")

        if missing:
            missing_str = " and ".join(missing)
            msg = _ERR_MISSING_CREDENTIALS.format(missing=missing_str)
            raise AuthenticationError(msg)

    def get_session_path(self) -> Path:
        """
        Get the full path for the session file.

        Returns:
            Path object pointing to the session file location
        """
        if self.session_path:
            return self.session_path / self.session_file
        return Path.cwd() / self.session_file

    async def connect(
        self,
        phone: Callable[[], str] | str | None = None,
        code_callback: Callable[[], str] | None = None,
        password: Callable[[], str] | str | None = None,
    ) -> TelegramClient:
        """
        Connect to Telegram and authenticate if needed.

        If a valid session exists, it will be reused without re-authentication.
        Otherwise, the user will be prompted for phone number and verification code.

        Args:
            phone: Phone number or callback to get phone number
            code_callback: Callback to get verification code
            password: 2FA password or callback to get password

        Returns:
            Connected TelegramClient instance

        Raises:
            AuthenticationError: If connection or authentication fails
        """
        session_path = self.get_session_path()

        try:
            self.client = TelegramClient(
                str(session_path),
                int(self.api_id),  # type: ignore[arg-type]
                self.api_hash,  # type: ignore[arg-type]
            )

            # Build start kwargs
            start_kwargs: dict[str, Any] = {}
            if phone is not None:
                start_kwargs["phone"] = phone
            if code_callback is not None:
                start_kwargs["code_callback"] = code_callback
            if password is not None:
                start_kwargs["password"] = password

            await self.client.start(**start_kwargs)
            return self.client

        except ConnectionError as e:
            self.client = None
            msg = _ERR_NETWORK_FAILED.format(error=e)
            raise AuthenticationError(msg) from e
        except ValueError as e:
            self.client = None
            msg = _ERR_INVALID_CREDENTIALS.format(error=e)
            raise AuthenticationError(msg) from e
        except Exception as e:
            self.client = None
            msg = _ERR_AUTH_FAILED.format(error=e)
            raise AuthenticationError(msg) from e

    async def disconnect(self) -> None:
        """
        Disconnect from Telegram.

        Safe to call even if not connected.
        """
        if self.client:
            await self.client.disconnect()
            self.client = None

    async def is_authorized(self) -> bool:
        """
        Check if the client is connected and authorized.

        Returns:
            True if connected and authorized, False otherwise
        """
        if not self.client:
            return False
        return await self.client.is_user_authorized()

    async def get_me(self) -> User:
        """
        Get information about the currently authenticated user.

        Returns:
            User object with information about current user

        Raises:
            AuthenticationError: If not connected
        """
        if not self.client:
            raise AuthenticationError(_ERR_NOT_CONNECTED)
        return await self.client.get_me()  # type: ignore[return-value]

    async def __aenter__(self) -> TelegramClient:
        """Enter async context manager."""
        return await self.connect()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit async context manager."""
        await self.disconnect()


# Legacy function-based API for backwards compatibility
async def create_client(
    api_id: str,
    api_hash: str,
    session_name: str = DEFAULT_SESSION_NAME,
    session_path: Path | None = None,
) -> TelegramClient:
    """
    Create and return a TelegramClient instance.

    This is a legacy function. Consider using TelegramAuth class instead.

    Args:
        api_id: Telegram API ID
        api_hash: Telegram API Hash
        session_name: Name for the session file
        session_path: Optional path for session storage

    Returns:
        Configured TelegramClient instance
    """
    session_file = session_path / session_name if session_path else Path.cwd() / session_name
    return TelegramClient(str(session_file), int(api_id), api_hash)


async def authenticate(client: TelegramClient) -> bool:
    """
    Authenticate the client with Telegram.

    This is a legacy function. Consider using TelegramAuth class instead.

    Args:
        client: TelegramClient instance to authenticate

    Returns:
        True if authentication successful, False otherwise
    """
    await client.start()
    return await client.is_user_authorized()


async def get_me(client: TelegramClient) -> Any:
    """
    Get information about the authenticated user.

    This is a legacy function. Consider using TelegramAuth class instead.

    Args:
        client: Authenticated TelegramClient instance

    Returns:
        User object with information about current user
    """
    return await client.get_me()
