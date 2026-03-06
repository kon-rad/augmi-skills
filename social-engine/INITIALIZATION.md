# Social Engine - Complete Initialization Guide

This guide walks you through setting up the social-engine system from scratch.

## Quick Overview

The initialization process will:
1. Define your niche and content strategy
2. Create all required directories
3. Generate style guides for each content type
4. Configure API keys and credentials
5. Set up daily cron job for analytics
6. Verify everything works
7. Launch your first content cycle

**Time Required**: 30-45 minutes
**Difficulty**: Beginner-friendly (interactive setup)

---

## Prerequisites

Before you start, make sure you have:

- ✅ Postiz account (for scheduling) - [postiz.com](https://postiz.com)
- ✅ Google Cloud account with Gemini API enabled
- ✅ Anthropic API key (for Claude)
- ✅ `.env.local` file in project root (or ready to create)

### Getting API Keys

**Postiz API Key**:
1. Log in to [postiz.com](https://postiz.com)
2. Go to Settings → API
3. Create new API token
4. Copy to clipboard

**Gemini API Key**:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project or select existing
3. Enable Gemini API
4. Create API key (Credentials → Create Credentials → API Key)
5. Copy to clipboard

**Anthropic API Key**:
1. Go to [Anthropic Dashboard](https://console.anthropic.com)
2. Go to API Keys
3. Create new key or use existing
4. Copy to clipboard

---

## Step 1: Start Initialization

### Option A: Interactive Setup (Recommended)
```bash
/social-engine init
```

This launches an interactive questionnaire that guides you through setup.

### Option B: Manual Setup
Follow the steps below manually.

---

## Step 2: Define Your Niche (Interactive or Manual)

### Interactive
The system will ask:
- What's your primary niche?
- What are 3-5 subtopics?
- Which platforms do you use? (Instagram, X, LinkedIn, YouTube)
- What's your target audience?
- How often do you want to post?

### Manual
Edit `social-engine-guide.md`:

```markdown
# Social Engine Guide

## Niche Definition
**Primary Niche**: AI Agents, OpenClaw, Claude Code
**Subtopics**:
- AI agent deployment and architecture
- OpenClaw framework features
- Claude Code integration
- Agent automation workflows
- Crypto-native AI agents
- Agent monetization

## Target Platforms
- Instagram (carousel + Reels)
- X/Twitter (threads + videos)
- LinkedIn (articles + images)
- YouTube (shorts)

## Audience Profile
- Developers building AI agents
- Crypto/Web3 founders
- Technical CTOs
- AI enthusiast communities

## Content Quality Standards
- Humanization Required: Yes (always `/humanizer`)
- Engagement Focus: Educational + actionable
- Posting Frequency: 3-5 posts/week
- Brand Voice: Authentic, enthusiastic, educational
```

---

## Step 3: Create Directory Structure (Automatic or Manual)

### Interactive
System creates all directories automatically.

### Manual
Create this structure in your project root:

```bash
mkdir -p content/strategy
mkdir -p content/style-guides
mkdir -p content/research
mkdir -p OUTPUT/social-analytics
mkdir -p OUTPUT/social-research
mkdir -p app/api/cron/social-analytics
```

---

## Step 4: Configure API Keys

### In `.env.local` (Project Root)

Add these environment variables:

```bash
# Postiz (Social media scheduling)
POSTIZ_API_KEY=pk_live_xxxxxxxxxxxxx

# Google/Gemini (Image generation)
GEMINI_API_KEY=AIza_xxxxxxxxxxxxxxxxxxxx

# Anthropic (AI text generation)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx

# Cron Security
CRON_SECRET=your_secret_key_here_min_32_chars

# Optional: Analytics Email
ANALYTICS_EMAIL=your-email@example.com

# Optional: Custom Cron Time (default 07:00 UTC)
ANALYTICS_CRON_TIME=07:00
```

**Never commit `.env.local` to git!**

---

## Step 5: Generate Style Guides

### Interactive
System asks about your brand and auto-generates guides.

### Manual
Copy templates to `content/style-guides/`:

```bash
cp templates/carousel-guide-template.md content/style-guides/carousel-guide.md
cp templates/blog-guide-template.md content/style-guides/blog-guide.md
cp templates/linkedin-twitter-video-guides.md content/style-guides/linkedin-twitter-video-guides.md
```

### Customize Each Guide

Edit each file to match your brand:

**carousel-guide.md**:
- Update color palette
- Set your fonts
- Adjust visual style (sci-fi, minimalist, etc.)

**blog-guide.md**:
- Add your primary brand color
- Set typography
- Update visual aesthetic

**linkedin-twitter-video-guides.md**:
- Professional brand guidelines
- Video requirements
- Platform-specific rules

---

## Step 6: Create Strategy File

### Initialize `social-growth-strategy.md`

Create with initial values:

```markdown
# Social Growth Strategy

**Last Updated**: [Today's date]
**Baseline Status**: Initial Setup

## Current Period Metrics

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Instagram Engagement | >3% | TBD | — |
| X Engagement | >2% | TBD | — |
| LinkedIn CTR | >1.5% | TBD | — |
| YouTube Completion | >70% | TBD | — |
| Monthly Follower Growth | 5-10% | TBD | — |

## Content Performance Analysis

### By Platform

#### Instagram
- Best Time: TBD
- High Engagement Topics: TBD
- Audience Size: TBD

#### X/Twitter
- Best Time: TBD
- High Engagement Topics: TBD

#### LinkedIn
- Best Time: TBD
- Professional Audience: TBD

#### YouTube
- Completion Rate: TBD
- Subscriber Conversion: TBD

## Growth Recommendations

[Will be updated daily at 7 AM UTC]

## Topics to Explore

[Will be populated by viral-research]

## Notes

Initial setup completed [date].
```

---

## Step 7: Create Posting Log

### Initialize `content/strategy/posting-log.md`

```markdown
# Posting Log

Tracks all scheduled posts with metrics.

## Schedule

| Date | Platform | Content Type | Topic | Post ID | Engagement | Notes |
|------|----------|--------------|-------|---------|------------|-------|
| TBD | Instagram | Carousel | [Topic] | TBD | TBD | First post |

## Performance Summary

- Total Posts: 0
- Average Engagement: 0%
- Best Performer: None yet
- Trending Topics: TBD
```

---

## Step 8: Set Up Daily Cron Job

### Option A: External Cron Service (EasyCron or cron-job.org)

**Recommended for beginners**

1. Go to [easycron.com](https://easycron.com) or [cron-job.org](https://cron-job.org)
2. Create account (free)
3. Create new cron job with:
   - **URL**: `https://augmi.world/api/cron/social-analytics`
   - **Method**: POST
   - **Headers**: `Authorization: Bearer {CRON_SECRET}`
   - **Schedule**: Every day at 07:00 UTC
   - **Timezone**: UTC

4. Test the cron job
5. Verify it runs daily

### Option B: Fly.io Built-in Cron

**If hosting on Fly.io**

Add to `fly.toml`:

```toml
[http_service]
processes = ["app"]

# Add cron handler
[[http_service.checks]]
grace_period = "5s"
interval = "10s"
timeout = "5s"

# Cron job for social analytics
[[services]]
internal_port = 3000
protocol = "tcp"

[[services.ports]]
port = 80
handlers = ["http"]

[[services.ports]]
port = 443
handlers = ["tls", "http"]

# Schedule cron
[env]
CRON_ENABLED = "true"
CRON_SCHEDULE = "0 7 * * *"  # 7 AM UTC daily
```

Then deploy:
```bash
fly deploy
```

### Option C: Local Testing (Development Only)

Test locally before deploying:

```bash
# Set CRON_SECRET
export CRON_SECRET="your_secret_key"

# Test the endpoint
curl -X POST http://localhost:3000/api/cron/social-analytics \
  -H "Authorization: Bearer $CRON_SECRET"
```

---

## Step 9: Configure Postiz Integration IDs

### Get Your Integration IDs

1. Log in to [postiz.com](https://postiz.com)
2. Go to Integrations
3. Note the integration IDs for:
   - Instagram: `cmlre90pk04d9mn0yosyhnx4o` (example)
   - X: `cmlrob0gp05g7mn0yncmwzg7c` (example)
   - LinkedIn: `cmlrecv0r04dimn0yl34lxmzx` (example)
   - YouTube: `cmlreb5vl04dcmn0yu3ej283a` (example)

### Update in Skills

These IDs should be in the `social-engine` and related skills. Update in:
- `app/api/cron/social-analytics/route.ts`
- `.claude/skills/social-engine/SKILL.md` (for documentation)

```bash
# Check current values
grep "integration" app/api/cron/social-analytics/route.ts
```

---

## Step 10: Verify Installation

### Run Verification
```bash
/social-engine verify
```

This checks:
- ✅ All directories exist
- ✅ All style guides present
- ✅ API keys configured
- ✅ Cron job accessible
- ✅ All skills available

### Manual Verification

Check each component:

```bash
# Check directories
ls -la content/strategy/
ls -la content/style-guides/
ls -la OUTPUT/

# Check files
cat social-engine-guide.md
cat social-growth-strategy.md
cat content/strategy/posting-log.md

# Check API keys (NEVER output these!)
echo $POSTIZ_API_KEY  # Should show value (redacted)
echo $GEMINI_API_KEY  # Should show value (redacted)

# Test cron endpoint
curl -X POST http://localhost:3000/api/cron/social-analytics \
  -H "Authorization: Bearer $CRON_SECRET"
```

---

## Step 11: Launch First Cycle

### Ready? Start with Trend Discovery

```bash
/viral-research
```

This will:
1. Search for trending topics in your niche
2. Return top 10 with scores
3. Ask you to select topics

### Then Run Full Pipeline

```bash
/social-engine
```

Follow the interactive prompts to:
1. View trending topics
2. Select topics to research
3. Review research
4. Create content (images, videos, carousels)
5. Humanize text
6. Schedule posts
7. Monitor daily analytics

---

## Configuration Checklist

Before declaring success, verify:

- ☐ `social-engine-guide.md` created and customized
- ☐ `social-growth-strategy.md` initialized
- ☐ `content/strategy/posting-log.md` created
- ☐ All style guides created in `content/style-guides/`
- ☐ `.env.local` has all API keys
- ☐ Cron job scheduled (external or Fly.io)
- ☐ Postiz integration IDs configured
- ☐ `/social-engine verify` passes all checks
- ☐ First `/viral-research` runs successfully
- ☐ Can access `/api/cron/social-analytics` endpoint

---

## Troubleshooting Setup

### "POSTIZ_API_KEY not found"
**Solution**:
1. Generate API key in Postiz dashboard
2. Add to `.env.local`
3. Reload shell: `source ~/.zshrc` (or bash profile)
4. Test: `echo $POSTIZ_API_KEY`

### "Cron job failed to initialize"
**Solution**:
1. Verify CRON_SECRET is at least 32 characters
2. Check external cron service setup
3. Test endpoint manually with curl
4. Check firewall/network access

### "Style guides not generating"
**Solution**:
1. Copy template files manually
2. Edit to customize for your brand
3. Verify files in `content/style-guides/`

### "API keys not working"
**Solution**:
1. Verify keys are correct (check provider dashboard)
2. Check for trailing whitespace in `.env.local`
3. Verify APIs are enabled (Gemini, etc.)
4. Check API quotas/limits

### "Viral-research returns no results"
**Solution**:
1. Check internet connectivity
2. Verify niche keywords are specific
3. Check API rate limits (try again in 1 hour)
4. Review error messages in logs

---

## Next Steps After Init

### Day 1
1. Run `/viral-research` to find trends
2. Select 2-3 topics
3. Run `/social-engine` to create first posts

### Day 2-7
- Monitor content creation progress
- Review images/videos before approval
- Approve posts for scheduling

### Day 8+
- Check analytics daily at 7 AM
- Review `social-growth-strategy.md` for insights
- Adjust strategy based on recommendations
- Run `/viral-research` again for next cycle

---

## File Reference

| File | Purpose | Location |
|------|---------|----------|
| social-engine-guide.md | Niche config | Root |
| social-growth-strategy.md | KPI tracking | Root |
| posting-log.md | Post history | content/strategy/ |
| carousel-guide.md | Carousel style | content/style-guides/ |
| blog-guide.md | Blog image style | content/style-guides/ |
| linkedin-twitter-video-guides.md | Other platforms | content/style-guides/ |
| Cron route | Daily analytics | app/api/cron/social-analytics/ |

---

## Support

**If something breaks**:
1. Check error messages carefully
2. Review SKILL.md files for details
3. Run `/social-engine verify` to diagnose
4. Check README.md troubleshooting section

**For questions**:
- Edit `social-engine-guide.md` to adjust niche
- Review example outputs in `OUTPUT/`
- Check daily strategy updates in `social-growth-strategy.md`

---

## You're Ready! 🚀

Your social engine is initialized and ready to run!

```bash
# Start trending topics discovery
/viral-research

# Or jump straight to full pipeline
/social-engine
```

Happy creating! 🎨📱✨

---

**Initialization Version**: 1.0
**Last Updated**: 2026-03-06
**Estimated Setup Time**: 30-45 minutes
