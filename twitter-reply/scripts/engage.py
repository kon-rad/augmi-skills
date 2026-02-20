#!/usr/bin/env python3
"""
Twitter engagement workflow: Search → Rank → Present engagement opportunities.

Combines TwitterAPI.io search with engagement scoring to find the best
tweets to reply to for brand awareness and community building.

Usage:
    # Find engagement opportunities for AI agents topic
    python engage.py --topic "AI agents"

    # Custom search queries
    python engage.py --queries "deploy AI agent" "AI coding assistant" "build AI bot"

    # Monitor brand mentions
    python engage.py --brand

    # Monitor competitors
    python engage.py --competitors

Requirements:
    pip install requests

Environment:
    TWITTERAPI_IO_KEY - TwitterAPI.io API key
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

# Default search queries for Augmi engagement
AUGMI_QUERIES = [
    '"AI agent" deploy -filter:retweets lang:en',
    '"AI coding agent" -filter:retweets lang:en',
    '"deploy AI bot" OR "build AI agent" -filter:retweets lang:en',
    '"openclaw" OR "open claw" -filter:retweets lang:en',
    '"AI assistant" telegram OR discord -filter:retweets lang:en',
    '"personal AI agent" -filter:retweets lang:en',
]

BRAND_QUERIES = [
    "@augmi_world OR augmi",
    '"augmi.world"',
    "augmi AI",
]

COMPETITOR_QUERIES = [
    '"openclaw" -from:augmi_world -filter:retweets lang:en',
    '"AI agent platform" -filter:retweets lang:en',
    '"deploy AI" crypto OR wallet -filter:retweets lang:en',
    '"elizaos" OR "eliza os" agent -filter:retweets lang:en',
]


def get_api_key():
    """Get TwitterAPI.io key from environment."""
    key = os.environ.get("TWITTERAPI_IO_KEY")
    if not key:
        print("Error: TWITTERAPI_IO_KEY not set.")
        print("Get your key from: https://twitterapi.io/dashboard")
        sys.exit(1)
    return key


def search_tweets(query, query_type="Latest", api_key=None):
    """Search tweets via TwitterAPI.io."""
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    params = {"query": query, "queryType": query_type}

    try:
        resp = requests.get(SEARCH_ENDPOINT, headers=headers, params=params, timeout=30)
        if resp.status_code == 429:
            print(f"  Rate limited on query: {query[:50]}...")
            return []
        resp.raise_for_status()
        return resp.json().get("tweets", [])
    except requests.RequestException as e:
        print(f"  Error searching '{query[:50]}...': {e}")
        return []


def score_tweet(tweet):
    """
    Score a tweet for engagement opportunity (0-100).

    Factors:
    - Moderate engagement (not too big, not too small)
    - Recency
    - Reply count (conversations are better)
    - Not a reply itself (original tweets are better targets)
    - Author follower count (sweet spot: 500-50K)
    """
    score = 50  # Base score

    likes = tweet.get("likeCount", 0) or 0
    retweets = tweet.get("retweetCount", 0) or 0
    replies = tweet.get("replyCount", 0) or 0
    views = tweet.get("viewCount", 0) or 0
    is_reply = tweet.get("isReply", False)

    author = tweet.get("author", {})
    followers = author.get("followers", 0) or 0
    is_verified = author.get("isBlueVerified", False)

    # Engagement sweet spot: enough to be visible, not so much you're lost
    if 5 <= likes <= 500:
        score += 15
    elif likes > 500:
        score += 5  # Still okay but harder to stand out
    elif likes < 5:
        score += 8  # Low engagement, but could be fresh

    # Active conversations are gold
    if 2 <= replies <= 50:
        score += 15
    elif replies > 50:
        score += 5

    # Author follower sweet spot (500-50K)
    if 500 <= followers <= 50000:
        score += 10
    elif followers > 50000:
        score += 5  # Big accounts = more visibility but less likely to engage back

    # Verified accounts get a small boost
    if is_verified:
        score += 5

    # Original tweets > replies (more visible)
    if not is_reply:
        score += 10

    # Views indicate reach
    if views and 1000 <= views <= 500000:
        score += 5

    return min(score, 100)


def deduplicate_tweets(tweets):
    """Remove duplicate tweets by ID."""
    seen = set()
    unique = []
    for tweet in tweets:
        tid = tweet.get("id")
        if tid and tid not in seen:
            seen.add(tid)
            unique.append(tweet)
    return unique


def format_number(n):
    """Format large numbers."""
    if n is None:
        return "0"
    n = int(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def build_engagement_report(tweets, mode="general"):
    """Build a markdown report of engagement opportunities."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []

    lines.append("# Twitter Engagement Opportunities")
    lines.append("")
    lines.append(f"> **Mode**: {mode}")
    lines.append(f"> **Found**: {len(tweets)} opportunities")
    lines.append(f"> **Generated**: {now}")
    lines.append("")

    if not tweets:
        lines.append("*No engagement opportunities found. Try broader queries.*")
        return "\n".join(lines)

    lines.append("## How to Use This Report")
    lines.append("")
    lines.append("1. Review each tweet below")
    lines.append("2. Decide which ones are worth replying to")
    lines.append("3. Draft your reply (use `/viral-tweet-crafter` for help)")
    lines.append("4. Post using the reply command shown with each tweet")
    lines.append("")

    lines.append("---")
    lines.append("")

    for i, tweet in enumerate(tweets, 1):
        author = tweet.get("author", {})
        username = author.get("userName", "unknown")
        display_name = author.get("name", username)
        verified = " ✓" if author.get("isBlueVerified") else ""
        followers = format_number(author.get("followers", 0))
        score = tweet.get("_score", 0)

        text = tweet.get("text", "").replace("\n", "\n> ")
        url = tweet.get("url", "")
        tweet_id = tweet.get("id", "")

        likes = format_number(tweet.get("likeCount", 0))
        retweets = format_number(tweet.get("retweetCount", 0))
        replies = format_number(tweet.get("replyCount", 0))
        views = format_number(tweet.get("viewCount", 0))

        # Score indicator
        if score >= 80:
            score_label = "HIGH"
        elif score >= 60:
            score_label = "MEDIUM"
        else:
            score_label = "LOW"

        lines.append(f"### {i}. @{username}{verified} ({display_name}) — {followers} followers [Score: {score}/100 {score_label}]")
        lines.append("")
        lines.append(f"> {text}")
        lines.append("")
        lines.append(f"**Engagement**: {likes} likes | {retweets} RTs | {replies} replies | {views} views")
        if url:
            lines.append(f"**Link**: {url}")
        lines.append("")

        # Reply command
        lines.append("**Reply command:**")
        lines.append(f"```bash")
        lines.append(f'python3 .claude/skills/twitter-reply/scripts/reply_tweet.py --tweet-id {tweet_id} --text "YOUR REPLY HERE"')
        lines.append(f"```")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Find Twitter engagement opportunities via TwitterAPI.io",
        epilog="""
Modes:
    Default: Search for AI agent / deploy / coding conversations
    --brand: Monitor Augmi brand mentions
    --competitors: Monitor competitor mentions
    --queries: Custom search queries
    --topic: Single topic search

Examples:
    python engage.py                                    # Default AI agent queries
    python engage.py --brand                            # Brand mentions
    python engage.py --topic "how to deploy AI agent"   # Specific topic
    python engage.py --queries "crypto AI" "web3 agent" # Custom queries
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--topic", type=str, help="Single topic to search for")
    parser.add_argument("--queries", nargs="+", type=str, help="Custom search queries")
    parser.add_argument("--brand", action="store_true", help="Monitor Augmi brand mentions")
    parser.add_argument("--competitors", action="store_true", help="Monitor competitor mentions")
    parser.add_argument("--limit", type=int, default=20, help="Max results per query (default: 20)")
    parser.add_argument("--top", type=int, default=15, help="Show top N results after scoring (default: 15)")
    parser.add_argument("--output", "-o", type=str, help="Output file path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    api_key = get_api_key()

    # Determine queries and mode
    if args.topic:
        queries = [f'{args.topic} -filter:retweets lang:en']
        mode = f"topic: {args.topic}"
    elif args.queries:
        queries = args.queries
        mode = "custom"
    elif args.brand:
        queries = BRAND_QUERIES
        mode = "brand monitoring"
    elif args.competitors:
        queries = COMPETITOR_QUERIES
        mode = "competitor monitoring"
    else:
        queries = AUGMI_QUERIES
        mode = "Augmi engagement"

    print(f"Searching Twitter ({mode})...")
    print(f"  Queries: {len(queries)}")

    all_tweets = []
    for i, query in enumerate(queries):
        print(f"  [{i+1}/{len(queries)}] Searching: {query[:60]}...")
        tweets = search_tweets(query, "Latest", api_key)
        print(f"    Found {len(tweets)} tweets")
        all_tweets.extend(tweets)

    # Deduplicate
    all_tweets = deduplicate_tweets(all_tweets)
    print(f"\n  Total unique tweets: {len(all_tweets)}")

    # Score and rank
    for tweet in all_tweets:
        tweet["_score"] = score_tweet(tweet)

    all_tweets.sort(key=lambda t: t["_score"], reverse=True)
    top_tweets = all_tweets[:args.top]

    print(f"  Top {len(top_tweets)} engagement opportunities selected")

    # Build output
    if args.json:
        output = json.dumps(
            {
                "mode": mode,
                "count": len(top_tweets),
                "generated_at": datetime.now().isoformat(),
                "tweets": [
                    {
                        "id": t.get("id"),
                        "text": t.get("text"),
                        "url": t.get("url"),
                        "score": t.get("_score"),
                        "author": t.get("author", {}).get("userName"),
                        "likes": t.get("likeCount", 0),
                        "replies": t.get("replyCount", 0),
                        "views": t.get("viewCount", 0),
                    }
                    for t in top_tweets
                ],
            },
            indent=2,
        )
        ext = ".json"
    else:
        output = build_engagement_report(top_tweets, mode)
        ext = ".md"

    # Write output
    if args.output:
        output_path = Path(args.output)
    else:
        today = datetime.now().strftime("%Y%m%d-%H%M")
        output_dir = Path("OUTPUT/twitter-engagement")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{today}-{mode.replace(' ', '-').replace(':', '')[:30]}{ext}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output)
    print(f"\nReport saved to: {output_path}")

    # Print to stdout
    print("\n" + "=" * 60)
    print(output)


if __name__ == "__main__":
    main()
