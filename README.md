# Telegram Chat Getter

Download and backup your Telegram chats with full message history, media files, and voice transcriptions.

## Features

- **Complete History** - Download ALL messages from any chat (private, group, channel)
- **Chronological Order** - Messages sorted from oldest to newest
- **Multiple Formats** - Export to Markdown and JSON
- **Media Download** - Photos, videos, documents, voice messages
- **Voice Transcription** - Transcribe voice messages to text (Telegram Premium)
- **Incremental Sync** - Only download new messages since last backup

## Installation

```bash
# Clone the repository
git clone https://github.com/rafeekpro/telegram-chat-getter.git
cd telegram-chat-getter

# Install dependencies
pip install -e .
```

### Requirements

- Python 3.11+
- Telegram API credentials (get from https://my.telegram.org)

## Quick Start

```bash
# 1. Set up your Telegram API credentials
export TELEGRAM_API_ID=your_api_id
export TELEGRAM_API_HASH=your_api_hash

# 2. Authenticate with Telegram
telegram-getter auth

# 3. List available chats
telegram-getter list

# 4. Download a chat
telegram-getter download "Chat Name" --all
```

## Usage

### Download All Messages

```bash
# Download complete chat history (chronological order)
telegram-getter download "My Chat" --all

# Download by chat ID
telegram-getter download --id 123456789 --all

# Download to specific directory
telegram-getter download "My Chat" --all --output ./backups
```

### Incremental Sync

```bash
# First time: full download
telegram-getter download "My Chat" --all

# Later: only new messages
telegram-getter download "My Chat" --sync
```

### Voice Transcription

```bash
# Transcribe voice messages (requires Telegram Premium)
telegram-getter download "My Chat" --all --transcribe

# Sync with transcription
telegram-getter download "My Chat" --sync --transcribe
```

### Date Filtering

```bash
# Download messages from specific period
telegram-getter download "My Chat" --from 2024-01-01 --to 2024-12-31
```

### Skip Media

```bash
# Download only text messages
telegram-getter download "My Chat" --all --no-media
```

## Output Structure

```
output/My_Chat/
├── messages.md      # Human-readable Markdown
├── messages.json    # Machine-readable JSON with all data
├── metadata.json    # Chat statistics
└── media/
    ├── images/      # Photos
    ├── video/       # Videos
    ├── audio/       # Voice messages
    └── documents/   # Files
```

### messages.md

```markdown
# Chat: My Chat
Downloaded: 2024-01-15T10:30:00+00:00
Total messages: 1234
Media files: 56

---

## 2024-01-01

### 10:30 - John
Hello!

### 10:31 - Jane
Hi there!
[Voice message](media/audio/2024-01-01_001.ogg)
> Transcription: Hey, how are you doing today?
```

### messages.json

```json
{
  "exported_at": "2024-01-15T10:30:00+00:00",
  "message_count": 1234,
  "messages": [
    {
      "id": 1,
      "date": "2024-01-01T10:30:00+00:00",
      "sender_id": 123456,
      "sender_name": "John",
      "text": "Hello!",
      "reply_to": null,
      "media_type": null,
      "media_path": null,
      "transcription": null
    }
  ]
}
```

## CLI Reference

```
telegram-getter --help
telegram-getter download --help
telegram-getter list --help
telegram-getter auth --help
```

### Commands

| Command | Description |
|---------|-------------|
| `auth` | Authenticate with Telegram |
| `list` | List available chats |
| `download` | Download chat messages and media |

### Download Options

| Option | Short | Description |
|--------|-------|-------------|
| `--all` | `-a` | Download ALL messages from beginning |
| `--sync` | `-s` | Incremental sync (only new messages) |
| `--transcribe` | `-t` | Transcribe voice messages |
| `--output` | `-o` | Output directory |
| `--from` | | Start date (YYYY-MM-DD) |
| `--to` | | End date (YYYY-MM-DD) |
| `--no-media` | | Skip media download |
| `--id` | | Download by chat ID |

## Configuration

Create a `.env` file or set environment variables:

```bash
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890  # Optional
```

Get your API credentials from https://my.telegram.org/apps

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=telegram_getter
```

## License

MIT License

## Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram client library
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
