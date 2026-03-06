# Viral Research Skill

Discovers trending topics in your niche by analyzing multiple sources and scoring by virality potential.

## Overview

This skill automatically finds what's trending in your defined niche across 5+ platforms. It uses trend velocity, engagement metrics, and recency to identify the most promising topics for content creation.

## Usage

```bash
/viral-research
```

No arguments needed - reads your niche from `social-engine-guide.md`.

## What It Does

1. **Reads Configuration**
   - Loads niche definition from `social-engine-guide.md`
   - Gets keywords, subtopics, target platforms
   - Uses `social-growth-strategy.md` for engagement patterns

2. **Multi-Source Search**
   - **Google Trends** - Search volume trends
   - **X/Twitter** - Trending hashtags and discussions
   - **Reddit** - Discussion volume and sentiment
   - **HackerNews** - Developer trends
   - **ProductHunt** - New product/feature launches
   - **LinkedIn** - Professional trends

3. **Trend Scoring**
   Each topic scored 0-100 based on:
   - Search volume growth (velocity)
   - Social engagement rate
   - Conversation volume
   - Recency (posted last 7 days)
   - Engagement-to-reach ratio
   - Competitor coverage gaps

4. **Deduplication**
   - Removes duplicate stories (different angles on same topic)
   - Keeps most promising angle for each story

5. **Smart Ranking**
   Uses `social-growth-strategy.md` to prioritize topics that match:
   - Your historical high-engagement topics
   - Your audience's proven interests
   - Underexplored content gaps

## Output Format

```markdown
# Top 10 Trending Topics for [Niche]

## 1. Topic Title
- **Trend Score**: 87/100
- **Why It's Trending**: Brief explanation (2-3 sentences)
- **Engagement Potential**: High/Medium/Low
- **Best For**: [Platform: Instagram | X | LinkedIn | YouTube]
- **Search Interest**: [Chart showing trend velocity]
- **Recent Signals**:
  - Source 1: [Volume]
  - Source 2: [Volume]
- **Content Angles**:
  - Angle A
  - Angle B
  - Angle C
- **Competitor Coverage**: Low (opportunity!)
- **Relevance to Your Niche**: 95% match

## 2. Topic Title
...
```

## Integration with Social Engine

This is **Phase 1** of the social-engine pipeline:

```
/viral-research
    ↓
Presents top 10 topics to user
    ↓
User selects 1-5 topics
    ↓
deep-research:full (Phase 3)
    ↓
Images + Videos + Carousels (Phase 4)
    ↓
humanizer (Phase 5)
    ↓
postiz (Phase 6)
    ↓
Daily analytics (Phase 7) → Updates strategy → Better viral-research next cycle
```

## Configuration

Edit `social-engine-guide.md` to customize:

```markdown
## Niche Definition
**Primary Niche**: AI Agents, OpenClaw, Claude Code
**Subtopics**:
- AI agent deployment
- OpenClaw features
- Claude Code capabilities
- Agent automation
- Crypto-native AI agents

## Target Platforms
- Instagram
- X/Twitter
- LinkedIn
- YouTube

## Content Quality Standards
- Humanization Required: Yes (always run /humanizer)
- Engagement Focus: Educational + actionable
- Posting Frequency: 3-5 posts/week
```

## Output Location

Results saved to:
```
OUTPUT/social-research/{date}/trending-topics.md
```

Also returned as interactive list for user to select topics.

## Learning from Strategy File

The skill automatically reads `social-growth-strategy.md` to:

1. **Identify High-Performing Topics**
   - Prioritizes topics similar to past high-engagement content
   - Avoids low-performing themes

2. **Align with Audience**
   - Looks at what platforms drive engagement
   - Considers audience demographics
   - Respects proven content pillars

3. **Find Content Gaps**
   - Identifies trending topics your audience cares about
   - Finds areas competitors haven't covered
   - Suggests unique angles

4. **Optimize Timing**
   - Suggests posting times based on historical data
   - Identifies seasonal trends
   - Avoids oversaturated content windows

## Technical Details

### Search APIs
- **Google Trends** - WebSearch tool
- **Twitter Search** - TwitterAPI.io (cheaper alternative to official X API)
- **Reddit API** - Trend detection via discussion volume
- **HackerNews** - RSS feed analysis
- **ProductHunt** - API for new launches

### Scoring Algorithm
```
Base Score = (Search Trend Velocity × 0.3)
           + (Social Engagement Rate × 0.3)
           + (Recency Bonus × 0.2)
           + (Niche Relevance × 0.2)

Final Score = Base Score × Competitor Coverage Factor
            × Your Historical Engagement Factor
```

### Caching
- Results cached for 24 hours
- Prevents redundant API calls
- Cached in: `OUTPUT/social-research/{date}/cache.json`

### Rate Limiting
- Respects all API rate limits
- Staggered requests to avoid throttling
- Falls back gracefully if API unavailable

## Platform-Specific Insights

### Instagram
- Looks for visual storytelling potential
- Scores carousel opportunities
- Identifies Reels-friendly topics

### X/Twitter
- Thread-friendly topics
- Hot takes and opinions
- Conversational angles

### LinkedIn
- Professional insights
- Career/industry trends
- Thought leadership opportunities

### YouTube
- Explainer video topics
- Long-form potential
- Educational angles

## Workflow Example

```
Day 1: /viral-research
├─ Searches all 5+ sources
├─ Scores 100+ potential topics
├─ Ranks top 10
├─ Returns for user selection
│
Day 1: User selects topics
├─ "AI Agents Replacing SaaS" (Score: 92)
├─ "Claude Code Benchmarks" (Score: 88)
└─ "Crypto Agent Wallets" (Score: 85)
│
Day 2-7: deep-research:full on each topic
└─ ... (rest of pipeline)
│
Day 8: Next /viral-research cycle
└─ Uses updated social-growth-strategy.md
└─ Better targeting, better topics
```

## Skill Dependencies

- WebSearch tool (Google Trends)
- Twitter Search skill (Twitter API)
- Reddit API access
- HackerNews RSS
- social-engine-guide.md (niche config)
- social-growth-strategy.md (learning data)

## Troubleshooting

**No trends returned**
- Check internet connectivity
- Verify niche keywords in `social-engine-guide.md` are specific enough
- Check if APIs are rate-limited (try again in 1 hour)
- Review error messages for API-specific issues

**Low-quality trends**
- Niche keywords might be too broad (narrow them in guide)
- Try again in 6 hours (trend data updates)
- Check if competitors dominate content (look for gaps instead)

**Missing a topic you expected**
- Check if topic is actually trending (use Google Trends directly)
- Verify topic matches your niche definition
- It might not have enough engagement yet (monitor and try next cycle)

## Performance Tips

1. **Specific Niche Keywords** - More specific = better results
2. **Regular Cycles** - Run weekly or bi-weekly for consistent flow
3. **User Review** - Don't just pick #1; review all 10 options
4. **Strategy Integration** - Let strategy file guide selections
5. **Feedback Loop** - Document what worked, what didn't

## Future Enhancements

- [ ] Competitor monitoring (track what they're posting)
- [ ] Sentiment analysis (is trend positive/negative?)
- [ ] Seasonal trend detection
- [ ] Long-form content potential scoring
- [ ] Influencer trend mapping
- [ ] Regional trend variations

---

**Version**: 1.0
**Location**: `/dev/startups/augmi-skills/viral-research/`
**Part of**: Social Engine skill suite

Trending = Revenue. Find better trends. 📈
