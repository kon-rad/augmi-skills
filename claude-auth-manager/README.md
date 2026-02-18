# Claude Auth Manager — How It Works

## The Problem

`claude login` is an interactive process:
1. It generates a secret key (`code_verifier`) and shows you an OAuth URL
2. You open the URL, authorize in your browser, get a one-time code
3. You type that code back into **the same process**
4. The process uses the code + its secret key to get your OAuth token

In Telegram, this breaks because each chat message runs a **separate command**.
The process from message 1 is dead by the time you send the code in message 2.
The agent starts a new `claude login` (new secret key), and your code doesn't
match — so it always fails.

## The Fix: tmux

tmux is a "virtual terminal" that stays open in the background, even when
nobody is looking at it.

```
Without tmux:

  "start login"     → [process starts, prints URL, DIES]
  "here's the code" → [NEW process, new secret key... old code is invalid]


With tmux:

  "start login"     → [process starts inside tmux, prints URL, KEEPS RUNNING]
  "here's the code" → [types code into the SAME process via tmux]
                       → code + original secret key match → SUCCESS
```

## The Three tmux Commands Used

```bash
# 1. START — create a background terminal running claude login
tmux new-session -d -s claude-auth 'claude login'

# 2. READ — screenshot what's on the virtual terminal (to grab the URL)
tmux capture-pane -t claude-auth -p

# 3. TYPE — simulate keyboard input (to enter the auth code)
tmux send-keys -t claude-auth 'your-auth-code-here' Enter
```

## Full Flow in Telegram

```
You:   "login to claude"
Agent: checks status → not authenticated
Agent: starts claude login in tmux → captures OAuth URL
Agent: "Click this link: https://claude.ai/oauth/authorize?..."

You:   *click link → authorize in browser → see code on page*
You:   "vU50Vvi9ie0TdpVtGg4bLb5AC3pqcF2dXhgHaOhrQ4FmCylK"

Agent: pipes your code into tmux → same process receives it
Agent: checks result → success!
Agent: "You're authenticated!"
```

## Prerequisites

The VPS needs:
- `tmux` — `apt install tmux`
- `claude` — `npm install -g @anthropic-ai/claude-code`
- `python3` — usually pre-installed

## Script Commands

```bash
python3 auth_manager.py status          # are we authenticated?
python3 auth_manager.py start           # begin login, get OAuth URL
python3 auth_manager.py submit <code>   # send auth code to waiting process
python3 auth_manager.py check           # did login succeed?
python3 auth_manager.py cleanup         # kill stale sessions
python3 auth_manager.py transfer <b64>  # alternative: paste base64 auth.json
```

## Backup Method: Credential Transfer

If the OAuth flow gives you trouble, you can transfer credentials directly:

```bash
# On your LOCAL machine (where claude login works in a real terminal):
claude login
cat ~/.config/claude-code/auth.json | base64

# Copy the base64 output, send it to the agent, which runs:
python3 auth_manager.py transfer "<base64_string>"
```

## Why the Code Kept Failing Before

The code you pasted (`vU50Vvi9ie...#x0FpOVhd...`) was valid, but:
1. The `#` separates `auth_code#state` — the code was just the first part
2. More importantly, the `claude login` process that generated the matching
   secret key was already dead
3. The agent started a NEW process with a NEW secret key
4. Anthropic's server saw: "this code was issued for secret key A, but you're
   trying to redeem it with secret key B" → rejected

tmux prevents this by keeping process A alive until the code is submitted.
