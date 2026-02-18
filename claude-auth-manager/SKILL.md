---
name: claude-auth-manager
description: >
  Manages Claude Code authentication on VPS/headless servers via Telegram.
  Handles the OAuth login flow by keeping the `claude login` process alive
  using tmux, allowing users to complete authentication through chat.
  Use this skill when users say "login", "authenticate", "auth", "connect claude",
  or when Claude Code authentication has expired.
---

# Claude Code Auth Manager

Authenticate Claude Code on a VPS through Telegram chat. Solves the problem of
`claude login` requiring an interactive terminal by using tmux to persist the
login process across chat messages.

## Prerequisites

The VPS must have:
```bash
# Required
tmux          # apt install tmux
claude        # npm install -g @anthropic-ai/claude-code
python3       # Usually pre-installed

# Verify
which tmux claude python3
```

## How It Works

The `claude login` OAuth flow requires:
1. CLI shows an interactive menu to select login method (subscription vs API)
2. CLI generates a PKCE code_challenge and shows an OAuth URL
3. User opens URL in browser and authorizes
4. Browser shows a one-time authorization code OR redirects to localhost
5. **The SAME CLI process** must receive that code/URL on stdin

The problem: in Telegram, the user's message goes to the AI agent, not to the
`claude login` subprocess. This skill uses **tmux** to keep the process alive,
**auto-selects the subscription option** from the menu, and pipes the code to
it when the user sends it.

## Commands

### Check Authentication Status
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py status
```
Returns JSON with `authenticated` or `not_authenticated` status.

### Start Login Flow
```bash
# Default: Claude subscription login (Pro/Max)
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py start

# Alternative: Anthropic Console / API key login
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py start console
```
Starts `claude login` in a tmux session, auto-selects the login method from the
interactive menu, waits for the OAuth URL, and returns it.
**Send this URL to the user and tell them to open it in their browser.**

### Submit Authorization Code or URL
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py submit "<code_or_url>"
```
Pipes the authorization code or callback URL into the waiting `claude login` process.
The input can be in any of these formats — the script passes it through to `claude login`:
- Just the code: `vU50Vvi9ie0TdpVtGg4bLb5AC3pqcF2dXhgHaOhrQ4FmCylK`
- Code#state: `vU50Vvi9ie...#x0FpOVhd...`
- Full callback URL: `https://platform.claude.com/oauth/code/callback?code=XXX&state=YYY`
- Localhost redirect URL: `http://localhost:PORT/oauth/callback?code=XXX&state=YYY`

**IMPORTANT**: Send whatever the user gives you — do NOT extract just the code.
Let `claude login` parse it.

### Check Login Result
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py check
```
Checks if the login completed successfully after submitting the code.

### Debug (Troubleshooting)
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py debug
```
Dumps the full tmux pane output for troubleshooting. Use this if login fails
to understand what `claude login` is showing.

### Activate Subscription (after login succeeds)
```bash
# Default: switches to anthropic/claude-sonnet-4-20250514
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py activate

# Or specify a model:
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py activate anthropic/claude-sonnet-4
```
**CRITICAL: Run this after `claude login` succeeds.** This command:
1. Reads the OAuth token from `~/.claude/.credentials.json`
2. Saves it to `/data/.claude-subscription-token` (persistent across restarts)
3. Calls AUGMI API (`PUT /api/agents/{id}/provider`) to:
   - Set `CLAUDE_CODE_OAUTH_TOKEN` on the machine
   - Clear `ANTHROPIC_API_KEY` (it takes priority over subscription)
   - Switch the model to a Claude model
4. Falls back to Fly.io Machines API if AUGMI API fails
5. Machine restarts automatically with subscription auth

This switches OpenClaw from API keys to the Claude Code subscription for ALL LLM calls.

### Cleanup Stale Sessions
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py cleanup
```
Kills any stale tmux auth sessions.

### Transfer Credentials (Backup Method)
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py transfer "<base64>"
```
Alternative method: user runs `cat ~/.claude/.credentials.json | base64` on their
LOCAL machine and sends the base64 string. The script writes it to the VPS.

## Interaction Flow (for the AI agent)

When the user asks to authenticate, login, or use Claude subscription:

### RECOMMENDED: Direct Token Method (set-token) — No Restart Needed

This is the most reliable method. The user generates a token on their local
machine and sends it to the agent. The agent applies it at runtime via the
OpenClaw CLI — no restart required.

#### Step 1: Ask user for their token
Tell the user:
"I need your Claude Code setup token. On your computer where Claude Code is
installed and logged in, run:

```
claude setup-token
```

This will open a browser for authorization and give you a token.
Send me the token (starts with `sk-ant-...`)."

**Alternative extraction methods (if `claude setup-token` isn't available):**

Mac:
```
security find-generic-password -s 'Claude Code-credentials' -g 2>&1 | grep password
```
Then from that JSON output, copy the `accessToken` value.

Linux:
```
cat ~/.claude/.credentials.json
```
Then copy the `accessToken` value from the `claudeAiOauth` object.

#### Step 2: Set the token
When the user sends a token starting with `sk-ant-`:
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py set-token "<token>"
```
This will:
1. Try `openclaw models auth paste-token` to apply auth at runtime (no restart)
2. Set the model to `anthropic/claude-sonnet-4-20250514` via `openclaw config set`
3. Fall back to direct config modification if CLI method fails
4. Save persistence files so the config survives restarts

Parse the JSON output to check the `method` field:
- `"openclaw_paste_token"` — applied live, tell user "Subscription activated!"
- `"config_file"` — applied via config, tell user "Subscription configured!"
- `null` — saved for restart only, tell user "Token saved, restart to activate."

#### Step 3 (optional): Specify a different model
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py set-token "<token>" "anthropic/claude-opus-4-5"
```

### ALTERNATIVE: OAuth Flow (start/submit/activate)

If the user prefers to authenticate directly through the browser (less reliable
in container environments due to credential file detection issues):

#### Step 1: Check current status
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py status
```
If already authenticated, tell the user and stop.

#### Step 2: Start login
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py start
```
Parse the JSON output. Send the `oauth_url` to the user with instructions.

#### Step 3: Submit the code
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py submit "<what_user_sent>"
```
**Pass the full user input AS-IS — do NOT extract just the code.**

#### Step 4: Verify
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py check
```

#### Step 5: Activate
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py activate
```

**If activate fails with "credentials not found"**, fall back to the set-token method.

### If it fails
1. **Credentials not found after login**: Use the `set-token` method instead
2. Run `debug-creds` to see what credential files exist on the filesystem
3. Run `debug` to see what `claude login` is showing in tmux
4. Run `cleanup` then try again, or use `set-token`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Credentials not found" after login | Use `set-token` method — the container can't reliably find the credentials file |
| "No OAuth URL found" | Run `debug` to see tmux output |
| Billing/credit error | The subscription may need credits. Check claude.ai/account |
| Token expired | Re-run `set-token` with a fresh token from local machine |

## Notes

- **`set-token` is the recommended method** — it bypasses all credential file issues
- The AUGMI API (`PUT /api/agents/{id}/provider`) handles machine env var updates
- OAuth tokens expire periodically — users may need to re-send their token
- All output is JSON for easy parsing by the AI agent
- The script has zero external dependencies (Python 3 standard library only)
