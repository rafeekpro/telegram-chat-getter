"""
TDD RED Phase: Tests for Telegram voice message transcription module.

These tests verify:
1. transcribe_voice_message function with valid input
2. Handling of pending transcription with polling
3. Error handling for no Premium, quota exceeded, etc.
4. Timeout handling for long-running transcriptions
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestTranscribeVoiceMessage:
    """Test transcribe_voice_message function."""

    @pytest.mark.asyncio
    async def test_transcribe_voice_message_returns_text_on_success(self) -> None:
        """
        GIVEN a voice message that can be transcribed
        WHEN calling transcribe_voice_message
        THEN the transcription text is returned
        """
        from telegram_getter.transcriber import transcribe_voice_message

        # Create mock client that is callable (using AsyncMock for __call__)
        mock_client = AsyncMock()

        # Mock successful transcription result
        mock_result = MagicMock()
        mock_result.pending = False
        mock_result.text = "Hello, this is a voice message transcription"

        mock_client.return_value = mock_result

        result = await transcribe_voice_message(
            client=mock_client,
            peer=12345,
            msg_id=100,
        )

        assert result == "Hello, this is a voice message transcription"

    @pytest.mark.asyncio
    async def test_transcribe_voice_message_accepts_username_as_peer(self) -> None:
        """
        GIVEN a username string as peer
        WHEN calling transcribe_voice_message
        THEN the request is made with the username
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()
        mock_result = MagicMock()
        mock_result.pending = False
        mock_result.text = "Transcribed text"

        mock_client.return_value = mock_result

        result = await transcribe_voice_message(
            client=mock_client,
            peer="@my_channel",
            msg_id=100,
        )

        assert result == "Transcribed text"

    @pytest.mark.asyncio
    async def test_transcribe_voice_message_waits_for_pending_transcription(self) -> None:
        """
        GIVEN a transcription that is initially pending
        WHEN calling transcribe_voice_message
        THEN it polls until transcription is complete
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()

        # First call returns pending, second call returns complete
        pending_result = MagicMock()
        pending_result.pending = True
        pending_result.text = None

        complete_result = MagicMock()
        complete_result.pending = False
        complete_result.text = "Transcription complete"

        mock_client.side_effect = [pending_result, complete_result]

        with patch("telegram_getter.transcriber.asyncio.sleep", new_callable=AsyncMock):
            result = await transcribe_voice_message(
                client=mock_client,
                peer=12345,
                msg_id=100,
                max_wait=30,
            )

        assert result == "Transcription complete"
        assert mock_client.call_count == 2

    @pytest.mark.asyncio
    async def test_transcribe_voice_message_respects_max_wait_timeout(self) -> None:
        """
        GIVEN a transcription that stays pending
        WHEN max_wait time is exceeded
        THEN None is returned
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()

        # Always returns pending
        pending_result = MagicMock()
        pending_result.pending = True
        pending_result.text = None

        mock_client.return_value = pending_result

        # Use very short max_wait and mock sleep to speed up test
        with patch("telegram_getter.transcriber.asyncio.sleep", new_callable=AsyncMock):
            result = await transcribe_voice_message(
                client=mock_client,
                peer=12345,
                msg_id=100,
                max_wait=4,  # Will timeout after 2 polls (2+2 = 4 seconds)
            )

        # Should return None when timed out (no text available)
        assert result is None

    @pytest.mark.asyncio
    async def test_transcribe_voice_message_returns_none_on_error(self) -> None:
        """
        GIVEN an error during transcription (no Premium, quota exceeded, etc.)
        WHEN calling transcribe_voice_message
        THEN None is returned without raising exception
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()
        mock_client.side_effect = Exception("PREMIUM_REQUIRED")

        result = await transcribe_voice_message(
            client=mock_client,
            peer=12345,
            msg_id=100,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_transcribe_voice_message_returns_none_for_missing_text(self) -> None:
        """
        GIVEN a transcription result with no text attribute
        WHEN calling transcribe_voice_message
        THEN None is returned
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()

        # Result with no text attribute (use spec to exclude 'text')
        mock_result = MagicMock(spec=["pending"])
        mock_result.pending = False
        # Note: mock_result.text will raise AttributeError due to spec

        # Use a regular MagicMock and delete text attribute
        mock_result = MagicMock()
        mock_result.pending = False
        del mock_result.text

        mock_client.return_value = mock_result

        result = await transcribe_voice_message(
            client=mock_client,
            peer=12345,
            msg_id=100,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_transcribe_voice_message_default_max_wait_is_30_seconds(self) -> None:
        """
        GIVEN no max_wait parameter
        WHEN calling transcribe_voice_message
        THEN default max_wait is 30 seconds
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()
        mock_result = MagicMock()
        mock_result.pending = False
        mock_result.text = "Text"

        mock_client.return_value = mock_result

        # The function should accept call without max_wait
        result = await transcribe_voice_message(
            client=mock_client,
            peer=12345,
            msg_id=100,
            # max_wait not specified - should default to 30
        )

        assert result == "Text"

    @pytest.mark.asyncio
    async def test_transcribe_voice_message_uses_correct_api_request(self) -> None:
        """
        GIVEN valid parameters
        WHEN calling transcribe_voice_message
        THEN it uses TranscribeAudioRequest with correct parameters
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()
        mock_result = MagicMock()
        mock_result.pending = False
        mock_result.text = "Transcribed"

        mock_client.return_value = mock_result

        await transcribe_voice_message(
            client=mock_client,
            peer=12345,
            msg_id=100,
        )

        # Check that client was called
        assert mock_client.call_count == 1
        # Get the request that was passed
        call_args = mock_client.call_args
        request = call_args[0][0]
        # Check that it's a TranscribeAudioRequest
        assert request.__class__.__name__ == "TranscribeAudioRequest"
        assert request.peer == 12345
        assert request.msg_id == 100


class TestTranscribeVoiceMessagePolling:
    """Test polling behavior during transcription."""

    @pytest.mark.asyncio
    async def test_polling_interval_is_2_seconds(self) -> None:
        """
        GIVEN a pending transcription
        WHEN polling for completion
        THEN the interval between polls is 2 seconds
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()

        # First pending, then complete
        pending_result = MagicMock()
        pending_result.pending = True
        pending_result.text = None

        complete_result = MagicMock()
        complete_result.pending = False
        complete_result.text = "Done"

        mock_client.side_effect = [pending_result, complete_result]

        sleep_calls = []

        async def mock_sleep(duration):
            sleep_calls.append(duration)

        with patch("telegram_getter.transcriber.asyncio.sleep", mock_sleep):
            await transcribe_voice_message(
                client=mock_client,
                peer=12345,
                msg_id=100,
            )

        assert sleep_calls == [2]

    @pytest.mark.asyncio
    async def test_multiple_polling_attempts(self) -> None:
        """
        GIVEN a transcription that takes multiple polls to complete
        WHEN calling transcribe_voice_message
        THEN it continues polling until complete or timeout
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()

        # Returns pending 3 times, then complete
        pending_result = MagicMock()
        pending_result.pending = True
        pending_result.text = None

        complete_result = MagicMock()
        complete_result.pending = False
        complete_result.text = "Finally done"

        mock_client.side_effect = [
            pending_result,
            pending_result,
            pending_result,
            complete_result,
        ]

        with patch("telegram_getter.transcriber.asyncio.sleep", new_callable=AsyncMock):
            result = await transcribe_voice_message(
                client=mock_client,
                peer=12345,
                msg_id=100,
                max_wait=30,
            )

        assert result == "Finally done"
        assert mock_client.call_count == 4


class TestTranscribeVoiceMessageErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_handles_flood_wait_error(self) -> None:
        """
        GIVEN a FloodWaitError from Telegram
        WHEN calling transcribe_voice_message
        THEN None is returned gracefully
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()
        mock_client.side_effect = Exception("A wait of 60 seconds is required")

        result = await transcribe_voice_message(
            client=mock_client,
            peer=12345,
            msg_id=100,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_handles_message_not_found_error(self) -> None:
        """
        GIVEN a message that doesn't exist
        WHEN calling transcribe_voice_message
        THEN None is returned
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()
        mock_client.side_effect = Exception("MESSAGE_ID_INVALID")

        result = await transcribe_voice_message(
            client=mock_client,
            peer=12345,
            msg_id=99999,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_handles_network_error(self) -> None:
        """
        GIVEN a network error during transcription
        WHEN calling transcribe_voice_message
        THEN None is returned
        """
        from telegram_getter.transcriber import transcribe_voice_message

        mock_client = AsyncMock()
        mock_client.side_effect = ConnectionError("Network unreachable")

        result = await transcribe_voice_message(
            client=mock_client,
            peer=12345,
            msg_id=100,
        )

        assert result is None
