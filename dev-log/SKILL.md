---
name: dev-log
description: >
  Creates a dev log entry for the Augmi project by analyzing recent git commits.
  Use this skill when the user asks to "create a dev log", "write a dev log",
  "update the dev log", or "log today's progress". Analyzes git history to
  summarize what was built, fixed, and improved.
---

# Dev Log Creator Skill

Generate a dev log entry from recent git activity for the Augmi project.

## How It Works

1. Reads recent git commits (since the last dev log or last 24 hours)
2. Groups changes by theme (features, fixes, infrastructure, content, etc.)
3. Writes a markdown file to `docs/dev-log/YYYYMMDD.md`
4. The dev log page at `/dev-log` automatically picks up new entries

## Dev Log Location

All dev log entries live in: `docs/dev-log/`

## File Naming

Files are named by date: `YYYYMMDD.md` (e.g., `20260218.md`)

## Required Frontmatter Format

Every dev log file MUST have this frontmatter:

```yaml
---
title: "Short descriptive title of what happened today"
date: "YYYY-MM-DD"
author: "Augmi Team"
summary: "One-sentence summary of the day's work."
---
```

## Content Structure

After the frontmatter, write the body in this format:

```markdown
# Dev Log - Month Day, Year

## Section Title (Feature/Fix/Improvement Area)
- Bullet point describing what was done
- Another bullet point with detail
- Reference specific files or APIs when relevant

## Another Section
- More bullets

## Stats
- **N commits** across the day
- **~X lines added** across Y files
- Key areas: area1, area2, area3
```

## Guidelines

- **Group by theme**, not by commit — combine related commits into logical sections
- **Use active voice**: "Added reset button" not "Reset button was added"
- **Be specific**: mention file names, API routes, component names when relevant
- **Include a Stats section** at the bottom with commit count and lines changed
- **Keep summaries concise** — the summary frontmatter field should be 1 sentence
- **Title should capture the day's highlights** — not just "Dev Log Feb 18"

## Determining Time Range

- Check the date of the most recent existing dev log in `docs/dev-log/`
- Analyze commits from that date to now
- If no previous dev log exists, analyze the last 7 days of commits

## Git Commands to Use

```bash
# Find the last dev log date
ls -1 docs/dev-log/*.md | sort | tail -1

# Get commits since a date
git log --since="2026-02-12" --oneline --stat

# Get detailed diff stats
git log --since="2026-02-12" --shortstat --format="%h %s"

# Count lines changed
git log --since="2026-02-12" --shortstat --format="" | awk '{added+=$1; deleted+=$4} END {print "+" added " -" deleted}'
```

## Example Entry

See `docs/dev-log/20260211.md` for a reference example of the expected format and tone.
