---
name: twitter-reply
user-invocable: true
description: >
  Twitter engagement workflow with human-in-the-loop approval. Searches for relevant tweets
  via TwitterAPI.io, ranks them by engagement opportunity, drafts replies, and posts approved
  replies via the official X API Free Tier (500 replies/mo free). New standalone posts go
  through Postiz. Triggers on "engage twitter", "reply to tweets", "twitter engagement",
  "find and reply", "twitter outreach".
allowed-tools: Bash, Read, Write, Edit, AskUserQuestion
---

# Twitter Reply & Engagement Skill

Search Twitter for relevant conversations, draft mission-aligned replies, and post them with human approval — all from Claude Code.

**Architecture (3 tools, each for its strength):**
- **Search**: TwitterAPI.io ($0.15/1K tweets) — finds relevant conversations
- **Reply to external tweets**: Official X API Free Tier via Tweepy (500 replies/mo, $0) — ToS-compliant
- **New standalone posts**: Postiz (scheduled content, multi-platform) — already configured
- **Approval**: Human-in-the-loop — you review and approve every reply before posting

**Why this split:** Postiz cannot reply to external tweets (no `in_reply_to_tweet_id` support). It can only create new posts and self-thread. The official X API Free Tier handles replies at zero cost.

## Prerequisites

### 1. Install Dependencies
```bash
pip3 install requests tweepy --break-system-packages
```

### 2. TwitterAPI.io Key (for search)
Already configured if you use the `twitter-search` skill.
```bash
export TWITTERAPI_IO_KEY="your-key"
```

### 3. Postiz (for new standalone posts)
Already configured. Integration ID for X: `cmlrob0gp05g7mn0yncmwzg7c`

### 4. Official X API Free Tier Credentials (for replies only)
Get these from [developer.x.com](https://developer.x.com):
1. Create a developer account (free — gives you the Free Tier automatically)
2. Create an app with **Read+Write** permissions
3. Generate all 4 credentials

```bash
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
```

**Free Tier limits:** 500 posts/month (write-only, no read). That's ~16 replies/day — plenty for engagement.

### 5. Verify Setup
```bash
# Verify X API credentials
python3 .claude/skills/twitter-reply/scripts/reply_tweet.py --verify

# Verify TwitterAPI.io key (run a test search)
python3 .claude/skills/twitter-search/scripts/search_twitter.py --query "test" --limit 1

# Verify Postiz
postiz integrations:list
```

---

## Engagement Workflow (FOLLOW THIS EXACTLY)

### Step 1: Find Engagement Opportunities

Run the engagement finder to search across multiple relevant queries and rank results:

```bash
# Default: searches AI agent / deploy / coding conversations
python3 .claude/skills/twitter-reply/scripts/engage.py

# Specific topic
python3 .claude/skills/twitter-reply/scripts/engage.py --topic "deploy AI agent"

# Brand monitoring
python3 .claude/skills/twitter-reply/scripts/engage.py --brand

# Competitor monitoring
python3 .claude/skills/twitter-reply/scripts/engage.py --competitors

# Custom queries
python3 .claude/skills/twitter-reply/scripts/engage.py --queries "crypto AI bot" "web3 agent"
```

### Step 2: Read and Present Results

Read the generated report from `OUTPUT/twitter-engagement/`. Present the top 5-10 tweets to the user in this format:

```
## Engagement Opportunities Found

I found [N] tweets worth engaging with. Here are the top picks:

### 1. @username (5.2K followers) — Score: 85/100
> [tweet text]
Likes: 45 | Replies: 12 | Views: 15K
Link: https://x.com/username/status/123456789

**Suggested reply:**
"[draft reply that adds value, aligns with Augmi mission]"

### 2. @username2 ...
```

### Step 3: WAIT FOR HUMAN APPROVAL (CRITICAL)

**NEVER post a reply without explicit user approval.**

Ask the user:
- "Which tweets do you want to reply to?"
- "Want me to adjust any of the draft replies?"
- "Ready to post? Say 'post #1' or 'post all' to confirm."

The user must explicitly say "post", "send", "reply", "go ahead", or similar confirmation.

### Step 4: Post Approved Replies

Only after explicit approval, use the appropriate tool:

**For replies to external tweets (use official X API via Tweepy):**
```bash
# Dry run first (recommended)
python3 .claude/skills/twitter-reply/scripts/reply_tweet.py \
  --tweet-id 1234567890 \
  --text "Your approved reply text here" \
  --dry-run

# Post for real
python3 .claude/skills/twitter-reply/scripts/reply_tweet.py \
  --tweet-id 1234567890 \
  --text "Your approved reply text here"
```

**For new standalone posts (use Postiz):**
```bash
# Schedule a new tweet via Postiz
postiz posts:create \
  -c "Your post content" \
  -s "2026-02-20T12:00:00Z" \
  --settings '{"who_can_reply_post":"everyone"}' \
  -i "cmlrob0gp05g7mn0yncmwzg7c"
```

### Step 5: Log Results

After posting, save a log of what was posted:
- The reply_tweet.py script outputs the reply URL
- Postiz returns a post ID

Report back to the user: "Posted reply to @username: [reply URL]"

---

## Subcommands

### /twitter-reply:engage [topic]
Full workflow: Search → Rank → Present → Approve → Post

### /twitter-reply:search [query]
Search only (no posting). Same as `/twitter-search` but with engagement scoring.

### /twitter-reply:reply [tweet-id] [text]
Reply to a specific tweet (requires approval confirmation first).

### /twitter-reply:post [text]
Create a new standalone tweet via Postiz (requires approval confirmation first).

### /twitter-reply:brand
Monitor and reply to Augmi brand mentions.

### /twitter-reply:competitors
Monitor competitor conversations for engagement opportunities.

### /twitter-reply:verify
Check that all credentials are configured correctly.

---

## Reply Drafting Guidelines

When drafting replies, follow these principles:

### DO:
- **Add genuine value** — share knowledge, answer questions, offer insights
- **Be conversational** — write like a human, not a brand
- **Reference specifics** from their tweet (shows you read it)
- **Keep it short** — 1-2 sentences max for replies
- **Include a soft CTA** only when natural (e.g., "we wrote about this at augmi.world/blog")
- **Ask a follow-up question** to start a conversation

### DON'T:
- Spam links in every reply
- Use generic/template responses
- Reply to tweets that are clearly not relevant
- Self-promote without adding value first
- Reply to highly controversial or political tweets
- Reply to the same person multiple times in a row

### Reply Templates (Adapt, Don't Copy)

**Answering a question:**
> "Great question! [Specific answer]. We ran into this too when building [relevant thing]. [Optional: link only if directly helpful]"

**Adding context:**
> "[New insight or data point they might not know]. [Why it matters]."

**Sharing experience:**
> "We built exactly this — [brief description]. The hardest part was [specific challenge]. Happy to share what worked."

**Engaging with an opinion:**
> "Interesting take. [Agree/respectfully disagree with reasoning]. What's been your experience with [specific aspect]?"

---

## Cost Estimate

| Action | Tool | Cost | Monthly Estimate |
|--------|------|------|-----------------|
| Search | TwitterAPI.io | $0.15 / 1K tweets | ~$5-10 |
| Reply to tweets | X API Free Tier | **$0** (500/mo limit) | **$0** |
| New posts | Postiz | Included in plan | $0 |
| **Total** | | | **~$5-10/month** |

---

## Troubleshooting

### "TWITTER_API_KEY not set"
Set up your X developer account credentials. See Prerequisites above.

### "Forbidden (403)" when replying
Your app permissions are Read-Only. Fix:
1. Go to developer.x.com → your app → Settings → App permissions
2. Change to "Read and Write"
3. **Regenerate** your Access Token and Secret (required after permission change)

### "Unauthorized (401)"
Credentials are wrong. Regenerate all 4 values from developer.x.com.

### Reply posted but not showing up
X may take a few seconds to propagate. Check the reply URL directly. If it 404s, the tweet you replied to may have been deleted.

### Rate limited (429)
X Free Tier: 500 posts/month total. Track your usage. The reply_tweet.py script counts each reply.

### Hitting the 500/month Free Tier cap
If you need more than 500 replies/month, upgrade to X API Basic ($200/mo) or use TwitterAPI.io's write endpoint ($0.001/reply, cookie-based, some risk).
