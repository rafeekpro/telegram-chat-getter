"""
CLI interface for telegram_getter.

Provides commands for listing and downloading Telegram chats.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from telegram_getter.auth import AuthenticationError, TelegramAuth
from telegram_getter.chats import format_chats_table, get_chat_type, list_chats
from telegram_getter.downloader import Message, MessageDownloader
from telegram_getter.exporter import (
    dict_to_message,
    export_messages_to_json,
    export_to_markdown,
    generate_metadata,
    load_existing_messages,
)
from telegram_getter.media import MediaDownloader
from telegram_getter.transcriber import transcribe_voice_message

console = Console()

# Create Typer app
app = typer.Typer(
    name="telegram-getter",
    help="""📱 Telegram Chat Getter - Download and backup your Telegram chats.

Features:
  • Download all messages from any chat (private, group, channel)
  • Export to Markdown and JSON formats
  • Download media files (photos, videos, documents)
  • Transcribe voice messages (requires Telegram Premium)
  • Incremental sync - only download new messages

Quick start:
  1. telegram-getter auth          # Authenticate first
  2. telegram-getter list          # See available chats
  3. telegram-getter download "Chat Name" --all  # Download everything
""",
    add_completion=False,
    rich_markup_mode="rich",
)


def _run_async(coro: object) -> object:
    """Run an async coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)  # type: ignore[arg-type]


def _parse_date(date_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format with UTC timezone."""
    from datetime import UTC

    naive_dt = datetime.strptime(date_str, "%Y-%m-%d")  # noqa: DTZ007
    return naive_dt.replace(tzinfo=UTC)


@app.command()
def auth() -> None:
    """
    Authenticate with Telegram.

    Connects to Telegram using API credentials from environment variables
    (API_ID and API_HASH). On first run, prompts for phone number and
    verification code. Session is saved for future use.
    """
    try:
        _run_async(_auth_async())
    except AuthenticationError as e:
        console.print(f"[red]Authentication error: {e}[/red]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1) from e


async def _auth_async() -> None:
    """Async implementation of auth command."""
    auth = TelegramAuth()

    # Connect without progress spinner - allows interactive input for phone/code
    async with auth as client:
        me = await client.get_me()
        username = me.username or me.first_name or "Unknown"

    console.print(f"[green]Successfully authenticated as {username}[/green]")


@app.command()
def list(
    groups: Annotated[
        bool,
        typer.Option("--groups", "-g", help="Show only groups (including supergroups)"),
    ] = False,
    private: Annotated[
        bool,
        typer.Option("--private", "-p", help="Show only private chats"),
    ] = False,
    channels: Annotated[
        bool,
        typer.Option("--channels", "-c", help="Show only channels"),
    ] = False,
) -> None:
    """
    List all Telegram chats (dialogs, groups, channels).

    By default, shows all chats. Use filter options to show specific types.
    """
    # Determine filter type based on options
    filter_type: Optional[str] = None
    filter_count = sum([groups, private, channels])

    if filter_count > 1:
        console.print("[red]Error: Only one filter option can be used at a time[/red]")
        raise typer.Exit(code=1)

    if groups:
        filter_type = "group"
    elif private:
        filter_type = "private"
    elif channels:
        filter_type = "channel"

    try:
        # Run the async list operation
        _run_async(_list_chats_async(filter_type))
    except AuthenticationError as e:
        console.print(f"[red]Authentication error: {e}[/red]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1) from e


async def _list_chats_async(filter_type: Optional[str]) -> None:
    """Async implementation of list chats command."""
    auth = TelegramAuth()

    async with auth as client:
        chats = await list_chats(client, filter_type=filter_type)

        if not chats:
            filter_msg = f" matching filter '{filter_type}'" if filter_type else ""
            console.print(f"[yellow]No chats found{filter_msg}[/yellow]")
            return

        table = format_chats_table(chats)
        console.print(table)
        console.print(f"\n[dim]Total: {len(chats)} chat(s)[/dim]")


@app.command(
    epilog="""
[bold]Examples:[/bold]

  [dim]# Download all messages from beginning[/dim]
  telegram-getter download "My Chat" --all

  [dim]# Sync only new messages (incremental)[/dim]
  telegram-getter download "My Chat" --sync

  [dim]# Download with voice transcription[/dim]
  telegram-getter download "My Chat" --all --transcribe

  [dim]# Download by chat ID[/dim]
  telegram-getter download --id 123456789 --all

  [dim]# Download specific date range[/dim]
  telegram-getter download "My Chat" --from 2024-01-01 --to 2024-12-31

[bold]Output files:[/bold]
  output/<chat_name>/
  ├── messages.md      # Markdown format (chronological)
  ├── messages.json    # JSON with all data
  ├── metadata.json    # Statistics
  └── media/           # Downloaded media files
"""
)
def download(
    chat: Annotated[
        str,
        typer.Argument(help="Chat name (use 'list' command to see available chats)"),
    ] = "",
    chat_id: Annotated[
        Optional[int],
        typer.Option("--id", help="Chat ID (alternative to name)"),
    ] = None,
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output directory [default: ./output]"),
    ] = Path("output"),
    from_date: Annotated[
        Optional[str],
        typer.Option("--from", help="Start date filter (YYYY-MM-DD)"),
    ] = None,
    to_date: Annotated[
        Optional[str],
        typer.Option("--to", help="End date filter (YYYY-MM-DD)"),
    ] = None,
    no_media: Annotated[
        bool,
        typer.Option("--no-media", help="Skip downloading media files"),
    ] = False,
    download_all: Annotated[
        bool,
        typer.Option(
            "--all", "-a", help="Download ALL messages from the beginning (chronological)"
        ),
    ] = False,
    transcribe: Annotated[
        bool,
        typer.Option(
            "--transcribe",
            "-t",
            help="Transcribe voice messages to text (Telegram Premium)",
        ),
    ] = False,
    sync: Annotated[
        bool,
        typer.Option(
            "--sync",
            "-s",
            help="Incremental sync - only download NEW messages",
        ),
    ] = False,
) -> None:
    """
    Download chat messages and media.

    Downloads all messages from the specified chat, optionally filtering by date.
    Media files are downloaded unless --no-media is specified.

    Examples:
        telegram-getter download "My Chat"
        telegram-getter download --id 123456789
        telegram-getter download "My Chat" --output ./backup --from 2025-01-01
    """
    # Validate that either chat name or chat ID is provided
    if not chat and chat_id is None:
        console.print("[red]Error: Either chat name or --id is required[/red]")
        raise typer.Exit(code=1)

    # Parse date options
    parsed_from_date: Optional[datetime] = None
    parsed_to_date: Optional[datetime] = None

    try:
        if from_date:
            parsed_from_date = _parse_date(from_date)
        if to_date:
            parsed_to_date = _parse_date(to_date)
    except ValueError as e:
        console.print(f"[red]Error: Invalid date format. Use YYYY-MM-DD. {e}[/red]")
        raise typer.Exit(code=1) from e

    try:
        _run_async(
            _download_async(
                chat_name=chat if chat else None,
                chat_id=chat_id,
                output_dir=output,
                from_date=parsed_from_date,
                to_date=parsed_to_date,
                download_media=not no_media,
                download_all=download_all,
                transcribe=transcribe,
                sync=sync,
            )
        )
    except AuthenticationError as e:
        console.print(f"[red]Authentication error: {e}[/red]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1) from e


async def _download_async(
    chat_name: Optional[str],
    chat_id: Optional[int],
    output_dir: Path,
    from_date: Optional[datetime],
    to_date: Optional[datetime],
    download_media: bool,
    download_all: bool = False,
    transcribe: bool = False,
    sync: bool = False,
) -> None:
    """Async implementation of download command."""
    auth = TelegramAuth()

    async with auth as client:
        # Find the chat
        target_chat = None
        target_entity = None

        if chat_id is not None:
            # Download by ID
            try:
                target_entity = await client.get_entity(chat_id)
                target_chat = {
                    "id": chat_id,
                    "name": getattr(target_entity, "title", None)
                    or getattr(target_entity, "first_name", "Unknown"),
                    "type": get_chat_type(target_entity),
                }
            except Exception as e:
                console.print(
                    f"[red]Error: Chat with ID {chat_id} not found: {e}[/red]"
                )
                raise typer.Exit(code=1) from e
        else:
            # Download by name - search in dialogs
            chats = await list_chats(client)
            for c in chats:
                if c["name"].lower() == chat_name.lower():  # type: ignore[union-attr]
                    target_chat = c
                    target_entity = await client.get_entity(c["id"])
                    break

            if target_chat is None:
                console.print(f"[red]Error: Chat '{chat_name}' not found[/red]")
                console.print(
                    "[dim]Tip: Use 'telegram-getter list' to see available chats[/dim]"
                )
                raise typer.Exit(code=1)

        chat_name_display = target_chat["name"]
        chat_output_dir = output_dir / _sanitize_filename(chat_name_display)
        chat_output_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"[blue]Downloading chat: {chat_name_display}[/blue]")

        # Download messages
        messages: list[Message] = []
        downloader = MessageDownloader(client=client)

        # When --all flag is used, download from beginning in chronological order
        reverse = download_all
        min_id = 0 if download_all else None

        # Load existing messages for sync mode
        existing_dicts: list[dict] = []
        if sync:
            existing_dicts, last_id = await load_existing_messages(chat_output_dir)
            if last_id > 0:
                console.print(
                    f"[blue]Sync mode: Found {len(existing_dicts)} existing messages "
                    f"(last ID: {last_id})[/blue]"
                )
                min_id = last_id  # Only get messages with ID > last_id
                reverse = True  # Get in chronological order for sync
            else:
                console.print(
                    "[yellow]No existing messages found, downloading all[/yellow]"
                )

        if download_all:
            console.print(
                "[blue]Downloading ALL messages from beginning (chronological order)...[/blue]"
            )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            task = progress.add_task("Downloading messages...", total=None)

            async for msg in downloader.download_messages(
                chat=target_chat["id"],
                from_date=from_date,
                to_date=to_date,
                store=True,
                reverse=reverse,
                min_id=min_id,
            ):
                messages.append(msg)
                progress.update(
                    task, description=f"Downloaded {len(messages)} messages..."
                )

        console.print(f"[green]Downloaded {len(messages)} new messages[/green]")

        # Merge with existing messages in sync mode
        if sync and existing_dicts:
            # Convert existing dicts to Message objects
            existing_messages = [dict_to_message(d) for d in existing_dicts]
            # Merge: existing + new (avoid duplicates by ID)
            existing_ids = {m.id for m in existing_messages}
            new_unique = [m for m in messages if m.id not in existing_ids]
            all_messages = existing_messages + new_unique
            # Sort chronologically
            all_messages.sort(key=lambda m: m.date)
            console.print(
                f"[green]Added {len(new_unique)} new messages "
                f"(total: {len(all_messages)})[/green]"
            )
            messages = all_messages

        # Download media if enabled
        if download_media and messages:
            media_downloader = MediaDownloader(
                client=client, output_dir=chat_output_dir
            )
            media_count = 0

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
                console=console,
            ) as progress:
                task = progress.add_task("Downloading media...", total=None)

                # We need to get the original Telegram messages to download media
                async for telegram_msg in client.iter_messages(
                    target_chat["id"],
                    offset_date=to_date,
                ):
                    if from_date and telegram_msg.date < from_date:
                        continue

                    if telegram_msg.media:
                        # Find corresponding message in our list
                        for msg in messages:
                            if msg.id == telegram_msg.id:
                                media_path = await media_downloader.download_media(
                                    telegram_msg
                                )
                                if media_path:
                                    msg.media_path = media_path
                                    media_count += 1
                                    progress.update(
                                        task,
                                        description=f"Downloaded {media_count} media files...",
                                    )
                                break

            console.print(f"[green]Downloaded {media_count} media files[/green]")

        # Transcribe voice messages if enabled
        if transcribe and messages:
            # Voice messages can be "audio" type or "document" with .ogg extension
            voice_messages = [
                msg
                for msg in messages
                if msg.media_type == "audio"
                or (msg.media_path and msg.media_path.endswith(".ogg"))
            ]
            if voice_messages:
                transcribe_count = 0
                failed_count = 0

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                    console=console,
                ) as progress:
                    task = progress.add_task(
                        "Transcribing voice messages...", total=len(voice_messages)
                    )

                    for msg in voice_messages:
                        transcription = await transcribe_voice_message(
                            client=client,
                            peer=target_chat["id"],
                            msg_id=msg.id,
                        )
                        if transcription:
                            msg.transcription = transcription
                            transcribe_count += 1
                        else:
                            failed_count += 1
                        progress.update(task, advance=1)

                if transcribe_count > 0:
                    console.print(
                        f"[green]Transcribed {transcribe_count} voice messages[/green]"
                    )
                if failed_count > 0:
                    console.print(
                        f"[yellow]Could not transcribe {failed_count} messages (no Premium or quota exceeded)[/yellow]"
                    )

        # Export to markdown
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task("Exporting to markdown...", total=None)
            await export_to_markdown(messages, chat_name_display, chat_output_dir)

        # Export to JSON (all messages in chronological order)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task("Exporting to JSON...", total=None)
            await export_messages_to_json(messages, chat_output_dir)

        # Generate metadata
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task("Generating metadata...", total=None)
            await generate_metadata(
                messages=messages,
                chat_name=chat_name_display,
                chat_id=target_chat["id"],
                chat_type=target_chat["type"],
                output_dir=chat_output_dir,
            )

        console.print(
            f"[green]Export complete! Files saved to: {chat_output_dir}[/green]"
        )


def _sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    # Replace problematic characters with underscores
    invalid_chars = '<>:"/\\|?*'
    result = name
    for char in invalid_chars:
        result = result.replace(char, "_")
    return result.strip()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", help="Show version and exit"),
    ] = None,
) -> None:
    """
    Telegram Chat Getter - CLI tool to download chat content from Telegram.
    """
    if version:
        from telegram_getter import __version__

        console.print(f"telegram-getter version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print("[bold blue]Telegram Chat Getter[/bold blue]")
        console.print("Use --help for available commands")


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        app()
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1


if __name__ == "__main__":
    sys.exit(main())
