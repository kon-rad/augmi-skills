---
name: twitter-search
user-invocable: true
description: >
  Search Twitter/X for relevant tweets using TwitterAPI.io (cheap alternative to official X API).
  Use when users want to find tweets to reply to, research conversations, monitor topics,
  or discover engagement opportunities. Triggers on requests like "search twitter",
  "find tweets", "twitter search", "find posts on X", "tweets about", or "monitor twitter".
allowed-tools: Bash, Read, Write, WebSearch, WebFetch
---

# Twitter Search Skill

Search Twitter/X for tweets by keyword, hashtag, user, or advanced query — powered by [TwitterAPI.io](https://twitterapi.io) at $0.15 per 1,000 tweets (vs $200+/mo for official X API).

## Prerequisites

### Required Dependencies
```bash
pip3 install requests --break-system-packages
```

### Required API Key
Get your API key from [twitterapi.io/dashboard](https://twitterapi.io/dashboard) ($1 free credit on signup).

Set it as an environment variable:
```bash
export TWITTERAPI_IO_KEY="your-key-here"
```

Or add to `.env.local`:
```
TWITTERAPI_IO_KEY=your-key-here
```

## Usage

### Basic Keyword Search

```bash
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "AI agents"
```

### Search Top/Popular Tweets

```bash
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "AI agents" --type Top
```

### Fetch More Results

```bash
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "AI agents" --limit 50
```

### Advanced Query Syntax

TwitterAPI.io supports the same advanced search syntax as Twitter's search:

```bash
# Exact phrase
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query '"AI coding agents"'

# From a specific user
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "from:elonmusk AI"

# High-engagement tweets only
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "AI agents min_faves:100"

# Date range
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "crypto wallet since:2025-01-01"

# Exclude retweets, English only
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "AI agents -filter:retweets lang:en"

# Boolean OR
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "(crypto OR blockchain) min_retweets:50"

# Mentions of a user
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "@augmi_world"

# Tweets with links only
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "AI agents filter:links"
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--query`, `-q` | Search query (required) | — |
| `--type`, `-t` | Sort order: `Latest` or `Top` | `Latest` |
| `--limit`, `-l` | Max tweets to fetch | `20` |
| `--output`, `-o` | Output file path | `OUTPUT/twitter-search/YYYYMMDD-HHMM-query.md` |
| `--json` | Output raw JSON instead of markdown | `false` |

### JSON Output (for programmatic use)

```bash
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "AI agents" --json --output results.json
```

## Output Format

The generated markdown report includes:

```markdown
# Twitter Search Results

> **Query**: `AI agents`
> **Type**: Latest
> **Results**: 20 tweets
> **Fetched**: 2026-02-18 10:30

## Summary

| Metric | Total |
|--------|-------|
| Tweets | 20 |
| Total Likes | 5.2K |
| Total Retweets | 1.1K |
| Total Replies | 340 |
| Total Views | 2.3M |

## Tweets

### 1. @username ✓ (Display Name) — 50K followers

> Tweet text content here...

**Engagement**: 500 likes · 120 RTs · 45 replies · 12 quotes · 150K views
**Posted**: 2026-02-18T10:00:00Z
**Link**: https://x.com/username/status/123456789
```

## Advanced Query Reference

| Operator | Description | Example |
|----------|-------------|---------|
| `"phrase"` | Exact phrase match | `"AI agents"` |
| `from:user` | Tweets by user | `from:elonmusk` |
| `to:user` | Replies to user | `to:anthropic` |
| `@user` | Mentioning user | `@augmi_world` |
| `since:date` | After date | `since:2025-06-01` |
| `until:date` | Before date | `until:2025-12-31` |
| `min_faves:N` | Min likes | `min_faves:100` |
| `min_retweets:N` | Min retweets | `min_retweets:50` |
| `min_replies:N` | Min replies | `min_replies:10` |
| `lang:code` | Language filter | `lang:en` |
| `-keyword` | Exclude term | `-spam` |
| `filter:links` | Has links | `filter:links` |
| `filter:media` | Has images/video | `filter:media` |
| `-filter:retweets` | Exclude RTs | `-filter:retweets` |
| `OR` | Boolean OR | `crypto OR blockchain` |
| `()` | Grouping | `(AI OR ML) agents` |

## Workflow: Find Tweets to Reply To

### Step 1: Search for relevant conversations

```bash
# Find recent tweets about your topic
python3 .claude/skills/twitter-search/scripts/search_twitter.py \
  --query "AI coding agents -filter:retweets lang:en" \
  --type Latest --limit 30
```

### Step 2: Filter for engagement opportunities

```bash
# Find tweets with moderate engagement (not too big, not too small)
python3 .claude/skills/twitter-search/scripts/search_twitter.py \
  --query "AI agents min_faves:10 min_replies:2" \
  --type Latest --limit 20
```

### Step 3: Review results and craft replies

Read the output file and identify tweets where you can add genuine value.
Use the `/viral-tweet-crafter` skill to draft mission-aligned replies.

## Workflow: Monitor Brand Mentions

```bash
# Search for mentions of your brand
python3 .claude/skills/twitter-search/scripts/search_twitter.py \
  --query "@augmi_world OR augmi" --limit 50

# Search for competitor mentions
python3 .claude/skills/twitter-search/scripts/search_twitter.py \
  --query "openclaw OR open-claw" --limit 30
```

## Cost

- **$0.15 per 1,000 tweets** fetched (pay-as-you-go)
- **$1 free credit** on signup (~6,600 tweets)
- 20 tweets per search = ~$0.003 per search
- 100 searches/day = ~$0.30/day = ~$9/month

Compared to official X API Basic tier at $200/month, this is **~95% cheaper**.

## Troubleshooting

### "TWITTERAPI_IO_KEY not set"
Set the environment variable: `export TWITTERAPI_IO_KEY="your-key"`

### "Invalid API key" (401)
Check your key at [twitterapi.io/dashboard](https://twitterapi.io/dashboard).

### "Rate limited" (429)
Wait a few seconds and retry. Default limit is 200 QPS which is very generous.

### Empty results
- Try broader keywords
- Check date ranges (very old tweets may not be indexed)
- Remove restrictive filters like `min_faves`

### Timeout errors
The API typically responds in ~700ms. If you get timeouts, check your network connection.
