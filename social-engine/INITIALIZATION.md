# Social Engine - Initialization Guide

**Version**: 2.0
**Date**: 2026-03-15
**Estimated Time**: 15-30 minutes

Everything the social engine needs — paths, API keys, platform IDs, schedules — lives in a single config file:

```
.claude/skills/social-content-engine/config.json
```

Running `/social-content-engine init` collects all required information and writes it there. Once the config exists, every skill reads from it automatically.

---

## Config-First Approach

Instead of scattered markdown files with hardcoded paths, one JSON config drives the entire system:

- Skills read paths from config (no hardcoded locations)
- Platform IDs live in config (easy to swap accounts)
- Automation tier is set in config (manual, semi-auto, or full-auto)
- Init validates everything before writing

---

## Step 1: Gather Required Information

Collect this before running init.

### Brand Info

| Field | Description | Example |
|-------|-------------|---------|
| `brand.name` | Project or brand name | "Acme AI" |
| `brand.domain` | Primary domain | "acme.ai" |
| `brand.handles.twitter` | Twitter/X handle | "@acmeai" |
| `brand.handles.instagram` | Instagram handle | "@acmeai" |
| `brand.handles.tiktok` | TikTok handle | "@acmeai" |
| `brand.handles.youtube` | YouTube channel handle | "@acmeai" |
| `brand.handles.linkedin` | LinkedIn company slug | "acme-ai" |

### Niche

| Field | Description | Example |
|-------|-------------|---------|
| `niche.keywords` | 3-5 primary niche keywords | ["AI agents", "automation", "no-code"] |
| `niche.subtopics` | 3-5 content subtopics | ["agent deployment", "LLM workflows", "AI tools"] |
| `niche.audience` | Target audience description | "indie hackers and founders building with AI" |

### File Paths: Strategy and Style Guides

These files define your content identity and rules. Provide the path relative to your project root.

| Config Key | Purpose | Typical Path |
|------------|---------|--------------|
| `paths.contentThesis` | Viral principles, what makes content shareable | `content/strategy/content-thesis.md` |
| `paths.styleGuide` | Hook templates, emotion targeting, brand voice | `content/strategy/content-style-guide.md` |
| `paths.contentGrades` | Quality scoring history, A/B test results | `content/strategy/content-grades.md` |
| `paths.postingLog` | Post history with engagement data | `content/strategy/posting-log.md` |
| `paths.postingSchedule` | When to post per platform | `content/strategy/posting-schedule.md` |
| `paths.conversionPlaybook` | Follower-to-customer conversion tactics | `content/strategy/follower-conversion-playbook.md` |
| `paths.analyticsStrategy` | KPIs, growth recommendations (updated daily) | `data/social-analytics/viral-growth-strategy.md` |
| `paths.businessThesis` | Growth thesis, revenue pipeline | `content/strategy/business-thesis.md` |
| `paths.brandFoundation` | Mission, value prop, brand pillars | `docs/brand/` |
| `paths.trendResearch` | Trend research directory | `content/research/` |

### File Paths: Data and Output

| Config Key | Purpose | Typical Path |
|------------|---------|--------------|
| `paths.analyticsData` | Aggregated metrics, raw data, reports | `data/social-analytics/` |
| `paths.contentOutput` | Generated content (images, videos, copy) | `OUTPUT/` |
| `paths.selfImprovementOutput` | Self-improvement loop results | `OUTPUT/self-improvement/` |
| `paths.templates` | Reusable templates directory | `content/templates/` |

### API Keys

Store these in your `.env.local` file. Never commit them.

| Variable | Required | Purpose |
|----------|----------|---------|
| `POSTIZ_API_KEY` | Required | Scheduling and publishing posts |
| `GEMINI_API_KEY` | Required | Image generation |
| `ANTHROPIC_API_KEY` | Required | Content generation (Claude) |
| `CRON_SECRET` | Required | Authenticating cron job endpoints (min 32 chars) |
| `TWITTERAPI_IO_KEY` | Optional | Enhanced Twitter analytics |
| `FAL_KEY` | Optional | Video generation via fal.ai |
| `DEEPGRAM_API_KEY` | Optional | Voice synthesis for video |

### Platform Config

| Config Key | Description | Example |
|------------|-------------|---------|
| `platforms.twitter.enabled` | Enable Twitter/X | `true` |
| `platforms.twitter.defaultFormat` | Default content format | `"thread"` |
| `platforms.twitter.postsPerWeek` | Posting frequency | `5` |
| `platforms.twitter.postizId` | Postiz integration ID | `"cmlrob0gp05g7mn0yncmwzg7c"` |
| `platforms.instagram.enabled` | Enable Instagram | `true` |
| `platforms.instagram.defaultFormat` | Default format | `"carousel"` |
| `platforms.instagram.postsPerWeek` | Posting frequency | `3` |
| `platforms.instagram.postizId` | Postiz integration ID | `"cmlre90pk04d9mn0yosyhnx4o"` |
| `platforms.linkedin.enabled` | Enable LinkedIn | `true` |
| `platforms.linkedin.defaultFormat` | Default format | `"image"` |
| `platforms.linkedin.postsPerWeek` | Posting frequency | `3` |
| `platforms.linkedin.postizId` | Postiz integration ID | `"cmlrecv0r04dimn0yl34lxmzx"` |
| `platforms.youtube.enabled` | Enable YouTube | `false` |
| `platforms.youtube.defaultFormat` | Default format | `"short"` |
| `platforms.youtube.postsPerWeek` | Posting frequency | `2` |
| `platforms.youtube.postizId` | Postiz integration ID | `"cmlreb5vl04dcmn0yu3ej283a"` |

**Getting Postiz integration IDs:**
1. Log in at [postiz.com](https://postiz.com)
2. Go to Integrations
3. Copy the ID for each connected platform

### Cron Jobs

| Config Key | Description | Example |
|------------|-------------|---------|
| `cron.analyticsSchedule` | When daily analytics runs (cron expression) | `"0 7 * * *"` (7 AM UTC) |
| `cron.analyticsEndpoint` | Full URL for analytics cron | `"https://yourdomain.com/api/cron/social-analytics"` |
| `cron.selfImprovementFrequency` | How often self-improvement loop runs | `"3x-daily"` |
| `cron.automationTier` | Automation level (see below) | `"semi-auto"` |

---

## Step 2: Run Init

```bash
/social-content-engine init
```

The init process will:
1. Ask for each piece of information listed above
2. Validate that required paths exist (or offer to create them)
3. Verify API keys are present in the environment
4. Write `.claude/skills/social-content-engine/config.json`
5. Run a verification pass and report any issues

---

## Step 3: Choose Your Automation Tier

Set `cron.automationTier` in config to one of:

### Manual
- User runs each command individually
- No cron jobs required
- Full control over every step
- Best for: getting started, low-volume accounts

```
/viral-research → select topics → /deep-research → /social-engine → review → /postiz
```

### Semi-Auto (Recommended)
- Daily analytics cron runs automatically at configured time
- Content creation is user-initiated
- User approves all content before posting
- Best for: active creators who want data without full automation

Cron required: `analyticsEndpoint` hit daily via external cron service.

### Full-Auto
- Daily analytics cron runs automatically
- Self-improvement loop runs 3x daily, refining strategy
- Content pipeline runs on schedule
- User still approves before posts go live (final gate)
- Best for: established accounts with proven content strategy

Cron required: analytics endpoint + self-improvement endpoint.

---

## Step 4: Verify

After init completes, run:

```bash
/social-content-engine verify
```

Verification checks:
- Config file exists and is valid JSON
- All required paths are defined
- Required API keys present in environment
- Postiz integration IDs are non-empty for enabled platforms
- Cron endpoint URL is reachable (if configured)
- Strategy and style guide files exist at configured paths

---

## Example config.json

This is a generic example. Replace all values with your own.

```json
{
  "version": "2.0",
  "brand": {
    "name": "Acme AI",
    "domain": "acme.ai",
    "handles": {
      "twitter": "@acmeai",
      "instagram": "@acmeai",
      "tiktok": "@acmeai",
      "youtube": "@acmeai",
      "linkedin": "acme-ai"
    }
  },
  "niche": {
    "keywords": ["AI agents", "automation", "no-code tools"],
    "subtopics": [
      "agent deployment",
      "LLM workflows",
      "AI productivity",
      "no-code automation",
      "indie hacking with AI"
    ],
    "audience": "indie hackers and founders building with AI"
  },
  "paths": {
    "contentThesis": "content/strategy/content-thesis.md",
    "styleGuide": "content/strategy/content-style-guide.md",
    "contentGrades": "content/strategy/content-grades.md",
    "postingLog": "content/strategy/posting-log.md",
    "postingSchedule": "content/strategy/posting-schedule.md",
    "conversionPlaybook": "content/strategy/follower-conversion-playbook.md",
    "analyticsStrategy": "data/social-analytics/viral-growth-strategy.md",
    "businessThesis": "content/strategy/business-thesis.md",
    "brandFoundation": "docs/brand/",
    "trendResearch": "content/research/",
    "analyticsData": "data/social-analytics/",
    "contentOutput": "OUTPUT/",
    "selfImprovementOutput": "OUTPUT/self-improvement/",
    "templates": "content/templates/"
  },
  "platforms": {
    "twitter": {
      "enabled": true,
      "defaultFormat": "thread",
      "postsPerWeek": 5,
      "postizId": ""
    },
    "instagram": {
      "enabled": true,
      "defaultFormat": "carousel",
      "postsPerWeek": 3,
      "postizId": ""
    },
    "linkedin": {
      "enabled": true,
      "defaultFormat": "image",
      "postsPerWeek": 3,
      "postizId": ""
    },
    "youtube": {
      "enabled": false,
      "defaultFormat": "short",
      "postsPerWeek": 2,
      "postizId": ""
    },
    "tiktok": {
      "enabled": false,
      "defaultFormat": "short",
      "postsPerWeek": 3,
      "postizId": ""
    }
  },
  "cron": {
    "analyticsSchedule": "0 7 * * *",
    "analyticsEndpoint": "https://yourdomain.com/api/cron/social-analytics",
    "selfImprovementFrequency": "3x-daily",
    "automationTier": "semi-auto"
  }
}
```

---

## Troubleshooting Init

**"Config path not found"**
The init process can create missing directories. Answer `yes` when prompted, or create them manually before running init.

**"API key not found in environment"**
Add the key to `.env.local` in your project root, then re-run init. Never commit `.env.local`.

**"Postiz integration ID is empty"**
Log in to [postiz.com](https://postiz.com), connect your social accounts, then copy the integration IDs from the Integrations page.

**"Cron endpoint unreachable"**
This is a warning, not a blocker. The endpoint won't exist until you deploy. Skip verification on that check for now.

---

## After Init

Start with trend discovery:

```bash
/viral-research
```

Then run the full pipeline:

```bash
/social-content-engine
```

For detailed pipeline documentation, see `SKILL.md`.
