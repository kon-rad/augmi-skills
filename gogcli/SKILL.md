---
name: gogcli
description: >
  Fast, script-friendly CLI for Google Workspace — Gmail, Calendar, Drive, Docs, Sheets, Slides,
  Contacts, Tasks, Forms, Groups, Keep, and more. JSON-first output, multiple account support,
  least-privilege auth with --readonly flag, and command allowlist for safe agent usage.
homepage: https://gogcli.sh
---

# gog — Google Workspace CLI

Use `gog` for Gmail, Calendar, Drive, Contacts, Sheets, Docs, Slides, Forms, Tasks, Groups, and Keep.

## Installation

```bash
brew install steipete/tap/gogcli
```

Or build from source: `git clone https://github.com/steipete/gogcli && cd gogcli && make && sudo make install`

## Setup (once)

1. Create a Google Cloud project and enable APIs
2. Create OAuth 2.0 Desktop credentials with redirect URI `http://localhost:8085/callback`
3. Download the credentials JSON file
4. Run: `gog auth add you@gmail.com ~/Downloads/client_secret_....json`
5. Verify: `gog auth list`

## Common Commands

- **Gmail search**: `gog gmail search 'newer_than:7d' --max 10`
- **Gmail send**: `gog gmail send --to a@b.com --subject "Hi" --body "Hello"`
- **Calendar events**: `gog calendar events <calendarId> --from <iso> --to <iso>`
- **Drive search**: `gog drive search "query" --max 10`
- **Contacts**: `gog contacts list --max 20`
- **Sheets get**: `gog sheets get <sheetId> "Tab!A1:D10" --json`
- **Sheets update**: `gog sheets update <sheetId> "Tab!A1:B2" --values-json '[["A","B"],["1","2"]]' --input USER_ENTERED`
- **Sheets append**: `gog sheets append <sheetId> "Tab!A:C" --values-json '[["x","y","z"]]' --insert INSERT_ROWS`
- **Sheets clear**: `gog sheets clear <sheetId> "Tab!A2:Z"`
- **Sheets metadata**: `gog sheets metadata <sheetId> --json`
- **Docs export**: `gog docs export <docId> --format txt --out /tmp/doc.txt`
- **Docs cat**: `gog docs cat <docId>`
- **Tasks list**: `gog tasks list`
- **Tasks create**: `gog tasks add "Task title" --list <listId>`

## Notes

- Set `GOG_ACCOUNT=you@gmail.com` to avoid repeating `--account`.
- For scripting, prefer `--json` plus `--no-input`.
- Sheets values can be passed via `--values-json` (recommended) or as inline rows.
- Docs supports export/cat/copy. In-place edits require a Docs API client (not in gog).
- Use `--readonly` flag for least-privilege access when you only need to read data.
- Confirm before sending mail or creating events.
