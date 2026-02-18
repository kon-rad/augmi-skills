#!/usr/bin/env python3
"""
Claude Code Auth Manager for VPS/Headless Environments

Manages the `claude login` OAuth flow using tmux to keep the process alive
across multiple interactions (e.g., from a Telegram bot).

Usage:
    python3 auth_manager.py status          # Check auth status
    python3 auth_manager.py start           # Start login (subscription by default)
    python3 auth_manager.py start console   # Start login with Console/API account
    python3 auth_manager.py submit <code>   # Submit auth code or callback URL
    python3 auth_manager.py check           # Check if login completed
    python3 auth_manager.py cleanup         # Kill any stale login sessions
    python3 auth_manager.py transfer        # Transfer auth.json from base64 stdin
    python3 auth_manager.py debug           # Dump full tmux output for troubleshooting
"""

import subprocess
import sys
import os
import time
import re
import json
import shutil

TMUX_SESSION = "claude-auth"
AUTH_TIMEOUT = 300  # 5 minutes max for the login process
POLL_INTERVAL = 1


def run(cmd, capture=True, timeout=30):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture,
            text=True, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 1
    except Exception as e:
        return "", str(e), 1


def has_tmux():
    """Check if tmux is installed."""
    return shutil.which("tmux") is not None


def has_claude():
    """Check if claude CLI is installed."""
    return shutil.which("claude") is not None


def tmux_session_exists():
    """Check if our auth tmux session exists."""
    _, _, code = run(f"tmux has-session -t {TMUX_SESSION} 2>/dev/null")
    return code == 0


def get_tmux_output():
    """Capture the current tmux pane content."""
    if not tmux_session_exists():
        return ""
    stdout, _, code = run(
        f"tmux capture-pane -t {TMUX_SESSION} -p -S -200"
    )
    return stdout if code == 0 else ""


def extract_url(text):
    """Extract OAuth URL from tmux output."""
    # Look for the OAuth authorization URL (claude.ai subscription flow)
    urls = re.findall(r'https://claude\.ai/oauth/authorize\S+', text)
    if urls:
        return urls[-1]

    # Console OAuth URL pattern
    urls = re.findall(r'https://console\.anthropic\.com/\S*oauth\S+', text)
    if urls:
        return urls[-1]

    # Fallback: look for any URL with oauth or authorize
    urls = re.findall(r'https://\S*(?:oauth|authorize)\S+', text)
    if urls:
        return urls[-1]

    # Fallback: any https URL (but not the "Open this URL" instruction itself)
    urls = re.findall(r'https://\S+', text)
    if urls:
        return urls[-1]

    return None


def detect_screen(text):
    """
    Detect what screen claude login is currently showing.
    Returns: 'theme', 'login_method', 'url', or 'unknown'.
    """
    # Check for OAuth URL first (highest priority)
    if re.search(r'https://\S*(?:oauth|authorize)\S+', text):
        return "url"

    lower = text.lower()

    # Login method selection screen (check before theme since it's more specific)
    login_method_keywords = [
        "select login",
        "login method",
        "how would you like",
        "subscription",
        "console account",
        "api usage",
        "claude.ai account",
        "anthropic console",
    ]
    if any(kw in lower for kw in login_method_keywords):
        return "login_method"

    # Theme/splash screen - detected by ASCII art block characters
    # Claude login shows a large ASCII art banner with block elements
    block_chars = ['\u2588', '\u2591', '\u2592', '\u2593']  # █ ░ ▒ ▓
    block_count = sum(text.count(c) for c in block_chars)
    if block_count > 10:
        return "theme"

    # Also detect theme by keywords
    theme_keywords = [
        "select a theme",
        "theme",
        "dark mode",
        "light mode",
        "color scheme",
    ]
    if any(kw in lower for kw in theme_keywords):
        return "theme"

    return "unknown"


def send_enter():
    """Send Enter key to the tmux session."""
    if tmux_session_exists():
        run(f"tmux send-keys -t {TMUX_SESSION} Enter")
        return True
    return False


def select_login_method(method="subscription"):
    """
    Navigate the login method menu in tmux.
    method: 'subscription' (default) for Pro/Max plan, 'console' for API billing
    """
    if not tmux_session_exists():
        return False

    if method == "console":
        # Option 2: Anthropic Console account - press Down then Enter
        run(f"tmux send-keys -t {TMUX_SESSION} Down")
        time.sleep(0.3)
        run(f"tmux send-keys -t {TMUX_SESSION} Enter")
    else:
        # Option 1: Claude subscription - already highlighted by default, just press Enter
        run(f"tmux send-keys -t {TMUX_SESSION} Enter")

    return True


def validate_input(user_input):
    """
    Validate that user input looks like an auth code or callback URL.
    Returns (is_valid, cleaned_input, input_type).
    """
    cleaned = user_input.strip()

    if not cleaned:
        return False, "", "empty"

    # Full callback URL
    if cleaned.startswith("http"):
        if "code=" in cleaned or "callback" in cleaned or "oauth" in cleaned:
            return True, cleaned, "url"
        # Any URL is worth trying
        if len(cleaned) > 20:
            return True, cleaned, "url"
        return False, cleaned, "short_url"

    # Code#state format
    if "#" in cleaned:
        return True, cleaned, "code_state"

    # Raw code - should be at least 10 chars of alphanumeric
    if len(cleaned) >= 10:
        return True, cleaned, "code"

    return False, cleaned, "too_short"


# ──────────────────────────────────────────────
# Commands
# ──────────────────────────────────────────────

def cmd_status():
    """Check if Claude Code is authenticated."""
    if not has_claude():
        print(json.dumps({
            "status": "error",
            "message": "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
        }))
        return 1

    # Try running a simple command to test auth
    stdout, stderr, code = run("claude -p 'hi' --output-format json 2>&1", timeout=30)

    if code == 0 and "error" not in stdout.lower():
        print(json.dumps({
            "status": "authenticated",
            "message": "Claude Code is authenticated and working."
        }))
        return 0

    # Check for OAuth token files
    config_dir = os.path.expanduser("~/.config/claude-code")
    auth_file = os.path.join(config_dir, "auth.json")
    has_auth_file = os.path.exists(auth_file)

    # Check if there's a pending login session
    has_pending = tmux_session_exists()

    print(json.dumps({
        "status": "not_authenticated",
        "auth_file_exists": has_auth_file,
        "pending_login": has_pending,
        "error": stderr[:200] if stderr else stdout[:200],
        "message": "Claude Code is NOT authenticated. Run 'start' to begin login."
    }))
    return 1


def cmd_start(method="subscription"):
    """Start the claude login flow in a tmux session."""
    if not has_tmux():
        print(json.dumps({
            "status": "error",
            "message": "tmux not found. Install with: apt install tmux (or brew install tmux)"
        }))
        return 1

    if not has_claude():
        print(json.dumps({
            "status": "error",
            "message": "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
        }))
        return 1

    # Kill any existing session
    if tmux_session_exists():
        run(f"tmux kill-session -t {TMUX_SESSION}")
        time.sleep(1)

    # Start claude login in a new tmux session
    # Use 'script' or direct command - tmux provides the PTY for interactive prompts
    run(
        f"tmux new-session -d -s {TMUX_SESSION} "
        f"'claude login 2>&1; echo AUTH_DONE; sleep 120'"
    )
    time.sleep(2)

    if not tmux_session_exists():
        print(json.dumps({
            "status": "error",
            "message": "Failed to start tmux session."
        }))
        return 1

    # Navigate through all interactive prompts until we find the OAuth URL.
    # claude login may show: theme screen → login method → OAuth URL
    # We handle each screen as we encounter it.
    url = None
    screens_handled = set()
    last_output = ""
    max_iterations = 45  # Up to ~60 seconds total (2s initial + 45*1.2s avg)

    for i in range(max_iterations):
        time.sleep(1)
        output = get_tmux_output()

        # Skip if output hasn't changed (still loading)
        if output == last_output and i < 5:
            continue
        last_output = output

        screen = detect_screen(output)

        if screen == "url":
            url = extract_url(output)
            if url:
                break

        elif screen == "theme" and "theme" not in screens_handled:
            # Theme/splash screen - press Enter to accept default
            send_enter()
            screens_handled.add("theme")
            time.sleep(2)  # Give time for next screen to load

        elif screen == "login_method" and "login_method" not in screens_handled:
            # Login method selection
            select_login_method(method)
            screens_handled.add("login_method")
            time.sleep(2)  # Give time for OAuth URL to generate

        elif screen == "unknown":
            # If we've been waiting a while and nothing is recognized,
            # try pressing Enter as a fallback (might be a "press Enter to continue" prompt)
            if i > 5 and i % 5 == 0:
                send_enter()
                time.sleep(1)

        # Safety: if tmux session died, bail out
        if not tmux_session_exists():
            break

    if not url:
        output = get_tmux_output()
        print(json.dumps({
            "status": "error",
            "message": (
                "No OAuth URL found after ~60 seconds. "
                "The login process may require manual interaction. "
                "Try: tmux attach -t claude-auth"
            ),
            "screens_handled": list(screens_handled),
            "tmux_output": output[-800:] if output else "empty"
        }))
        return 1

    print(json.dumps({
        "status": "waiting_for_code",
        "oauth_url": url,
        "message": (
            "Login started! Open this URL in your browser and authorize.\n"
            "After authorizing, you will see either:\n"
            "  a) A code on the page - send me that code\n"
            "  b) A redirect to localhost that fails - copy the FULL URL "
            "from your browser address bar and send it to me\n"
            "Either format works - just send whatever you see."
        ),
        "method": method,
        "session": TMUX_SESSION
    }))
    return 0


def cmd_submit(user_input):
    """Submit the authorization code or callback URL to the waiting claude login process."""
    if not tmux_session_exists():
        print(json.dumps({
            "status": "error",
            "message": (
                "No login session found. The login process may have timed out. "
                "Run 'start' to begin a new login."
            )
        }))
        return 1

    # Validate the input
    is_valid, cleaned_input, input_type = validate_input(user_input)

    if not is_valid:
        print(json.dumps({
            "status": "error",
            "message": (
                f"Invalid input ({input_type}). Please paste either:\n"
                "  - The authorization code shown on the page\n"
                "  - The full redirect URL from your browser address bar"
            ),
            "received_input": user_input[:100]
        }))
        return 1

    # Send the FULL user input to the tmux session using literal mode (-l)
    # This lets claude login parse it however it expects (code, URL, code#state)
    # We use -l to prevent tmux from interpreting any characters as special keys
    escaped = cleaned_input.replace("'", "'\\''")
    run(f"tmux send-keys -t {TMUX_SESSION} -l '{escaped}'")
    time.sleep(0.3)
    run(f"tmux send-keys -t {TMUX_SESSION} Enter")

    # Wait longer and check the result (up to 15 seconds)
    for i in range(15):
        time.sleep(1)
        output = get_tmux_output()
        lower_output = output.lower()

        # Success indicators
        if any(kw in output for kw in ["AUTH_DONE"]):
            run(f"tmux kill-session -t {TMUX_SESSION}")
            print(json.dumps({
                "status": "success",
                "message": "Authentication completed successfully! Claude Code is now logged in."
            }))
            return 0

        if any(kw in lower_output for kw in [
            "successfully", "authenticated", "logged in", "set up",
            "you are now logged in", "welcome"
        ]):
            run(f"tmux kill-session -t {TMUX_SESSION}")
            print(json.dumps({
                "status": "success",
                "message": "Authentication completed successfully! Claude Code is now logged in."
            }))
            return 0

        # Error indicators
        if any(kw in lower_output for kw in [
            "invalid code", "expired", "invalid_grant", "authorization failed",
            "could not authenticate", "try again"
        ]):
            print(json.dumps({
                "status": "error",
                "message": "Authentication failed. The code may be expired or invalid.",
                "input_type": input_type,
                "tmux_output": output[-800:],
                "suggestion": "Run 'start' to get a fresh login URL and try again quickly."
            }))
            return 1

    # After 15s, check final state
    output = get_tmux_output()

    # Check if tmux session ended (might have succeeded and exited)
    if not tmux_session_exists():
        # Verify auth by testing claude
        stdout, _, code = run("claude -p 'test' --output-format json 2>&1", timeout=20)
        if code == 0 and "error" not in stdout.lower():
            print(json.dumps({
                "status": "success",
                "message": "Authentication completed! Claude Code is now logged in."
            }))
            return 0

    # Not sure yet - might still be processing
    print(json.dumps({
        "status": "pending",
        "message": (
            "Code submitted but no clear success/error after 15 seconds. "
            "Run 'check' to verify, or 'debug' to see the full output."
        ),
        "input_type": input_type,
        "tmux_output": output[-500:]
    }))
    return 0


def cmd_check():
    """Check if the login completed."""
    if tmux_session_exists():
        output = get_tmux_output()
        lower_output = output.lower()

        success_keywords = [
            "auth_done", "success", "set up", "logged in",
            "authenticated", "welcome", "you are now"
        ]
        if any(kw in lower_output for kw in success_keywords):
            run(f"tmux kill-session -t {TMUX_SESSION}")
            print(json.dumps({
                "status": "success",
                "message": "Authentication completed! Claude Code is logged in."
            }))
            return 0

        error_keywords = [
            "invalid", "expired", "failed", "could not",
            "try again", "authorization failed"
        ]
        if any(kw in lower_output for kw in error_keywords):
            print(json.dumps({
                "status": "error",
                "message": "Login appears to have failed.",
                "tmux_output": output[-800:]
            }))
            return 1

        print(json.dumps({
            "status": "pending",
            "message": "Login still in progress...",
            "tmux_output": output[-500:]
        }))
        return 0

    # No tmux session - check if auth works
    stdout, stderr, code = run("claude -p 'test' --output-format json 2>&1", timeout=20)
    if code == 0 and "error" not in stdout.lower():
        print(json.dumps({
            "status": "success",
            "message": "Claude Code is authenticated and working!"
        }))
        return 0

    print(json.dumps({
        "status": "not_authenticated",
        "message": "No active login session and not authenticated. Run 'start' to begin."
    }))
    return 1


def cmd_cleanup():
    """Kill any stale login sessions."""
    if tmux_session_exists():
        run(f"tmux kill-session -t {TMUX_SESSION}")
        print(json.dumps({
            "status": "cleaned",
            "message": "Killed stale auth session."
        }))
    else:
        print(json.dumps({
            "status": "clean",
            "message": "No auth sessions to clean up."
        }))
    return 0


def cmd_debug():
    """Dump full tmux output for troubleshooting."""
    if not tmux_session_exists():
        print(json.dumps({
            "status": "no_session",
            "message": "No active tmux session. Nothing to debug."
        }))
        return 0

    output = get_tmux_output()
    print(json.dumps({
        "status": "debug",
        "session": TMUX_SESSION,
        "tmux_output": output,
        "output_length": len(output),
        "message": "Full tmux pane content shown above."
    }))
    return 0


def find_oauth_token():
    """
    Find the OAuth access token from Claude Code's credentials file.
    Returns (access_token, refresh_token, cred_path) or (None, None, None).
    """
    # Possible credential file locations
    cred_paths = [
        os.path.expanduser("~/.claude/.credentials.json"),
        os.path.expanduser("~/.claude/credentials.json"),
        os.path.expanduser("~/.config/claude-code/auth.json"),
        os.path.expanduser("~/.config/claude/credentials.json"),
    ]

    for path in cred_paths:
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        # Format 1: {"claudeAiOauth": {"accessToken": "...", "refreshToken": "..."}}
        if "claudeAiOauth" in data and isinstance(data["claudeAiOauth"], dict):
            oauth = data["claudeAiOauth"]
            token = oauth.get("accessToken") or oauth.get("access_token")
            refresh = oauth.get("refreshToken") or oauth.get("refresh_token")
            if token:
                return token, refresh, path

        # Format 2: {"accessToken": "...", "refreshToken": "..."}
        token = data.get("accessToken") or data.get("access_token")
        if token:
            refresh = data.get("refreshToken") or data.get("refresh_token")
            return token, refresh, path

        # Format 3: {"oauth_access_token": "...", ...}
        token = data.get("oauth_access_token") or data.get("oauthAccessToken")
        if token:
            refresh = data.get("oauth_refresh_token") or data.get("oauthRefreshToken")
            return token, refresh, path

        # Format 4: nested under provider key like {"anthropic": {"accessToken": "..."}}
        for key, val in data.items():
            if isinstance(val, dict):
                token = val.get("accessToken") or val.get("access_token")
                if token:
                    refresh = val.get("refreshToken") or val.get("refresh_token")
                    return token, refresh, path

    return None, None, None


def cmd_activate():
    """
    After claude login succeeds, activate subscription auth for OpenClaw.
    Extracts the OAuth token, saves it persistently, clears API keys,
    and restarts the gateway so OpenClaw uses the subscription.
    """
    # Step 1: Find the OAuth token from claude login credentials
    access_token, refresh_token, cred_path = find_oauth_token()

    if not access_token:
        # Maybe claude login hasn't been done, or credentials are elsewhere
        # Try running claude to check if it works
        stdout, stderr, code = run("claude -p 'test' --output-format json 2>&1", timeout=20)
        if code == 0 and "error" not in stdout.lower():
            print(json.dumps({
                "status": "warning",
                "message": (
                    "Claude Code CLI is authenticated, but could not find "
                    "the credentials file to extract the OAuth token. "
                    "Checked: ~/.claude/.credentials.json, ~/.config/claude-code/auth.json. "
                    "The subscription may still work if ANTHROPIC_API_KEY is cleared."
                )
            }))
        else:
            print(json.dumps({
                "status": "error",
                "message": (
                    "No OAuth token found. Run 'start' to authenticate with "
                    "claude login first, then run 'activate'."
                ),
                "checked_paths": [
                    "~/.claude/.credentials.json",
                    "~/.claude/credentials.json",
                    "~/.config/claude-code/auth.json",
                ]
            }))
            return 1

    state_dir = os.environ.get("OPENCLAW_STATE_DIR", "/data")

    # Step 2: Save token persistently to /data/ volume (survives restarts)
    if access_token:
        token_data = {
            "accessToken": access_token,
            "source": cred_path,
            "savedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if refresh_token:
            token_data["refreshToken"] = refresh_token

        token_file = os.path.join(state_dir, ".claude-subscription-token")
        try:
            with open(token_file, "w") as f:
                json.dump(token_data, f)
            os.chmod(token_file, 0o600)
        except IOError as e:
            print(json.dumps({
                "status": "error",
                "message": f"Failed to save token to {token_file}: {e}"
            }))
            return 1

    # Step 3: Create env override script (sourced by start.sh on boot)
    env_file = os.path.join(state_dir, ".env.subscription")
    try:
        with open(env_file, "w") as f:
            if access_token:
                f.write(f'export CLAUDE_CODE_OAUTH_TOKEN="{access_token}"\n')
            f.write('export ANTHROPIC_API_KEY=""\n')
            f.write('export AUTH_MODE="subscription"\n')
        os.chmod(env_file, 0o600)
    except IOError as e:
        print(json.dumps({
            "status": "error",
            "message": f"Failed to write env override: {e}"
        }))
        return 1

    # Step 4: Try to call AUGMI API to update machine env vars for persistence
    augmi_url = os.environ.get("AUGMI_API_URL", "")
    project_id = os.environ.get("PROJECT_ID", "")
    api_key = os.environ.get("CONTAINER_API_KEY", "")
    api_updated = False

    if augmi_url and project_id and api_key and access_token:
        import urllib.request
        import urllib.error
        try:
            payload = json.dumps({
                "authMode": "subscription",
                "oauthAccessToken": access_token,
                "provider": "anthropic",
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{augmi_url}/api/agents/{project_id}/provider",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                method="PUT",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    api_updated = True
        except Exception:
            pass  # Non-fatal, we still have the file-based fallback

    # Step 5: Report results
    result = {
        "status": "success",
        "message": "Subscription auth activated!",
        "token_saved": os.path.join(state_dir, ".claude-subscription-token"),
        "env_override": env_file,
        "api_updated": api_updated,
    }

    if api_updated:
        result["next_step"] = (
            "Machine env vars updated. The container will restart automatically "
            "with subscription auth. ANTHROPIC_API_KEY has been cleared."
        )
    else:
        result["next_step"] = (
            "Token saved to persistent storage. To fully activate, restart the "
            "agent from the AUGMI dashboard or run: "
            "flyctl machines restart <machine_id> -a hexly-sandboxes"
        )

    print(json.dumps(result))
    return 0


def cmd_transfer():
    """
    Transfer auth credentials from base64-encoded auth.json.

    Usage: echo '<base64>' | python3 auth_manager.py transfer
    Or:    python3 auth_manager.py transfer <base64_string>
    """
    import base64

    # Read base64 from argument or stdin
    if len(sys.argv) > 2:
        b64_data = sys.argv[2]
    else:
        b64_data = sys.stdin.read().strip()

    if not b64_data:
        print(json.dumps({
            "status": "error",
            "message": (
                "No data provided. On your LOCAL machine run:\n"
                "  cat ~/.config/claude-code/auth.json | base64\n"
                "Then send that string here."
            )
        }))
        return 1

    try:
        auth_json = base64.b64decode(b64_data).decode('utf-8')
        # Validate it's valid JSON
        json.loads(auth_json)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Invalid base64 or JSON: {e}"
        }))
        return 1

    config_dir = os.path.expanduser("~/.config/claude-code")
    os.makedirs(config_dir, exist_ok=True)
    auth_file = os.path.join(config_dir, "auth.json")

    # Backup existing
    if os.path.exists(auth_file):
        backup = auth_file + ".backup"
        shutil.copy2(auth_file, backup)

    with open(auth_file, 'w') as f:
        f.write(auth_json)
    os.chmod(auth_file, 0o600)

    print(json.dumps({
        "status": "success",
        "message": f"Auth credentials written to {auth_file}. Run 'status' to verify."
    }))
    return 0


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

COMMANDS = {
    "status": (cmd_status, "Check authentication status"),
    "start": (cmd_start, "Start OAuth login flow"),
    "submit": (cmd_submit, "Submit auth code or callback URL"),
    "check": (cmd_check, "Check if login completed"),
    "activate": (cmd_activate, "Switch OpenClaw to use subscription auth"),
    "cleanup": (cmd_cleanup, "Kill stale login sessions"),
    "transfer": (cmd_transfer, "Transfer auth.json via base64"),
    "debug": (cmd_debug, "Dump full tmux output for troubleshooting"),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print("Claude Code Auth Manager")
        print(f"\nUsage: {sys.argv[0]} <command> [args]")
        print("\nCommands:")
        for name, (_, desc) in COMMANDS.items():
            print(f"  {name:12s} {desc}")
        print("\nExamples:")
        print(f"  {sys.argv[0]} status")
        print(f"  {sys.argv[0]} start                    # Subscription login (default)")
        print(f"  {sys.argv[0]} start console             # Console/API login")
        print(f"  {sys.argv[0]} submit <code_or_url>      # Submit code or full redirect URL")
        print(f"  {sys.argv[0]} debug                     # Dump tmux output")
        return 0

    cmd_name = sys.argv[1]
    if cmd_name not in COMMANDS:
        print(json.dumps({
            "status": "error",
            "message": f"Unknown command: {cmd_name}. Use 'help' for usage."
        }))
        return 1

    cmd_func = COMMANDS[cmd_name][0]

    if cmd_name == "submit":
        if len(sys.argv) < 3:
            print(json.dumps({
                "status": "error",
                "message": "Missing auth code/URL. Usage: submit <code_or_url>"
            }))
            return 1
        # Join all remaining args in case the URL was split by spaces
        return cmd_func(" ".join(sys.argv[2:]))

    if cmd_name == "start":
        method = sys.argv[2] if len(sys.argv) > 2 else "subscription"
        return cmd_func(method)

    return cmd_func()


if __name__ == "__main__":
    sys.exit(main())
