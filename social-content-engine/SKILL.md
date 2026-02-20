---
name: social-content-engine
user-invocable: true
description: >
  Full trend-to-content pipeline: discovers trending topics, scores them for virality
  and Augmi relevance, researches the top 3, writes platform-adapted content (blog,
  Twitter thread, Instagram carousel, LinkedIn post), generates images, and saves
  to Google Drive. Triggers on "social content", "content engine", "trending content",
  "create social posts", or "content pipeline".
allowed-tools: Bash, Read, Write, WebSearch, WebFetch, Task
---

# Social Content Engine

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
