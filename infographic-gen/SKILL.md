---
name: infographic-gen
description: >
  Generates infographics from a topic by conducting research, then using an AI infographic designer
  to create an optimized prompt, and finally generating the visual using Google's Nano Banana 3 model.
  Use this skill when users want to create infographics, data visualizations, or educational graphics
  from a topic or concept. Triggers on requests like "create an infographic about", "generate an
  infographic for", "make a visual explainer about", or "design an infographic".
user_invocable:
  - name: generate
    description: "Generate an infographic from a topic with automatic research"
  - name: from-content
    description: "Generate an infographic from provided content/research (skip research phase)"
---

# Infographic Generator Skill

Generate professional infographics from any topic using AI-powered research and design.

## Overview

This skill automates the entire infographic creation workflow:

1. **Research Phase**: Conducts web research on the topic to gather facts, statistics, and key points
2. **Design Phase**: Uses an AI infographic designer to analyze the research and create an optimized image prompt
3. **Generation Phase**: Uses Google's Nano Banana 3 model to generate the final infographic

## Prerequisites

### Required Environment Variable
```bash
GEMINI_API_KEY=<your Google AI API key>
```

The API key should be in the root `.env` file. Get your API key from: https://aistudio.google.com/apikey

### Required Dependencies
```bash
pip install google-genai pillow requests
```

## Commands

### /infographic-gen:generate

Generate an infographic with automatic research on the topic.

**Usage:**
```bash
/infographic-gen:generate "The Rise of AI Agents in 2026"
```

**Options:**
- Topic (required): The subject to research and visualize
- `--style`: Visual style (modern, minimal, corporate, playful, technical)
- `--aspect-ratio`: Image ratio (16:9, 1:1, 9:16, 4:3)
- `--output`: Output file path

### /infographic-gen:from-content

Generate an infographic from existing content (skip research phase).

**Usage:**
```bash
/infographic-gen:from-content --file research.md --output infographic.png
```

## Script Usage

### Basic Usage - From Topic

```bash
# Load env and generate
export $(grep -v '^#' .env | xargs) && python3 .claude/skills/infographic-gen/scripts/generate_infographic.py \
  --topic "The Growth of Electric Vehicles" \
  --output OUTPUT/infographics/ev-growth.png
```

### From Existing Content

```bash
export $(grep -v '^#' .env | xargs) && python3 .claude/skills/infographic-gen/scripts/generate_infographic.py \
  --content "Your research content here..." \
  --output my-infographic.png
```

### From File

```bash
export $(grep -v '^#' .env | xargs) && python3 .claude/skills/infographic-gen/scripts/generate_infographic.py \
  --file INPUT/20260201/research.md \
  --output infographic.png
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--topic` | Topic to research and visualize | - |
| `--content` | Direct content to visualize (skip research) | - |
| `--file` | Path to file with content to visualize | - |
| `--output` | Output path for generated image | `infographic.png` |
| `--aspect-ratio` | Image aspect ratio | `16:9` |
| `--style` | Infographic style | `modern` |
| `--verbose` | Show detailed output including prompts | `false` |
| `--save-research` | Save research to file | `false` |
| `--save-prompt` | Save generated prompt to file | `false` |

### Styles

| Style | Description | Best For |
|-------|-------------|----------|
| `modern` | Clean, bold typography, vibrant colors | General purpose |
| `minimal` | White space, simple icons, muted palette | Professional |
| `corporate` | Traditional, structured, data-focused | Business |
| `playful` | Colorful, illustrated, engaging | Education |
| `technical` | Detailed, precise, diagram-focused | Tech topics |
| `dark` | Dark background, neon accents | Tech/gaming |

### Aspect Ratios

- **16:9** - Presentations, blog headers, YouTube
- **1:1** - Social media squares, Instagram
- **9:16** - Stories, Pinterest, vertical displays
- **4:3** - Traditional presentations
- **3:4** - Portrait infographics

## How It Works

### Phase 1: Research (if topic provided)

The script uses Gemini to search and gather:
- Key facts and statistics
- Important dates and milestones
- Notable quotes or statements
- Relevant comparisons
- Current trends

Research is structured for infographic use with:
- Headline-worthy findings
- Quotable statistics
- Logical flow of information

### Phase 2: Infographic Design

An AI infographic designer analyzes the content and creates:
- Visual hierarchy and layout concept
- Color palette recommendations
- Icon and illustration suggestions
- Typography guidance
- Data visualization approach

The designer generates an optimized prompt that captures:
- Core message and headline
- Visual metaphors and symbols
- Data representation style
- Emotional tone and mood
- Composition and balance

### Phase 3: Image Generation

Uses Nano Banana 3 (`gemini-2.0-flash-exp`) to generate the final infographic based on the optimized prompt.

## Example Workflow

**Input:** Topic "The Impact of Sleep on Productivity"

**Phase 1 - Research Output:**
```
Key Statistics:
- Adults need 7-9 hours of sleep per night
- Sleep deprivation costs US employers $411 billion annually
- 35% of adults report getting less than 7 hours
- Productivity drops 29% after a poor night's sleep
...
```

**Phase 2 - Designer Prompt:**
```
Professional infographic about sleep and productivity. Layout: vertical flow with
headline at top. Visual elements: Large moon-to-sun gradient header, sleeping
figure icon, clock showing recommended hours, downward arrow to productivity
graph, dollar signs for economic impact. Color palette: Deep navy (#1a237e),
soft purple (#7c4dff), warm amber accent (#ffc107). Typography: Bold sans-serif
headlines, clean body text. Data viz: Simple bar chart showing productivity drop,
circular percentage displays. Style: Modern, clean, corporate-friendly...
```

**Phase 3 - Generated Infographic:** High-quality PNG image

## Troubleshooting

### "Research failed"
- Check your API key has access to Gemini models
- The topic may be too niche for web research
- Try providing content directly with `--content` or `--file`

### "Image generation blocked"
- The prompt may have triggered safety filters
- Try a different `--style` option
- Simplify the topic or content

### "Model not available"
- Nano Banana 3 requires API access to preview models
- Ensure your API key has access to `gemini-2.0-flash-exp`

## Output

- PNG format by default
- High quality suitable for presentations and social media
- Includes SynthID watermark (invisible, identifies as AI-generated)
- Optional: Saved research and prompt files for iteration

## Tips for Best Results

1. **Be specific**: "AI agents in enterprise software 2026" > "AI"
2. **Include context**: Add industry, time period, or audience
3. **Choose appropriate style**: Match style to content tone
4. **Iterate**: Use `--save-prompt` to refine the design prompt manually
5. **Combine with research**: Use deep-research skill first for complex topics
