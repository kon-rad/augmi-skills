---
name: social-media-analyst
description: >
  Analyze any social media channel's performance — scrape data, detect patterns,
  cross-reference Google Trends, compare against strategy, and generate rich
  reports with 7 interactive charts. Currently supports YouTube via yt-dlp.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Task
  - AskUserQuestion
metadata:
  commands:
    - social-media-analyst
    - social-media-analyst:analyze
    - social-media-analyst:scrape
    - social-media-analyst:report
---

# Social Media Analyst

Comprehensive channel analytics: scrape, analyze, trend-check, and report.

## Commands

| Command | What it does |
|---------|-------------|
| `social-media-analyst` | Full pipeline: scrape → analyze → trends → web research → report → upload |
| `social-media-analyst:analyze` | Analysis + reports only (skip scraping, use `--data-dir`) |
| `social-media-analyst:scrape` | Scrape a YouTube channel only |
| `social-media-analyst:report` | Generate reports from existing analysis.json |

## Required Input

Ask the user for:
1. **Channel** — YouTube handle (e.g., `@Jakexplains`) or URL
2. **Data directory** — Where to store/read data (e.g., `OUTPUT/JakeExplains/data`)
3. **Strategy file** (optional) — Path to a strategy markdown file to compare against

If the user provides `--data-dir` with existing data, skip scraping.

## Workflow

### Phase 1: SCRAPE (skip if `--data-dir` has data)

```bash
python3 .claude/skills/social-media-analyst/scripts/scrape_youtube.py \
  --channel "@ChannelHandle" \
  --output OUTPUT/<ChannelSlug>/data
```

This produces:
- `channel-info.json` — Channel metadata
- `shorts-flat.jsonl` / `videos-flat.jsonl` — Flat playlist listings
- `shorts-flat-sorted.json` / `videos-flat-sorted.json` — Sorted by views
- `shorts-detail/` / `videos-detail/` — Per-video metadata (id, title, upload_date, duration, view_count, like_count, comment_count)

**Flags:**
- `--skip-details` — Only fetch flat playlists (faster, no per-video stats)
- `--shorts-only` / `--videos-only` — Limit to one content type
- `--delay 1.0` — Delay between detail requests (default 1s)

### Phase 2: ANALYZE

```bash
python3 .claude/skills/social-media-analyst/scripts/analyze_performance.py \
  --data-dir OUTPUT/<ChannelSlug>/data \
  --output OUTPUT/<ChannelSlug>/data/analysis.json
```

Produces `analysis.json` with:
- **overview** — Total views, likes, comments, content counts
- **hook_patterns** — Question, curiosity gap, superlative, listicle, emotional, geographic hooks with avg views
- **categories** — Auto-detected content topics (geography, science, technology, etc.) with engagement rates
- **duration_analysis** — Performance by video length
- **view_distribution** — Bucket counts (1M+, 100K-1M, etc.)
- **engagement_scatter** — Per-item views vs engagement rate with quadrant labels
- **monthly_views** — Time-series of views, uploads, likes per month
- **growth_eras** — Detected content eras based on upload gaps
- **top_shorts / top_videos / top_content** — Ranked lists
- **top_topics** — Top 5 category keywords for trend research

### Phase 3: TRENDS

Use the trend-finder skill to check Google Trends for the channel's top topics:

```bash
python3 .claude/skills/trend-finder/scripts/find_trends.py \
  --topic "<topic>" --related
```

Run this for each topic in `analysis.json → top_topics` (up to 5).

Read the output and note:
- Whether the topic is trending up or down
- Related rising queries (content opportunities)
- Peak interest periods

### Phase 4: WEB RESEARCH

Use WebSearch to find:
1. **Niche news** — Recent developments in the channel's top categories
2. **Competitor channels** — Similar creators, their recent performance
3. **Algorithm updates** — Recent YouTube algorithm changes affecting shorts/videos
4. **Content gaps** — Topics trending on Google but not covered by the channel

Summarize findings as bullet points in the final report.

### Phase 5: STRATEGY COMPARISON (optional)

If the user provides a strategy file (e.g., `jake-explains-strategy.md`):
1. Read the strategy file
2. Compare actual performance against stated goals
3. Note gaps between strategy and execution
4. Add a "Strategy Alignment" section to the report

### Phase 6: REPORT GENERATION

#### Markdown Report

```bash
python3 .claude/skills/social-media-analyst/scripts/generate_report.py \
  --analysis OUTPUT/<ChannelSlug>/data/analysis.json \
  --output OUTPUT/<ChannelSlug>/reports/<slug>-report.md
```

After the script generates the base report, **manually append** these Claude-generated sections:
- **Trend Insights** — Findings from Phase 3
- **Market Research** — Findings from Phase 4
- **Strategy Alignment** — Findings from Phase 5 (if applicable)
- **Recommendations** — 5-10 actionable recommendations based on all data

#### HTML + PDF Report (7 charts)

```bash
NODE_PATH=$(npm root -g) node .claude/skills/social-media-analyst/scripts/generate_html_report.js \
  --analysis OUTPUT/<ChannelSlug>/data/analysis.json \
  --output OUTPUT/<ChannelSlug>/reports/ \
  --pdf
```

The HTML report includes these 7 charts:
1. **Content Split** — Doughnut pair: content count + views split
2. **Top 20 Content** — Horizontal bar by views (color-coded short/video)
3. **Hook Patterns** — Bar chart: avg views per hook type
4. **Engagement by Category** — Stacked bar: likes + comments per category
5. **View Distribution** — Stacked bar: bucket counts for shorts + videos
6. **Engagement vs Views Scatter** — Quadrant plot (underrated, balanced hit, clickbait)
7. **Growth Timeline** — Dual-axis line: views + uploads per month

### Phase 7: UPLOAD (optional)

Upload reports to Google Drive:

```bash
gog drive upload OUTPUT/<ChannelSlug>/reports/ \
  --folder "augmi/channel-analytics/<channel-slug>/$(date +%Y-%m-%d)" \
  --account synducer@gmail.com
```

## Output Structure

```
OUTPUT/<ChannelSlug>/
├── data/
│   ├── channel-info.json
│   ├── shorts-flat.jsonl
│   ├── shorts-flat-sorted.json
│   ├── videos-flat.jsonl
│   ├── videos-flat-sorted.json
│   ├── shorts-detail/          # Per-short metadata
│   ├── videos-detail/          # Per-video metadata
│   └── analysis.json           # Core analysis output
└── reports/
    ├── <slug>-report.md        # Full markdown report
    ├── <slug>-analytics.html   # Interactive HTML with 7 charts
    └── <slug>-analytics.pdf    # PDF export (if Puppeteer available)
```

## Example: Jake Explains

```bash
# Full pipeline with existing data
/social-media-analyst:analyze --data-dir OUTPUT/JakeExplains/data

# Scrape fresh + analyze
/social-media-analyst --channel @Jakexplains

# Just regenerate reports
/social-media-analyst:report --analysis OUTPUT/JakeExplains/data/analysis.json
```

## Dependencies

- **Python 3** — No external packages needed (stdlib only)
- **yt-dlp** — For YouTube scraping (`pip3 install yt-dlp --break-system-packages`)
- **Node.js** — For HTML report generation
- **Puppeteer** (optional) — For PDF export (`npm install -g puppeteer`)
- **gog CLI** (optional) — For Google Drive upload
