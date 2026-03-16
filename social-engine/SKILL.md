# Social Engine Skill

Complete automated social media content orchestrator from trend discovery to daily analytics and continuous learning.

## Configuration

All paths, settings, and schedules live in `.claude/skills/social-content-engine/config.json`.
Run `/social-content-engine init` to create or update this config.

See `INITIALIZATION.md` for the full list of required fields and an example config.

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
- Updates KPI tracking in `data/social-analytics/viral-growth-strategy.md`
- Generates 10 growth recommendations
- Feeds back into viral-research for better targeting

**Output**:
```
data/social-analytics/{date}/
├── metrics.json
└── recommendations.md

data/social-analytics/viral-growth-strategy.md (updated with latest KPIs)
```

---

## Continuous Learning Loop

The strategy file is the centerpiece:

```
Daily Analytics (7 AM)
    ↓
Updates data/social-analytics/viral-growth-strategy.md
    ↓
viral-research reads strategy
    ↓
Finds BETTER trending topics
    ↓
Next cycle is smarter
```

---

## File Structure

All paths below are configured in `config.json` and can be customized. This shows the recommended defaults.

```
project-root/
├── .claude/skills/social-content-engine/
│   └── config.json                        ← single source of truth
├── content/
│   ├── strategy/
│   │   ├── content-thesis.md              ← viral principles & shareability rules
│   │   ├── content-style-guide.md         ← hooks, tone, brand voice (unified)
│   │   ├── content-grades.md              ← quality scoring history
│   │   ├── posting-log.md                 ← post history with engagement data
│   │   ├── posting-schedule.md            ← when to post per platform
│   │   ├── follower-conversion-playbook.md
│   │   └── business-thesis.md
│   ├── research/
│   │   └── [topic-specific research files]
│   └── templates/
│       └── [reusable content templates]
├── data/
│   └── social-analytics/
│       ├── viral-growth-strategy.md       ← KPIs + recommendations (updated daily)
│       ├── {date}/
│       │   ├── metrics.json
│       │   └── recommendations.md
│       └── raw/
├── docs/
│   └── brand/                             ← mission, value prop, brand foundation
└── OUTPUT/
    ├── {date}/
    │   └── {slug}/
    │       ├── research-summary.md
    │       ├── images/
    │       ├── carousel/
    │       └── videos/
    └── self-improvement/
        └── {date}/
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

## Key Config-Driven Files

All paths below are read from `config.json`. These are the recommended defaults.

**`content/strategy/content-style-guide.md`** - Unified style guide
- Hook templates per platform
- Emotion targeting frameworks
- Brand voice rules
- Visual aesthetic guidelines (replaces the old per-format style-guides directory)

**`data/social-analytics/viral-growth-strategy.md`** - KPI tracking (updated daily by cron)
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

**`content/strategy/posting-log.md`** - Post history with engagement data
```markdown
| Date | Platform | Content | Post ID | Engagement | Notes |
|------|----------|---------|---------|------------|-------|
| ... | Instagram | Carousel | id123 | 3.2% | [notes] |
```

**`content/strategy/content-thesis.md`** - Viral principles
- What makes content shareable in your niche
- Emotional triggers that work for your audience
- Format-specific performance patterns

---

## Setup & Initialization

Run the initialization command:

```bash
/social-content-engine init
```

This collects your brand info, niche, file paths, API keys, platform IDs, and automation tier, then writes them all to `.claude/skills/social-content-engine/config.json`.

See `INITIALIZATION.md` for the complete step-by-step guide, including all required fields and an example config.

After init, verify your setup:

```bash
/social-content-engine verify
```

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
cat data/social-analytics/viral-growth-strategy.md
```

**View Posting History**:
```bash
cat content/strategy/posting-log.md
```

**Check Latest Analytics**:
```bash
ls -lt data/social-analytics/ | head
cat data/social-analytics/{latest-date}/recommendations.md
```

---

## Daily Automation

The cron job at 7:00 AM UTC automatically:

1. Connects to Postiz API
2. Scrapes metrics from all platforms
3. Analyzes engagement patterns
4. Generates 10 growth recommendations
5. Updates `data/social-analytics/viral-growth-strategy.md`
6. Saves JSON metrics to `data/social-analytics/{date}/`

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
- Verify niche keywords in `.claude/skills/social-content-engine/config.json` (`niche.keywords`)
- Check API rate limits

**Low engagement**
- Review recommendations in `data/social-analytics/viral-growth-strategy.md`
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

1. Run `/social-content-engine init` to create `config.json`
2. Configure API keys in `.env.local`
3. Run `/social-content-engine verify` to confirm setup
4. Set up daily cron job pointing at your analytics endpoint
5. Run `/viral-research` to find first topics
6. Run `/social-content-engine` to start first cycle
7. Monitor `data/social-analytics/viral-growth-strategy.md` daily

---

**Version**: 2.0
**Date**: 2026-03-15
**Location**: `augmi-skills/social-engine/`
**Maintained By**: @konradgnat
