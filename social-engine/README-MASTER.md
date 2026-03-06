# Social Engine - Complete Social Media Automation

🚀 **Fully automated social media content pipeline** from trend discovery to daily analytics and continuous improvement.

**Location**: `/dev/startups/augmi-skills/social-engine/`
**Version**: 1.0
**Status**: ✅ Production Ready

---

## What Is Social Engine?

Social Engine is an end-to-end orchestration system that completely automates your social media content creation and management:

1. **Discovers** what's trending in your niche
2. **Researches** topics deeply
3. **Creates** multi-format content (images, videos, carousels)
4. **Humanizes** all text for authentic voice
5. **Schedules** posts across platforms
6. **Analyzes** performance daily
7. **Learns** to improve future content

All with **human approval at every step** and **continuous learning from daily analytics**.

---

## Quick Start (5 Minutes)

### In Claude Code or Claude.ai

```bash
# Initialize the system (interactive, 30-45 min setup)
/social-engine init

# Then discover trending topics
/viral-research

# Or run full 7-phase pipeline
/social-engine
```

That's it! The system will guide you through everything.

---

## How to Use

### Option 1: Claude Code (Recommended)

Claude Code gives you full CLI access with integrated file management.

**Steps**:
1. Open Claude Code
2. Navigate to your project folder
3. Run: `/social-engine init`
4. Follow interactive prompts
5. Run: `/social-engine` to start

**Benefits**:
- Full access to files and directories
- See outputs in real-time
- Modify files directly
- Test cron jobs locally

### Option 2: Claude.ai (claude.ai/code)

Use the web interface for lighter usage.

**Steps**:
1. Open [claude.ai/code](https://claude.ai/code)
2. Start conversation with: "I want to use social-engine"
3. Ask Claude to help initialize
4. Follow the step-by-step guide

**Benefits**:
- No local setup required
- Access from anywhere
- Conversational guidance
- Great for first-time setup

### Option 3: Augmi Skills Dashboard

If installed in Augmi dashboard, access as skill.

**Steps**:
1. Go to Augmi dashboard
2. Find "Social Engine" skill
3. Click "Initialize"
4. Fill in configuration
5. Launch

---

## Installation & Setup

### Prerequisites

Before starting, you need:

**Required Accounts**:
- ✅ Postiz account (social media scheduling) - [postiz.com](https://postiz.com)
- ✅ Google Cloud account (Gemini API for image generation) - [console.cloud.google.com](https://console.cloud.google.com)
- ✅ Anthropic account (Claude API) - [console.anthropic.com](https://console.anthropic.com)

**Required API Keys**:
- ✅ POSTIZ_API_KEY (generate from Postiz settings)
- ✅ GEMINI_API_KEY (generate from Google Cloud)
- ✅ ANTHROPIC_API_KEY (generate from Anthropic)
- ✅ CRON_SECRET (you create, min 32 characters)

**Optional**:
- ANALYTICS_EMAIL (for email reports)

### Getting API Keys

#### Postiz API Key
1. Log in to [postiz.com](https://postiz.com)
2. Go to **Settings → API**
3. Click **Create New API Token**
4. Copy the token
5. Add to `.env.local`: `POSTIZ_API_KEY=pk_live_xxxxx`

#### Gemini API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create or select a project
3. Enable **Gemini API** (Generative AI → APIs)
4. Go to **Credentials → Create Credentials → API Key**
5. Copy the key
6. Add to `.env.local`: `GEMINI_API_KEY=AIza_xxxxx`

#### Anthropic API Key
1. Go to [Anthropic Console](https://console.anthropic.com)
2. Click **API Keys**
3. Create or copy existing key
4. Add to `.env.local`: `ANTHROPIC_API_KEY=sk-ant-xxxxx`

#### Cron Secret
1. Create a strong random string (min 32 characters)
2. Add to `.env.local`: `CRON_SECRET=your_secret_here_min_32_chars`

**Example `.env.local`**:
```bash
POSTIZ_API_KEY=pk_live_xxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIza_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
CRON_SECRET=super_secret_key_min_32_characters_long_xxxx
```

---

## Initialization Process

### Step 1: Run Init Command

```bash
/social-engine init
```

This launches an interactive setup that will:
- Ask about your niche
- Create all directories
- Generate style guides
- Configure API keys
- Set up cron job
- Verify everything works

**Time**: 30-45 minutes
**Effort**: ~15 minutes of active decisions

### Step 2: Answer Setup Questions

The system will ask:

**Niche Definition**
- What's your primary niche? (e.g., "AI Agents, OpenClaw, Claude Code")
- What are 3-5 subtopics?
- Which platforms? (Instagram, X, LinkedIn, YouTube)
- Who's your target audience?

**Configuration**
- Where to store outputs? (default: OUTPUT/)
- Where to archive research? (default: content/research/)
- Preferred posting frequency?
- Brand colors and fonts?

**API Keys**
- Confirm POSTIZ_API_KEY
- Confirm GEMINI_API_KEY
- Confirm ANTHROPIC_API_KEY
- Confirm CRON_SECRET

**Cron Setup**
- Daily analytics at what time? (default: 7 AM UTC)
- Which cron service? (External like EasyCron or Fly.io)

### Step 3: Verify Installation

After init completes, run:

```bash
/social-engine verify
```

This checks:
- ✅ All directories created
- ✅ All style guides generated
- ✅ API keys configured
- ✅ Cron job accessible
- ✅ All skills available

If all pass, you're ready to use!

---

## Parameters & Configuration

### Initialization Parameters

When running `/social-engine init`, you'll configure:

| Parameter | Type | Example | Required |
|-----------|------|---------|----------|
| Primary Niche | string | "AI Agents, OpenClaw" | ✅ Yes |
| Subtopics | array | ["Agent deployment", "OpenClaw features"] | ✅ Yes |
| Platforms | array | ["Instagram", "X", "LinkedIn", "YouTube"] | ✅ Yes |
| Audience | string | "Developers, crypto founders" | ✅ Yes |
| Post Frequency | string | "3-5 per week" | ✅ Yes |
| Output Location | path | "./OUTPUT" | ✅ Yes |
| Research Location | path | "./content/research" | ✅ Yes |
| Analytics Location | path | "./OUTPUT/social-analytics" | ✅ Yes |
| POSTIZ_API_KEY | secret | pk_live_xxxxx | ✅ Yes |
| GEMINI_API_KEY | secret | AIza_xxxxx | ✅ Yes |
| ANTHROPIC_API_KEY | secret | sk-ant-xxxxx | ✅ Yes |
| CRON_SECRET | secret | 32+ char string | ✅ Yes |
| Cron Time | time | "07:00" (UTC) | ⭕ Optional (default: 07:00) |
| Cron Service | enum | "easycron" or "flyio" | ⭕ Optional (default: easycron) |

### Usage Parameters

When running `/social-engine` or `/viral-research`, you'll select:

| Parameter | Type | Example | Required |
|-----------|------|---------|----------|
| Niche Keywords | string | Auto-read from guide | ✅ Yes |
| Topics to Research | array | User selects 2-5 | ✅ Yes |
| Content Types | array | Auto (images, video, carousel) | ✅ Yes |
| Posting Platforms | array | Auto (from init) | ✅ Yes |

---

## Configuration Files

After initialization, you'll have:

### Main Configuration

**`social-engine-guide.md`** (Root of project)
- Your niche definition
- Target platforms
- Content quality standards
- Brand voice guidelines

Edit to customize niche:
```markdown
## Niche Definition
**Primary**: AI Agents, OpenClaw, Claude Code
**Subtopics**:
- AI agent deployment
- OpenClaw architecture
- Claude Code integration

## Target Platforms
- Instagram
- X/Twitter
- LinkedIn
- YouTube
```

**`social-growth-strategy.md`** (Root of project)
- KPI tracking (auto-updated daily)
- Performance metrics
- Growth recommendations
- Content analysis

Auto-updated every day at 7 AM UTC.

### Style Guides

**`content/style-guides/carousel-guide.md`**
- Instagram carousel specifications
- 1080x1350px, 6 slides
- Sci-fi aesthetic guidelines

**`content/style-guides/blog-guide.md`**
- Blog featured images (16:9)
- Social media card specs
- Color palette and typography

**`content/style-guides/linkedin-twitter-video-guides.md`**
- LinkedIn professional guidelines
- Twitter thread format
- Short-form video (9:16 vertical)

### Environment Variables

**`.env.local`** (Project root, NOT in git)
```bash
POSTIZ_API_KEY=pk_live_xxxx
GEMINI_API_KEY=AIza_xxxx
ANTHROPIC_API_KEY=sk-ant-xxxx
CRON_SECRET=your_32_char_secret
ANALYTICS_EMAIL=optional@example.com (optional)
ANALYTICS_CRON_TIME=07:00 (optional, default)
```

---

## Usage Commands

### Discover Trends Only
```bash
/viral-research
```
Returns top 10 trending topics in your niche (10 minutes).
Use when you just want to check what's trending.

### Full 7-Phase Pipeline
```bash
/social-engine
```
Runs complete pipeline: discover → research → create → humanize → schedule → analyze (2-3 hours).
Creates complete posts ready to publish.

### Research Specific Topic
```bash
/deep-research:full "Topic Name"
```
Deep dive into a single topic without trend discovery.

### View Strategy & KPIs
```bash
cat social-growth-strategy.md
```
See daily metrics and 10 growth recommendations (updated 7 AM UTC).

### View Post History
```bash
cat content/strategy/posting-log.md
```
See all scheduled posts with engagement metrics.

### Verify Setup
```bash
/social-engine verify
```
Check all components are working properly.

---

## API Keys Explained

### POSTIZ_API_KEY
**What it does**: Allows posting to Instagram, X, LinkedIn, YouTube
**Where to get**: Postiz dashboard → Settings → API
**Format**: `pk_live_xxxxxxxxxxxx`
**Required**: ✅ Yes (scheduling won't work without it)

### GEMINI_API_KEY
**What it does**: Generates images for social media posts
**Where to get**: Google Cloud Console → Credentials → API Key
**Format**: `AIza_xxxxxxxxxxxxxxxxxxxx`
**Required**: ✅ Yes (image generation won't work without it)
**Cost**: Free tier (300 requests/month), then paid

### ANTHROPIC_API_KEY
**What it does**: Powers Claude AI for research and content creation
**Where to get**: Anthropic Console → API Keys
**Format**: `sk-ant-xxxxxxxxxxxxxxxxxxxx`
**Required**: ✅ Yes (all AI features depend on this)

### CRON_SECRET
**What it does**: Secures the daily analytics cron job
**Format**: Any string, 32+ characters recommended
**Required**: ✅ Yes (protects your daily automation)
**Example**: `aB3cD9eF1gH7iJ2kL5mN8oPqR4sT6uVwXyZ0abc1def`

---

## Daily Automation

The system automatically runs at **7:00 AM UTC every day**:

1. **Connects to Postiz** - Retrieves metrics from all platforms
2. **Collects Data**:
   - Impressions and reach
   - Engagement (likes, comments, shares)
   - Click-through rates
   - Follower growth
3. **Analyzes Patterns** - What worked, what didn't
4. **Generates Recommendations** - 10 actionable improvements
5. **Updates Strategy File** - New KPIs feed into next cycle
6. **Saves Reports** - JSON metrics + PDF report

No action needed from you—it's fully automated!

---

## Performance Targets

### Engagement Rates
- **Instagram**: >3% (likes + comments + shares / impressions)
- **X/Twitter**: >2%
- **LinkedIn**: >1.5% click-through rate
- **YouTube**: >70% completion rate

### Growth Targets
- **Monthly Follower Growth**: 5-10%
- **Weekly Reach Growth**: 10-20%
- **Post Frequency**: 3-5 per week (all platforms)

### Optimal Posting Times
- **Instagram**: Tue-Thu, 11 AM - 1 PM
- **X/Twitter**: Mon & Wed, 9-10 AM
- **LinkedIn**: Tue-Thu, 8-10 AM
- **YouTube Shorts**: Fri-Sun

---

## File Structure After Setup

```
your-project/
├── social-engine-guide.md              # Your niche config
├── social-growth-strategy.md           # KPIs (auto-updated daily)
│
├── content/
│   ├── strategy/
│   │   └── posting-log.md              # Post history
│   ├── style-guides/
│   │   ├── carousel-guide.md
│   │   ├── blog-guide.md
│   │   └── linkedin-twitter-video-guides.md
│   └── research/                       # Archived research
│
├── OUTPUT/
│   ├── 20260306/
│   │   ├── topic-slug/
│   │   │   ├── research-summary.md
│   │   │   ├── images/
│   │   │   ├── carousel/
│   │   │   └── videos/
│   │   └── [other topics]
│   └── social-analytics/
│       └── 2026-03-06/
│           ├── metrics.json
│           ├── performance-report.pdf
│           └── recommendations.md
│
├── app/api/cron/
│   └── social-analytics/
│       └── route.ts                    # Daily 7 AM automation
│
└── .env.local (NOT in git!)
    ├── POSTIZ_API_KEY
    ├── GEMINI_API_KEY
    ├── ANTHROPIC_API_KEY
    └── CRON_SECRET
```

---

## Troubleshooting

### "Init command not found"
**Solution**: Make sure you're in your project root directory

### "API Key not found in .env.local"
**Solution**:
1. Create `.env.local` if it doesn't exist
2. Add keys exactly as shown above
3. Reload shell: `source ~/.zshrc` (or `.bashrc`)
4. Test: `echo $POSTIZ_API_KEY`

### "Cron job not running"
**Solution**:
1. Verify CRON_SECRET in `.env.local` matches setup
2. Check external cron service (EasyCron, cron-job.org)
3. Test endpoint: `curl -X POST https://yoururl/api/cron/social-analytics -H "Authorization: Bearer $CRON_SECRET"`

### "Trends not found"
**Solution**:
1. Check internet connection
2. Verify niche keywords in `social-engine-guide.md`
3. Check API rate limits (try again in 1 hour)

### "Images not generating"
**Solution**:
1. Verify GEMINI_API_KEY is correct
2. Check Google Cloud API quota
3. Ensure Gemini API is enabled

See [INITIALIZATION.md](./INITIALIZATION.md) for detailed troubleshooting.

---

## Documentation

| Document | Purpose | Read When |
|----------|---------|-----------|
| **README-MASTER.md** | This file - overview and setup | First time |
| [SKILL.md](./SKILL.md) | Technical documentation | Understanding how it works |
| [README.md](./README.md) | Comprehensive guide + examples | Learning advanced features |
| [INITIALIZATION.md](./INITIALIZATION.md) | Step-by-step setup guide | During init, if stuck |
| [SOCIAL-ENGINE-SUMMARY.md](./SOCIAL-ENGINE-SUMMARY.md) | Quick reference | Quick lookups |

### In Your Project (After Init)
- `social-engine-guide.md` - Your niche config
- `social-growth-strategy.md` - Daily KPIs & recommendations
- `content/style-guides/carousel-guide.md` - Carousel specs
- `content/style-guides/blog-guide.md` - Blog/image specs
- `content/style-guides/linkedin-twitter-video-guides.md` - Platform guides

---

## Features Overview

✅ **Intelligent Trend Discovery**
- Searches 5+ sources (Google Trends, Twitter, Reddit, HackerNews)
- Scores by virality potential
- Deduplicates similar stories

✅ **Deep Research**
- Gathers insights from web + social media
- Creates detailed research documents
- Generates image prompts and content angles

✅ **Multi-Format Content Creation**
- Blog images (16:9 landscape)
- Instagram carousels (1080x1350px, 6 slides)
- Short-form videos (9:16 vertical, 30-60 sec)
- LinkedIn professional images

✅ **Humanized Copywriting**
- Removes 24 AI writing patterns
- Ensures authentic human voice
- Maintains brand tone

✅ **Multi-Platform Scheduling**
- Instagram (carousel + Reels)
- X/Twitter (threads + videos)
- LinkedIn (articles + images)
- YouTube (shorts)

✅ **Daily Analytics & Learning**
- Automatic 7 AM UTC collection
- Platform metrics from Postiz
- 10 actionable recommendations
- Feeds back into next content cycle

✅ **Continuous Improvement**
- Strategy file guides future content
- Performance data drives topic selection
- Weekly insights and patterns

---

## Success Timeline

| Timeframe | What to Expect |
|-----------|----------------|
| **Week 1** | 5-10 posts created, first analytics |
| **Weeks 2-3** | 10-20 posts, engagement patterns emerging |
| **Month 1** | 20-40 posts, clear KPIs, recommendations improving |
| **Months 2-3** | 40-80 posts, engagement increasing 5-10% |
| **Months 3-6** | 80-200 posts, 10-15% monthly follower growth, viral cycles emerging |

---

## Skills Orchestrated

The social-engine automatically coordinates with:

1. **viral-research** - Discovers trending topics
2. **deep-research:full** - Researches topics deeply
3. **blog-image-gen** - Generates images
4. **carousel-image-gen** - Creates carousels
5. **short-video-gen** - Creates short videos
6. **humanizer** - Humanizes text
7. **postiz** - Schedules posts
8. **social-analytics** - Collects metrics
9. **trend-finder** - Alternative trend source

All integration is automatic—you don't manage individual skills.

---

## Getting Help

### First Time?
1. Read this README-MASTER.md
2. Run `/social-engine init` (interactive setup)
3. Follow the prompts

### Stuck During Setup?
- Check [INITIALIZATION.md](./INITIALIZATION.md) step-by-step guide
- Review troubleshooting section above
- Check error messages carefully

### Want to Learn More?
- Read [SKILL.md](./SKILL.md) for technical details
- Read [README.md](./README.md) for comprehensive guide
- Check [SOCIAL-ENGINE-SUMMARY.md](./SOCIAL-ENGINE-SUMMARY.md) for quick reference

### Have a Bug?
1. Run `/social-engine verify` to diagnose
2. Check logs in `OUTPUT/social-analytics/{date}/`
3. Review error messages for clues
4. Check API key configuration

---

## Next Steps

1. **Get API Keys** (10 min)
   - Postiz, Google Cloud, Anthropic

2. **Add to .env.local** (2 min)
   - Copy keys to project root `.env.local`

3. **Run Init** (30-45 min)
   - `/social-engine init` with interactive setup

4. **Verify** (2 min)
   - `/social-engine verify` checks everything

5. **Start First Cycle** (10 min + content generation)
   - `/viral-research` to find trends
   - `/social-engine` for full pipeline

---

## System Requirements

- **Node.js**: >= 22
- **Python**: 3.8+ (for image generation)
- **Disk Space**: 5GB minimum for outputs
- **Internet**: Required for all API calls
- **Memory**: 4GB+ recommended

---

## Version & Support

**Version**: 1.0
**Created**: 2026-03-06
**Status**: ✅ Production Ready
**Location**: `/dev/startups/augmi-skills/social-engine/`
**Maintained By**: @konradgnat

---

## Ready to Start?

```bash
# Step 1: Add API keys to .env.local
POSTIZ_API_KEY=pk_live_xxxxx
GEMINI_API_KEY=AIza_xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
CRON_SECRET=your_secret_32_chars

# Step 2: Initialize
/social-engine init

# Step 3: Discover trends
/viral-research

# Step 4: Create content
/social-engine
```

**That's it!** Your automated social media empire starts here. 🚀

---

## Quick Links

- **GitHub**: [augmi-skills](https://github.com/kon-rad/augmi-skills)
- **Augmi**: [augmi.world](https://augmi.world)
- **API Docs**: See individual SKILL.md files
- **Issues**: Report via GitHub

---

🎯 **Happy creating!** 🎨📱✨

Questions? Read [INITIALIZATION.md](./INITIALIZATION.md) or [README.md](./README.md).
