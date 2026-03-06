# Social Engine - Complete Social Media Automation System

🚀 **Full-stack automated social media content pipeline** from trend discovery to daily analytics and continuous improvement.

## What Is This?

Social Engine is an end-to-end orchestration system that:

1. **Discovers** what's trending in your niche
2. **Researches** topics deeply
3. **Creates** multi-format content (images, videos, carousels)
4. **Humanizes** all text for authentic voice
5. **Schedules** posts across platforms
6. **Analyzes** performance daily
7. **Learns** to improve future content

All with **human approval at every step** and **continuous learning from analytics**.

---

## Quick Start (5 Minutes)

### 1. Initialize Social Engine
```bash
/social-engine init
```

This interactive setup will:
- Define your niche
- Create all required directories
- Generate style guides for each content type
- Configure API keys
- Set up daily cron job
- Verify everything works

### 2. Start First Cycle
```bash
/social-engine
```

### 3. Monitor Daily
Check daily updates in `social-growth-strategy.md` (updated 7 AM UTC)

---

## File Structure

After initialization, your project will have:

```
hexly/
├── 📋 social-engine-guide.md              # Your niche definition
├── 📊 social-growth-strategy.md           # KPIs (auto-updated daily)
│
├── content/
│   ├── strategy/
│   │   └── posting-log.md                 # Post history + metrics
│   ├── style-guides/
│   │   ├── carousel-guide.md              # Instagram carousel style
│   │   ├── blog-guide.md                  # Blog image style
│   │   ├── linkedin-guide.md              # LinkedIn style
│   │   ├── twitter-guide.md               # Twitter thread style
│   │   └── video-guide.md                 # Short-form video style
│   └── research/
│       └── [archived research from cycles]
│
├── OUTPUT/
│   ├── 20260306/
│   │   ├── ai-agents-replacing-saas/
│   │   │   ├── research-summary.md
│   │   │   ├── image-prompts-formatted.md
│   │   │   ├── images/
│   │   │   │   ├── featured.png
│   │   │   │   └── linkedin-hero.png
│   │   │   ├── carousel/
│   │   │   │   ├── slide1.png
│   │   │   │   └── ...slide6.png
│   │   │   └── videos/
│   │   │       └── short-form.mp4
│   │   └── [other topics]
│   └── social-analytics/
│       └── 2026-03-06/
│           ├── metrics.json
│           ├── performance-report.pdf
│           └── recommendations.md
│
└── app/api/cron/
    └── social-analytics/
        └── route.ts                       # Daily 7 AM cron job
```

---

## The 7-Phase Pipeline

```
Phase 1: Discover Trends (viral-research)
    ↓
Phase 2: User Selects Topics
    ↓
Phase 3: Deep Research (deep-research:full)
    ↓
Phase 4: Create Content (images, videos, carousels)
    ↓
Phase 5: Humanize Text (humanizer)
    ↓
Phase 6: Schedule Posts (postiz)
    ↓
Phase 7: Daily Analytics (7 AM cron) → Updates strategy → Improve next cycle
```

Each phase shows you results and asks for approval before proceeding.

---

## Skills Included

The social-engine integrates with **8+ existing skills**:

| Skill | Purpose | Phase |
|-------|---------|-------|
| **viral-research** | Discovers trending topics | 1 |
| **deep-research:full** | Researches topics deeply | 3 |
| **blog-image-gen** | Generates blog/social images | 4 |
| **carousel-image-gen** | Creates Instagram carousels | 4 |
| **short-video-gen** | Creates short-form videos | 4 |
| **humanizer** | Removes AI patterns | 5 |
| **postiz** | Schedules posts | 6 |
| **social-analytics** | Collects daily metrics | 7 |
| **trend-finder** | Alternative trend source | 1 |

All are orchestrated automatically by social-engine.

---

## Initialization & Setup

### Step 1: Run Init
```bash
/social-engine init
```

This is interactive. You'll answer questions about:

**Niche Definition**
- Primary niche (e.g., "AI Agents, OpenClaw, Claude Code")
- Subtopics
- Target platforms (Instagram, X, LinkedIn, YouTube)

**Directory Configuration**
- Output location (default: `OUTPUT/`)
- Research archive location
- Analytics storage location
- Style guides location

**Style Guides Creation**
- Carousel guide (Instagram 1080x1350px)
- Blog guide (featured images)
- LinkedIn guide (professional 1:1)
- Twitter guide (thread format)
- Video guide (9:16 vertical)

**API Configuration**
- POSTIZ_API_KEY
- GEMINI_API_KEY
- ANTHROPIC_API_KEY
- CRON_SECRET

**Cron Setup**
- Daily analytics collection
- Time: 7:00 AM UTC (customizable)
- Service: External (EasyCron) or Fly.io

### Step 2: Verify Installation
```bash
/social-engine verify
```

Checks:
- ✅ All directories created
- ✅ All style guides generated
- ✅ API keys configured
- ✅ Cron job set up
- ✅ All skills available

---

## Configuration Files

### social-engine-guide.md
Defines your niche and content strategy:

```markdown
# Social Engine Guide

## Niche Definition
**Primary**: AI Agents, OpenClaw, Claude Code
**Subtopics**:
- AI agent deployment
- OpenClaw architecture
- Claude Code integration
- Agent automation workflows
- Crypto-native agents

## Target Platforms
- Instagram (carousel + Reels)
- X/Twitter (threads + videos)
- LinkedIn (articles + images)
- YouTube (shorts)

## Content Quality Standards
- Engagement Target: >3% on Instagram, >2% on X
- Posting Frequency: 3-5 posts/week
- Humanization Required: Yes
- Brand Voice: Educational, authentic, enthusiastic
```

### social-growth-strategy.md
Tracks KPIs and receives daily analytics updates:

```markdown
# Social Growth Strategy

## Current Period Metrics
| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Instagram Engagement | >3% | 2.8% | ↗️ |
| X Engagement | >2% | 1.9% | ↗️ |
| LinkedIn CTR | >1.5% | 1.2% | → |
| YouTube Completion | >70% | 72% | ↑ |

## Content Performance Analysis
- High performers: [topics with >3% engagement]
- Medium performers: [1-3% engagement]
- Low performers: [<1% engagement]

## Growth Recommendations (Updated Daily at 7 AM)
1. Focus on [high-engagement platform]
2. Test [new content format]
3. Increase [proven content type]
... (10 recommendations)
```

### Style Guides
Each content type has a dedicated guide:

- **carousel-guide.md** - 1080x1350px, 6 slides, sci-fi aesthetic
- **blog-guide.md** - Featured images, visual hierarchy
- **linkedin-guide.md** - Professional, 1:1 square, subtle design
- **twitter-guide.md** - Minimal, text-forward, bold typography
- **video-guide.md** - 9:16 vertical, captions, fast-paced edits

All reference:
- Shared color palette
- Typography
- Brand tone
- Visual hierarchy

---

## Usage Patterns

### Full Pipeline (Recommended)
```bash
/social-engine
```
Runs all 7 phases with your approval at each step.

**Time**: ~2-3 hours (mostly waiting for content generation)
**Effort**: ~30 minutes of active decisions
**Output**: 3-5 complete posts ready to schedule

---

### Just Discover Trends
```bash
/viral-research
```
Find trending topics without creating content yet.

**Time**: 10 minutes
**Output**: Top 10 trending topics

---

### Research a Specific Topic
```bash
/deep-research:full "Topic Name"
```
Research one topic without trend discovery.

**Time**: 20-30 minutes
**Output**: Research summary + image prompts

---

### View Strategy & Analytics
```bash
cat social-growth-strategy.md
```
See daily KPIs, engagement metrics, and recommendations.

**Updated**: 7:00 AM UTC automatically

---

### View Post History
```bash
cat content/strategy/posting-log.md
```
See all scheduled posts, engagement metrics, and notes.

---

## Continuous Learning

The system improves with every cycle:

```
Week 1: Initial topics (generic)
  ↓
Week 2: Analytics show high-engagement topics
  ↓
Week 3: Viral-research prioritizes similar topics
  ↓
Week 4: Engagement increases (better targeting)
  ↓
Week 5: Even better topics discovered
  ↓
Repeat...
```

The strategy file guides each subsequent cycle.

---

## Platform-Specific Guidelines

### Instagram
- **Format**: Carousel (6 slides) + Reels
- **Dimensions**: 1080x1350px (4:5 portrait)
- **Captions**: 2200 characters max, emojis, hashtags
- **Hashtags**: 30 max, 5-10 relevant
- **Best Time**: Tuesday-Thursday 11 AM - 1 PM
- **Engagement**: Target >3% (likes + comments)

### X/Twitter
- **Format**: Threads (5-10 tweets) + Videos
- **Dimensions**: 1200x675px (videos in tweets)
- **Length**: Threads, 280 chars per tweet
- **Hashtags**: 2-3 per thread
- **Best Time**: Monday, Wednesday 9-10 AM
- **Engagement**: Target >2% (retweets + replies)

### LinkedIn
- **Format**: Article + Image
- **Dimensions**: 1200x628px (image), 1:1 optional
- **Length**: 300-1000 words for articles
- **Tone**: Professional, thought leadership
- **Best Time**: Tuesday-Thursday 8-10 AM
- **Engagement**: Target 100+ reactions per week

### YouTube
- **Format**: Shorts (vertical video)
- **Dimensions**: 1080x1920px (9:16 vertical)
- **Length**: 30-60 seconds
- **Captions**: Burned-in + auto
- **Best Time**: Friday-Sunday
- **Engagement**: Target >70% completion rate

---

## Daily Automation

At **7:00 AM UTC every day**, the cron job automatically:

1. **Connects to Postiz** - Retrieves metrics from all platforms
2. **Collects Metrics**:
   - Impressions, reach, clicks
   - Engagement (likes, comments, shares)
   - Completion rates (videos)
   - Follower growth
3. **Analyzes Patterns**:
   - Which topics performed best
   - Which platforms drive engagement
   - Best posting times
   - Content format effectiveness
4. **Generates Recommendations** - 10 actionable improvements
5. **Updates Strategy File**:
   - New KPI metrics
   - Performance analysis
   - Growth recommendations
6. **Saves Reports**:
   - JSON metrics: `OUTPUT/social-analytics/{date}/metrics.json`
   - PDF report: `OUTPUT/social-analytics/{date}/performance-report.pdf`

This feeds back into viral-research for the next cycle.

---

## Performance Tracking

**Automatically tracked and saved daily**:

| Metric | Definition | Platform |
|--------|-----------|----------|
| Engagement Rate | (Likes + Comments + Shares) / Impressions | All |
| Reach | Unique viewers | All |
| Impressions | Total views | All |
| Click-Through Rate | Clicks / Impressions | X, LinkedIn |
| Video Completion Rate | Watched to end / Total watch time | YouTube |
| Follower Growth | New followers per period | All |
| Conversion Rate | Content views → Signup/Link click | All |

All saved to `social-growth-strategy.md`.

---

## Troubleshooting

### Initialization Issues

**"POSTIZ_API_KEY not found"**
- Make sure you have a Postiz account
- Generate API key at postiz.com/settings/api
- Add to `.env.local`

**"Cron job failed to set up"**
- If using external service (EasyCrom, cron-job.org):
  - Verify URL is `https://augmi.world/api/cron/social-analytics`
  - Check CRON_SECRET matches `.env.local`
- If using Fly.io:
  - Add cron config to `fly.toml`
  - Deploy with `fly deploy`

### Content Generation Issues

**"Images not generating"**
- Verify GEMINI_API_KEY is set and valid
- Check API quota at console.cloud.google.com
- Try again (might be temporary service issue)

**"Videos failing"**
- Check available disk space
- Verify ANTHROPIC_API_KEY is valid
- Try with shorter topic name or simpler prompt

**"Posts not scheduling"**
- Verify media uploaded successfully to Postiz
- Check Postiz integration IDs are correct
- Test Postiz credentials: `postiz auth:test`

### Analytics Issues

**"Cron job not running"**
- Verify external cron service shows "Success"
- Check error logs at cron service
- Test manually: `curl -X POST https://augmi.world/api/cron/social-analytics -H "Authorization: Bearer $CRON_SECRET"`

**"Low engagement on posts"**
- Review recommendations in `social-growth-strategy.md`
- Check if niche keywords match your audience
- A/B test different posting times
- Vary content format (carousel vs video vs image)

### General Help

**Review these files**:
- `.claude/skills/social-engine/SKILL.md` - Detailed pipeline
- `.claude/skills/viral-research/SKILL.md` - Trend discovery
- `social-engine-guide.md` - Your niche config
- `social-growth-strategy.md` - Daily KPIs

**Run verification**:
```bash
/social-engine verify
```

**Check logs**:
```bash
tail -f OUTPUT/social-analytics/{latest-date}/metrics.json
```

---

## Best Practices

### Planning
- Run viral-research 1-2x per week
- Select 2-5 topics per cycle
- Batch content for efficiency

### Creation
- Always humanize text with `/humanizer`
- Review images/videos before scheduling
- Test captions on all platforms

### Posting
- Never post without approval (wait for your confirmation)
- Space posts 2-3 days apart for reach
- Cross-promote across platforms

### Optimization
- Review strategy file daily
- Follow recommendations from analytics
- Document what works, what doesn't
- Adjust posting times based on engagement

### Maintenance
- Update `social-engine-guide.md` quarterly
- Archive old research to `content/research/`
- Review and update style guides as brand evolves
- Rotate between content types for variety

---

## Integration with Your Workflow

### With Hexly (Augmi Dashboard)
- Social Engine creates content
- Augmi platform hosts the dashboard
- Monitor agent performance alongside content metrics

### With Augmi Skills
- Uses all existing skills automatically
- No manual orchestration needed
- Parallel processing where possible

### With Your Calendar
- Content scheduled via Postiz
- Analytics update daily at 7 AM
- Recommendations available every morning

---

## Advanced Configuration

### Custom Cron Time
Edit `/api/cron/social-analytics/route.ts`:
```typescript
// Change from 7 AM UTC to your preferred time
const scheduleTime = process.env.ANALYTICS_CRON_TIME || '07:00';
```

### Custom Style Guides
Edit style guide files in `content/style-guides/`:
- Adjust colors, fonts, layouts
- All guides reference shared palette
- Changes apply to next content cycle

### Multi-Niche Setup
Create separate instances:
```bash
/social-engine init --niche "niche-1"
/social-engine init --niche "niche-2"
```

Each has own config, style guides, strategy file.

---

## File Locations Reference

| File | Purpose | Location |
|------|---------|----------|
| SKILL.md | Main documentation | `.claude/skills/social-engine/SKILL.md` |
| README.md | This file | `.claude/skills/social-engine/README.md` |
| viral-research SKILL.md | Trend discovery | `.claude/skills/viral-research/SKILL.md` |
| Niche config | Your niche definition | `social-engine-guide.md` |
| KPI tracking | Daily metrics | `social-growth-strategy.md` |
| Post history | Scheduling log | `content/strategy/posting-log.md` |
| Style guides | Content styles | `content/style-guides/` |
| Research | Archived research | `content/research/` |
| Content output | Generated files | `OUTPUT/{date}/{slug}/` |
| Analytics | Daily metrics | `OUTPUT/social-analytics/{date}/` |
| Cron endpoint | Daily automation | `app/api/cron/social-analytics/route.ts` |

---

## Success Metrics

**After 1 Week**:
- ✅ 5-10 pieces of content created
- ✅ All platforms have posts
- ✅ First analytics data collected

**After 1 Month**:
- ✅ 20-40 posts published
- ✅ Clear engagement patterns emerging
- ✅ Recommendations improving topic selection

**After 3 Months**:
- ✅ 60-120 posts published
- ✅ Engagement increasing month-over-month
- ✅ Strong follower growth
- ✅ Clear content-performance patterns

**After 6 Months**:
- ✅ Highly optimized posting schedule
- ✅ Consistent 3-5% engagement
- ✅ Viral cycles emerging (some posts >10% engagement)
- ✅ Audience growing 10-15% monthly

---

## Support & Questions

**First Time?**
- Run `/social-engine init` (interactive setup)
- Review this README
- Run `/social-engine verify` to check setup

**Need Help?**
- Check SKILL.md for pipeline details
- Review viral-research SKILL.md for trend discovery
- Look at `social-growth-strategy.md` for performance insights
- Edit `social-engine-guide.md` to adjust niche

**Found a Bug?**
- Check GitHub issues in augmi-skills repo
- File new issue with: setup, steps to reproduce, error message

---

## Roadmap

**Q2 2026**:
- [ ] Automated A/B testing
- [ ] Competitor monitoring
- [ ] Audience sentiment tracking
- [ ] Real-time trend alerts

**Q3 2026**:
- [ ] Multi-account management
- [ ] Budget optimization for ads
- [ ] Custom reporting dashboard
- [ ] Influencer collaboration suggestions

**Q4 2026**:
- [ ] Community sentiment analysis
- [ ] Revenue impact tracking
- [ ] AI-powered copy variations
- [ ] Seasonal trend forecasting

---

## Glossary

- **Viral Score** - 0-100 rating of how trending a topic is
- **Engagement Rate** - (Likes + Comments + Shares) / Impressions
- **Reach** - Number of unique users who see content
- **Trending** - Rapidly increasing search interest or social discussion
- **Content Cycle** - One full run of the 7-phase pipeline
- **Strategy File** - `social-growth-strategy.md` (updated daily)
- **Style Guide** - Content format specifications (carousel, blog, etc.)

---

## Credits

**Created**: 2026-03-06
**Maintained By**: @konradgnat
**Part of**: Augmi Social Media Suite

---

🚀 **Ready to automate your social media?**

**Start here**:
```bash
/social-engine init
```

Then:
```bash
/social-engine
```

Your first trend discovery cycle starts in 10 minutes.

Good luck! 📈✨
