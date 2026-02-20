#!/usr/bin/env python3
"""
Search Twitter/X using TwitterAPI.io — cheap alternative to the official X API.

Searches tweets by keyword, hashtag, user, or advanced query syntax.
Returns formatted results with engagement metrics.

Usage:
    # Simple keyword search
    python search_twitter.py --query "AI agents"

    # Search with filters
    python search_twitter.py --query "AI agents" --type Top --limit 30

    # Advanced Twitter search syntax
    python search_twitter.py --query 'from:elonmusk "AI" since:2025-01-01'

    # Search and save results
    python search_twitter.py --query "crypto wallet" --output OUTPUT/tweets/crypto.md

Requirements:
    pip install requests

Environment:
    TWITTERAPI_IO_KEY  — your API key from twitterapi.io/dashboard
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests not installed.")
    print("Install it with: pip3 install requests --break-system-packages")
    sys.exit(1)


API_BASE = "https://api.twitterapi.io/twitter"
SEARCH_ENDPOINT = f"{API_BASE}/tweet/advanced_search"


def get_api_key():
    """Get the API key from environment variable."""
    key = os.environ.get("TWITTERAPI_IO_KEY")
    if not key:
        print("Error: TWITTERAPI_IO_KEY environment variable not set.")
        print("")
        print("Get your API key from: https://twitterapi.io/dashboard")
        print("Then set it:")
        print('  export TWITTERAPI_IO_KEY="your-key-here"')
        print("")
        print("Or add to .env.local:")
        print('  TWITTERAPI_IO_KEY=your-key-here')
        sys.exit(1)
    return key


def search_tweets(query, query_type="Latest", cursor="", api_key=None):
    """
    Search tweets using TwitterAPI.io advanced search.

    Args:
        query: Search query (supports Twitter advanced search syntax)
        query_type: "Latest" or "Top"
        cursor: Pagination cursor (empty string for first page)
        api_key: TwitterAPI.io API key

    Returns:
        dict with tweets, has_next_page, next_cursor
    """
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    params = {
        "query": query,
        "queryType": query_type,
    }
    if cursor:
        params["cursor"] = cursor

    resp = requests.get(SEARCH_ENDPOINT, headers=headers, params=params, timeout=30)

    if resp.status_code == 400:
        error = resp.json()
        print(f"API Error: {error.get('message', 'Bad request')}")
        sys.exit(1)
    elif resp.status_code == 401:
        print("Error: Invalid API key. Check your TWITTERAPI_IO_KEY.")
        sys.exit(1)
    elif resp.status_code == 429:
        print("Error: Rate limited. Wait a moment and try again.")
        sys.exit(1)

    resp.raise_for_status()
    return resp.json()


def fetch_all_tweets(query, query_type="Latest", limit=20, api_key=None):
    """
    Fetch tweets with pagination up to the specified limit.

    Args:
        query: Search query
        query_type: "Latest" or "Top"
        limit: Maximum number of tweets to fetch
        api_key: API key

    Returns:
        list of tweet objects
    """
    all_tweets = []
    cursor = ""
    pages = 0
    max_pages = (limit + 19) // 20  # 20 results per page

    while pages < max_pages:
        print(f"  -> Fetching page {pages + 1}...")
        result = search_tweets(query, query_type, cursor, api_key)

        tweets = result.get("tweets", [])
        if not tweets:
            break

        all_tweets.extend(tweets)
        pages += 1

        if len(all_tweets) >= limit:
            all_tweets = all_tweets[:limit]
            break

        if not result.get("has_next_page"):
            break

        cursor = result.get("next_cursor", "")
        if not cursor:
            break

    return all_tweets


def format_number(n):
    """Format large numbers for readability."""
    if n is None:
        return "0"
    n = int(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_tweet_compact(tweet, index):
    """Format a single tweet as a compact markdown block."""
    author = tweet.get("author", {})
    username = author.get("userName", "unknown")
    display_name = author.get("name", username)
    verified = " ✓" if author.get("isBlueVerified") else ""
    followers = format_number(author.get("followers", 0))

    text = tweet.get("text", "").replace("\n", "\n> ")
    created = tweet.get("createdAt", "")
    url = tweet.get("url", "")

    likes = format_number(tweet.get("likeCount", 0))
    retweets = format_number(tweet.get("retweetCount", 0))
    replies = format_number(tweet.get("replyCount", 0))
    views = format_number(tweet.get("viewCount", 0))
    quotes = format_number(tweet.get("quoteCount", 0))

    is_reply = tweet.get("isReply", False)
    reply_tag = " [Reply]" if is_reply else ""
    lang = tweet.get("lang", "")

    lines = []
    lines.append(f"### {index}. @{username}{verified} ({display_name}) — {followers} followers{reply_tag}")
    lines.append("")
    lines.append(f"> {text}")
    lines.append("")
    lines.append(f"**Engagement**: {likes} likes · {retweets} RTs · {replies} replies · {quotes} quotes · {views} views")
    lines.append(f"**Posted**: {created}")
    if url:
        lines.append(f"**Link**: {url}")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def build_report(tweets, query, query_type, total_fetched):
    """Build a markdown report from search results."""
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []

    lines.append(f"# Twitter Search Results")
    lines.append("")
    lines.append(f"> **Query**: `{query}`")
    lines.append(f"> **Type**: {query_type}")
    lines.append(f"> **Results**: {len(tweets)} tweets")
    lines.append(f"> **Fetched**: {today}")
    lines.append("")

    if not tweets:
        lines.append("*No tweets found for this query.*")
        return "\n".join(lines)

    # Summary stats
    total_likes = sum(t.get("likeCount", 0) or 0 for t in tweets)
    total_retweets = sum(t.get("retweetCount", 0) or 0 for t in tweets)
    total_views = sum(t.get("viewCount", 0) or 0 for t in tweets)
    total_replies = sum(t.get("replyCount", 0) or 0 for t in tweets)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Total |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Tweets | {len(tweets)} |")
    lines.append(f"| Total Likes | {format_number(total_likes)} |")
    lines.append(f"| Total Retweets | {format_number(total_retweets)} |")
    lines.append(f"| Total Replies | {format_number(total_replies)} |")
    lines.append(f"| Total Views | {format_number(total_views)} |")
    lines.append("")

    # Individual tweets
    lines.append("## Tweets")
    lines.append("")

    for i, tweet in enumerate(tweets, 1):
        lines.append(format_tweet_compact(tweet, i))

    return "\n".join(lines)


def build_json_output(tweets, query, query_type):
    """Build a JSON output for programmatic use."""
    return json.dumps({
        "query": query,
        "query_type": query_type,
        "count": len(tweets),
        "fetched_at": datetime.now().isoformat(),
        "tweets": tweets,
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Search Twitter/X via TwitterAPI.io",
        epilog="""
Advanced query syntax (same as Twitter's search):
  "exact phrase"           Match exact phrase
  from:username            Tweets from a specific user
  to:username              Tweets replying to a user
  @username                Tweets mentioning a user
  since:YYYY-MM-DD         Tweets after date
  until:YYYY-MM-DD         Tweets before date
  min_replies:N            Minimum reply count
  min_faves:N              Minimum like count
  min_retweets:N           Minimum retweet count
  lang:en                  Filter by language
  -keyword                 Exclude keyword
  filter:links             Only tweets with links
  filter:media             Only tweets with media
  OR                       Boolean OR between terms

Examples:
  "AI agents" min_faves:100
  from:elonmusk "AI" since:2025-01-01
  (crypto OR blockchain) min_retweets:50 lang:en
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--query", "-q", type=str, required=True, help="Search query")
    parser.add_argument(
        "--type", "-t", type=str, default="Latest", choices=["Latest", "Top"],
        help="Sort by Latest or Top (default: Latest)",
    )
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max tweets to fetch (default: 20)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output file path (.md or .json)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of markdown")
    parser.add_argument("--compact", action="store_true", help="Compact output (just text + metrics, no headers)")

    args = parser.parse_args()

    api_key = get_api_key()

    print(f'Searching Twitter for: "{args.query}" (type: {args.type}, limit: {args.limit})')

    tweets = fetch_all_tweets(args.query, args.type, args.limit, api_key)

    print(f"  -> Found {len(tweets)} tweets")

    if args.json:
        output = build_json_output(tweets, args.query, args.type)
        ext = ".json"
    else:
        output = build_report(tweets, args.query, args.type, len(tweets))
        ext = ".md"

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        today = datetime.now().strftime("%Y%m%d-%H%M")
        slug = args.query[:40].lower().replace(" ", "-").replace('"', "").replace(":", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        output_dir = Path("OUTPUT/twitter-search")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{today}-{slug}{ext}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output)
    print(f"\nResults saved to: {output_path}")

    # Also print to stdout
    print("\n" + "=" * 60)
    print(output)


if __name__ == "__main__":
    main()
