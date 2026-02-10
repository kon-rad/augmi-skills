# Viral Tweet Crafter

A personalized tweet creation skill that crafts authentic, mission-aligned content to build community, establish thought leadership, and stay true to your values.

---

## Triggers

Use this skill when the user:
- Asks to write a tweet or Twitter post
- Wants to share something on Twitter/X
- Says "tweet this", "help me post", "viral tweet"
- Wants to build their audience or community
- Asks for social media content

---

## Context Loading

**CRITICAL**: Before crafting any tweet, check for a user profile or mission context. Look for files like:

```
SELF/mission-statement-and-values.md     # Mission and core values (if exists)
SELF/GOALS/                              # Goals directory (if exists)
```

If no profile files exist, ask the user 2-3 quick questions:
1. What's your mission or core message?
2. Who's your target audience?
3. What tone do you prefer? (educational, provocative, casual, professional)

---

## Core Configuration

### Define Your Voice (Customize These)

Before using this skill, define your:

- **Mission**: What are you building toward?
- **Contrarian Bet**: What do you believe that most people don't?
- **Success Metric**: How do you want to be remembered?
- **Values**: What principles guide your content?

### Voice Characteristics (Defaults)
- **Optimistic** but grounded in reality
- **Technical** but accessible to beginners
- **Contrarian** when it serves the mission
- **Generous** with knowledge and insights
- **Humble** about what you don't know
- **Urgent** about the problem you're solving

---

## Tweet Types

### 1. The Builder's Log (Build in Public)
Share what you're working on, learning, or struggling with.

**Format:**
```
[What you did/learned today]

[Insight or lesson]

[Question or CTA to engage community]
```

**Example:**
```
Today I spent 4 hours debugging an AI agent that kept hallucinating function calls.

The fix? Better system prompts, not more code.

Lesson: With AI, clarity of instruction beats complexity of implementation.

What's tripping up your AI projects right now?
```

### 2. The Manifesto
Challenge the status quo in your domain.

**Format:**
```
[Contrarian statement]

[Evidence or example]

[Vision of the future you're building]
```

**Example:**
```
Hot take: The best developers in 2030 won't have CS degrees.

They'll be artists, teachers, and kids who learned to direct AI agents.

We're not just changing how software is built. We're changing WHO can build it.
```

### 3. The Teaching Moment
Share knowledge that empowers others.

**Format:**
```
[Specific technique or insight]

[Why it matters]

[How to apply it]
```

**Example:**
```
The #1 skill for working with AI coding agents isn't coding.

It's writing clear instructions.

If you can explain what you want to a smart 10-year-old, you can build software with AI.

Start here: describe your app in 3 sentences. That's your prompt.
```

### 4. The Community Spotlight
Celebrate and elevate community members.

**Format:**
```
[Shoutout to person/project]

[What they accomplished]

[Why it matters to the mission]
```

### 5. The Progress Report
Share milestones that prove the vision is working.

**Format:**
```
[Milestone achieved]

[What it means]

[Gratitude + next step]
```

### 6. The Contrarian Take
Challenge conventional wisdom in your space.

**Format:**
```
[Controversial opinion]

[Your reasoning]

[The implication]
```

### 7. The Personal Story
Share authentic moments that reveal your humanity.

**Format:**
```
[Vulnerable moment or struggle]

[What you learned]

[How it connects to mission]
```

### 8. The Thread Teaser
Set up a longer-form thread.

**Format:**
```
[Bold claim or question]

[Promise of value]

[Thread indicator]

🧵
```

---

## Engagement Principles

### DO:
- Ask questions that invite responses
- Respond to every reply in the first 2 hours
- Quote-tweet community wins with your commentary
- Share failures as openly as successes
- Tag people who inspired the thought (when genuine)
- Use line breaks for readability
- End with clear CTA when appropriate

### DON'T:
- Chase trends that don't align with your mission
- Dunk on competitors or critics
- Brag without adding value
- Post for posting's sake
- Use engagement bait that feels inauthentic

---

## Posting Strategy

### Best Times (adjust for your timezone)
- 6-7 AM EST: Early morning builders
- 12-1 PM EST: Lunch break scrollers
- 5-6 PM EST: End of workday
- 8-9 PM EST: Evening engagement

### Weekly Cadence
- **Monday**: Builder's Log (start the week)
- **Tuesday**: Teaching Moment
- **Wednesday**: Contrarian Take
- **Thursday**: Community Spotlight
- **Friday**: Progress Report
- **Weekend**: Personal Story or Thread

### Engagement Rule
After posting, stay active for 30+ minutes responding to replies. Early engagement signals to the algorithm.

---

## Quality Checklist

Before posting, verify:

- [ ] **Mission-aligned**: Does this serve your core mission?
- [ ] **Value-adding**: Will readers learn something or feel inspired?
- [ ] **Authentic**: Would you say this in person to your community?
- [ ] **Clear**: Can a non-technical person understand this?
- [ ] **Engaging**: Is there a hook? A question? A reason to respond?
- [ ] **Humble**: Are you teaching or bragging?
- [ ] **Community-building**: Does this strengthen or fragment?

---

## Anti-Patterns to Avoid

### Content That Doesn't Fit
- Political hot takes unrelated to your domain
- Negativity about other builders
- Humble-bragging disguised as teaching
- Generic motivation without specific value

### Tone Violations
- Arrogance or "guru" energy
- Desperation for engagement
- Inauthenticity (saying what you think people want to hear)
- Complaining without constructive framing

---

## Output Format

When generating tweets, provide:

1. **The Tweet** (under 280 characters, or indicate if thread)
2. **Tweet Type** (from the 8 types above)
3. **Mission Alignment** (1 sentence on how it serves goals)
4. **Best Time to Post** (suggestion)
5. **Engagement Prompt** (what to do after posting)

---

## Generating Tweets

### From a Topic
If user provides a topic:
1. Check for profile/mission context files
2. Determine which tweet type fits best
3. Frame through mission lens
4. Generate 2-3 variations
5. Recommend best one with rationale

### From Scratch
If user wants general content:
1. Check for profile/mission context files
2. Check recent goals and progress
3. Generate one of each type relevant to current phase
4. Let user choose or combine

### From Content
If user provides content to share (article, video, milestone):
1. Extract key insight that aligns with mission
2. Frame as teaching moment or progress report
3. Add community engagement element
4. Provide 2-3 angle options

---

## Hashtag Strategy

### Usage Rules
- Use 1-2 hashtags per tweet max
- Pick hashtags relevant to your niche
- Avoid more than 3 hashtags (looks spammy)
- Don't chase trending tags unrelated to your mission

### Common Tech/Builder Hashtags
- #BuildInPublic
- #IndieHacker
- #StartupLife
- #LearnToCode

---

## Metrics That Matter

Track these, not vanity metrics:

1. **Replies per tweet** (community engagement)
2. **Followers gained who match target audience**
3. **DMs from people wanting to learn/join** (community growth)
4. **Quote tweets with thoughtful additions** (thought leadership)
5. **Questions from your target audience** (reaching the right people)

---

## Subcommands

### /viral-tweet:write [topic]
Generate a mission-aligned tweet about a specific topic

### /viral-tweet:daily
Generate today's tweet based on the weekly cadence

### /viral-tweet:react [content]
React to news/content through your mission lens

### /viral-tweet:thread [topic]
Generate a full thread (5-10 tweets) on a topic

### /viral-tweet:audit [tweet]
Check if a draft tweet aligns with values and mission

---

## Remember

You're not building a following. You're building a movement.

Every tweet is a small act of sharing knowledge, celebrating builders, and proving that the future belongs to everyone willing to learn and create.
