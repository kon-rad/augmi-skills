# Social Engine Complete System Summary

**Created**: 2026-03-06
**Status**: ✅ Ready for use
**Location**: `/dev/startups/augmi-skills/social-engine/` and `/dev/startups/augmi-skills/viral-research/`

---

## What Is Social Engine?

A complete, automated social media content orchestration system that:
- Discovers trending topics in your niche
- Researches them deeply
- Creates multi-format content (images, videos, carousels)
- Humanizes all text
- Schedules across platforms
- Analyzes daily performance
- Learns from analytics to improve future content

---

## Quick Start

```bash
# Initialize everything (interactive setup)
/social-engine init

# Then start discovering trends
/viral-research

# Or run full pipeline
/social-engine
```

---

## Files Created in augmi-skills

### Main Skills

#### `/social-engine/`
- **SKILL.md** - Main skill documentation (7-phase pipeline)
- **README.md** - Comprehensive guide with examples
- **INITIALIZATION.md** - Step-by-step setup guide
- **SETUP.md** - Quick setup reference (in hexly)

#### `/viral-research/`
- **SKILL.md** - Trend discovery skill documentation

### Style Guide Templates

#### `/social-engine/templates/`
- **carousel-guide-template.md** - Instagram carousel 1080x1350px
- **blog-guide-template.md** - Blog featured images 16:9
- **linkedin-twitter-video-guides.md** - LinkedIn, Twitter, video guides

---

## Files Created in hexly Project

### Configuration Files (Root)
- **social-engine-guide.md** - Your niche definition
- **social-growth-strategy.md** - KPI tracking (updated daily)

### Content Structure
```
content/
├── strategy/
│   └── posting-log.md              # Post history
├── style-guides/                   # (Generated during init)
│   ├── carousel-guide.md
│   ├── blog-guide.md
│   ├── linkedin-twitter-video-guides.md
│   └── [your customized guides]
└── research/                       # Archive of research

OUTPUT/
├── {date}/{topic}/                 # Content generation
│   ├── research-summary.md
│   ├── images/
│   ├── carousel/
│   └── videos/
└── social-analytics/{date}/        # Daily metrics
    ├── metrics.json
    ├── performance-report.pdf
    └── recommendations.md

app/api/cron/
└── social-analytics/
    └── route.ts                    # Daily 7 AM cron job
```

---

## Integration with Existing Skills

The social-engine orchestrates **8+ existing skills**:

| Skill | Phase | Purpose |
|-------|-------|---------|
| viral-research | 1 | Discovers trending topics |
| deep-research:full | 3 | Deep topic research |
| blog-image-gen | 4 | Blog/social images |
| carousel-image-gen | 4 | Instagram carousels |
| short-video-gen | 4 | Short-form videos |
| humanizer | 5 | Text humanization |
| postiz | 6 | Post scheduling |
| social-analytics | 7 | Daily metrics collection |
| trend-finder | 1 | Alternative trends |

---

## The 7-Phase Pipeline

```
Phase 1: Discover Trends
    ↓ (viral-research finds 10 topics)
Phase 2: User Selects Topics
    ↓ (You pick which to develop)
Phase 3: Deep Research
    ↓ (deep-research:full researches each)
Phase 4: Create Content
    ↓ (Images, videos, carousels generated)
Phase 5: Humanize Text
    ↓ (/humanizer removes AI patterns)
Phase 6: Schedule Posts
    ↓ (postiz uploads to all platforms)
Phase 7: Daily Analytics (7 AM UTC)
    ↓ (Updates strategy for next cycle)
```

Each phase shows results and asks for approval.

---

## Daily Automation

At **7:00 AM UTC every day**, the cron job automatically:

1. **Connects to Postiz** - Retrieves metrics from all platforms
2. **Collects Data** - Impressions, engagement, reach, growth
3. **Analyzes Patterns** - What worked, what didn't
4. **Generates Recommendations** - 10 actionable improvements
5. **Updates Strategy File** - New KPIs and insights
6. **Saves Reports** - JSON metrics + PDF report

---

## Key Features

✅ **Intelligent Trend Discovery** - Multi-source search
✅ **Data-Driven Content** - Uses strategy for better targeting
✅ **Fully Humanized** - All text passes `/humanizer`
✅ **Continuous Learning** - Improves with each cycle
✅ **Multi-Platform** - Instagram, X, LinkedIn, YouTube
✅ **User Approval** - Human-in-loop at every step
✅ **Style Guides** - Consistent brand across formats
✅ **Daily Analytics** - Automatic metrics collection

---

## File Structure After Init

```
hexly/
├── 📋 Configuration Files
│   ├── social-engine-guide.md          # Your niche
│   └── social-growth-strategy.md       # KPIs (auto-updated)
│
├── 📁 Content Organization
│   └── content/
│       ├── strategy/
│       │   └── posting-log.md          # Post history
│       ├── style-guides/               # Content styles
│       │   ├── carousel-guide.md
│       │   ├── blog-guide.md
│       │   └── linkedin-twitter-video-guides.md
│       └── research/                   # Archived research
│
├── 🎨 Generated Content
│   └── OUTPUT/
│       ├── 20260306/
│       │   ├── ai-agents-replacing-saas/
│       │   │   ├── research-summary.md
│       │   │   ├── image-prompts-formatted.md
│       │   │   ├── images/
│       │   │   │   ├── featured.png
│       │   │   │   └── linkedin-hero.png
│       │   │   ├── carousel/
│       │   │   │   ├── slide1.png
│       │   │   │   └── ...slide6.png
│       │   │   └── videos/
│       │   │       └── short-form.mp4
│       │   └── [other topics]
│       └── social-analytics/           # Daily reports
│           └── 2026-03-06/
│               ├── metrics.json
│               ├── performance-report.pdf
│               └── recommendations.md
│
└── ⚙️ Backend
    └── app/api/cron/
        └── social-analytics/
            └── route.ts                # Daily 7 AM cron
```

---

## Configuration Checklist

### Before First Run
- ☐ Run `/social-engine init` OR manually complete steps below
- ☐ `social-engine-guide.md` created and customized
- ☐ `social-growth-strategy.md` initialized
- ☐ API keys in `.env.local` (POSTIZ, GEMINI, ANTHROPIC, CRON_SECRET)
- ☐ All style guides created in `content/style-guides/`
- ☐ Daily cron job configured (external service or Fly.io)
- ☐ Postiz integration IDs configured
- ☐ Run `/social-engine verify` (passes all checks)

### After First Run
- ☐ First `/viral-research` returns trending topics
- ☐ Selected topics for first cycle
- ☐ Content generates successfully
- ☐ Posts scheduled to platforms
- ☐ Cron job runs daily at 7 AM
- ☐ `social-growth-strategy.md` receives daily updates

---

## Usage Commands

### Discover Trends
```bash
/viral-research
```
Find top 10 trending topics in your niche.

### Full Pipeline
```bash
/social-engine
```
Run all 7 phases (30-60 min depending on content speed).

### Quick Research
```bash
/deep-research:full "Topic Name"
```
Research one topic without trend discovery.

### View Strategy & KPIs
```bash
cat social-growth-strategy.md
```
See daily metrics and recommendations (updated 7 AM UTC).

### View Post History
```bash
cat content/strategy/posting-log.md
```
See all scheduled posts and engagement.

### Verify Setup
```bash
/social-engine verify
```
Check all components are working.

---

## Performance Targets

### Engagement Rates
- **Instagram**: >3% (likes + comments + shares / impressions)
- **X/Twitter**: >2%
- **LinkedIn**: >1.5% CTR
- **YouTube**: >70% completion rate

### Growth Targets
- **Monthly Follower Growth**: 5-10%
- **Weekly Reach Growth**: 10-20%
- **Post Frequency**: 3-5 per week (all platforms)

### Posting Schedule
- **Instagram**: Tue-Thu, 11 AM - 1 PM
- **X/Twitter**: Mon & Wed, 9-10 AM
- **LinkedIn**: Tue-Thu, 8-10 AM
- **YouTube Shorts**: Fri-Sun

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| No trends found | Check internet, verify niche keywords |
| API key error | Verify key in `.env.local`, reload shell |
| Images not generating | Check GEMINI_API_KEY, verify quota |
| Cron not running | Test endpoint with curl, check service |
| Low engagement | Review strategy file recommendations |
| Posts not scheduling | Verify Postiz API key, check integration IDs |

See INITIALIZATION.md for detailed troubleshooting.

---

## Documentation Map

| Document | Location | Purpose |
|----------|----------|---------|
| SKILL.md | social-engine/ | Main skill documentation |
| README.md | social-engine/ | Comprehensive guide + examples |
| INITIALIZATION.md | social-engine/ | Step-by-step setup |
| viral-research SKILL.md | viral-research/ | Trend discovery details |
| carousel-guide-template.md | social-engine/templates/ | Instagram style template |
| blog-guide-template.md | social-engine/templates/ | Blog image style template |
| linkedin-twitter-video-guides.md | social-engine/templates/ | Platform-specific guides |
| This file | augmi-skills/ | Summary & overview |

---

## What Happens When You Run It

### Day 1: `/viral-research`
- System searches Google Trends, Twitter, Reddit, HackerNews
- Returns top 10 trending topics in your niche
- Scores each by virality potential
- You select 2-5 topics to develop

### Day 1-2: `/social-engine` (Full Pipeline)
- **Phase 1**: Viral trends presented
- **Phase 2**: You select topics
- **Phase 3**: Deep research on each topic
- **Phase 4**: Content created (images, videos, carousels)
- **Phase 5**: Text humanized
- **Phase 6**: Posts scheduled to platforms
- System returns to you for approval at each step

### Daily: Automatic at 7 AM UTC
- Cron job collects metrics from all platforms
- Updates `social-growth-strategy.md` with new KPIs
- Generates 10 growth recommendations
- Feeds back into viral-research for next cycle

### Weekly: Manual Review
- Review strategy file for patterns
- Adjust posting times if needed
- Plan topics for next cycle
- Document what's working

---

## Success Timeline

| Timeframe | What to Expect |
|-----------|----------------|
| **Week 1** | 5-10 posts created, first analytics |
| **Week 2-3** | 10-20 posts, engagement patterns emerging |
| **Month 1** | 20-40 posts, clear KPIs, recommendations improving |
| **Month 2-3** | 40-80 posts, engagement increasing, follower growth |
| **Month 3-6** | 80-200 posts, viral cycles, 10-15% monthly growth |

---

## Support & Help

### First Time Using?
1. Read README.md
2. Run `/social-engine init`
3. Follow interactive setup
4. Review INITIALIZATION.md if stuck

### Need Guidance?
- Check SKILL.md for detailed documentation
- Review examples in README.md
- Check `social-growth-strategy.md` for insights
- Edit `social-engine-guide.md` to adjust

### Found an Issue?
- Run `/social-engine verify` to diagnose
- Check INITIALIZATION.md troubleshooting section
- Review error messages carefully
- Contact support with: setup step, error message, logs

---

## Files Checklist

### In augmi-skills/social-engine/
- ✅ SKILL.md
- ✅ README.md
- ✅ INITIALIZATION.md
- ✅ SETUP.md (reference in hexly)
- ✅ templates/carousel-guide-template.md
- ✅ templates/blog-guide-template.md
- ✅ templates/linkedin-twitter-video-guides.md

### In augmi-skills/viral-research/
- ✅ SKILL.md

### In hexly (after init)
- ✅ social-engine-guide.md
- ✅ social-growth-strategy.md
- ✅ content/strategy/posting-log.md
- ✅ content/style-guides/* (customized copies)
- ✅ app/api/cron/social-analytics/route.ts

---

## System Architecture

```
┌─────────────────────────────────────┐
│     User Command: /social-engine    │
└────────────┬────────────────────────┘
             │
    ┌────────▼─────────┐
    │ Phase 1: Trends  │ ← viral-research discovers 10 topics
    └────────┬─────────┘
             │ (user selects topics)
    ┌────────▼──────────┐
    │ Phase 2: Research │ ← deep-research:full (parallel)
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │ Phase 3: Content  │ ← blog-image-gen, carousel-image-gen, short-video-gen
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │ Phase 4: Humanize │ ← /humanizer (removes AI patterns)
    └────────┬──────────┘
             │
    ┌────────▼────────┐
    │ Phase 5: Post   │ ← postiz (schedules to platforms)
    └────────┬────────┘
             │
             └─────────────────────────────────────┐
                                                   │
    ┌─────────────────────────────────────────────▼──────┐
    │ Phase 6: Daily Analytics (7 AM UTC - Automated)   │
    │ - Collects metrics from all platforms             │
    │ - Updates social-growth-strategy.md               │
    │ - Generates 10 recommendations                     │
    │ - Feeds back to viral-research for next cycle     │
    └──────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Initialize**: `/social-engine init` (30-45 min)
2. **Configure**: Set up API keys, style guides, cron
3. **Test**: Run `/viral-research` (10 min)
4. **Create**: Run `/social-engine` for first posts
5. **Monitor**: Review daily at 7 AM in `social-growth-strategy.md`
6. **Iterate**: Let recommendations guide next cycle

---

## Version & Maintenance

**Version**: 1.0
**Created**: 2026-03-06
**Status**: ✅ Production Ready
**Maintained By**: @konradgnat
**Location**: `augmi-skills/social-engine/` + `augmi-skills/viral-research/`

---

🚀 **You're ready to launch your automated social media empire!**

Start with:
```bash
/social-engine init
```

Then:
```bash
/viral-research
```

Happy creating! 📱🎨✨
