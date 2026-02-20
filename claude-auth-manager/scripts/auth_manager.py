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

    # Parse JSON output to check is_error field (more reliable than string matching)
    is_authenticated = False
    if code == 0 and stdout:
        try:
            parsed = json.loads(stdout)
            # JSON output has {"is_error": false, "result": "..."} on success
            if parsed.get("is_error") is False:
                is_authenticated = True
        except (json.JSONDecodeError, TypeError):
            # Fallback: check for actual error keywords (not "is_error")
            # Avoid matching "is_error":false which contains "error"
            if "authentication_error" not in stdout.lower() and "unauthorized" not in stdout.lower():
                is_authenticated = True

    if is_authenticated:
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
    """Check if the login completed by verifying credentials file exists."""
    if tmux_session_exists():
        output = get_tmux_output()
        lower_output = output.lower()

        # Check for clear error indicators FIRST (before success)
        error_keywords = [
            "invalid code", "expired", "authorization failed",
            "try again", "could not exchange", "invalid_grant"
        ]
        if any(kw in lower_output for kw in error_keywords):
            print(json.dumps({
                "status": "error",
                "message": "Login appears to have failed.",
                "tmux_output": output[-800:]
            }))
            return 1

        success_keywords = [
            "auth_done", "success", "set up", "logged in",
            "authenticated", "welcome", "you are now"
        ]
        if any(kw in lower_output for kw in success_keywords):
            # Verify credentials file actually exists before declaring success
            token, _, cred_path = find_oauth_token()
            if token:
                run(f"tmux kill-session -t {TMUX_SESSION}")
                print(json.dumps({
                    "status": "success",
                    "message": "Authentication completed! Credentials saved.",
                    "credentials_path": cred_path,
                }))
                return 0
            else:
                # Keywords matched but no cred file yet — wait a bit
                time.sleep(3)
                token, _, cred_path = find_oauth_token()
                if token:
                    run(f"tmux kill-session -t {TMUX_SESSION}")
                    print(json.dumps({
                        "status": "success",
                        "message": "Authentication completed! Credentials saved.",
                        "credentials_path": cred_path,
                    }))
                    return 0
                # Still no file — report the situation
                print(json.dumps({
                    "status": "warning",
                    "message": (
                        "Login output shows success keywords but credentials "
                        "file not found. The token exchange may have failed. "
                        "Run 'debug' to see full output."
                    ),
                    "tmux_output": output[-800:]
                }))
                return 1

        print(json.dumps({
            "status": "pending",
            "message": "Login still in progress...",
            "tmux_output": output[-500:]
        }))
        return 0

    # No tmux session — check credentials file directly
    token, _, cred_path = find_oauth_token()
    if token:
        print(json.dumps({
            "status": "success",
            "message": "Claude Code credentials found and valid!",
            "credentials_path": cred_path,
        }))
        return 0

    # Fall back to trying the CLI
    stdout, stderr, code = run("claude -p 'test' --output-format json 2>&1", timeout=20)
    if code == 0:
        # CLI works — might be billing error but still authenticated
        if "billing" in stdout.lower() or "credit" in stdout.lower() or "balance" in stdout.lower():
            print(json.dumps({
                "status": "authenticated_but_billing_error",
                "message": (
                    "Claude Code IS authenticated but has a billing/credit issue. "
                    "The subscription may still work — try running 'activate'."
                ),
                "cli_output": stdout[:500],
            }))
            return 0
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


def _try_extract_token(path):
    """Try to extract OAuth token from a JSON file at the given path.
    Returns (access_token, refresh_token, path) or (None, None, None).
    """
    if not os.path.exists(path):
        return None, None, None
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None, None, None

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


def find_oauth_token():
    """
    Find the OAuth access token from Claude Code's credentials file.
    Returns (access_token, refresh_token, cred_path) or (None, None, None).
    """
    home = os.path.expanduser("~")

    # Known credential file locations (in priority order)
    cred_paths = [
        os.path.join(home, ".claude", ".credentials.json"),
        os.path.join(home, ".claude", "credentials.json"),
        os.path.join(home, ".config", "claude-code", "auth.json"),
        os.path.join(home, ".config", "claude", "credentials.json"),
        # Explicit /root paths (container often runs as root)
        "/root/.claude/.credentials.json",
        "/root/.claude/credentials.json",
        "/root/.config/claude-code/auth.json",
        # Data volume paths (might be persisted there)
        "/data/.claude-subscription-token",
        "/data/.claude/.credentials.json",
    ]

    # De-duplicate while preserving order
    seen = set()
    unique_paths = []
    for p in cred_paths:
        rp = os.path.realpath(p)
        if rp not in seen:
            seen.add(rp)
            unique_paths.append(p)

    for path in unique_paths:
        token, refresh, found_path = _try_extract_token(path)
        if token:
            return token, refresh, found_path

    # Fallback: search filesystem for credential files
    search_dirs = [home, "/root", "/data"]
    search_names = [".credentials.json", "credentials.json", "auth.json"]

    searched = set()
    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        real_dir = os.path.realpath(search_dir)
        if real_dir in searched:
            continue
        searched.add(real_dir)
        try:
            for dirpath, dirnames, filenames in os.walk(search_dir):
                # Skip deep traversal to avoid slow searches
                depth = dirpath.replace(search_dir, "").count(os.sep)
                if depth > 4:
                    dirnames.clear()
                    continue
                # Skip irrelevant directories
                skip = {"node_modules", ".npm", ".cache", "logs", "workspace"}
                dirnames[:] = [d for d in dirnames if d not in skip]
                for fname in filenames:
                    if fname in search_names:
                        full = os.path.join(dirpath, fname)
                        if os.path.realpath(full) not in seen:
                            seen.add(os.path.realpath(full))
                            token, refresh, found_path = _try_extract_token(full)
                            if token:
                                return token, refresh, found_path
        except PermissionError:
            continue

    return None, None, None


def cmd_activate(model=None):
    """
    After claude login succeeds, switch OpenClaw to use the Claude Code
    subscription for ALL LLM calls. This:
    1. Extracts the OAuth token from claude login credentials
    2. Saves it persistently to /data/ (survives restarts)
    3. Calls the Augmi API to update machine env vars:
       - Sets CLAUDE_CODE_OAUTH_TOKEN
       - Clears ANTHROPIC_API_KEY (it takes priority over subscription)
       - Switches model to a Claude model
    4. Falls back to direct Fly.io API if Augmi API fails
    5. The machine restarts with subscription auth active
    """
    import urllib.request
    import urllib.error

    # Default to claude-sonnet-4 if no model specified
    if not model:
        model = "anthropic/claude-sonnet-4-20250514"

    # Step 1: Find the OAuth token from claude login credentials
    access_token, refresh_token, cred_path = find_oauth_token()

    if not access_token:
        # Debug: find what credential-like files exist
        home = os.path.expanduser("~")
        debug_info = {"home": home, "found_files": []}
        for search_dir in [home, "/root", "/data"]:
            if not os.path.isdir(search_dir):
                continue
            try:
                for dirpath, dirnames, filenames in os.walk(search_dir):
                    depth = dirpath.replace(search_dir, "").count(os.sep)
                    if depth > 3:
                        dirnames.clear()
                        continue
                    skip = {"node_modules", ".npm", ".cache", "logs", "workspace"}
                    dirnames[:] = [d for d in dirnames if d not in skip]
                    for fname in filenames:
                        if "credential" in fname.lower() or "auth" in fname.lower() or "oauth" in fname.lower():
                            full = os.path.join(dirpath, fname)
                            try:
                                size = os.path.getsize(full)
                            except OSError:
                                size = -1
                            debug_info["found_files"].append({"path": full, "size": size})
            except PermissionError:
                continue

        # Also check if claude CLI works at all
        stdout, stderr, code = run(
            "claude -p 'say ok' --output-format json 2>&1", timeout=30
        )
        debug_info["claude_cli_exit_code"] = code
        if stdout:
            debug_info["claude_cli_output"] = stdout[:500]

        # Distinguish: billing error (authenticated) vs auth error (not authenticated)
        lower_out = stdout.lower()
        is_billing_error = any(kw in lower_out for kw in [
            "billing", "credit", "balance", "insufficient", "quota",
            "rate limit", "payment", "exceeded"
        ])
        is_auth_error = any(kw in lower_out for kw in [
            "not authenticated", "unauthorized", "invalid api key",
            "authentication required", "not logged in"
        ])
        cli_works = code == 0 and not is_auth_error

        debug_info["claude_cli_works"] = cli_works
        debug_info["is_billing_error"] = is_billing_error

        if cli_works or is_billing_error:
            # CLI is authenticated (even if billing fails) — the cred file
            # is just not where we expected. Offer transfer method.
            print(json.dumps({
                "status": "error",
                "message": (
                    "Claude Code IS authenticated (CLI responds) but "
                    "credentials file not found at any expected path. "
                    "This happens when claude stores tokens in a non-standard "
                    "location. Use the transfer method instead: on your LOCAL "
                    "machine run 'cat ~/.claude/.credentials.json | base64' "
                    "and send the base64 string."
                ),
                "debug": debug_info,
            }))
        else:
            print(json.dumps({
                "status": "error",
                "message": (
                    "Could not find OAuth credentials file and claude CLI "
                    "is not authenticated. Run 'start' to begin the login "
                    "flow, then 'activate' after login completes."
                ),
                "debug": debug_info,
            }))
        return 1

    state_dir = os.environ.get("OPENCLAW_STATE_DIR", "/data")

    # Step 2: Save token persistently to /data/ volume
    token_data = {
        "accessToken": access_token,
        "source": cred_path,
        "model": model,
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

    # Step 3: Create env override script
    env_file = os.path.join(state_dir, ".env.subscription")
    try:
        with open(env_file, "w") as f:
            f.write(f'export CLAUDE_CODE_OAUTH_TOKEN="{access_token}"\n')
            f.write('export ANTHROPIC_API_KEY=""\n')
            f.write('export AUTH_MODE="subscription"\n')
        os.chmod(env_file, 0o600)
    except IOError as e:
        pass  # Non-fatal

    # Step 4: Try Augmi API to update machine env vars and restart
    augmi_url = os.environ.get("AUGMI_API_URL", "")
    project_id = os.environ.get("PROJECT_ID", "")
    container_key = os.environ.get("CONTAINER_API_KEY", "")
    machine_id = os.environ.get("FLY_MACHINE_ID", "")
    api_method = None
    api_error = None

    # Attempt 4a: Augmi provider API
    if augmi_url and project_id and container_key:
        try:
            payload = json.dumps({
                "authMode": "subscription",
                "oauthAccessToken": access_token,
                "provider": "anthropic",
                "model": model,
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{augmi_url}/api/agents/{project_id}/provider",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {container_key}",
                },
                method="PUT",
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status == 200:
                    api_method = "augmi_api"
        except Exception as e:
            api_error = str(e)[:200]

    # Attempt 4b: Direct Fly.io Machines API (if Augmi API failed)
    fly_token = os.environ.get("FLY_API_TOKEN", "")
    if not api_method and fly_token and machine_id:
        fly_app = os.environ.get("FLY_APP_NAME", "hexly-sandboxes")
        try:
            # First get current machine config
            req = urllib.request.Request(
                f"https://api.machines.dev/v1/apps/{fly_app}/machines/{machine_id}",
                headers={
                    "Authorization": f"Bearer {fly_token}",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                machine_data = json.loads(resp.read().decode("utf-8"))

            # Update env vars in the machine config
            config = machine_data.get("config", {})
            env = config.get("env", {})
            env["CLAUDE_CODE_OAUTH_TOKEN"] = access_token
            env["ANTHROPIC_API_KEY"] = ""
            config["env"] = env

            # Update the machine
            payload = json.dumps({"config": config}).encode("utf-8")
            req = urllib.request.Request(
                f"https://api.machines.dev/v1/apps/{fly_app}/machines/{machine_id}",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {fly_token}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status in (200, 201):
                    api_method = "fly_api"
        except Exception as e:
            api_error = (api_error or "") + f" | Fly: {str(e)[:200]}"

    # Step 5: Report results
    result = {
        "status": "success" if api_method else "partial",
        "token_found": True,
        "token_source": cred_path,
        "token_saved": token_file,
        "model": model,
        "api_method": api_method,
    }

    if api_method:
        result["message"] = (
            f"Subscription auth activated via {api_method}! "
            f"Model set to {model}. "
            "The container will restart with subscription auth. "
            "ANTHROPIC_API_KEY has been cleared."
        )
    else:
        result["message"] = (
            "OAuth token extracted and saved to persistent storage, but "
            "could not update machine env vars automatically. "
            "The token is saved and will work on next restart if start.sh "
            "checks for it. To restart now, use the Augmi dashboard."
        )
        if api_error:
            result["api_error"] = api_error
        result["manual_steps"] = [
            "Option 1: Restart from Augmi dashboard",
            "Option 2: flyctl machines restart " + (machine_id or "<machine_id>") + " -a hexly-sandboxes",
            "Option 3: Ask the admin to set CLAUDE_CODE_OAUTH_TOKEN on the machine",
        ]

    print(json.dumps(result))
    return 0 if api_method else 0  # Still return success since token was saved


def cmd_set_token():
    """
    Set OAuth token directly and activate subscription auth at runtime.
    No restart needed — uses OpenClaw CLI to apply auth and model changes
    immediately. Also writes persistence files so the config survives restarts.

    Usage: python3 auth_manager.py set-token <oauth_token> [model]

    The token should start with 'sk-ant-' (from `claude setup-token` or keychain).
    """
    if len(sys.argv) < 3:
        print(json.dumps({
            "status": "error",
            "message": (
                "Missing token. Usage: set-token <oauth_token> [model]\n\n"
                "To get your token, on your LOCAL machine run:\n"
                "  claude setup-token\n\n"
                "Or extract manually:\n"
                "  Mac: security find-generic-password -s "
                "'Claude Code-credentials' -g 2>&1\n"
                "  Linux: cat ~/.claude/.credentials.json"
            )
        }))
        return 1

    # Join all token args and strip whitespace/newlines — Telegram often
    # breaks long tokens across multiple lines or messages
    token_parts = sys.argv[2:]
    # If a model arg is present (doesn't start with sk-ant-), separate it
    model_arg = None
    token_pieces = []
    for part in token_parts:
        stripped = part.strip()
        if stripped.startswith("anthropic/") or stripped.startswith("openrouter/"):
            model_arg = stripped
        else:
            token_pieces.append(stripped)
    token = "".join(token_pieces).replace("\n", "").replace("\r", "").replace(" ", "")

    if not token.startswith("sk-ant-"):
        print(json.dumps({
            "status": "error",
            "message": (
                f"Token doesn't look like a Claude token "
                f"(should start with 'sk-ant-'). "
                f"Got: {token[:20]}..."
            )
        }))
        return 1

    model = model_arg if model_arg else "anthropic/claude-sonnet-4-20250514"
    state_dir = os.environ.get("OPENCLAW_STATE_DIR", "/data")
    config_file = os.path.join(state_dir, "openclaw.json")
    applied_method = None
    errors = []

    # ── Method 1: OpenClaw CLI (paste-token) ──
    # Try piping the token to the CLI. This is the official way and
    # triggers auto-reload without restart.
    if shutil.which("openclaw"):
        # Try paste-token via stdin
        try:
            result = subprocess.run(
                ["openclaw", "models", "auth", "paste-token",
                 "--provider", "anthropic",
                 "--profile-id", "anthropic:default"],
                input=token + "\n",
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode == 0:
                applied_method = "openclaw_paste_token"
            else:
                errors.append(f"paste-token: {result.stderr[:200]}")
        except Exception as e:
            errors.append(f"paste-token: {str(e)[:200]}")

        # Set model via CLI — try high-level command first, fall back to config set
        model_set_ok = False
        try:
            result = subprocess.run(
                ["openclaw", "models", "set", model],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                model_set_ok = True
            else:
                errors.append(f"models set: {result.stderr[:200]}")
        except Exception as e:
            errors.append(f"models set: {str(e)[:200]}")

        if not model_set_ok:
            # Fall back to config set with empty fallbacks (avoids invalid model names)
            try:
                model_json = json.dumps({
                    "primary": model,
                    "fallbacks": [],
                })
                result = subprocess.run(
                    ["openclaw", "config", "set",
                     "agents.defaults.model", "--json", model_json],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode != 0:
                    errors.append(f"config set model: {result.stderr[:200]}")
            except Exception as e:
                errors.append(f"config set model: {str(e)[:200]}")

        # Clear fallbacks — invalid fallback models cause "Unknown model" errors at session start
        try:
            result = subprocess.run(
                ["openclaw", "models", "fallbacks", "clear"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                # Not fatal — fallbacks may already be empty or command not available
                errors.append(f"fallbacks clear: {result.stderr[:100]}")
        except Exception as e:
            errors.append(f"fallbacks clear: {str(e)[:100]}")

    # ── Method 2: Direct config modification (fallback) ──
    # If the CLI didn't work, modify openclaw.json directly.
    # OpenClaw auto-reloads on file changes (SIGUSR1).
    if not applied_method and os.path.exists(config_file):
        try:
            with open(config_file) as f:
                config = json.load(f)

            # Add a custom provider with inline apiKey
            if "models" not in config:
                config["models"] = {}
            if "providers" not in config["models"]:
                config["models"]["providers"] = {}

            config["models"]["providers"]["claude-subscription"] = {
                "api": "anthropic-messages",
                "apiKey": token,
            }

            # Update auth profile
            if "auth" not in config:
                config["auth"] = {}
            if "profiles" not in config["auth"]:
                config["auth"]["profiles"] = {}

            config["auth"]["profiles"]["claude-subscription:default"] = {
                "mode": "token",
                "provider": "claude-subscription",
            }

            # Update model to use the custom provider
            if "agents" not in config:
                config["agents"] = {}
            if "defaults" not in config["agents"]:
                config["agents"]["defaults"] = {}

            config["agents"]["defaults"]["model"] = {
                "primary": model,   # model already has full provider/name format
                "fallbacks": [],    # Empty — invalid fallbacks cause immediate session failure
            }

            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            applied_method = "config_file"
        except Exception as e:
            errors.append(f"config file: {str(e)[:200]}")

    # ── Persistence: write files for restart survival ──
    # These files are read by start.sh on container boot.
    token_data = {
        "accessToken": token,
        "source": "set-token",
        "model": model,
        "savedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    token_file = os.path.join(state_dir, ".claude-subscription-token")
    try:
        with open(token_file, "w") as f:
            json.dump(token_data, f)
        os.chmod(token_file, 0o600)
    except IOError:
        pass

    env_file = os.path.join(state_dir, ".env.subscription")
    try:
        with open(env_file, "w") as f:
            f.write(f'export CLAUDE_CODE_OAUTH_TOKEN="{token}"\n')
            f.write('export ANTHROPIC_API_KEY=""\n')
            f.write('export AUTH_MODE="subscription"\n')
            f.write(f'export OPENCLAW_DEFAULT_MODEL="{model}"\n')
            f.write('export OPENCLAW_DEFAULT_PROVIDER="anthropic"\n')
        os.chmod(env_file, 0o600)
    except IOError:
        pass

    # ── Report result ──
    result = {
        "status": "success" if applied_method else "error",
        "method": applied_method,
        "model": model,
        "token_prefix": token[:20] + "...",
        "persistence_files": [token_file, env_file],
    }

    if applied_method == "openclaw_paste_token":
        result["message"] = (
            f"Subscription auth activated via OpenClaw CLI! "
            f"Model set to {model}. "
            "Changes are live — no restart needed."
        )
    elif applied_method == "config_file":
        result["message"] = (
            f"Subscription auth configured via direct config modification. "
            f"Model set to claude-subscription/{model.split('/')[-1]}. "
            "OpenClaw should auto-reload the config. "
            "If it doesn't respond, a restart will pick up the changes."
        )
    else:
        result["message"] = (
            "Could not apply auth at runtime. Token saved to "
            "persistent storage — it will activate on next restart."
        )
        if errors:
            result["errors"] = errors

    print(json.dumps(result))
    return 0 if applied_method else 1


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


def cmd_debug_creds():
    """
    Diagnostic: show exactly where credentials exist on the filesystem.
    Run this if activate can't find the credentials file.
    """
    home = os.path.expanduser("~")
    result = {
        "status": "debug",
        "home": home,
        "user": os.environ.get("USER", "unknown"),
        "claude_config_dir": os.environ.get("CLAUDE_CONFIG_DIR", "(not set)"),
        "known_paths": {},
        "found_credential_files": [],
        "claude_dir_contents": {},
    }

    # Check known paths
    known = [
        os.path.join(home, ".claude", ".credentials.json"),
        os.path.join(home, ".claude", "credentials.json"),
        os.path.join(home, ".config", "claude-code", "auth.json"),
        os.path.join(home, ".config", "claude", "credentials.json"),
        "/root/.claude/.credentials.json",
        "/root/.claude/credentials.json",
        "/data/.claude-subscription-token",
    ]
    for p in known:
        if os.path.exists(p):
            try:
                size = os.path.getsize(p)
                with open(p) as f:
                    content = f.read(200)
                result["known_paths"][p] = {"exists": True, "size": size, "preview": content}
            except Exception as e:
                result["known_paths"][p] = {"exists": True, "error": str(e)}
        else:
            result["known_paths"][p] = {"exists": False}

    # List contents of ~/.claude/ and /root/.claude/
    for claude_dir in [os.path.join(home, ".claude"), "/root/.claude"]:
        if os.path.isdir(claude_dir):
            try:
                entries = os.listdir(claude_dir)
                result["claude_dir_contents"][claude_dir] = entries
            except PermissionError:
                result["claude_dir_contents"][claude_dir] = "(permission denied)"

    # Search for any credential-like files
    for search_dir in [home, "/root", "/data"]:
        if not os.path.isdir(search_dir):
            continue
        try:
            for dirpath, dirnames, filenames in os.walk(search_dir):
                depth = dirpath.replace(search_dir, "").count(os.sep)
                if depth > 3:
                    dirnames.clear()
                    continue
                skip = {"node_modules", ".npm", ".cache", "logs", "workspace"}
                dirnames[:] = [d for d in dirnames if d not in skip]
                for fname in filenames:
                    if "credential" in fname.lower() or fname == "auth.json":
                        full = os.path.join(dirpath, fname)
                        try:
                            size = os.path.getsize(full)
                        except OSError:
                            size = -1
                        result["found_credential_files"].append({
                            "path": full, "size": size
                        })
        except PermissionError:
            continue

    # Try find_oauth_token to see what it returns
    token, refresh, cred_path = find_oauth_token()
    result["find_oauth_token_result"] = {
        "found": token is not None,
        "path": cred_path,
        "token_prefix": token[:20] + "..." if token else None,
    }

    print(json.dumps(result, indent=2))
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
    "set-token": (cmd_set_token, "Set OAuth token directly (most reliable)"),
    "cleanup": (cmd_cleanup, "Kill stale login sessions"),
    "transfer": (cmd_transfer, "Transfer auth.json via base64"),
    "debug": (cmd_debug, "Dump full tmux output for troubleshooting"),
    "debug-creds": (cmd_debug_creds, "Show credential file locations and contents"),
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

    if cmd_name == "activate":
        model = sys.argv[2] if len(sys.argv) > 2 else None
        return cmd_func(model)

    return cmd_func()


if __name__ == "__main__":
    sys.exit(main())
