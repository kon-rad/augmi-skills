# Social Engine Skill

Complete automated social media content orchestrator from trend discovery to daily analytics and continuous learning.

## Overview

The Social Engine is a full-stack content generation pipeline that discovers trending topics, researches them deeply, creates multi-format content (images, videos, carousels), humanizes text, schedules posts across platforms, and learns from daily analytics to improve future content.

## Quick Start

```bash
/social-engine
```

This launches the 7-phase pipeline with user approvals at each step.

## The 7-Phase Pipeline

### Phase 1: Discover Trends
**Skill**: `viral-research`
- Searches 5+ sources (Google Trends, Twitter, Reddit, HackerNews, ProductHunt)
- Ranks by virality potential and relevance to your niche
- Returns top 10 trending topics

**Output**: Interactive list for user selection

---

### Phase 2: User Topic Selection
User reviews the 10 trending topics and selects 1-5 to develop further.

**Output**: Selected topics list

---

### Phase 3: Deep Research
**Skill**: `deep-research:full`
- Researches each selected topic comprehensively
- Gathers insights from web search + social media
- Produces detailed research documents
- Creates image prompts and content angles

**Output**:
```
OUTPUT/{date}/{slug}/
├── research-summary.md
├── detailed-research.md
├── image-prompts-formatted.md
├── article-draft.md
└── social-thread.md
```

---

### Phase 4: Create Visual Content
Creates all visual assets in parallel:

**Blog/Social Images** - `blog-image-gen` skill
- High-quality featured images
- Social media post images
- LinkedIn hero images (1:1 square)

**Instagram Carousels** - `carousel-image-gen` skill
- 6-slide carousel sets
- 1080x1350px portrait format
- Sci-fi artistic aesthetic

**Short-Form Videos** - `short-video-gen` skill
- 30-60 second vertical videos
- YouTube Shorts / Instagram Reels format
- Captions and text overlays

**Output**:
```
OUTPUT/{date}/{slug}/
├── images/
│   ├── featured.png
│   ├── linkedin-hero.png
│   └── social-cards.png
├── carousel/
│   ├── slide1.png
│   ├── slide2.png
│   └── ...slide6.png
└── videos/
    └── short-form.mp4
```

---

### Phase 5: Humanize Text
**Skill**: `humanizer`
- Removes AI writing patterns (24-point detection)
- Ensures authentic, human voice
- Refines captions and descriptions
- Maintains brand tone while sounding natural

**Output**: Humanized captions ready for posting

---

### Phase 6: Schedule Posts
**Skill**: `postiz`
- Uploads all media to Postiz
- Schedules across all platforms simultaneously:
  - **Instagram**: Carousel + Reels
  - **X/Twitter**: Threads + Videos
  - **LinkedIn**: Articles + Images
  - **YouTube**: Shorts

**Output**:
```
content/strategy/posting-log.md (updated with post IDs)
```

---

### Phase 7: Daily Analytics (Automated at 7 AM UTC)
**Trigger**: Cron job `/api/cron/social-analytics`
- Collects engagement metrics from all platforms
- Updates KPI tracking in `social-growth-strategy.md`
- Generates 10 growth recommendations
- Feeds back into viral-research for better targeting

**Output**:
```
OUTPUT/social-analytics/{date}/
├── metrics.json
├── performance-report.pdf
└── recommendations.md

social-growth-strategy.md (updated with latest KPIs)
```

---

## Continuous Learning Loop

The strategy file is the centerpiece:

```
Daily Analytics (7 AM)
    ↓
Updates social-growth-strategy.md
    ↓
viral-research reads strategy
    ↓
Finds BETTER trending topics
    ↓
Next cycle is smarter
```

---

## File Structure

When you run `/social-engine init`, it creates:

```
hexly/
├── social-engine-guide.md
├── social-growth-strategy.md
├── content/
│   ├── strategy/
│   │   └── posting-log.md
│   ├── style-guides/
│   │   ├── carousel-guide.md
│   │   ├── blog-guide.md
│   │   ├── linkedin-guide.md
│   │   ├── twitter-guide.md
│   │   └── video-guide.md
│   └── research/
│       └── [topic-specific research files]
├── OUTPUT/
│   ├── {date}/
│   │   └── {slug}/
│   │       ├── research-summary.md
│   │       ├── images/
│   │       ├── carousel/
│   │       └── videos/
│   └── social-analytics/
│       └── {date}/
│           ├── metrics.json
│           ├── performance-report.pdf
│           └── recommendations.md
└── app/api/cron/
    └── social-analytics/
        └── route.ts
```

---

## Integration with Other Skills

| Skill | Purpose | Phase |
|-------|---------|-------|
| `viral-research` | Discovers trends | Phase 1 |
| `deep-research:full` | Deep topic research | Phase 3 |
| `blog-image-gen` | Generates blog/social images | Phase 4 |
| `carousel-image-gen` | Creates Instagram carousels | Phase 4 |
| `short-video-gen` | Creates short-form videos | Phase 4 |
| `humanizer` | Removes AI patterns | Phase 5 |
| `postiz` | Schedules posts | Phase 6 |
| `social-analytics` | Collects daily metrics | Phase 7 |
| `trend-finder` | Alternative trend discovery | Phase 1 |

---

## Configuration Files

**social-engine-guide.md** - Define your niche
```markdown
# Social Engine Guide

## Niche Definition
- Primary: AI Agents, OpenClaw, Claude Code
- Subtopics: [...]

## Target Platforms
- Instagram, X, LinkedIn, YouTube

## Content Quality Standards
- Engagement targets
- Posting frequency
- Brand voice guidelines
```

**social-growth-strategy.md** - Track KPIs (updated daily)
```markdown
# Social Growth Strategy

## Current Period Metrics
- Instagram Engagement Rate: [%]
- X Engagement Rate: [%]
- LinkedIn CTR: [%]
- YouTube Completion: [%]

## Content Performance Analysis
- High performers: [topics]
- Low performers: [topics]

## Growth Recommendations
[10 actionable recommendations]
```

**content/strategy/posting-log.md** - Post history
```markdown
| Date | Platform | Content | Post ID | Engagement | Notes |
|------|----------|---------|---------|------------|-------|
| ... | Instagram | Carousel | id123 | 3.2% | [notes] |
```

---

## Style Guides

Each content type has a dedicated style guide:

- **carousel-guide.md** - Instagram carousel 1080x1350px, 6-slide format
- **blog-guide.md** - Blog/social featured images, visual hierarchy
- **linkedin-guide.md** - Professional aesthetic, 1:1 aspect ratio
- **twitter-guide.md** - Thread format, concise captions
- **video-guide.md** - 9:16 vertical, 30-60 sec, captions

All guides reference shared color palette, typography, and brand voice.

---

## Setup & Initialization

Run the initialization command:

```bash
/social-engine init
```

This interactive setup will:

1. **Define Your Niche**
   - Enter primary niche keywords
   - Define subtopics
   - Set target platforms

2. **Configure Directories**
   - Create output folders
   - Set research location
   - Configure analytics storage

3. **Create Style Guides**
   - Generate carousel guide
   - Generate blog guide
   - Generate LinkedIn guide
   - Generate Twitter guide
   - Generate video guide

4. **Set API Keys**
   - POSTIZ_API_KEY
   - GEMINI_API_KEY
   - ANTHROPIC_API_KEY
   - CRON_SECRET

5. **Configure Cron**
   - Choose cron service (external or Fly.io)
   - Set time (default 7 AM UTC)
   - Test connection

6. **Summary**
   - Review all configurations
   - Ready to run `/social-engine`

---

## Usage Commands

**Full Pipeline** (with user approvals):
```bash
/social-engine
```

**Just Find Trends**:
```bash
/viral-research
```

**Research Specific Topic**:
```bash
/deep-research:full "Topic name"
```

**View Strategy & KPIs**:
```bash
cat social-growth-strategy.md
```

**View Posting History**:
```bash
cat content/strategy/posting-log.md
```

**Check Latest Analytics**:
```bash
ls -lt OUTPUT/social-analytics/ | head
cat OUTPUT/social-analytics/{latest-date}/recommendations.md
```

---

## Daily Automation

The cron job at 7:00 AM UTC automatically:

1. Connects to Postiz API
2. Scrapes metrics from all platforms
3. Analyzes engagement patterns
4. Generates 10 growth recommendations
5. Updates `social-growth-strategy.md`
6. Saves JSON metrics to `OUTPUT/social-analytics/{date}/`
7. Generates PDF performance report

---

## Performance Metrics

Tracked daily and saved to strategy file:

- **Engagement Rate** - Likes + comments + shares / impressions
- **Reach** - Unique viewers
- **Click-Through Rate** - Clicks / impressions
- **Video Completion Rate** - Watch time / total length
- **Follower Growth** - New followers per period
- **Conversion Rate** - From content to action

---

## Troubleshooting

**No trends found**
- Check internet connectivity
- Verify niche keywords in `social-engine-guide.md`
- Check API rate limits

**Low engagement**
- Review recommendations in `social-growth-strategy.md`
- Check posting times and audience timezone
- A/B test different content formats

**Cron not running**
- Verify `CRON_SECRET` is set
- Check external cron service configuration
- Test: `curl -X POST https://augmi.world/api/cron/social-analytics -H "Authorization: Bearer $CRON_SECRET"`

**Posts not scheduling**
- Verify Postiz API key
- Check integration IDs
- Verify media uploaded successfully

---

## Next Steps

1. Run `/social-engine init` to set up
2. Configure API keys in `.env.local`
3. Set up daily cron job
4. Run `/social-engine` to start first cycle
5. Monitor `social-growth-strategy.md` daily

---

**Version**: 1.0
**Location**: `/dev/startups/augmi-skills/social-engine/`
**Maintained By**: @konradgnat

Ready to automate your social media? Start with `/social-engine init` 🚀
