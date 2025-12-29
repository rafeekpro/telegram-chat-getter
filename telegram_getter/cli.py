"""
CLI interface for telegram_getter.
"""

import sys

from rich.console import Console

console = Console()


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    console.print("[bold blue]Telegram Chat Getter[/bold blue]")
    console.print("Use --help for available commands")
    return 0


if __name__ == "__main__":
    sys.exit(main())
