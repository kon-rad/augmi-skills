---
name: social-analytics
description: Daily social media analytics collection and reporting. Collects metrics from Postiz across LinkedIn, Instagram, X/Twitter, YouTube, and Facebook. Generates markdown + PDF reports with charts. Uploads to Google Drive.
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["postiz","gog","python3","node"],"env":["POSTIZ_API_KEY"]}}}
---

# Social Analytics Skill

Collects social media analytics daily from Postiz, stores as time-series JSON, generates reports (markdown + PDF with Chart.js charts), and uploads to Google Drive.

**Primary KPI**: Follower growth across all platforms
**Platforms**: Instagram, X/Twitter, LinkedIn (personal + page), YouTube, Facebook
**Data Source**: Postiz analytics API (`postiz` CLI)
**Storage**: Local JSON + Google Drive (`augmi/social-analytics`)
**Reports**: Markdown tables + branded PDF with line/bar charts

---

## Commands

### `social-analytics` or `social-analytics:daily` — Full Daily Workflow

The main command. Runs collect + report + Google Drive upload in sequence.

**Execute these steps in order:**

#### Step 1: Load API Key and Collect Data

```bash
export POSTIZ_API_KEY=$(grep POSTIZ_API_KEY .env.local | cut -d'=' -f2)

python3 .claude/skills/social-analytics/scripts/collect.py \
  --config .claude/skills/social-analytics/config/integrations.json \
  --output-dir data/social-analytics
```

This pulls analytics for all enabled platforms. On first run (no existing `data/social-analytics/raw/` directory), it automatically pulls 365 days of historical data. On subsequent runs, it pulls 7 days (configurable in `integrations.json`).

#### Step 2: Generate Markdown Report

```bash
DATE=$(date +%Y-%m-%d)

python3 .claude/skills/social-analytics/scripts/generate_report.py \
  --data-dir data/social-analytics \
  --output "data/social-analytics/reports/${DATE}-daily.md" \
  --date "$DATE"
```

#### Step 3: Generate PDF Report with Charts

```bash
NODE_PATH=$(npm root -g) node .claude/skills/social-analytics/scripts/generate_pdf.js \
  --data data/social-analytics \
  --output "data/social-analytics/reports/${DATE}-daily.pdf" \
  --date "$DATE"
```

The `NODE_PATH=$(npm root -g)` prefix is required so Node can find the globally-installed `puppeteer` module.

#### Step 4: Upload to Google Drive

1. **Check gog auth:**
   ```bash
   gog auth list
   ```
   If no tokens are shown, skip the upload and tell the user: "Google Drive upload skipped — run `gog login <email>` first."

2. **Read the Google Drive account from config:**
   ```bash
   GOG_ACCOUNT=$(python3 -c "import json; print(json.load(open('.claude/skills/social-analytics/config/integrations.json'))['google_drive']['account'])")
   ```

3. **Find or create the `augmi` folder:**
   ```bash
   AUGMI_FOLDER=$(gog drive search "augmi" --type folder --json -a "$GOG_ACCOUNT" | jq -r '.[0].id // empty')
   if [ -z "$AUGMI_FOLDER" ]; then
     AUGMI_FOLDER=$(gog drive mkdir "augmi" --json -a "$GOG_ACCOUNT" | jq -r '.id')
   fi
   ```

4. **Find or create the `social-analytics` subfolder:**
   ```bash
   SA_FOLDER=$(gog drive search "social-analytics" --type folder --json -a "$GOG_ACCOUNT" | jq -r '.[] | select(.parents[]? == "'$AUGMI_FOLDER'") | .id' 2>/dev/null | head -1)
   if [ -z "$SA_FOLDER" ]; then
     SA_FOLDER=$(gog drive mkdir "social-analytics" --parent "$AUGMI_FOLDER" --json -a "$GOG_ACCOUNT" | jq -r '.id')
   fi
   ```

5. **Create date subfolder and upload both reports:**
   ```bash
   DATE_FOLDER=$(gog drive mkdir "$DATE" --parent "$SA_FOLDER" --json -a "$GOG_ACCOUNT" | jq -r '.id')

   gog drive upload "data/social-analytics/reports/${DATE}-daily.md" --parent "$DATE_FOLDER" -a "$GOG_ACCOUNT"
   gog drive upload "data/social-analytics/reports/${DATE}-daily.pdf" --parent "$DATE_FOLDER" -a "$GOG_ACCOUNT"
   ```

6. **Record uploaded file URLs** in `data/social-analytics/reports/drive-links.md`.

#### Step 5: Print Summary

After all steps, display a summary like:

```
=== Social Analytics Daily Report ===

Date: YYYY-MM-DD
Platforms: N/N successful
Posts analyzed: N

Reports:
  Markdown: data/social-analytics/reports/YYYY-MM-DD-daily.md
  PDF: data/social-analytics/reports/YYYY-MM-DD-daily.pdf

Google Drive: uploaded / skipped
```

Then read and show the user the markdown report contents.

---

### `social-analytics:collect` — Collect Data Only

Pull analytics from Postiz for all enabled platforms without generating reports.

```bash
export POSTIZ_API_KEY=$(grep POSTIZ_API_KEY .env.local | cut -d'=' -f2)

python3 .claude/skills/social-analytics/scripts/collect.py \
  --config .claude/skills/social-analytics/config/integrations.json \
  --output-dir data/social-analytics
```

**Optional flags:**
- `--days <N>` — Override the lookback period (default: 7, first run: 365)

---

### `social-analytics:report` — Generate Reports Only

Generate markdown + PDF reports from already-collected data.

```bash
DATE=$(date +%Y-%m-%d)

python3 .claude/skills/social-analytics/scripts/generate_report.py \
  --data-dir data/social-analytics \
  --output "data/social-analytics/reports/${DATE}-daily.md" \
  --date "$DATE"

NODE_PATH=$(npm root -g) node .claude/skills/social-analytics/scripts/generate_pdf.js \
  --data data/social-analytics \
  --output "data/social-analytics/reports/${DATE}-daily.pdf" \
  --date "$DATE"
```

**Optional flags:**
- `--date YYYY-MM-DD` — Generate report for a specific date (default: today)

---

### `social-analytics:setup` — First-Time Setup

Interactive setup to configure the skill for a new user.

**Step 1: Verify Postiz CLI is installed**
```bash
postiz --version
```
If not installed: `npm install -g postiz`

**Step 2: Get Postiz integration IDs**
```bash
export POSTIZ_API_KEY=$(grep POSTIZ_API_KEY .env.local | cut -d'=' -f2)
postiz integrations:list
```
This outputs all connected social accounts. Update `.claude/skills/social-analytics/config/integrations.json` with the correct `id` for each platform.

**Step 3: Set up Google Drive auth**
```bash
gog login <email>
```
Update the `google_drive.account` field in `integrations.json` with the authenticated email.

**Step 4: Test X/Twitter analytics availability**
```bash
postiz analytics:platform <twitter-integration-id> -d 7
```
If this returns empty/error, X/Twitter analytics are unavailable on the current API tier. Set `"enabled": false` for twitter in config, or upgrade to X API Basic ($200/mo).

**Step 5: Install Puppeteer for PDF generation**
```bash
npm install -g puppeteer
```
This downloads Chromium (~200MB) on first install.

**Step 6: Run first collection**
```bash
python3 .claude/skills/social-analytics/scripts/collect.py \
  --config .claude/skills/social-analytics/config/integrations.json \
  --output-dir data/social-analytics
```
First run auto-detects empty data directory and pulls maximum history (365 days).

---

## Configuration

### `integrations.json`

Location: `.claude/skills/social-analytics/config/integrations.json`

```json
{
  "platforms": {
    "instagram": {
      "id": "<postiz-integration-id>",
      "name": "Instagram (@handle)",
      "enabled": true
    },
    "twitter": {
      "id": "<postiz-integration-id>",
      "name": "X/Twitter (@handle)",
      "enabled": true
    },
    "linkedin": {
      "id": "<postiz-integration-id>",
      "name": "LinkedIn (Personal Profile)",
      "enabled": true
    },
    "linkedin-page": {
      "id": "<postiz-integration-id>",
      "name": "LinkedIn Page (Company)",
      "enabled": true
    },
    "youtube": {
      "id": "<postiz-integration-id>",
      "name": "YouTube (@handle)",
      "enabled": true
    },
    "facebook": {
      "id": "",
      "name": "Facebook",
      "enabled": false
    }
  },
  "google_drive": {
    "folder_path": "augmi/social-analytics",
    "account": "user@gmail.com"
  },
  "collection": {
    "default_days": 7,
    "first_run_days": 365
  }
}
```

**Platform fields:**
- `id` — The Postiz integration ID. Get it from `postiz integrations:list`. Required.
- `name` — Display name for reports. Include the handle for clarity.
- `enabled` — Set to `true` to collect analytics, `false` to skip.

**Google Drive fields:**
- `folder_path` — The Drive folder hierarchy (auto-created). Reports go into `<folder_path>/YYYY-MM-DD/`.
- `account` — The Google account email used with `gog`. Must be authenticated via `gog login <email>`.

**Collection fields:**
- `default_days` — How many days of data to pull on each run (default: 7).
- `first_run_days` — How many days to pull on first run when no data exists (default: 365).

### Getting Postiz Integration IDs

```bash
export POSTIZ_API_KEY=$(grep POSTIZ_API_KEY .env.local | cut -d'=' -f2)
postiz integrations:list
```

Each integration in the output has an `id` field. Copy the ID for each platform into the config.

### Environment Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `POSTIZ_API_KEY` | `.env.local` | Authenticates with Postiz analytics API |

The collect script reads `POSTIZ_API_KEY` from the environment. Always load it before running:
```bash
export POSTIZ_API_KEY=$(grep POSTIZ_API_KEY .env.local | cut -d'=' -f2)
```

---

## Data Directory Structure

```
data/social-analytics/
├── .gitkeep
├── raw/                              # Daily API snapshots (GITIGNORED)
│   └── YYYY-MM-DD/
│       ├── instagram.json            # Raw Postiz response per platform
│       ├── twitter.json
│       ├── linkedin.json
│       ├── linkedin-page.json
│       ├── youtube.json
│       └── posts/
│           └── <post-id>.json        # Individual post analytics
├── aggregated/                       # Time-series data (GIT-TRACKED)
│   ├── followers.json                # KPI: daily follower counts per platform
│   └── all-metrics.json              # Full metrics history (impressions, likes, etc.)
└── reports/                          # Generated reports (GITIGNORED, backed up to Drive)
    ├── YYYY-MM-DD-daily.md           # Markdown report
    ├── YYYY-MM-DD-daily.pdf          # PDF with charts
    └── drive-links.md                # Google Drive upload URLs
```

**What's git-tracked vs gitignored:**
- `data/social-analytics/raw/` — **gitignored** (large daily JSON dumps, regenerable)
- `data/social-analytics/reports/` — **gitignored** (regenerable, backed up to Google Drive)
- `data/social-analytics/aggregated/` — **git-tracked** (compact time-series, the source of truth)
- `data/social-analytics/.gitkeep` — **git-tracked** (ensures the directory exists)

---

## Report Contents

### Markdown Report

Sections generated by `generate_report.py`:

1. **YAML Frontmatter** — Metadata (date, platforms, report type)
2. **KPI: Follower Growth** — Table with daily/7-day/30-day changes per platform + total
3. **Engagement Summary** — Table with impressions, likes, comments, shares, engagement rate
4. **Platform Details** — Per-platform breakdown of all available metrics
5. **Trends** — Fastest growing platform, highest engagement rate
6. **Recent Post Performance** — Top 10 recent posts with key metrics
7. **Footer** — Generation timestamp and data source

### PDF Report

Generated by `generate_pdf.js` using the HTML template at `scripts/templates/report.html`:

1. **Header** — Augmi branded header with date
2. **KPI Dashboard Cards** — Follower count + daily change per platform, plus total (dark green card)
3. **Follower Growth Line Chart** — All platforms over last 30 days, platform-colored lines
4. **Engagement Bar Chart** — Likes/comments/shares by platform (amber-gold, dark green, emerald)
5. **Detailed Metrics Table** — Full breakdown: followers, impressions, likes, comments, shares, engagement rate
6. **Footer** — Generated by Augmi Social Analytics

**Brand colors used:**
- Dark green: `#1B5E20` (headers, KPI cards)
- Amber-gold: `#D4A017` (accent, likes bar)
- Platform-specific: Instagram pink, Twitter blue, LinkedIn blue, YouTube red, Facebook blue

---

## Dependencies

| Tool | Purpose | Install | Notes |
|------|---------|---------|-------|
| `postiz` CLI | Analytics API access | `npm install -g postiz` | Requires `POSTIZ_API_KEY` |
| `python3` | Data collection + markdown reports | Pre-installed | No pip dependencies needed |
| `node` | PDF generation | Pre-installed | Requires `NODE_PATH` for global modules |
| `puppeteer` | Headless Chrome for PDF rendering | `npm install -g puppeteer` | ~200MB download (Chromium) |
| `gog` | Google Drive upload | Pre-installed | Requires `gog login <email>` |
| `jq` | JSON parsing in shell scripts | `brew install jq` | Used in Drive upload steps |

---

## Rate Limits and Performance

- **Postiz API**: 30 requests/hour
- **Daily collection run**: ~15-25 requests (5 platforms + up to 20 post analytics)
- **Well within limits** for daily use — even running 2x/day is safe
- **Collection timeout**: Each `postiz` command has a 120-second timeout
- **PDF generation**: Takes 5-15 seconds (browser launch + chart render + PDF export)

---

## Aggregated Data Schema

### `followers.json` (Primary KPI)

```json
{
  "metric": "followers",
  "last_updated": "2026-02-19T13:50:00.000Z",
  "platforms": {
    "instagram": {
      "history": [
        { "date": "2026-02-19", "value": 150, "change": 5 }
      ]
    }
  },
  "total": {
    "history": [
      { "date": "2026-02-19", "total": 500, "change": 12 }
    ]
  }
}
```

### `all-metrics.json` (All Metrics)

```json
{
  "last_updated": "2026-02-19T13:50:00.000Z",
  "platforms": {
    "instagram": {
      "history": [
        {
          "date": "2026-02-19",
          "metrics": {
            "followers": { "value": 150, "percentage_change": 3.4, "time_series": [...] },
            "impressions": { "value": 1200, "percentage_change": 10.2, "time_series": [...] },
            "likes": { "value": 85, "percentage_change": 5.0, "time_series": [...] }
          }
        }
      ]
    }
  }
}
```

---

## Troubleshooting

### "POSTIZ_API_KEY environment variable not set"
Load it from `.env.local` before running:
```bash
export POSTIZ_API_KEY=$(grep POSTIZ_API_KEY .env.local | cut -d'=' -f2)
```

### X/Twitter analytics return empty data
The free tier of the X API does not include analytics. You need X API Basic ($200/mo). Set `"enabled": false` for twitter in `integrations.json` to skip it.

### Post analytics show `{"missing": true}`
Some platforms don't return post IDs immediately after posting. Wait 24 hours and retry. You can also try:
```bash
postiz posts:missing <post-id>
postiz posts:connect
```

### PDF generation fails — "Puppeteer not found"
Install globally:
```bash
npm install -g puppeteer
```
Then run with `NODE_PATH`:
```bash
NODE_PATH=$(npm root -g) node .claude/skills/social-analytics/scripts/generate_pdf.js ...
```

### Chart.js fails to load in PDF
The HTML template loads Chart.js from CDN. Ensure internet connectivity. After first load, it's cached.

### Google Drive upload fails — "No tokens"
Authenticate first:
```bash
gog login <email>
```
Use the same email configured in `integrations.json` → `google_drive.account`.

### "Skipped <platform> — no data returned"
The platform may not have any analytics data yet. This is normal for new accounts or accounts with no recent activity. Postiz needs at least one post to start tracking metrics.

### Follower count shows 0 for a platform
Some platforms (like LinkedIn Pages) report 0 followers through the Postiz API when the account hasn't accumulated enough data. The count will populate once Postiz syncs the platform's analytics.
