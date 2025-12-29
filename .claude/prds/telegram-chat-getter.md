---
title: Telegram Chat Getter
status: draft
priority: P2
created: 2025-12-29T12:41:56Z
updated: 2025-12-29T12:45:00Z
author: claude
timeline: TBD
---

# PRD: telegram-chat-getter

## Executive Summary
A Python CLI tool that connects to a personal Telegram account and downloads chat/group content including messages, images, audio, and files to the local computer. Uses the Telethon library for Telegram Client API access.

## Problem Statement
### Background
Users need to backup or export Telegram chat history including all media files for archival, migration, or offline access purposes.

### Current State
- Telegram's built-in export is limited and requires desktop app
- No easy CLI-based solution for scripted/automated downloads
- Media files are not easily organized

### Desired State
- Simple CLI command to download any chat/group
- All messages exported to readable Markdown format
- Media files (images, audio, documents) downloaded and organized
- Easy to use with personal Telegram account

## Target Users
- **Primary**: Users who want to backup their Telegram chats locally
- **Secondary**: Developers who need to archive project discussions

### User Stories
- As a user, I want to authenticate with my Telegram account, so that I can access my private chats
- As a user, I want to download all messages from a specific chat, so that I have a local backup
- As a user, I want to download all media files, so that I don't lose images and documents
- As a user, I want organized output, so that I can easily find specific content

## Technical Decisions
- **Language**: Python 3.11+
- **Telegram Library**: Telethon (async Telegram Client API)
- **File Organization**: By chat name
- **Message Format**: Markdown

## Key Features
### Must Have (P0)
- [ ] Telegram Client API authentication (phone + code)
- [ ] List available chats/groups
- [ ] Download messages from specified chat
- [ ] Export messages to Markdown format
- [ ] Download images/photos
- [ ] Download audio/voice messages
- [ ] Download documents/files
- [ ] Organize files by chat name

### Should Have (P1)
- [ ] Filter by date range
- [ ] Resume interrupted downloads
- [ ] Progress indicator
- [ ] Download specific message range

### Nice to Have (P2)
- [ ] Incremental sync (only new messages)
- [ ] Export to JSON alongside Markdown
- [ ] Media deduplication

## Output Structure
```
output/
└── {chat-name}/
    ├── messages.md          # All messages in Markdown
    ├── metadata.json        # Chat info and download stats
    └── media/
        ├── images/
        │   ├── 2025-01-15_001.jpg
        │   └── 2025-01-15_002.png
        ├── audio/
        │   ├── 2025-01-15_001.ogg
        │   └── 2025-01-15_002.mp3
        ├── video/
        │   └── 2025-01-15_001.mp4
        └── documents/
            ├── report.pdf
            └── data.xlsx
```

## Message Markdown Format
```markdown
# Chat: {chat_name}
Downloaded: 2025-01-15T14:30:00Z
Total messages: 1234

---

## 2025-01-15

### 14:30 - John Doe
Hello everyone!

### 14:31 - Jane Smith
Hi John! How are you?

### 14:32 - John Doe
Great! Check out this image:
![image](media/images/2025-01-15_001.jpg)

### 14:35 - Jane Smith
[Voice message](media/audio/2025-01-15_001.ogg)

---

## 2025-01-14
...
```

## CLI Interface
```bash
# First-time setup (authenticate)
python telegram_getter.py auth

# List available chats
python telegram_getter.py list

# Download specific chat by name or ID
python telegram_getter.py download "Chat Name"
python telegram_getter.py download --id 123456789

# Download with options
python telegram_getter.py download "Chat Name" --output ./backup
python telegram_getter.py download "Chat Name" --from 2025-01-01 --to 2025-01-31
python telegram_getter.py download "Chat Name" --no-media  # Messages only
```

## Authentication Flow
1. User provides API credentials (api_id, api_hash from my.telegram.org)
2. User enters phone number
3. Telegram sends verification code
4. User enters code
5. Session saved locally for future use

## Technical Requirements
### Dependencies
- Python 3.11+
- telethon (Telegram Client API)
- aiofiles (async file operations)
- python-dotenv (environment variables)
- rich (progress bars and CLI output)

### Non-Functional Requirements
- **Performance**: Handle chats with 100K+ messages
- **Reliability**: Resume interrupted downloads
- **Security**: Store session securely, never log credentials

## Implementation Plan
### Phase 1: Foundation
- [ ] Project setup (pyproject.toml, dependencies)
- [ ] Telegram authentication module
- [ ] Session management

### Phase 2: Core Features
- [ ] List chats command
- [ ] Download messages
- [ ] Markdown export
- [ ] Media download (images, audio, video, documents)

### Phase 3: Enhancement
- [ ] Date filtering
- [ ] Progress indicators
- [ ] Resume capability

### Phase 4: Release
- [ ] Testing
- [ ] Documentation
- [ ] Usage examples

## Risks and Mitigation
- **Rate Limiting**: Telegram limits requests. Mitigation: Respect limits, add delays.
- **Large Media**: Big files take time. Mitigation: Progress bars, async downloads.
- **Session Expiry**: Sessions can expire. Mitigation: Handle re-auth gracefully.

## Setup Requirements
Users need to:
1. Go to https://my.telegram.org
2. Log in with phone number
3. Create an application to get `api_id` and `api_hash`
4. Store credentials in `.env` file

## Open Questions
- [ ] Should we support multiple accounts?
- [ ] Maximum file size limit for downloads?

## Changelog
- 2025-12-29T12:41:56Z: Initial PRD created
- 2025-12-29T12:45:00Z: Updated with user preferences (Python, by-chat-name, Markdown)
