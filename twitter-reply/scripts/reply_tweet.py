#!/usr/bin/env python3
"""
Post a reply to a specific tweet using the official X API v2 via Tweepy.

Uses OAuth 1.0a (required for write operations on X API).

Usage:
    # Reply to a specific tweet
    python reply_tweet.py --tweet-id 1234567890 --text "Great point! Check out augmi.world"

    # Reply with a quote
    python reply_tweet.py --tweet-id 1234567890 --text "This is exactly what we're building"

    # Dry run (shows what would be posted without posting)
    python reply_tweet.py --tweet-id 1234567890 --text "Hello!" --dry-run

Requirements:
    pip install tweepy

Environment:
    TWITTER_API_KEY           - X API Key (from developer.x.com)
    TWITTER_API_SECRET        - X API Secret
    TWITTER_ACCESS_TOKEN      - X Access Token (with Read+Write)
    TWITTER_ACCESS_TOKEN_SECRET - X Access Token Secret
"""

import argparse
import json
import os
import sys
from datetime import datetime

try:
    import tweepy
except ImportError:
    print("Error: tweepy not installed.")
    print("Install it with: pip3 install tweepy --break-system-packages")
    sys.exit(1)


def get_credentials():
    """Get X API credentials from environment variables."""
    required = {
        "TWITTER_API_KEY": os.environ.get("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.environ.get("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.environ.get("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.environ.get("TWITTER_ACCESS_TOKEN_SECRET"),
    }

    missing = [k for k, v in required.items() if not v]
    if missing:
        print("Error: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("")
        print("Set up your X API credentials:")
        print("  1. Go to developer.x.com and create a developer account")
        print("  2. Create an app with Read+Write permissions")
        print("  3. Generate API Key, API Secret, Access Token, Access Token Secret")
        print("  4. Export them:")
        print('     export TWITTER_API_KEY="your_key"')
        print('     export TWITTER_API_SECRET="your_secret"')
        print('     export TWITTER_ACCESS_TOKEN="your_token"')
        print('     export TWITTER_ACCESS_TOKEN_SECRET="your_token_secret"')
        sys.exit(1)

    return required


def create_client(creds):
    """Create an authenticated Tweepy client using OAuth 1.0a (for writes)."""
    client = tweepy.Client(
        consumer_key=creds["TWITTER_API_KEY"],
        consumer_secret=creds["TWITTER_API_SECRET"],
        access_token=creds["TWITTER_ACCESS_TOKEN"],
        access_token_secret=creds["TWITTER_ACCESS_TOKEN_SECRET"],
    )
    return client


def reply_to_tweet(client, tweet_id, text, dry_run=False):
    """
    Post a reply to a specific tweet.

    Args:
        client: Authenticated Tweepy client
        tweet_id: ID of the tweet to reply to
        text: Reply text (max 280 characters)
        dry_run: If True, don't actually post

    Returns:
        dict with response data or dry run info
    """
    if len(text) > 280:
        print(f"Warning: Text is {len(text)} characters (max 280). Truncating.")
        text = text[:277] + "..."

    if dry_run:
        print("\n[DRY RUN] Would post reply:")
        print(f"  In reply to: https://x.com/i/status/{tweet_id}")
        print(f"  Text: {text}")
        print(f"  Length: {len(text)}/280 characters")
        return {"dry_run": True, "tweet_id": tweet_id, "text": text}

    try:
        response = client.create_tweet(
            text=text,
            in_reply_to_tweet_id=tweet_id,
        )

        reply_id = response.data["id"]
        print(f"\nReply posted successfully!")
        print(f"  Reply ID: {reply_id}")
        print(f"  In reply to: https://x.com/i/status/{tweet_id}")
        print(f"  Reply URL: https://x.com/i/status/{reply_id}")
        print(f"  Text: {text}")

        return {
            "success": True,
            "reply_id": reply_id,
            "in_reply_to": tweet_id,
            "text": text,
            "url": f"https://x.com/i/status/{reply_id}",
            "posted_at": datetime.now().isoformat(),
        }

    except tweepy.errors.Forbidden as e:
        print(f"\nError: Forbidden (403). Check your app permissions.")
        print(f"  - Ensure your app has Read+Write access")
        print(f"  - Regenerate Access Token after changing permissions")
        print(f"  Details: {e}")
        sys.exit(1)

    except tweepy.errors.Unauthorized as e:
        print(f"\nError: Unauthorized (401). Check your credentials.")
        print(f"  Details: {e}")
        sys.exit(1)

    except tweepy.errors.TooManyRequests as e:
        print(f"\nError: Rate limited (429). Wait and try again.")
        print(f"  Details: {e}")
        sys.exit(1)

    except tweepy.errors.TweepyException as e:
        print(f"\nError posting reply: {e}")
        sys.exit(1)


def post_tweet(client, text, dry_run=False):
    """
    Post a new tweet (not a reply).

    Args:
        client: Authenticated Tweepy client
        text: Tweet text (max 280 characters)
        dry_run: If True, don't actually post

    Returns:
        dict with response data
    """
    if len(text) > 280:
        print(f"Warning: Text is {len(text)} characters (max 280). Truncating.")
        text = text[:277] + "..."

    if dry_run:
        print("\n[DRY RUN] Would post tweet:")
        print(f"  Text: {text}")
        print(f"  Length: {len(text)}/280 characters")
        return {"dry_run": True, "text": text}

    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        print(f"\nTweet posted successfully!")
        print(f"  Tweet ID: {tweet_id}")
        print(f"  URL: https://x.com/i/status/{tweet_id}")
        print(f"  Text: {text}")

        return {
            "success": True,
            "tweet_id": tweet_id,
            "text": text,
            "url": f"https://x.com/i/status/{tweet_id}",
            "posted_at": datetime.now().isoformat(),
        }

    except tweepy.errors.TweepyException as e:
        print(f"\nError posting tweet: {e}")
        sys.exit(1)


def verify_credentials(client):
    """Verify the credentials work by fetching the authenticated user."""
    try:
        me = client.get_me()
        if me and me.data:
            print(f"Authenticated as: @{me.data.username} ({me.data.name})")
            return me.data
        else:
            print("Warning: Could not verify credentials (get_me returned empty)")
            return None
    except tweepy.errors.TweepyException as e:
        print(f"Warning: Could not verify credentials: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Post a reply to a tweet via official X API v2",
        epilog="""
Examples:
    # Reply to a tweet
    python reply_tweet.py --tweet-id 1234567890 --text "Great thread!"

    # Dry run
    python reply_tweet.py --tweet-id 1234567890 --text "Testing" --dry-run

    # Post a new tweet (not a reply)
    python reply_tweet.py --text "Hello from my agent!" --new

    # Verify credentials
    python reply_tweet.py --verify
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tweet-id", "-id", type=str, help="Tweet ID to reply to")
    parser.add_argument("--text", "-t", type=str, help="Reply/tweet text (max 280 chars)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be posted without posting")
    parser.add_argument("--new", action="store_true", help="Post as new tweet (not a reply)")
    parser.add_argument("--verify", action="store_true", help="Verify credentials and exit")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    creds = get_credentials()
    client = create_client(creds)

    if args.verify:
        user = verify_credentials(client)
        if user:
            print(f"  User ID: {user.id}")
            print("Credentials are valid.")
        sys.exit(0)

    if not args.text and not args.verify:
        parser.error("--text is required (or use --verify to check credentials)")

    if args.new:
        result = post_tweet(client, args.text, dry_run=args.dry_run)
    else:
        if not args.tweet_id:
            parser.error("--tweet-id is required for replies (or use --new for a new tweet)")
        result = reply_to_tweet(client, args.tweet_id, args.text, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
