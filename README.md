# Telegram Chat Getter

CLI tool to download chat content from Telegram.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
telegram-getter --help
```

Or run as module:

```bash
python -m telegram_getter --help
```

## Configuration

Create a `.env` file with your Telegram API credentials:

```
API_ID=your_api_id
API_HASH=your_api_hash
```

Get your API credentials from https://my.telegram.org/apps

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```
