---
name: gogcli
description: >
  Google Workspace CLI for Gmail, Calendar, Drive, Sheets, Docs, Slides, Contacts, Tasks,
  Forms, Groups, and Keep. Use when user asks to interact with Google services — reading emails,
  searching Drive, checking calendar, updating spreadsheets, or managing contacts.
  JSON-first output, multiple account support, least-privilege auth with --readonly flag.
category: productivity
version: 0.5.0
homepage: https://gogcli.sh
source: https://github.com/steipete/gogcli
key_capabilities: gmail, calendar, drive, sheets, docs, contacts, tasks, slides, forms, groups, keep
when_to_use: >
  Google Workspace operations — email search/send, calendar events, Drive file management,
  Sheets read/write, Docs export, contact lookup, task management
metadata:
  openclaw:
    emoji: "🎮"
    requires:
      bins:
        - gog
    install:
      id: brew
      kind: brew
      formula: steipete/tap/gogcli
      bins:
        - gog
      label: "Install gog (brew)"
    os:
      - darwin
      - linux
---

# gog — Google Workspace CLI

Use `gog` for Gmail, Calendar, Drive, Contacts, Sheets, Docs, Slides, Forms, Tasks, Groups, and Keep.

## Installation

### macOS / Linux (Homebrew)

```bash
brew install steipete/tap/gogcli
```

### Linux (Pre-built Binary)

```bash
wget https://github.com/steipete/gogcli/releases/latest/download/gog-linux-amd64
chmod +x gog-linux-amd64
sudo mv gog-linux-amd64 /usr/local/bin/gog
```

### Build from Source

```bash
git clone https://github.com/steipete/gogcli && cd gogcli && make && sudo make install
```

## First-Time Setup

### Step 1: Google Cloud OAuth Credentials

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g., "OpenClaw-Drive")
3. Navigate to **APIs & Services > Library** and enable:
   - Google Drive API
   - Google Sheets API
   - Google Docs API
   - Gmail API
   - Google Calendar API
4. Go to **APIs & Services > OAuth consent screen**
   - User type: External
   - Add your email as test user
   - **Click "Publish App"** to set to Production (avoids 7-day token expiry)
5. Go to **APIs & Services > Credentials**
   - Click **Create Credentials > OAuth client ID**
   - Application type: **Desktop app**
   - Download the JSON file immediately

### Step 2: Authenticate

```bash
# Store credentials
gog auth credentials ~/Downloads/client_secret_*.json

# Add your account with desired services
gog auth add you@gmail.com --services gmail,calendar,drive,contacts,sheets,docs

# For headless/remote servers (no browser)
gog auth add you@gmail.com --services gmail,calendar,drive --manual
```

### Step 3: Verify

```bash
gog auth list
gog gmail search 'newer_than:1d' --max 3
```

### Environment

```bash
# Set default account to avoid repeating --account
export GOG_ACCOUNT=you@gmail.com
```

## Common Commands

### Gmail

- **Search**: `gog gmail search 'newer_than:7d' --max 10`
- **Search from sender**: `gog gmail search 'from:john@example.com' --max 5`
- **Send**: `gog gmail send --to a@b.com --subject "Hi" --body "Hello"`
- **Get message**: `gog gmail get <messageId>`
- **Labels**: `gog gmail labels`
- **Drafts**: `gog gmail drafts --max 5`

### Calendar

- **Today's events**: `gog calendar events primary --from $(date -I) --to $(date -I)`
- **Date range**: `gog calendar events <calendarId> --from <iso> --to <iso>`
- **List calendars**: `gog calendar list`
- **Create event**: `gog calendar create primary --summary "Meeting" --start "2026-02-20T14:00:00" --duration 30m`

### Drive

- **Search files**: `gog drive search "query" --max 10`
- **Search by type**: `gog drive search "mimeType='application/pdf'" --max 10`
- **Get file info**: `gog drive get <fileId>`
- **Upload**: `gog drive upload file.pdf --parent <folderId>`
- **Download**: `gog drive download <fileId> --output ./local-file.pdf`
- **Share**: `gog drive share <fileId> --email user@example.com --role writer`

### Sheets

- **Get data**: `gog sheets get <sheetId> "Tab!A1:D10" --json`
- **Update cells**: `gog sheets update <sheetId> "Tab!A1:B2" --values-json '[["A","B"],["1","2"]]' --input USER_ENTERED`
- **Append rows**: `gog sheets append <sheetId> "Tab!A:C" --values-json '[["x","y","z"]]' --insert INSERT_ROWS`
- **Clear range**: `gog sheets clear <sheetId> "Tab!A2:Z"`
- **Metadata**: `gog sheets metadata <sheetId> --json`

### Docs

- **Read content**: `gog docs cat <docId>`
- **Export as text**: `gog docs export <docId> --format txt --out /tmp/doc.txt`
- **Copy doc**: `gog docs copy <docId> --title "Copy of Doc"`

### Contacts

- **List**: `gog contacts list --max 20`
- **Search**: `gog contacts search "John"`

### Tasks

- **List task lists**: `gog tasks list`
- **Add task**: `gog tasks add "Task title" --list <listId>`

## Notes

- Set `GOG_ACCOUNT=you@gmail.com` to avoid repeating `--account`.
- For scripting, prefer `--json` plus `--no-input`.
- Sheets values can be passed via `--values-json` (recommended) or as inline rows.
- Docs supports export/cat/copy. In-place edits require a Docs API client (not in gog).
- Use `--readonly` flag for least-privilege access when you only need to read data.
- Confirm before sending mail or creating events.
- Revoke access anytime at https://myaccount.google.com/permissions

## Troubleshooting

- **"invalid_grant" error**: OAuth app is in Testing mode. Go to Cloud Console > OAuth consent screen > click "Publish App".
- **"Access Denied"**: Required APIs not enabled. Check APIs & Services > Library.
- **Token expired**: Re-authenticate with `gog auth add you@gmail.com --force --services gmail,calendar,drive`.
- **Headless server**: Use `--manual` flag or SSH tunnel port 8085: `ssh -L 8085:localhost:8085 user@server`.
