---
name: social-content-engine
user-invocable: true
description: >
  Self-improving content engine: grades recent content quality, analyzes performance
  data from social-analytics, researches viral trends, proposes improvements to
  content thesis and style guides, and applies refinements. Includes full
  trend-to-content pipeline with video production via ai-film-maker and
  short-form-video-ai skills. Run 3x daily via /loop 8h or manually.
  Triggers on "social content", "content engine", "improve content",
  "self improve", "content loop", "grade content", "refine strategy".
allowed-tools: Bash, Read, Write, Edit, WebSearch, WebFetch, Task, Agent, Glob, Grep
---

# Social Content Engine — Self-Improving Content System

Self-improving content engine that grades content, analyzes performance, researches trends, and refines strategy files automatically. Designed to run 3x daily as a loop.

Also includes the full trend-to-content pipeline for creating platform-adapted content (text, images, and video).

---

## Configuration & Setup

### Required Skills (Dependencies)

This skill orchestrates several other skills. Ensure these are installed in `.claude/skills/`:

| Skill | Purpose | Required For |
|-------|---------|-------------|
| **social-analytics** | Collects metrics from all platforms, generates reports | Performance data for grading & analysis |
| **ai-film-maker** | Creates 30-second AI short films from concepts | Video content for social posts |
| **short-form-video-ai** | Generates 30-60s vertical videos with captions | YouTube Shorts, Reels, TikTok content |
| **trend-finder** | Google Trends discovery | Phase 1: DISCOVER |
| **blog-image-gen** | Generates images via Gemini Imagen | Phase 5: IMAGES |
| **carousel-image-gen** | Generates branded Instagram carousel images | Instagram carousel posts |
| **humanizer** | Removes AI writing patterns | **MUST run before posting** to any platform |
| **postiz** | Schedules and publishes social posts | Publishing to all platforms |

### Required API Keys (in `.env.local`)

| Key | Purpose | Required For |
|-----|---------|-------------|
| `POSTIZ_API_KEY` | Postiz social scheduling API | Publishing posts, analytics collection |
| `TWITTERAPI_IO_KEY` | TwitterAPI.io ($0.15/1K tweets) | X/Twitter analytics & trend research |
| `GEMINI_API_KEY` | Google AI (Imagen, Gemini Vision) | Image generation, video scene creation |
| `FAL_KEY` | Fal.ai API | Video generation (Kling), background music (Lyria2) |
| `DEEPGRAM_API_KEY` | Deepgram TTS | Voice narration for short-form videos |

### Required CLI Tools

```bash
# Social analytics & posting
npm install -g postiz puppeteer

# Image generation
pip3 install google-genai pillow requests --break-system-packages

# Video production (for ai-film-maker / short-form-video-ai)
pip3 install fal-client --break-system-packages
brew install ffmpeg  # Required for video composition
```

### Data Sources (from social-analytics skill)

The self-improvement loop reads real metrics from these files. Run `/social-analytics` first to populate them:

| File | Content | Updated By |
|------|---------|-----------|
| `data/social-analytics/aggregated/followers.json` | Follower time-series per platform | social-analytics collect |
| `data/social-analytics/aggregated/all-metrics.json` | All engagement metrics history | social-analytics collect |
| `data/social-analytics/viral-growth-strategy.md` | KPIs, platform performance, recommendations | social-analytics + this skill |
| `data/social-analytics/business-thesis.md` | Growth thesis, content principles, 30-day targets | social-analytics + this skill |
| `data/social-analytics/reports/YYYY-MM-DD-daily.md` | Daily analytics report | social-analytics report |
| `data/social-analytics/reports/YYYY-MM-DD-comprehensive.pdf` | Branded PDF with charts | social-analytics report |

### Analytics Report Style Guide

For PDF report branding, colors, chart specs, and logo usage, see:
`.claude/skills/social-analytics/analytics-report-style-guide.md`

### Strategy & Content Files (read/written by this skill)

| File | Purpose |
|------|---------|
| `content/strategy/content-thesis.md` | Viral growth thesis, content principles, trend radar |
| `content/strategy/content-grades.md` | Content quality grades history |
| `content/strategy/posting-log.md` | Post IDs, timestamps, platforms (update after every post) |
| `content/strategy/twitter-viral-strategy.md` | X/Twitter-specific style guide |
| `social-engine-guide.md` | Business model, niche definition, audience profile |
| `content/strategy/viral-growth-week1/strategy.md` | Campaign strategy (if exists) |
| `content/strategy/trend-research/` | Scouted trends (PROPOSED → SELECTED → RESEARCHED → PUBLISHED) |

### Platform Accounts

| Platform | Handle | Analytics Source |
|----------|--------|-----------------|
| Instagram | @augmiworld | Postiz API |
| X/Twitter | @augmidotworld | TwitterAPI.io |
| TikTok | @augmidotworld | Postiz API |
| YouTube | @augmiworld | Postiz API |
| LinkedIn Page | Augmi.world | Postiz API |
| LinkedIn Personal | Konrad Gnat | Postiz API (post-level backfill) |

### Content Production Capabilities

| Content Type | Skill Used | Output Format |
|-------------|-----------|---------------|
| Blog post (800-1200 words) | This skill (templates) | Markdown |
| Twitter/X thread (5-10 tweets) | This skill (templates) | Markdown |
| Instagram carousel (7-10 slides) | carousel-image-gen | Markdown + PNG images |
| LinkedIn post (150-300 words) | This skill (templates) | Markdown |
| Short-form video (30-60s) | short-form-video-ai | MP4 with captions |
| AI short film (30s) | ai-film-maker | MP4 with narration + music |
| Static images | blog-image-gen | PNG via Gemini Imagen |

### Video Production Quick Reference

**Short-form video (Reels/Shorts/TikTok):**
```bash
# 1. Create script.json with narration text + scene descriptions
# 2. Generate via short-form-video-ai skill:
#    - 6 AI images (Gemini Imagen 4, 9:16)
#    - Image-to-video (Fal.ai Kling, 5s/scene)
#    - TTS narration (Deepgram, female voice)
#    - Word-synced captions (cyan highlight, 70px)
#    - Background music (Fal.ai Lyria2)
```

**AI short film (cinematic 30s):**
```bash
# 1. Provide concept or seed image
# 2. ai-film-maker handles:
#    - Story development (5 scenes)
#    - Image generation (Fal.ai / Google / Together)
#    - Video generation (Fal.ai Kling)
#    - Narration + music
#    - Final composition
```

---

## DEFAULT ACTION: Self-Improvement Loop

When `/social-content-engine` is invoked without flags, run the **Self-Improvement Loop** (not the full pipeline). To run the full pipeline, use `/social-content-engine --full-pipeline`.

To run automatically 3x daily:
```
/loop 8h /social-content-engine
```

---

## Self-Improvement Loop (7 Steps)

### Step 1: GATHER — Read All Strategy Data

Read these files to understand current state:

```
# Analytics data (from social-analytics skill — run /social-analytics first if stale)
data/social-analytics/viral-growth-strategy.md     # Platform KPIs, recommendations, what's working/not
data/social-analytics/business-thesis.md           # Growth thesis, 30-day targets, revenue pipeline
data/social-analytics/aggregated/followers.json    # Follower time-series (source of truth)
data/social-analytics/aggregated/all-metrics.json  # All engagement metrics history

# Strategy & content files
content/strategy/content-thesis.md                 # Current viral growth thesis & principles
content/strategy/content-grades.md                 # Grade history & trends
content/strategy/posting-log.md                    # Recent posts & engagement data
content/strategy/twitter-viral-strategy.md         # X/Twitter style guide
social-engine-guide.md                             # Business model & niche definition
content/strategy/viral-growth-week1/strategy.md    # Campaign strategy (if exists)
```

Also check for recent analytics output and previous trend scouting:
```
data/social-analytics/reports/                     # Daily analytics reports (markdown + PDF)
content/strategy/trend-research/                   # Scouted trends (proposed topics)
```

**Trend research folder** (`content/strategy/trend-research/`):
- Each file is `YYYY-MM-DD-trends.md` with scored topics
- Statuses: PROPOSED → SELECTED → RESEARCHED → PUBLISHED
- Always save new trend scouts here before proceeding

### Step 2: GRADE — Score Recent Content

For each post in `posting-log.md` from the last 7 days that hasn't been graded yet:

**Grade on 7 dimensions (1-10 scale):**

| Dimension | Weight | What to Evaluate |
|-----------|--------|-----------------|
| Hook Quality | 25% | Does the first line stop the scroll? Is it specific? Does it create curiosity? |
| Emotional Resonance | 20% | Does it trigger one clear emotion (WTF, OHHHH, WOW, FINALLY, YAYY, LOL)? |
| Specificity | 15% | Uses concrete numbers, names, examples? Not vague generalizations? |
| Shareability | 15% | Would someone share this to look smart/helpful/in-the-know? |
| Brand Alignment | 10% | Sounds like Augmi's voice? Builder-to-builder? Not corporate? |
| Trend Relevance | 10% | Attached to current conversations? Riding a wave? |
| Visual Impact | 5% | Image/video stops the scroll and reinforces the message? |

**Calculate weighted grade:**
```
Overall = (Hook × 0.25) + (Emotion × 0.20) + (Specificity × 0.15) +
          (Shareability × 0.15) + (Brand × 0.10) + (Trends × 0.10) + (Visual × 0.05)
```

**Letter grade:** A (9-10), B (7-8), C (5-6), D (3-4), F (1-2)

**Cross-reference with actual engagement metrics** from `social-growth-strategy.md`:
- Does high-graded content actually get high engagement?
- Does low-graded content get low engagement?
- Any surprises? (Low grade but high engagement = we're wrong about what works)

**Update `content/strategy/content-grades.md`** with new grades and update rolling averages.

### Step 3: ANALYZE — Find Patterns

Analyze the data to find actionable patterns:

1. **Top performers**: Which posts got the most engagement? What do they have in common?
   - Topic? Format? Emotion? Time of day? Platform?

2. **Bottom performers**: Which posts flopped? What patterns emerge?
   - Too generic? Wrong emotion? Bad timing? Weak hook?

3. **Grade-to-performance correlation**:
   - Are our grades predictive of engagement? If not, our grading rubric needs adjustment.

4. **Content gaps**:
   - Topics we haven't covered that our audience cares about
   - Formats we haven't tried (e.g., polls, memes, threads vs single posts)
   - Platforms where we're underperforming

5. **Thesis validation**:
   - Is our core thesis in `content-thesis.md` holding up?
   - Which principles are confirmed by data? Which are contradicted?

### Step 4: SCOUT — Research New Viral Trends

Search for new trends we can jump on:

1. **Run trend research:**
   - Use WebSearch: `"trending AI agents" OR "trending AI news" OR "viral tech" site:twitter.com OR site:reddit.com`
   - Use WebSearch: `"trending crypto" OR "Web3 viral" OR "AI agents news today"`
   - Use WebSearch: `"OpenClaw" OR "Claude Code" OR "AI agent deployment" trending`

2. **Evaluate each trend:**
   - Is it still rising or already peaked?
   - Can we add a unique Augmi angle?
   - Does it align with our content thesis?
   - Estimated window: how many hours/days until it's old news?

3. **Save results to `content/strategy/trend-research/YYYY-MM-DD-trends.md`:**
   - Score each trend: Virality (1-10), Relevance (1-10), Combined = (V × 0.6) + (R × 0.4)
   - Include: window (hours/days), emotion, Augmi angle, suggested format
   - Mark status: PROPOSED
   - Top 3 recommended for immediate content

4. **Update `content/strategy/content-thesis.md` Trend Radar:**
   - Add new trends under "Trends We're Currently Riding"
   - Move expired trends to "Expired Trends"
   - Add promising trends to "Trends to Watch"

### Step 5: PROPOSE — Generate Improvement Proposal

Based on Steps 2-4, write a specific improvement proposal. Save to:
```
OUTPUT/self-improvement/YYYYMMDD-HHMM/improvement-proposal.md
```

Format:
```markdown
# Self-Improvement Proposal — YYYY-MM-DD HH:MM

## Current Performance Summary
- Overall grade average: X.X (last 7 days)
- Top performing content: [description]
- Biggest gap: [description]
- Grade trend: improving/declining/flat

## Proposed Changes

### 1. Content Thesis Updates
- **Change**: [specific change to content-thesis.md]
- **Why**: [data-backed reason]
- **Expected Impact**: [what we expect to improve]

### 2. Style Guide Updates
- **Change**: [specific change to twitter-viral-strategy.md or social-engine-guide.md]
- **Why**: [data-backed reason]
- **Expected Impact**: [what we expect to improve]

### 3. Strategy Updates
- **Change**: [specific change to social-growth-strategy.md]
- **Why**: [data-backed reason]
- **Expected Impact**: [what we expect to improve]

### 4. Trend Opportunities
- **Trend**: [trend to jump on]
- **Window**: [how long we have]
- **Angle**: [our unique take]
- **Format**: [suggested content format]

## Risk Assessment
- What could go wrong with these changes?
- What are we uncertain about?
```

### Step 6: APPLY — Implement Improvements

Apply the proposed changes to the strategy files:

1. **Update `content/strategy/content-thesis.md`:**
   - Refine core thesis if data contradicts it
   - Update viral growth principles based on what's working
   - Update platform-specific thesis with engagement data
   - Move hypotheses between Active/Validated/Invalidated
   - Add to refinement history table
   - Increment refinement count and update timestamp

2. **Update `content/strategy/twitter-viral-strategy.md`:**
   - Add new hook templates that performed well
   - Remove hook patterns that consistently underperform
   - Update emotion targeting based on engagement data
   - Add new narrative frames based on top performers

3. **Update `social-engine-guide.md`:**
   - Adjust audience profile if we're reaching different segments
   - Update content quality standards based on what drives engagement
   - Refine analytics targets based on realistic benchmarks

4. **Update `social-growth-strategy.md`:**
   - Update KPI targets based on actual data
   - Add new recommendations
   - Update content themes performing well

5. **Log all changes:**
   Save to `OUTPUT/self-improvement/YYYYMMDD-HHMM/changes-applied.md`:
   ```markdown
   # Changes Applied — YYYY-MM-DD HH:MM

   ## Files Modified
   1. content/strategy/content-thesis.md — [what changed]
   2. content/strategy/twitter-viral-strategy.md — [what changed]
   3. social-engine-guide.md — [what changed]
   4. social-growth-strategy.md — [what changed]

   ## Refinement Number: X
   ## Previous Grade Average: X.X
   ## Target Grade Average: X.X
   ```

### Step 7: REPORT — Print Summary

Print a concise summary:

```
=== Self-Improvement Loop Complete ===

Date: YYYY-MM-DD HH:MM
Refinement #: X

Content Graded: X posts
Average Grade: X.X (A/B/C/D/F)
Grade Trend: improving/declining/flat (vs last cycle)

Changes Applied:
  - Content thesis: [brief description]
  - Style guide: [brief description]
  - Strategy: [brief description]

Trend Opportunities Found: X
  - [trend 1] (window: Xh)
  - [trend 2] (window: Xh)

Proposal: OUTPUT/self-improvement/YYYYMMDD-HHMM/improvement-proposal.md
Changes: OUTPUT/self-improvement/YYYYMMDD-HHMM/changes-applied.md

Next cycle: ~8 hours
===
```

---
---

# FULL CONTENT PIPELINE (use --full-pipeline flag)

The original trend-to-content pipeline. Run with `/social-content-engine --full-pipeline`.

Automates the full trend-to-content pipeline: discover trending topics, score them, research the best ones, write platform-adapted content, generate images, and save to Google Drive.

## Prerequisites

### Required Dependencies
```bash
pip3 install requests --break-system-packages
```

### Required for Image Generation
```bash
pip3 install google-genai pillow --break-system-packages
```

`GEMINI_API_KEY` must be set in the root `.env.local` file (already configured in this project).

### Required for Google Drive Upload
The `gog` CLI must be installed and authenticated (`gog auth login`).

## Usage

```bash
# Full pipeline — discover trends, score, research top 3, write all content, save to Drive
/social-content-engine

# With a niche focus
/social-content-engine --topic "AI agents"

# Skip image generation (text only)
/social-content-engine --no-images

# Only discover + score (no content writing)
/social-content-engine --discover-only
```

## Output Directory

```
OUTPUT/social-content/YYYYMMDD/
├── raw-trends.md
├── scored-topics.md
├── topic-1-slug/
│   ├── processing.md
│   ├── blog-post.md
│   ├── twitter-thread.md
│   ├── instagram-carousel.md
│   ├── linkedin-post.md
│   └── images/
│       ├── instagram-cover.png
│       └── linkedin-image.png
├── topic-2-slug/
│   └── (same structure)
├── topic-3-slug/
│   └── (same structure)
└── drive-links.md
```

---

## Phase 1: DISCOVER

Find what's trending right now across multiple signals.

### Steps

1. **Run trend-finder for Google Trends:**
   ```bash
   python3 .claude/skills/trend-finder/scripts/find_trends.py --related --limit 20
   ```
   If `--topic` was provided:
   ```bash
   python3 .claude/skills/trend-finder/scripts/find_trends.py --topic "<TOPIC>" --related --limit 20
   ```

2. **Search for Twitter/X trends:**
   Use WebSearch with query: `"trending on twitter today" OR "viral tweets today" <TOPIC_IF_PROVIDED>`

3. **Search for general social media trends:**
   Use WebSearch with query: `"trending topics today" OR "viral social media" <TOPIC_IF_PROVIDED>`

4. **Search for tech/AI trends (if topic is tech-related):**
   Use WebSearch with query: `"trending AI" OR "trending tech" OR "viral tech news today"`

5. **Merge all signals** into `OUTPUT/social-content/YYYYMMDD/raw-trends.md` using this format:

```markdown
# Raw Trend Signals — YYYY-MM-DD

> Focus: {topic if provided, otherwise "General"}

## Google Trends (via trend-finder)

| # | Topic | Traffic | Context |
|---|-------|---------|---------|
| 1 | Example | 500K+ | News headline |

## Twitter/X Signals

| # | Topic | Source | Context |
|---|-------|--------|---------|
| 1 | Example | @source | Why it's trending |

## Social Media Signals

| # | Topic | Platform | Context |
|---|-------|----------|---------|
| 1 | Example | Reddit | Why it's trending |

## Combined Topic List

1. Topic A (Google Trends + Twitter)
2. Topic B (Twitter)
3. Topic C (Google Trends)
...
```

If `--discover-only` is set, also run Phase 2 (scoring) then stop.

---

## Phase 2: SCORE

Score and rank all discovered topics to select the top 3 for content creation.

### Steps

1. **Run the scoring script:**
   ```bash
   python3 .claude/skills/social-content-engine/scripts/score_topics.py \
     --input OUTPUT/social-content/YYYYMMDD/raw-trends.md \
     --output OUTPUT/social-content/YYYYMMDD/scored-topics.md
   ```

2. **Review the scored output.** The script produces a preliminary score. Now **refine** the scores using AI judgment:
   - Read `scored-topics.md`
   - For each topic, evaluate:
     - **Virality Score (1-10):** search volume, multi-source signal, recency, emotional hook potential
     - **Augmi Relevance (1-10):** AI/agents, crypto/Web3, dev tools, entrepreneurship, natural tie to Augmi
   - **Combined Score = (Virality x 0.6) + (Relevance x 0.4)**
   - Re-rank and update `scored-topics.md`

3. **Select top 3 topics** and mark them clearly in the file.

### Scoring Rubric

**Virality Score (1-10):**
- 8-10: Massive search volume, trending across multiple platforms, strong emotional hook
- 5-7: Moderate interest, trending on 1-2 platforms, decent hook
- 1-4: Niche interest, single source, weak hook

**Augmi Relevance Score (1-10):**
- 8-10: Directly about AI agents, crypto wallets, autonomous AI, no-code creation
- 5-7: Adjacent (AI tools, Web3 general, startup tech, automation)
- 1-4: Tangentially related (general tech news, business, science)

### Output Format (`scored-topics.md`)

```markdown
# Scored Topics — YYYY-MM-DD

## Scoring Rubric
Combined = (Virality x 0.6) + (Relevance x 0.4)

## Top 3 Selected

### 1. [Topic Name] — Score: X.X
- Virality: X/10 — [reason]
- Relevance: X/10 — [reason]
- Content angle: [how to tie to Augmi]

### 2. [Topic Name] — Score: X.X
...

### 3. [Topic Name] — Score: X.X
...

## Full Rankings

| # | Topic | Virality | Relevance | Combined | Selected |
|---|-------|----------|-----------|----------|----------|
| 1 | ...   | 9        | 8         | 8.6      | YES      |
...
```

If `--discover-only` is set, stop here.

---

## Phase 3: RESEARCH

For each of the top 3 selected topics, conduct deep research.

### Steps (repeat for each topic)

1. **Create topic directory:**
   ```
   OUTPUT/social-content/YYYYMMDD/{topic-slug}/
   ```

2. **WebSearch for 10 sources** on the topic:
   - Search for news articles, blog posts, expert opinions
   - Search for social media reactions and discussions
   - Search for data, statistics, reports on the topic

3. **WebFetch each source** — extract key information:
   - Main thesis/argument
   - Key data points or statistics
   - Notable quotes
   - Unique angles or perspectives

4. **Write `processing.md`** with the research synthesis:

```markdown
# Research: {Topic Name}

## Summary
[2-3 paragraph synthesis of all sources]

## Key Facts & Data
- Fact 1 (Source: ...)
- Fact 2 (Source: ...)

## Expert Opinions
- "Quote" — Person, Source
- "Quote" — Person, Source

## Augmi Angle
[How this topic connects to AI agents, crypto, autonomous AI, or democratizing tech]

## Sources
1. [Title](URL) — key takeaway
2. [Title](URL) — key takeaway
...
```

---

## Phase 4: WRITE

For each researched topic, produce 4 content pieces. Read the templates before writing:

```
.claude/skills/social-content-engine/templates/blog-post-template.md
.claude/skills/social-content-engine/templates/twitter-thread-template.md
.claude/skills/social-content-engine/templates/instagram-carousel-template.md
.claude/skills/social-content-engine/templates/linkedin-post-template.md
```

### Augmi Brand Voice (inline reference)

- **Conversational**, not corporate
- **Empowering**, not condescending — users are "builders", not "non-technical users"
- **Crypto-native** language — wallets, USDC, ownership, on-chain
- **Playful** — building is fun, not intimidating
- Never say: "enterprise-grade", "leverage our AI capabilities", "comprehensive suite"
- CTA examples: "Deploy your own AI agent at augmi.world", "Start building at augmi.world"
- Augmi deploys AI agents that run 24/7, connect to Telegram/Discord, and (soon) hold their own crypto wallets

### 4a. Blog Post (`blog-post.md`)

Write a 800-1200 word blog post following the template. Key rules:
- Hook-first opening paragraph
- Synthesize research — don't just list facts
- Weave in the Augmi angle naturally (not forced)
- End with a soft CTA: "Deploy your own AI agent at augmi.world"
- Include `generated_at` timestamp in frontmatter
- Be accurate about source counts (from deep-research guidelines)

### 4b. Twitter Thread (`twitter-thread.md`)

Write a 5-10 tweet thread following the template. Key rules:
- Tweet 1 is the hook — most compelling claim or question
- Each tweet is self-contained but flows as a story
- Include data points where possible
- Tweet 2-3: context and "why now"
- Middle tweets: insights, examples, data
- Final tweet: CTA + follow prompt
- Verify each tweet is under 280 characters

### 4c. Instagram Carousel (`instagram-carousel.md`)

Write 7-10 slide texts + 1 image generation prompt. Key rules:
- Slide 1: Bold hook statement (large text)
- Slides 2-8: One insight per slide, short punchy text
- Final slide: CTA + "Follow for more"
- Include an image prompt for the cover slide (1:1 aspect ratio)
- The image prompt should be for a visual that would make someone stop scrolling

### 4d. LinkedIn Post (`linkedin-post.md`)

Write a professional LinkedIn post. Key rules:
- Professional but not boring — match the "builder" voice
- Open with a hook line, then blank line (LinkedIn truncation)
- 150-300 words
- Include relevant hashtags (3-5)
- Include an image prompt for a supporting image (16:9 aspect ratio)

---

## Phase 5: IMAGES

Generate images using the existing `blog-image-gen` skill.

### Steps

For each topic, look at the image prompts in `instagram-carousel.md` and `linkedin-post.md`.

1. **Generate Instagram cover image (1:1):**
   ```bash
   python3 .claude/skills/blog-image-gen/scripts/generate_blog_images.py \
     --prompt "<PROMPT_FROM_INSTAGRAM_CAROUSEL>" \
     --output OUTPUT/social-content/YYYYMMDD/{topic-slug}/images/instagram-cover.png \
     --model imagen-4 \
     --aspect-ratio 1:1
   ```

2. **Generate LinkedIn image (16:9):**
   ```bash
   python3 .claude/skills/blog-image-gen/scripts/generate_blog_images.py \
     --prompt "<PROMPT_FROM_LINKEDIN_POST>" \
     --output OUTPUT/social-content/YYYYMMDD/{topic-slug}/images/linkedin-image.png \
     --model imagen-4 \
     --aspect-ratio 16:9
   ```

**IMPORTANT:** Load `GEMINI_API_KEY` from the root `.env.local` before running:
```bash
export GEMINI_API_KEY=$(grep GEMINI_API_KEY .env.local | cut -d'=' -f2)
```

If `--no-images` is set, skip this phase entirely.

---

## Phase 6: SAVE TO DRIVE

Upload all generated content to Google Drive.

### Steps

1. **Check for `gog` CLI:**
   ```bash
   which gog
   ```
   If not found, skip this phase and note it in the output.

2. **Find or create the parent folder:**
   ```bash
   gog drive search "social-media-posts" --type folder --json
   ```

3. **Create date subfolder:**
   ```bash
   gog drive mkdir "YYYYMMDD" --parent <parent-folder-id>
   ```

4. **For each topic, create a subfolder and upload all files:**
   ```bash
   gog drive mkdir "{topic-slug}" --parent <date-folder-id>
   gog drive upload OUTPUT/social-content/YYYYMMDD/{topic-slug}/blog-post.md --parent <topic-folder-id>
   gog drive upload OUTPUT/social-content/YYYYMMDD/{topic-slug}/twitter-thread.md --parent <topic-folder-id>
   gog drive upload OUTPUT/social-content/YYYYMMDD/{topic-slug}/instagram-carousel.md --parent <topic-folder-id>
   gog drive upload OUTPUT/social-content/YYYYMMDD/{topic-slug}/linkedin-post.md --parent <topic-folder-id>
   # Upload images if they exist
   gog drive upload OUTPUT/social-content/YYYYMMDD/{topic-slug}/images/instagram-cover.png --parent <topic-folder-id>
   gog drive upload OUTPUT/social-content/YYYYMMDD/{topic-slug}/images/linkedin-image.png --parent <topic-folder-id>
   ```

5. **Write `drive-links.md`** with all uploaded file URLs:

```markdown
# Google Drive Links — YYYY-MM-DD

## Topic 1: {name}
- Blog: [link]
- Twitter: [link]
- Instagram: [link]
- LinkedIn: [link]
- Instagram Cover: [link]
- LinkedIn Image: [link]

## Topic 2: {name}
...
```

If `gog` is not available, skip upload and note: "Google Drive upload skipped — install gogcli and run `gog auth login`."

---

## Phase Summary

After all phases complete, print a summary:

```
=== Social Content Engine Complete ===

Date: YYYY-MM-DD
Topics processed: 3

Topic 1: {name} (Score: X.X)
  - Blog: OUTPUT/social-content/YYYYMMDD/{slug}/blog-post.md
  - Twitter: OUTPUT/social-content/YYYYMMDD/{slug}/twitter-thread.md
  - Instagram: OUTPUT/social-content/YYYYMMDD/{slug}/instagram-carousel.md
  - LinkedIn: OUTPUT/social-content/YYYYMMDD/{slug}/linkedin-post.md
  - Images: 2 generated

Topic 2: {name} (Score: X.X)
  ...

Google Drive: {uploaded/skipped}
Total files created: {N}
```

---

## Tips

- The `--topic` flag focuses all phases on a niche. Without it, you get general trending topics.
- Image generation costs ~$0.02/image. 3 topics x 2 images = ~$0.12 per run.
- If Google Trends rate-limits, wait 5 minutes and retry.
- Content is written by Claude (not scripted) for brand voice quality.
- All content templates are in `.claude/skills/social-content-engine/templates/`.
