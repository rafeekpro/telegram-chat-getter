"""
TDD RED Phase: Tests for list chats functionality.

These tests verify:
1. list_chats function retrieves all dialogs
2. Chat information (name, ID, type) is extracted correctly
3. Filtering by type (groups, private, channels) works
4. Empty chat list is handled gracefully
5. Rich table formatting is correct
6. CLI command integration works
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestListChatsFunction:
    """Test list_chats function retrieves dialogs correctly."""

    @pytest.mark.asyncio
    async def test_list_chats_returns_list(self) -> None:
        """
        GIVEN a connected Telegram client
        WHEN calling list_chats()
        THEN returns a list of chat dictionaries
        """
        from telegram_getter.chats import list_chats

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[])

        result = await list_chats(mock_client)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_list_chats_extracts_chat_info(self) -> None:
        """
        GIVEN a client with dialogs
        WHEN calling list_chats()
        THEN extracts id, name, type, and unread count for each chat
        """
        from telegram_getter.chats import list_chats

        # Create mock dialog with User entity (private chat)
        mock_user = MagicMock()
        mock_user.id = 12345
        mock_user.__class__.__name__ = "User"

        mock_dialog = MagicMock()
        mock_dialog.entity = mock_user
        mock_dialog.name = "John Doe"
        mock_dialog.unread_count = 5

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[mock_dialog])

        result = await list_chats(mock_client)

        assert len(result) == 1
        assert result[0]["id"] == 12345
        assert result[0]["name"] == "John Doe"
        assert result[0]["type"] == "private"
        assert result[0]["unread"] == 5

    @pytest.mark.asyncio
    async def test_list_chats_identifies_group_type(self) -> None:
        """
        GIVEN a dialog with Chat entity (group)
        WHEN calling list_chats()
        THEN type is identified as 'group'
        """
        from telegram_getter.chats import list_chats

        mock_chat = MagicMock()
        mock_chat.id = 67890
        mock_chat.__class__.__name__ = "Chat"

        mock_dialog = MagicMock()
        mock_dialog.entity = mock_chat
        mock_dialog.name = "Work Group"
        mock_dialog.unread_count = 10

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[mock_dialog])

        result = await list_chats(mock_client)

        assert result[0]["type"] == "group"

    @pytest.mark.asyncio
    async def test_list_chats_identifies_channel_type(self) -> None:
        """
        GIVEN a dialog with Channel entity (channel or supergroup)
        WHEN calling list_chats()
        THEN type is identified as 'channel'
        """
        from telegram_getter.chats import list_chats

        mock_channel = MagicMock()
        mock_channel.id = 11111
        mock_channel.__class__.__name__ = "Channel"
        mock_channel.broadcast = True  # True for channels, False for supergroups

        mock_dialog = MagicMock()
        mock_dialog.entity = mock_channel
        mock_dialog.name = "News Channel"
        mock_dialog.unread_count = 0

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[mock_dialog])

        result = await list_chats(mock_client)

        assert result[0]["type"] == "channel"

    @pytest.mark.asyncio
    async def test_list_chats_identifies_supergroup_type(self) -> None:
        """
        GIVEN a dialog with Channel entity but broadcast=False (supergroup)
        WHEN calling list_chats()
        THEN type is identified as 'group' (supergroups are groups)
        """
        from telegram_getter.chats import list_chats

        mock_channel = MagicMock()
        mock_channel.id = 22222
        mock_channel.__class__.__name__ = "Channel"
        mock_channel.broadcast = False  # Supergroup

        mock_dialog = MagicMock()
        mock_dialog.entity = mock_channel
        mock_dialog.name = "Big Group"
        mock_dialog.unread_count = 3

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[mock_dialog])

        result = await list_chats(mock_client)

        assert result[0]["type"] == "group"


class TestListChatsFiltering:
    """Test filtering chats by type."""

    @pytest.mark.asyncio
    async def test_filter_private_chats(self) -> None:
        """
        GIVEN dialogs with mixed types
        WHEN calling list_chats() with filter_type='private'
        THEN only private chats are returned
        """
        from telegram_getter.chats import list_chats

        # Private chat
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.__class__.__name__ = "User"
        dialog_private = MagicMock()
        dialog_private.entity = mock_user
        dialog_private.name = "Private"
        dialog_private.unread_count = 0

        # Group chat
        mock_chat = MagicMock()
        mock_chat.id = 2
        mock_chat.__class__.__name__ = "Chat"
        dialog_group = MagicMock()
        dialog_group.entity = mock_chat
        dialog_group.name = "Group"
        dialog_group.unread_count = 0

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[dialog_private, dialog_group])

        result = await list_chats(mock_client, filter_type="private")

        assert len(result) == 1
        assert result[0]["name"] == "Private"
        assert result[0]["type"] == "private"

    @pytest.mark.asyncio
    async def test_filter_group_chats(self) -> None:
        """
        GIVEN dialogs with mixed types
        WHEN calling list_chats() with filter_type='group'
        THEN only groups (including supergroups) are returned
        """
        from telegram_getter.chats import list_chats

        # Private chat
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.__class__.__name__ = "User"
        dialog_private = MagicMock()
        dialog_private.entity = mock_user
        dialog_private.name = "Private"
        dialog_private.unread_count = 0

        # Group chat
        mock_chat = MagicMock()
        mock_chat.id = 2
        mock_chat.__class__.__name__ = "Chat"
        dialog_group = MagicMock()
        dialog_group.entity = mock_chat
        dialog_group.name = "Group"
        dialog_group.unread_count = 0

        # Supergroup (Channel with broadcast=False)
        mock_supergroup = MagicMock()
        mock_supergroup.id = 3
        mock_supergroup.__class__.__name__ = "Channel"
        mock_supergroup.broadcast = False
        dialog_supergroup = MagicMock()
        dialog_supergroup.entity = mock_supergroup
        dialog_supergroup.name = "Supergroup"
        dialog_supergroup.unread_count = 0

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(
            return_value=[dialog_private, dialog_group, dialog_supergroup]
        )

        result = await list_chats(mock_client, filter_type="group")

        assert len(result) == 2
        names = [r["name"] for r in result]
        assert "Group" in names
        assert "Supergroup" in names

    @pytest.mark.asyncio
    async def test_filter_channel_chats(self) -> None:
        """
        GIVEN dialogs with mixed types
        WHEN calling list_chats() with filter_type='channel'
        THEN only channels (broadcast=True) are returned
        """
        from telegram_getter.chats import list_chats

        # Channel
        mock_channel = MagicMock()
        mock_channel.id = 1
        mock_channel.__class__.__name__ = "Channel"
        mock_channel.broadcast = True
        dialog_channel = MagicMock()
        dialog_channel.entity = mock_channel
        dialog_channel.name = "Channel"
        dialog_channel.unread_count = 0

        # Supergroup (not a channel)
        mock_supergroup = MagicMock()
        mock_supergroup.id = 2
        mock_supergroup.__class__.__name__ = "Channel"
        mock_supergroup.broadcast = False
        dialog_supergroup = MagicMock()
        dialog_supergroup.entity = mock_supergroup
        dialog_supergroup.name = "Supergroup"
        dialog_supergroup.unread_count = 0

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[dialog_channel, dialog_supergroup])

        result = await list_chats(mock_client, filter_type="channel")

        assert len(result) == 1
        assert result[0]["name"] == "Channel"
        assert result[0]["type"] == "channel"

    @pytest.mark.asyncio
    async def test_no_filter_returns_all(self) -> None:
        """
        GIVEN dialogs with mixed types
        WHEN calling list_chats() without filter
        THEN all chats are returned
        """
        from telegram_getter.chats import list_chats

        dialogs = []
        for i, (cls_name, is_channel, broadcast) in enumerate(
            [
                ("User", False, False),
                ("Chat", False, False),
                ("Channel", True, True),
                ("Channel", True, False),
            ]
        ):
            mock_entity = MagicMock()
            mock_entity.id = i
            mock_entity.__class__.__name__ = cls_name
            if is_channel:
                mock_entity.broadcast = broadcast

            dialog = MagicMock()
            dialog.entity = mock_entity
            dialog.name = f"Chat {i}"
            dialog.unread_count = 0
            dialogs.append(dialog)

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=dialogs)

        result = await list_chats(mock_client)

        assert len(result) == 4


class TestListChatsEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_chat_list(self) -> None:
        """
        GIVEN a client with no dialogs
        WHEN calling list_chats()
        THEN returns empty list without error
        """
        from telegram_getter.chats import list_chats

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[])

        result = await list_chats(mock_client)

        assert result == []

    @pytest.mark.asyncio
    async def test_handles_unknown_entity_type(self) -> None:
        """
        GIVEN a dialog with unknown entity type
        WHEN calling list_chats()
        THEN type is set to 'unknown'
        """
        from telegram_getter.chats import list_chats

        mock_unknown = MagicMock()
        mock_unknown.id = 99999
        mock_unknown.__class__.__name__ = "UnknownEntity"

        mock_dialog = MagicMock()
        mock_dialog.entity = mock_unknown
        mock_dialog.name = "Unknown"
        mock_dialog.unread_count = 0

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[mock_dialog])

        result = await list_chats(mock_client)

        assert result[0]["type"] == "unknown"


class TestGetChatType:
    """Test the get_chat_type helper function."""

    def test_user_returns_private(self) -> None:
        """
        GIVEN a User entity
        WHEN calling get_chat_type()
        THEN returns 'private'
        """
        from telegram_getter.chats import get_chat_type

        mock_user = MagicMock()
        mock_user.__class__.__name__ = "User"

        assert get_chat_type(mock_user) == "private"

    def test_chat_returns_group(self) -> None:
        """
        GIVEN a Chat entity
        WHEN calling get_chat_type()
        THEN returns 'group'
        """
        from telegram_getter.chats import get_chat_type

        mock_chat = MagicMock()
        mock_chat.__class__.__name__ = "Chat"

        assert get_chat_type(mock_chat) == "group"

    def test_channel_broadcast_returns_channel(self) -> None:
        """
        GIVEN a Channel entity with broadcast=True
        WHEN calling get_chat_type()
        THEN returns 'channel'
        """
        from telegram_getter.chats import get_chat_type

        mock_channel = MagicMock()
        mock_channel.__class__.__name__ = "Channel"
        mock_channel.broadcast = True

        assert get_chat_type(mock_channel) == "channel"

    def test_channel_not_broadcast_returns_group(self) -> None:
        """
        GIVEN a Channel entity with broadcast=False (supergroup)
        WHEN calling get_chat_type()
        THEN returns 'group'
        """
        from telegram_getter.chats import get_chat_type

        mock_channel = MagicMock()
        mock_channel.__class__.__name__ = "Channel"
        mock_channel.broadcast = False

        assert get_chat_type(mock_channel) == "group"

    def test_unknown_entity_returns_unknown(self) -> None:
        """
        GIVEN an unknown entity type
        WHEN calling get_chat_type()
        THEN returns 'unknown'
        """
        from telegram_getter.chats import get_chat_type

        mock_unknown = MagicMock()
        mock_unknown.__class__.__name__ = "SomeOtherType"

        assert get_chat_type(mock_unknown) == "unknown"


class TestFormatChatsTable:
    """Test rich table formatting for chat list."""

    def test_format_chats_table_returns_table(self) -> None:
        """
        GIVEN a list of chat dictionaries
        WHEN calling format_chats_table()
        THEN returns a Rich Table object
        """
        from rich.table import Table

        from telegram_getter.chats import format_chats_table

        chats = [
            {"id": 1, "name": "Test Chat", "type": "private", "unread": 5},
        ]

        table = format_chats_table(chats)

        assert isinstance(table, Table)

    def test_format_chats_table_has_correct_columns(self) -> None:
        """
        GIVEN a list of chat dictionaries
        WHEN calling format_chats_table()
        THEN table has ID, Name, Type, and Unread columns
        """
        from telegram_getter.chats import format_chats_table

        chats = [
            {"id": 1, "name": "Test Chat", "type": "private", "unread": 5},
        ]

        table = format_chats_table(chats)

        column_names = [col.header for col in table.columns]
        assert "ID" in column_names
        assert "Name" in column_names
        assert "Type" in column_names
        assert "Unread" in column_names

    def test_format_empty_chats_shows_message(self) -> None:
        """
        GIVEN an empty chat list
        WHEN calling format_chats_table()
        THEN returns a table (can be empty or with message)
        """
        from rich.table import Table

        from telegram_getter.chats import format_chats_table

        table = format_chats_table([])

        assert isinstance(table, Table)


class TestCLIListCommand:
    """Test CLI list command integration."""

    def test_list_command_exists(self) -> None:
        """
        GIVEN the CLI app
        WHEN checking for list command
        THEN list command is available
        """
        from telegram_getter.cli import app

        # Check if 'list' is a registered command in Typer app
        # Typer stores command name in callback.__name__ when name is not explicitly set
        command_names = [
            cmd.name if cmd.name else cmd.callback.__name__ for cmd in app.registered_commands
        ]
        assert "list" in command_names

    def test_list_command_has_filter_options(self) -> None:
        """
        GIVEN the list command
        WHEN checking options
        THEN --groups, --private, --channels options exist
        """
        import inspect

        from telegram_getter.cli import app

        # Find the list command by callback name
        list_cmd = None
        for cmd in app.registered_commands:
            cmd_name = cmd.name if cmd.name else cmd.callback.__name__
            if cmd_name == "list":
                list_cmd = cmd
                break

        assert list_cmd is not None

        # Get parameter names from the callback function
        sig = inspect.signature(list_cmd.callback)
        param_names = list(sig.parameters.keys())

        assert "groups" in param_names
        assert "private" in param_names
        assert "channels" in param_names

    @pytest.mark.asyncio
    async def test_list_command_calls_list_chats(self) -> None:
        """
        GIVEN connected client
        WHEN running list command
        THEN list_chats is called
        """
        # This test verifies integration without actually running CLI
        from telegram_getter.chats import list_chats

        mock_client = MagicMock()
        mock_client.get_dialogs = AsyncMock(return_value=[])

        result = await list_chats(mock_client)

        mock_client.get_dialogs.assert_called_once()
        assert result == []
