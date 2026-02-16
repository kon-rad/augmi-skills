#!/usr/bin/env python3
"""
Meta API Authentication & Account Discovery.
Handles token exchange, validation, and listing connected accounts.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


def get_env(key: str, required: bool = True) -> str | None:
    val = os.getenv(key)
    if required and not val:
        print(f"Error: {key} environment variable is not set.")
        sys.exit(1)
    return val


def debug_token(access_token: str) -> dict:
    """Inspect an access token to check validity and permissions."""
    app_id = get_env("META_APP_ID")
    app_secret = get_env("META_APP_SECRET")

    resp = requests.get(
        f"{GRAPH_API_BASE}/debug_token",
        params={
            "input_token": access_token,
            "access_token": f"{app_id}|{app_secret}",
        },
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


def exchange_token(short_lived_token: str) -> dict:
    """Exchange a short-lived token for a long-lived token (60 days)."""
    app_id = get_env("META_APP_ID")
    app_secret = get_env("META_APP_SECRET")

    resp = requests.get(
        f"{GRAPH_API_BASE}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_lived_token,
        },
    )
    resp.raise_for_status()
    data = resp.json()

    print("Long-lived access token generated!")
    print(f"Token: {data['access_token'][:20]}...{data['access_token'][-10:]}")
    print(f"Expires in: {data.get('expires_in', 'unknown')} seconds")
    print(f"\nSet this in your environment:")
    print(f"export META_ACCESS_TOKEN=\"{data['access_token']}\"")
    return data


def verify_token() -> dict:
    """Verify the current access token and show its details."""
    access_token = get_env("META_ACCESS_TOKEN")
    info = debug_token(access_token)

    print("=== Token Status ===")
    print(f"Valid: {info.get('is_valid', False)}")
    print(f"App ID: {info.get('app_id', 'unknown')}")
    print(f"Type: {info.get('type', 'unknown')}")

    if info.get("expires_at"):
        exp = datetime.fromtimestamp(info["expires_at"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        remaining = exp - now
        print(f"Expires: {exp.isoformat()}")
        print(f"Remaining: {remaining.days} days, {remaining.seconds // 3600} hours")
    else:
        print("Expires: Never (System User Token)")

    scopes = info.get("scopes", [])
    print(f"\nPermissions ({len(scopes)}):")
    for scope in scopes:
        print(f"  - {scope}")

    required = [
        "instagram_basic",
        "instagram_content_publish",
        "pages_show_list",
        "pages_read_engagement",
        "pages_manage_posts",
    ]
    missing = [p for p in required if p not in scopes]
    if missing:
        print(f"\nMissing required permissions:")
        for p in missing:
            print(f"  - {p}")
    else:
        print("\nAll required permissions granted.")

    return info


def list_accounts() -> dict:
    """List all Instagram Business accounts and Facebook Pages."""
    access_token = get_env("META_ACCESS_TOKEN")

    # Get Facebook Pages
    print("=== Facebook Pages ===")
    resp = requests.get(
        f"{GRAPH_API_BASE}/me/accounts",
        params={
            "access_token": access_token,
            "fields": "id,name,access_token,instagram_business_account",
        },
    )
    resp.raise_for_status()
    pages = resp.json().get("data", [])

    result = {"pages": [], "instagram_accounts": []}

    for page in pages:
        page_info = {
            "id": page["id"],
            "name": page["name"],
            "page_access_token": page.get("access_token", "")[:20] + "...",
        }
        result["pages"].append(page_info)
        print(f"\nPage: {page['name']}")
        print(f"  Page ID: {page['id']}")

        # Check for linked Instagram account
        ig = page.get("instagram_business_account")
        if ig:
            ig_id = ig["id"]
            # Get Instagram account details
            ig_resp = requests.get(
                f"{GRAPH_API_BASE}/{ig_id}",
                params={
                    "access_token": access_token,
                    "fields": "id,username,name,profile_picture_url,followers_count,media_count",
                },
            )
            if ig_resp.ok:
                ig_data = ig_resp.json()
                ig_info = {
                    "id": ig_data["id"],
                    "username": ig_data.get("username", "unknown"),
                    "name": ig_data.get("name", ""),
                    "followers": ig_data.get("followers_count", 0),
                    "media_count": ig_data.get("media_count", 0),
                }
                result["instagram_accounts"].append(ig_info)
                print(f"  Instagram: @{ig_data.get('username', 'unknown')}")
                print(f"  IG Account ID: {ig_data['id']}")
                print(f"  Followers: {ig_data.get('followers_count', 'N/A')}")
                print(f"  Posts: {ig_data.get('media_count', 'N/A')}")
        else:
            print("  Instagram: Not linked")

    if not pages:
        print("No Facebook Pages found. Make sure your token has pages_show_list permission.")

    print(f"\n=== Summary ===")
    print(f"Facebook Pages: {len(result['pages'])}")
    print(f"Instagram Accounts: {len(result['instagram_accounts'])}")

    if result["instagram_accounts"]:
        ig = result["instagram_accounts"][0]
        print(f"\nRecommended .env settings:")
        print(f'INSTAGRAM_BUSINESS_ACCOUNT_ID="{ig["id"]}"')
    if result["pages"]:
        page = result["pages"][0]
        print(f'FACEBOOK_PAGE_ID="{page["id"]}"')

    return result


def main():
    parser = argparse.ArgumentParser(description="Meta API Authentication")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # exchange-token
    exchange_parser = subparsers.add_parser(
        "exchange-token", help="Exchange short-lived token for long-lived token"
    )
    exchange_parser.add_argument(
        "--short-lived-token", required=True, help="Short-lived access token"
    )

    # verify
    subparsers.add_parser("verify", help="Verify current access token")

    # list-accounts
    subparsers.add_parser(
        "list-accounts", help="List connected Instagram and Facebook accounts"
    )

    args = parser.parse_args()

    if args.command == "exchange-token":
        exchange_token(args.short_lived_token)
    elif args.command == "verify":
        verify_token()
    elif args.command == "list-accounts":
        list_accounts()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
