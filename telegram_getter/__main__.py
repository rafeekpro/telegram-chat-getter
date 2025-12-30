"""
Entry point for running telegram_getter as a module.

Usage: python -m telegram_getter
"""

import sys

from telegram_getter.cli import main

if __name__ == "__main__":
    sys.exit(main())
