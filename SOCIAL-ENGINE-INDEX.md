# Social Engine - Complete Skill Suite

**Status**: ✅ Production Ready
**Version**: 1.0
**Created**: 2026-03-06

---

## Welcome to Social Engine 🚀

A complete, professional social media automation system that handles everything from trend discovery to daily analytics.

### What You Get
- ✅ Automated trend discovery
- ✅ Deep topic research
- ✅ Multi-format content creation (images, videos, carousels)
- ✅ Text humanization
- ✅ Multi-platform scheduling
- ✅ Daily analytics & learning

---

## Quick Start

```bash
# 1. Navigate to your project
cd your-project

# 2. Initialize (interactive, 30-45 min)
/social-engine init

# 3. Discover trends
/viral-research

# 4. Or run full pipeline
/social-engine
```

---

## File Structure

```
augmi-skills/
├── social-engine/                    # Main skill
│   ├── README-MASTER.md             # 👈 START HERE (overview + setup)
│   ├── SKILL.md                     # Technical documentation
│   ├── README.md                    # Comprehensive guide
│   ├── INITIALIZATION.md            # Step-by-step setup walkthrough
│   └── templates/                   # Style guide templates
│       ├── carousel-guide-template.md
│       ├── blog-guide-template.md
│       └── linkedin-twitter-video-guides.md
│
├── viral-research/                   # Trend discovery skill
│   └── SKILL.md                     # Trend discovery documentation
│
├── SOCIAL-ENGINE-INDEX.md           # This file
├── SOCIAL-ENGINE-SUMMARY.md         # Quick reference
└── [other skills...]
```

---

## Documentation Map

### For First-Time Users 👈 START HERE
1. **[social-engine/README-MASTER.md](./social-engine/README-MASTER.md)** (This file system)
   - What is Social Engine?
   - How to install and setup
   - API keys required
   - Parameters and configuration
   - Troubleshooting

### For Detailed Setup
2. **[social-engine/INITIALIZATION.md](./social-engine/INITIALIZATION.md)**
   - Step-by-step walkthrough
   - File structure guide
   - Configuration checklist
   - Detailed troubleshooting

### For Technical Details
3. **[social-engine/SKILL.md](./social-engine/SKILL.md)**
   - 7-phase pipeline details
   - File integration guide
   - API route documentation
   - Performance metrics

### For Comprehensive Guide
4. **[social-engine/README.md](./social-engine/README.md)**
   - Complete feature overview
   - Platform-specific guidelines
   - Advanced configuration
   - Best practices

### For Viral Research Skill
5. **[viral-research/SKILL.md](./viral-research/SKILL.md)**
   - Trend discovery algorithm
   - Scoring methodology
   - Integration with strategy

### For Quick Reference
6. **[SOCIAL-ENGINE-SUMMARY.md](./SOCIAL-ENGINE-SUMMARY.md)**
   - Quick file structure
   - Commands reference
   - Troubleshooting guide

---

## Key Features

### 🎯 Intelligent Trend Discovery
- Searches 5+ sources (Google Trends, Twitter, Reddit, HackerNews, ProductHunt)
- Scores by virality potential and relevance to your niche
- Returns top 10 trending topics with detailed analysis

### 📊 Deep Research
- Comprehensive research on selected topics
- Image prompts for visual content
- Multiple content angles identified

### 🎨 Multi-Format Content Creation
- **Blog Images**: 16:9 landscape, high-resolution
- **Instagram Carousels**: 1080x1350px, 6-slide sets
- **Short Videos**: 9:16 vertical, 30-60 seconds
- **LinkedIn Images**: Professional, 1:1 or 1.91:1

### 🤖 Humanized Copywriting
- Removes 24 AI writing patterns
- Ensures authentic human voice
- Maintains brand consistency

### 📱 Multi-Platform Distribution
- **Instagram**: Carousels + Reels
- **X/Twitter**: Threads + Videos
- **LinkedIn**: Articles + Professional Images
- **YouTube**: Shorts

### 📈 Daily Analytics & Learning
- Automatic 7 AM UTC collection
- Platform metrics from Postiz
- 10 actionable recommendations
- Feeds insights back into trend discovery

---

## Getting Started

### Step 1: Get API Keys (10 minutes)
1. **Postiz API Key** - [postiz.com](https://postiz.com) → Settings → API
2. **Gemini API Key** - [Google Cloud](https://console.cloud.google.com) → Credentials
3. **Anthropic API Key** - [Anthropic](https://console.anthropic.com) → API Keys
4. **Cron Secret** - Create a random string (32+ characters)

### Step 2: Add to .env.local (2 minutes)
Create `.env.local` in your project root:
```bash
POSTIZ_API_KEY=pk_live_xxxxxxxxxxxxx
GEMINI_API_KEY=AIza_xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
CRON_SECRET=your_secret_key_min_32_chars
```

### Step 3: Initialize (30-45 minutes)
```bash
/social-engine init
```
Follow interactive prompts. Creates all directories and style guides.

### Step 4: Verify (2 minutes)
```bash
/social-engine verify
```
Checks all components working properly.

### Step 5: Start! (10 minutes)
```bash
/viral-research
```
Or:
```bash
/social-engine
```

---

## Using in Claude Code vs Claude.ai

### Claude Code (Recommended)
**Best for**: Full-featured setup and management

```bash
# 1. Open Claude Code
# 2. Navigate to project folder
# 3. Run command:
/social-engine init
```

**Advantages**:
- Full file access and modification
- Real-time output viewing
- Can edit files directly
- Better for troubleshooting

### Claude.ai (claude.ai/code)
**Best for**: Learning and lighter usage

```
User: I want to use social-engine

Claude: Here's how to get started...
[Guide provided interactively]
```

**Advantages**:
- No local setup needed
- Access from anywhere
- Conversational guidance
- Great for first-time learners

### Augmi Dashboard
**Best for**: Integrated platform usage

Dashboard integration coming soon.

---

## API Keys Required

| Key | Provider | What It Does | Get It At |
|-----|----------|-------------|-----------|
| `POSTIZ_API_KEY` | Postiz | Schedule posts to all platforms | [postiz.com](https://postiz.com)/settings/api |
| `GEMINI_API_KEY` | Google Cloud | Generate images for posts | [Google Cloud Console](https://console.cloud.google.com) |
| `ANTHROPIC_API_KEY` | Anthropic | Power Claude AI features | [Anthropic Console](https://console.anthropic.com) |
| `CRON_SECRET` | You | Secure daily automation | Create random string |

### Optional
- `ANALYTICS_EMAIL` - Email for reports (optional)
- `ANALYTICS_CRON_TIME` - Daily run time, default 07:00 UTC

---

## Initialization Parameters

When you run `/social-engine init`, you'll configure:

| Parameter | Type | Example | Required |
|-----------|------|---------|----------|
| Primary Niche | string | "AI Agents, OpenClaw" | ✅ |
| Subtopics | array | ["Agent deployment", "Agent wallets"] | ✅ |
| Target Platforms | array | ["Instagram", "X", "LinkedIn", "YouTube"] | ✅ |
| Target Audience | string | "Developers, crypto founders" | ✅ |
| Post Frequency | string | "3-5 per week" | ✅ |
| Output Directory | path | "./OUTPUT" | ✅ |
| POSTIZ_API_KEY | secret | pk_live_xxxxx | ✅ |
| GEMINI_API_KEY | secret | AIza_xxxxx | ✅ |
| ANTHROPIC_API_KEY | secret | sk-ant-xxxxx | ✅ |
| CRON_SECRET | secret | random string | ✅ |
| Daily Cron Time | time | "07:00" UTC | ⭕ (default: 07:00) |

---

## Usage Commands

### Discover Trends
```bash
/viral-research
```
Find top 10 trending topics in your niche (10 minutes).

### Full Pipeline
```bash
/social-engine
```
Run all 7 phases: discover → research → create → humanize → schedule → analyze (2-3 hours).

### Research Specific Topic
```bash
/deep-research:full "Topic Name"
```
Deep dive on one topic without trend discovery.

### View Strategy & KPIs
```bash
cat social-growth-strategy.md
```
See daily metrics and recommendations (updated 7 AM UTC).

### Verify Setup
```bash
/social-engine verify
```
Check all components working.

---

## What Happens After Init

### Your Project Structure
```
your-project/
├── social-engine-guide.md           # Your niche config
├── social-growth-strategy.md        # KPIs (updated daily)
├── content/
│   ├── strategy/posting-log.md      # Post history
│   ├── style-guides/                # Customized guides
│   └── research/                    # Archived research
├── OUTPUT/
│   ├── {date}/{topic}/              # Content output
│   └── social-analytics/{date}/     # Daily metrics
├── app/api/cron/
│   └── social-analytics/route.ts    # Daily 7 AM automation
└── .env.local                       # Your API keys
```

### Daily Automation
Every day at **7:00 AM UTC**, the system automatically:
1. Collects metrics from all platforms
2. Updates KPI tracking
3. Generates 10 recommendations
4. Saves analytics reports

No action needed from you!

---

## Performance Targets

### Engagement Rates
- Instagram: >3%
- X/Twitter: >2%
- LinkedIn: >1.5% CTR
- YouTube: >70% completion

### Growth
- 5-10% monthly follower growth
- 3-5 posts per week
- 10-15% reach growth per month

### Timeline
- **Week 1**: 5-10 posts created
- **Month 1**: 20-40 posts, engagement patterns clear
- **Month 3**: 40-80 posts, measurable growth
- **Month 6**: 80-200 posts, viral cycles emerging

---

## Skills Integrated

Social-engine orchestrates:

1. **viral-research** - Discovers trending topics
2. **deep-research:full** - Researches topics deeply
3. **blog-image-gen** - Generates images
4. **carousel-image-gen** - Creates carousels
5. **short-video-gen** - Creates short videos
6. **humanizer** - Humanizes text
7. **postiz** - Schedules posts
8. **social-analytics** - Collects metrics
9. **trend-finder** - Alternative trends

All coordination is automatic!

---

## Troubleshooting Quick Guide

| Issue | Solution |
|-------|----------|
| Command not found | Make sure in project root directory |
| API key error | Check `.env.local`, reload shell |
| No trends returned | Check internet, verify niche keywords |
| Cron not running | Test endpoint with curl, check service config |
| Images not generating | Verify GEMINI_API_KEY, check quota |
| Posts not scheduling | Verify Postiz API key correct |

**For detailed troubleshooting**: See [INITIALIZATION.md](./social-engine/INITIALIZATION.md)

---

## Support & Resources

### Need Help?
1. **First time?** → Read [README-MASTER.md](./social-engine/README-MASTER.md)
2. **During setup?** → Follow [INITIALIZATION.md](./social-engine/INITIALIZATION.md)
3. **Technical details?** → Check [SKILL.md](./social-engine/SKILL.md)
4. **Quick reference?** → See [SOCIAL-ENGINE-SUMMARY.md](./SOCIAL-ENGINE-SUMMARY.md)

### Found an Issue?
1. Run `/social-engine verify` to diagnose
2. Check error messages
3. Review troubleshooting section
4. Check API configuration

### GitHub
- Repository: [github.com/kon-rad/augmi-skills](https://github.com/kon-rad/augmi-skills)
- Issues: Report bugs via GitHub

---

## Platform Guides

Each platform has custom specifications:

### Instagram
- 1080x1350px carousels (6 slides)
- 9:16 vertical Reels
- Post Tue-Thu, 11 AM - 1 PM
- Target: >3% engagement

### X/Twitter
- Threads (5-15 tweets each)
- 1200x675px images
- Post Mon & Wed, 9-10 AM
- Target: >2% engagement

### LinkedIn
- Professional articles + images
- 1200x627px (1.91:1)
- Post Tue-Thu, 8-10 AM
- Target: >1.5% CTR

### YouTube
- 1080x1920px vertical shorts
- 30-60 seconds
- Post Fri-Sun
- Target: >70% completion

Each has dedicated style guide in `content/style-guides/` after init.

---

## System Requirements

- **Node.js**: >= 22
- **Python**: 3.8+ (for image generation)
- **Disk**: 5GB minimum for outputs
- **Memory**: 4GB+ recommended
- **Internet**: Required for all APIs

---

## Version Info

**Current Version**: 1.0
**Release Date**: 2026-03-06
**Status**: ✅ Production Ready
**Maintained By**: @konradgnat

---

## Next Steps

1. **Read** [README-MASTER.md](./social-engine/README-MASTER.md) (10 min)
2. **Get API Keys** (10 min)
3. **Add to .env.local** (2 min)
4. **Run Init** (30-45 min): `/social-engine init`
5. **Start Discovering Trends**: `/viral-research` (10 min)
6. **Create Content**: `/social-engine` (2-3 hours)
7. **Monitor Daily**: Check `social-growth-strategy.md` at 7 AM UTC

---

## Files in This Suite

- **README-MASTER.md** ← Overview & setup guide (start here!)
- **SKILL.md** - Technical documentation
- **README.md** - Comprehensive guide
- **INITIALIZATION.md** - Step-by-step walkthrough
- **SOCIAL-ENGINE-SUMMARY.md** - Quick reference
- **templates/** - Style guide templates
  - carousel-guide-template.md
  - blog-guide-template.md
  - linkedin-twitter-video-guides.md

---

## Ready? 🚀

```bash
/social-engine init
```

This single command will guide you through everything!

Questions? Read [README-MASTER.md](./social-engine/README-MASTER.md).

---

**Happy creating!** 🎨📱✨

---

**Last Updated**: 2026-03-06
**Created in**: `/dev/startups/augmi-skills/`
**For updates**: Check GitHub or project documentation
