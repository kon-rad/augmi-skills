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
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py activate
```
**CRITICAL: Run this after `claude login` succeeds.** This command:
1. Reads the OAuth token from `~/.claude/.credentials.json`
2. Saves it to `/data/.claude-subscription-token` (persistent across restarts)
3. Creates `/data/.env.subscription` (sourced by start.sh on boot)
4. Tries to update the Fly.io machine env vars via AUGMI API
5. Clears `ANTHROPIC_API_KEY` so OpenClaw uses the subscription

After activation, the container needs to restart for OpenClaw to pick up the change.

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

When the user asks to authenticate or login:

### Step 1: Check current status
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py status
```
If already authenticated, tell the user and stop.

### Step 2: Start login
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py start
```
Parse the JSON output. Send the `oauth_url` to the user with these instructions:
1. "Click this link to open in your browser"
2. "Sign in with your Anthropic account (the one with Max/Pro subscription)"
3. "After authorizing, you'll see EITHER:"
   - "A code on the page — copy and send it to me"
   - "A redirect to localhost that fails — copy the FULL URL from the address bar and send it"
4. "Send whatever you see — code, URL, anything. I can handle all formats."

### Step 3: Receive and submit the code/URL
When the user sends back a string (code, URL, or anything), submit it AS-IS:
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py submit "<what_user_sent>"
```
**Do NOT try to parse or extract just the code — pass the full user input.**

### Step 4: Verify
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py check
```
Tell the user if authentication succeeded or failed.

### Step 5: Activate subscription auth
**After login is confirmed successful, ALWAYS run activate:**
```bash
python3 .claude/skills/claude-auth-manager/scripts/auth_manager.py activate
```
This switches OpenClaw from API key to subscription auth. It:
- Extracts the OAuth token from `~/.claude/.credentials.json`
- Saves it to `/data/` for persistence across restarts
- Clears `ANTHROPIC_API_KEY` so the subscription takes over
- Tries to update machine env vars via AUGMI API

Tell the user: "Subscription activated! The agent will restart to apply the change."

### If it fails
1. Run `debug` to see what `claude login` is showing
2. Run `cleanup` then `start` again to get a fresh URL
3. The most common failures are:
   - Code expired (user took too long — they need to be faster)
   - Wrong format (old scripts extracted just the code; new one passes through)
   - Menu wasn't selected (check debug output for menu still showing)
4. Alternative: suggest the `transfer` method

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No OAuth URL found" | Run `debug` to see tmux output. May need to manually select menu: `tmux attach -t claude-auth` |
| "No login session found" | The process timed out. Run `start` again |
| Code always fails | Make sure you're sending the FULL input (code or URL), not extracting just the code |
| Menu not auto-selected | The menu format may have changed. Run `debug` and check the output. Try `tmux attach -t claude-auth` |
| Auth works then expires | Re-run the full flow. Consider setting up a cron check |

## Notes

- The tmux session is named `claude-auth` and is auto-cleaned after success
- OAuth tokens expire periodically — users may need to re-authenticate
- All output is JSON for easy parsing by the AI agent
- The script has zero external dependencies (Python 3 standard library only)
- Default login method is `subscription` (Pro/Max); use `start console` for API billing
- The `sleep 120` at the end of the tmux command gives 2 minutes for the user to respond
