---
name: trend-finder
user-invocable: true
description: >
  Finds trending topics using Google Trends for social media content ideation.
  Use when users want to discover what's trending, find viral topics, or research
  trending keywords for content creation. Triggers on requests like "find trends",
  "what's trending", "trending topics", "viral topics", or "social media trends".
allowed-tools: Bash, Read, Write, WebSearch, WebFetch
---

# Trend Finder Skill

Find trending topics and viral content ideas using Google Trends data. Designed to feed into content creation workflows (blog posts, social media, video scripts).

## Prerequisites

### Required Dependencies
```bash
pip3 install requests --break-system-packages
```

No API key required — uses Google Trends' public endpoints directly (no pytrends dependency).

## Usage

### Find General Trending Topics (default)

Get the hottest trending searches right now:
```bash
python3 .claude/skills/trend-finder/scripts/find_trends.py
```

### Find Trends for a Specific Topic

Research what's trending around a keyword or niche:
```bash
python3 .claude/skills/trend-finder/scripts/find_trends.py --topic "AI agents"
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--topic` | Keyword/niche to research trends around | None (general trends) |
| `--geo` | Country code for regional trends | `united_states` |
| `--output` | Output file path | `OUTPUT/trends/YYYYMMDD-trends.md` |
| `--limit` | Max number of trending items to return | `20` |
| `--related` | Include related topics and queries (with `--topic`) | `false` |

### Examples

```bash
# What's trending in the US right now
python3 .claude/skills/trend-finder/scripts/find_trends.py

# AI-related trends with related queries
python3 .claude/skills/trend-finder/scripts/find_trends.py --topic "artificial intelligence" --related

# Crypto trends in the UK
python3 .claude/skills/trend-finder/scripts/find_trends.py --topic "crypto" --geo "united_kingdom"

# Social media marketing trends, save to custom path
python3 .claude/skills/trend-finder/scripts/find_trends.py --topic "social media marketing" --output OUTPUT/smm-trends.md
```

## Workflow

### Step 1: Discover Trends

Run the script with or without a topic to generate a trends report:
```bash
python3 .claude/skills/trend-finder/scripts/find_trends.py --topic "your niche" --related
```

### Step 2: Review the Output

The script produces a markdown file with:
- **Trending searches** — what people are searching for right now
- **Related topics** (with `--related`) — topics associated with your keyword
- **Related queries** (with `--related`) — specific search queries people use
- **Content angle suggestions** — ideas for how to create content around each trend

### Step 3: Feed into Content Creation

Use the trends report as input for other skills:
- `/deep-research:blog` — write a blog post around a trending topic
- `/blog-image-gen` — generate images for trend-based content
- `/content-to-pptx` — turn trends into a presentation

## Output Format

The generated markdown file follows this structure:

```markdown
# Trending Topics Report — 2026-02-16

## Top Trending Searches (US)

| # | Topic | Context |
|---|-------|---------|
| 1 | Example Topic | Brief context if available |
| 2 | Another Topic | ... |

## Related Topics (for "your keyword")

### Rising Topics
| Topic | Growth |
|-------|--------|
| Example | Breakout |

### Top Topics
| Topic | Score |
|-------|-------|
| Example | 100 |

## Related Queries (for "your keyword")

### Rising Queries
| Query | Growth |
|-------|--------|
| "example query" | +5000% |

## Content Angle Ideas
- Angle 1 based on trend + your topic
- Angle 2...
```

## Rate Limiting

Google Trends may rate-limit after many sequential requests. The script:
- Adds a 1-second delay between API calls
- Retries once on failure with a 60-second backoff
- If rate-limited, wait 5 minutes and try again

## Troubleshooting

### "TooManyRequestsError" or 429 responses
Wait 5 minutes then retry. Google Trends throttles aggressive scraping.

### Empty results for a topic
The topic may be too niche for Google Trends. Try broader keywords.

### pytrends import error
```bash
pip3 install pytrends pandas --break-system-packages
```
