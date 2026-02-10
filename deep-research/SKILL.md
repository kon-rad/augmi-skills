---
name: deep-research
description: Deep research workflow that takes a topic and links, conducts comprehensive research across web and social media, creates executive summaries, finds patterns and connections, then produces analysis documents, Twitter threads, blog posts, and YouTube scripts. Use this skill when the user wants to deeply research a topic, analyze multiple sources, and create multi-format content from the research.
---

# Deep Research Skill

A comprehensive research-to-content workflow that transforms a topic and source links into deep analysis and multi-platform content.

## Overview

This skill:
1. Takes a topic and optional seed links as input
2. Conducts deep research using web search, social media (Twitter/X), and other platforms
3. Scrapes and saves all research to organized folders
4. Creates one-paragraph executive summaries for each source
5. Analyzes patterns, finds deep connections across all materials
6. Produces a comprehensive analysis document with insights and conclusions
7. Transforms the analysis into Twitter threads, blog posts, and YouTube scripts

## Directory Structure

```
INPUT/<YYYYMMDD>/<topic-name>/
  ├── sources/                    # Raw scraped content
  │   ├── web/                    # Web articles
  │   ├── social/                 # Twitter/X threads, posts
  │   └── other/                  # Other platforms
  ├── executive-summaries.md      # One-paragraph summaries of each source
  └── research-log.md             # Research process notes

OUTPUT/<YYYYMMDD>/<topic-name>/
  ├── analysis.md                 # Full analysis document
  ├── twitter-thread.md           # Twitter/X thread
  ├── blog-post.md                # Long-form blog post
  └── youtube-script.md           # YouTube video script
```

## Workflow Phases

### 1. Research (`/deep-research:research`)
Deep dive into the topic using multiple channels:
- Web search for articles, papers, news
- Twitter/X for threads, discussions, expert opinions
- Other platforms as relevant (Reddit, LinkedIn, etc.)
- User-provided seed links

**Input:** Topic name + optional seed links
**Output:** Organized source materials in INPUT folder

### 2. Summarize (`/deep-research:summarize`)
Create executive summaries:
- Read each scraped source
- Write one-paragraph summary (3-5 sentences max)
- Capture: main thesis, key evidence, unique insights
- Save to executive-summaries.md

**Input:** Scraped sources
**Output:** Executive summaries file

### 3. Analyze (`/deep-research:analyze`)
Find patterns and connections:
- Identify common themes across sources
- Find contradictions and debates
- Discover non-obvious connections
- Surface implications and predictions
- Determine what's novel vs established consensus

**Input:** Executive summaries + source materials
**Output:** Pattern analysis document (in PROCESSING)

### 4. Produce (`/deep-research:produce`)
Create final content outputs:
- **Analysis Document:** Full writeup with connections, insights, implications, and conclusions
- **Twitter Thread:** Distilled insights in thread format (5-15 tweets)
- **Blog Post:** Long-form article with narrative structure
- **YouTube Script:** Video script with visual cues and talking points
- **Viral Tweets:** Standalone viral tweets (10 tweets)
- **LinkedIn Post:** 3 LinkedIn post variants
- **Image Prompts:** 5-7 image generation prompts for blog visuals

**Input:** Pattern analysis
**Output:** All content files in OUTPUT folder

**Timestamp:** Each output file should include a `generated_at` timestamp in the frontmatter or metadata section indicating when the content was created (ISO 8601 format: YYYY-MM-DDTHH:MM:SS)

## Usage

### One-Step Full Workflow (Recommended)
```
/deep-research:full topic: "AI Agents" links: [url1, url2, url3]
```

Runs all phases automatically: Research -> Summarize -> Analyze -> Produce

### Individual Phases (Manual Control)
```
/deep-research:research topic: "AI Agents" links: [url1, url2]
/deep-research:summarize
/deep-research:analyze
/deep-research:produce
```

## Output Formats

### Analysis Document (analysis.md)
```markdown
---
generated_at: "YYYY-MM-DDTHH:MM:SS"
topic: "[Topic Name]"
sources_count: [N]
---

# [Topic]: Deep Analysis

## Executive Summary
[2-3 paragraph overview]

## Key Findings
[Numbered list of major discoveries]

## Pattern Analysis
### Theme 1: [Name]
[Description and evidence]

### Theme 2: [Name]
[Description and evidence]

## Connections and Insights
[Non-obvious relationships between sources]

## Contradictions and Debates
[Where sources disagree]

## Implications
[What this means for the future]

## Conclusions
[Key takeaways and recommendations]

## Sources
[Linked references to all materials]
```

### Twitter Thread (twitter-thread.md)
```markdown
# Twitter Thread: [Topic]

1/ [Hook tweet - most compelling finding]

2/ [Context/background]

3-N/ [Key insights, one per tweet]

N/ [Conclusion + call to action]

---
Character counts verified: [Yes/No]
Total tweets: [N]
```

### Blog Post (blog-post.md)
```markdown
---
generated_at: "YYYY-MM-DDTHH:MM:SS"
topic: "[Topic Name]"
word_count: [N]
reading_time: "[N] min"
---

# [Headline]

## [Subtitle/Deck]

[Hook paragraph]

## [Section 1]
[Content]

## [Section 2]
[Content]

## Takeaways
[Actionable conclusions]
```

### YouTube Script (youtube-script.md)
```markdown
# [Video Title]

**Target length:** [N] minutes

## Hook (0:00-0:30)
[Opening hook to capture attention]

## Intro (0:30-1:00)
[What viewers will learn]

## Section 1: [Title] (1:00-X:00)
[Talking points]
[Visual cues: B-roll suggestions]

## Section 2: [Title]
[Content]

## Conclusion
[Summary and call to action]

---
Key timestamps for description
```

## Blog Writing Standards

When producing blog posts, follow these accuracy and honesty guidelines:

1. **Accurate source counts** - Say "analyzed 12 sources" if you analyzed 12, not "extensive research"
2. **No fabricated timeframes** - Never claim "weeks of research" or "months of investigation"
3. **Synthesizer voice** - Write as someone synthesizing research, not claiming personal expertise
4. **Specific citations** - Link to actual sources used
5. **No exaggeration** - Let quality speak for itself; avoid inflating credibility

## Notes

- All research respects rate limits and terms of service
- Twitter/X scraping may require authentication
- Web scraping uses respectful delays
- All sources are attributed and linked
- Date format: YYYYMMDD (e.g., 20260119)
