---
name: blog-visual-gen
description: >
  Generates graphic visuals from blog post content using Google's Nano Banana 3 model via Gemini API.
  Use this skill when users want to create a visual representation of a blog post, article, or text content.
  The AI reads the content and generates a contextually relevant image that captures the essence of the post.
  Triggers on requests like "create a visual for this blog post", "generate a graphic from my article",
  or "make a blog visual".
user_invocable:
  - name: generate
    description: "Generate a visual from a blog post file or text"
  - name: from-file
    description: "Generate a visual from a specific blog post markdown file"
---

# Blog Visual Generator Skill

Generate contextually relevant graphic visuals from blog post content using Google's Nano Banana 3 model.

## Overview

This skill analyzes blog post content and generates an image that visually represents the key themes, concepts, and mood of the article. Unlike simple prompt-to-image generation, this skill:

1. **Reads and analyzes** the full blog post content
2. **Extracts key themes** and visual concepts
3. **Generates a custom prompt** optimized for the content
4. **Creates a visual** using Nano Banana 3 (Google's advanced image generation model)

## Prerequisites

### Required Environment Variable
```bash
GEMINI_API_KEY=<your Google AI API key>
```

The API key should be in the root `.env` file. Get your API key from: https://aistudio.google.com/apikey

### Required Dependencies
```bash
pip install google-genai pillow
```

## Commands

### /blog-visual-gen:generate

Generate a visual from blog post content provided as text or from a file.

**Usage:**
```bash
# From a file
/blog-visual-gen:generate OUTPUT/20260127/my-blog-post/blog-post.md

# The skill will analyze the content and generate an appropriate visual
```

### /blog-visual-gen:from-file

Generate a visual specifically from a markdown file path.

**Usage:**
```bash
/blog-visual-gen:from-file OUTPUT/20260127/social-prediction-markets/blog-post.md
```

## Script Usage

### Basic Usage - From File

```bash
# Load env and run
export $(grep -v '^#' .env | xargs) && python3 .claude/skills/blog-visual-gen/scripts/generate_blog_visual.py \
  --file OUTPUT/20260127/my-blog/blog-post.md \
  --output OUTPUT/20260127/my-blog/images/blog-visual.png
```

### Basic Usage - From Text

```bash
export $(grep -v '^#' .env | xargs) && python3 .claude/skills/blog-visual-gen/scripts/generate_blog_visual.py \
  --text "Your blog post content here..." \
  --output my-visual.png
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--file` | Path to blog post markdown file | - |
| `--text` | Direct text content to visualize | - |
| `--output` | Output path for generated image | `blog-visual.png` |
| `--aspect-ratio` | Image aspect ratio | `16:9` |
| `--style` | Visual style hint | `modern digital art` |
| `--verbose` | Show detailed output including generated prompt | `false` |

### Aspect Ratios

Supported: `1:1`, `3:4`, `4:3`, `9:16`, `16:9`

- **16:9** - Blog headers, YouTube thumbnails (default)
- **1:1** - Social media squares
- **9:16** - Stories, vertical content
- **4:3** - Presentations

## How It Works

1. **Content Analysis**: The script reads the blog post and uses Gemini to analyze:
   - Main theme and topic
   - Key concepts and ideas
   - Emotional tone
   - Visual metaphors present in the text

2. **Prompt Generation**: Based on analysis, generates an optimized image prompt that captures:
   - Core visual concept
   - Appropriate style and mood
   - Relevant symbolic elements
   - Color palette suggestions

3. **Image Generation**: Uses Nano Banana 3 (`nano-banana-pro-preview`) to create the final visual

## Examples

### Example 1: Tech Blog Post

Input: A blog post about "Building a Social Prediction Market"

Generated prompt might be:
```
A vibrant digital illustration of interconnected people represented as glowing nodes
forming a honeycomb network pattern, with floating prediction probability displays
and golden data streams flowing between connections. Modern tech aesthetic with
warm amber and electric blue color palette. Clean, optimistic, social.
```

### Example 2: Philosophy Post

Input: A blog post about "The Wisdom of Crowds"

Generated prompt might be:
```
Abstract visualization of collective intelligence - thousands of small luminous
particles converging to form a larger coherent shape resembling a brain or
lightbulb, set against a deep space background. Ethereal, contemplative mood
with soft purple and gold gradients.
```

## Troubleshooting

### "Model not available"
The Nano Banana model (`nano-banana-pro-preview`) requires API access. Ensure your API key has access to preview models.

### "Content too short"
The script needs meaningful content to analyze. Provide at least a few paragraphs.

### "Image blocked"
The generated prompt may have triggered safety filters. Try adding `--style "professional illustration"` for safer outputs.

## Output

- PNG format by default
- High quality suitable for blog headers
- Includes SynthID watermark (invisible, identifies as AI-generated)
