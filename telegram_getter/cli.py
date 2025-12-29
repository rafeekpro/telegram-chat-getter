"""
CLI interface for telegram_getter.

Provides commands for listing and downloading Telegram chats.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Annotated

import typer
from rich.console import Console

from telegram_getter.auth import AuthenticationError, TelegramAuth
from telegram_getter.chats import format_chats_table, list_chats

console = Console()

# Create Typer app
app = typer.Typer(
    name="telegram-getter",
    help="CLI tool to download chat content from Telegram",
    add_completion=False,
)


def _run_async(coro: object) -> object:
    """Run an async coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)  # type: ignore[arg-type]


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
    filter_type: str | None = None
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


async def _list_chats_async(filter_type: str | None) -> None:
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


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
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
