---
name: market-research-ai-agents
description: Market research workflow for finding latest trends and marketing angles in AI agents, OpenClaw, AI agent economy, and AI-agent social marketing. Use when the user wants fresh trend intelligence, source-backed analysis, and a ranked list of viral content or GTM angles matched to Augmi ICP.
---

# Market Research AI Agents

Find the newest, most marketable narratives and convert them into ICP-fit viral angles.

## Use This Skill When

- User asks for latest trends/news/angles in:
  - AI agents
  - OpenClaw (or "open claude")
  - AI agent economy
  - Social marketing with AI agents
- User needs a ranked shortlist of high-upside topics for content, growth, or positioning.

## Workflow

### 1) Brainstorm Research Map

Build a hypothesis map before searching.

- Define 4 topic buckets:
  - `ai-agents-core`
  - `openclaw-open-claude`
  - `agent-economy`
  - `social-marketing-ai-agents`
- For each bucket, draft:
  - 5-10 trend queries
  - 3 counter-positioning queries (contrarian takes)
  - 3 buying-intent queries (signals of commercial demand)
- Keep a date window: default last 14 days, expand to 30 days if signal is weak.

### 2) Collect Multi-Channel Signals

Use at least 3 channels: web search, API feeds, and social data.

- Web/news:
  - Pull latest high-signal posts, launch notes, product updates, benchmarks, funding events.
- APIs (if available):
  - Trend APIs, social APIs, SEO keyword trend tools, or internal analytics exports.
- Social scraping/search:
  - X/Twitter, LinkedIn, Reddit, YouTube comments/posts.
  - Capture engagement metrics: views, likes, reposts/shares, comments, velocity if available.

For every source, store:
- `title`
- `url`
- `published_at`
- `channel`
- `engagement_signals`
- `thesis`
- `relevance_bucket`

### 3) Build Analysis

Synthesize signals into market meaning.

- Cluster sources into narratives (3-7 clusters).
- For each cluster:
  - What changed now?
  - Why this matters for operators/builders?
  - Where market attention is compounding?
  - What angle is overused vs underused?
- Flag risk:
  - Hype-only narratives
  - Weak evidence narratives
  - Non-ICP narratives

### 4) Produce ICP-Matched Viral Angles

Load ICP first, then score candidate angles.

1. Try Google Drive ICP folder first.
- Use `gog` CLI (or equivalent) to locate the `ICP` folder and latest ICP docs.
- Extract pains, desired outcomes, objections, triggers, language patterns.

2. Fallback if Drive is unavailable.
- Use local ICP reference: `references/icp-augmi-fallback.md`.

3. Score each candidate angle with this rubric:
- `virality_potential` (0-10): controversy, novelty, social spread potential
- `icp_fit` (0-10): direct match to ICP pain/outcome/objection
- `business_relevance` (0-10): product tie-in and monetization relevance
- `timeliness` (0-10): freshness and momentum in last 14 days
- `proof_strength` (0-10): evidence quality and source credibility

Weighted score:
`0.30*virality + 0.30*icp_fit + 0.20*business_relevance + 0.10*timeliness + 0.10*proof_strength`

Return top 5-10 angles.

## Required Output

Return 4 sections in this exact order:

1. `Trend Snapshot (Latest Window)`
- Date window used
- Top narrative shifts
- 5-10 key sources with links

2. `Market Analysis`
- Clustered narratives
- Market implications
- Saturated vs underpriced angles

3. `Top Viral ICP Angles`
- Ranked list with score breakdown
- Why this fits ICP
- Best format per angle (thread, video, carousel, article)
- Hook draft (1 line)

4. `Execution Backlog (7 Days)`
- 5 concrete content/GTM moves
- Expected upside
- Required proof/assets

## Rules

- Prioritize recency and provide exact dates.
- Do not present claims without a source link.
- Separate observed facts from inference.
- If ICP docs are missing, state the fallback used.
- Prefer concise, decision-ready outputs over long summaries.

## Reference Files

- ICP fallback: [references/icp-augmi-fallback.md](references/icp-augmi-fallback.md)
- Output template: [references/research-output-template.md](references/research-output-template.md)
