"""
Chat listing module for Telegram API.

Provides functions to list and filter Telegram dialogs (chats, groups, channels),
with rich table formatting for CLI output.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.table import Table

if TYPE_CHECKING:
    from collections.abc import Sequence

    from telethon import TelegramClient

# Chat type constants
CHAT_TYPE_PRIVATE = "private"
CHAT_TYPE_GROUP = "group"
CHAT_TYPE_CHANNEL = "channel"
CHAT_TYPE_UNKNOWN = "unknown"


def get_chat_type(entity: Any) -> str:
    """
    Determine the type of a Telegram entity.

    Args:
        entity: Telegram entity (User, Chat, or Channel)

    Returns:
        String indicating the chat type: 'private', 'group', 'channel', or 'unknown'
    """
    entity_type = entity.__class__.__name__

    if entity_type == "User":
        return CHAT_TYPE_PRIVATE
    if entity_type == "Chat":
        return CHAT_TYPE_GROUP
    if entity_type == "Channel":
        # Channels with broadcast=True are channels
        # Channels with broadcast=False are supergroups (treated as groups)
        if getattr(entity, "broadcast", False):
            return CHAT_TYPE_CHANNEL
        return CHAT_TYPE_GROUP
    return CHAT_TYPE_UNKNOWN


async def list_chats(
    client: TelegramClient,
    filter_type: str | None = None,
) -> list[dict[str, Any]]:
    """
    List all dialogs (chats, groups, channels) from Telegram.

    Args:
        client: Connected TelegramClient instance
        filter_type: Optional filter - 'private', 'group', or 'channel'

    Returns:
        List of dictionaries with chat information:
        - id: Chat ID
        - name: Chat name
        - type: Chat type (private, group, channel)
        - unread: Number of unread messages
    """
    dialogs = await client.get_dialogs()
    chats: list[dict[str, Any]] = []

    for dialog in dialogs:
        entity = dialog.entity
        chat_type = get_chat_type(entity)

        # Apply filter if specified
        if filter_type and chat_type != filter_type:
            continue

        chats.append(
            {
                "id": entity.id,
                "name": dialog.name,
                "type": chat_type,
                "unread": dialog.unread_count,
            }
        )

    return chats


def format_chats_table(chats: Sequence[dict[str, Any]]) -> Table:
    """
    Format a list of chats as a Rich table for display.

    Args:
        chats: List of chat dictionaries from list_chats()

    Returns:
        Rich Table object ready for display
    """
    table = Table(title="Telegram Chats")

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Type", style="magenta")
    table.add_column("Unread", style="yellow", justify="right")

    for chat in chats:
        unread_str = str(chat["unread"]) if chat["unread"] > 0 else "-"
        table.add_row(
            str(chat["id"]),
            chat["name"],
            chat["type"],
            unread_str,
        )

    return table
