"""
Voice message transcription using Telegram Premium API.

Provides functionality to transcribe voice messages using Telegram's
built-in transcription API. Requires Telegram Premium or limited free uses.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from telethon import functions

if TYPE_CHECKING:
    from telethon import TelegramClient


async def transcribe_voice_message(
    client: TelegramClient,
    peer: int | str,
    msg_id: int,
    max_wait: int = 30,
) -> str | None:
    """
    Transcribe a voice message using Telegram's API.

    Uses Telegram's TranscribeAudioRequest API to convert voice messages
    to text. This feature requires Telegram Premium or uses limited free
    transcription quota.

    If the transcription is initially pending, the function will poll
    every 2 seconds until completion or timeout.

    Args:
        client: Authenticated TelegramClient
        peer: Chat ID (int) or username (str) containing the voice message
        msg_id: Message ID to transcribe
        max_wait: Maximum seconds to wait for transcription (default: 30)

    Returns:
        Transcription text if successful, None if:
        - Transcription failed
        - No Premium subscription
        - Quota exceeded
        - Timeout waiting for transcription
        - Any other error

    Example:
        >>> async with client:
        ...     text = await transcribe_voice_message(client, chat_id, msg_id)
        ...     if text:
        ...         print(f"Transcription: {text}")
        ...     else:
        ...         print("Transcription not available")
    """
    try:
        result = await client(
            functions.messages.TranscribeAudioRequest(
                peer=peer,
                msg_id=msg_id,
            )
        )

        # If pending, wait for completion
        wait_time = 0
        while getattr(result, "pending", False) and wait_time < max_wait:
            await asyncio.sleep(2)
            wait_time += 2
            # Re-fetch transcription status
            result = await client(
                functions.messages.TranscribeAudioRequest(
                    peer=peer,
                    msg_id=msg_id,
                )
            )

        return getattr(result, "text", None)
    except Exception:
        # Transcription not available (no Premium, quota exceeded, etc.)
        return None
