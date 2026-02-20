---
name: blog-image-gen
description: >
  Generates high-quality images for blog posts using Google's Imagen API via Gemini.
  Use this skill when users want to create images from text prompts for blog posts,
  articles, social media, or YouTube thumbnails. Triggers on requests like
  "generate blog images", "create images for my article", "make thumbnails",
  or when image-prompts.md files exist in OUTPUT folders.
---

# Blog Image Generator Skill

Generate high-quality images for blog posts, articles, and social media using Google's Imagen API.

## Prerequisites

### Required Environment Variable
```bash
GEMINI_API_KEY=<your Google AI API key>
# or
GOOGLE_AI_API_KEY=<your Google AI API key>
```

Get your API key from: https://aistudio.google.com/apikey

### Required Dependencies
```bash
pip install google-genai pillow
```

## Usage

### Basic Usage

Generate a single image:
```bash
python .claude/skills/blog-image-gen/scripts/generate_blog_images.py \
  --prompt "A confident software developer at a command center with 5 glowing terminal screens" \
  --output OUTPUT/my-blog/images/hero.png
```

### Generate from Prompts File

Generate all images from an image-prompts.md file:
```bash
python .claude/skills/blog-image-gen/scripts/generate_blog_images.py \
  --prompts-file OUTPUT/20260119/personal-ai-infrastructure-claude-code/image-prompts.md \
  --output-dir OUTPUT/20260119/personal-ai-infrastructure-claude-code/images
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--prompt` | Single text prompt to generate | - |
| `--prompts-file` | Path to markdown file with prompts | - |
| `--output` | Output path for single image | `output.png` |
| `--output-dir` | Output directory for multiple images | Current directory |
| `--model` | Model to use (see below) | `imagen-4` |
| `--aspect-ratio` | Image aspect ratio | `16:9` |
| `--count` | Number of images per prompt | `1` |
| `--size` | Image size: `1K` or `2K` | `1K` |

### Available Models

| Model | Description | Cost | Best For |
|-------|-------------|------|----------|
| `imagen-4` | Imagen 4 Standard (default) | ~$0.02/image | General purpose, good quality |
| `imagen-4-ultra` | Imagen 4 Ultra | ~$0.04/image | Highest quality, fine details |
| `imagen-4-fast` | Imagen 4 Fast | ~$0.01/image | Quick iterations, drafts |
| `gemini-image` | Gemini 2.5 Flash Image | ~$0.02/image | Creative, contextual images |

### Aspect Ratios

Supported ratios: `1:1`, `3:4`, `4:3`, `9:16`, `16:9`

- **16:9** - YouTube thumbnails, blog headers, landscape
- **1:1** - Social media, Twitter, Instagram square
- **9:16** - Instagram stories, TikTok, vertical
- **4:3** - Presentations, traditional photos
- **3:4** - Portrait orientation

## Workflow

### Step 1: Create Image Prompts

Create an `image-prompts.md` file with your prompts. Use this format:

```markdown
# Image Prompts

## Prompt 1: Hero Image

**Use case:** Blog header

\`\`\`
A confident software developer sitting at a command center desk with
5 glowing terminal screens arranged in a semicircle. Soft blue and
purple ambient lighting. Cinematic composition, photorealistic.
\`\`\`

## Prompt 2: Concept Diagram

**Use case:** Article section

\`\`\`
Abstract visualization of a human brain merging with a digital neural
network. Flowing data streams in electric blue. Dark background with
bioluminescent accents. Digital art, high detail.
\`\`\`
```

### Step 2: Generate Images

```bash
python .claude/skills/blog-image-gen/scripts/generate_blog_images.py \
  --prompts-file OUTPUT/my-blog/image-prompts.md \
  --output-dir OUTPUT/my-blog/images \
  --model imagen-4 \
  --aspect-ratio 16:9
```

### Step 3: Review and Regenerate

If an image doesn't meet expectations:
```bash
# Regenerate a specific prompt with different settings
python .claude/skills/blog-image-gen/scripts/generate_blog_images.py \
  --prompt "Your refined prompt here" \
  --output OUTPUT/my-blog/images/hero-v2.png \
  --model imagen-4-ultra \
  --size 2K
```

## Prompt Best Practices

### Do Include
- **Subject**: What/who is in the image
- **Action**: What's happening
- **Setting**: Where it takes place
- **Lighting**: Type of light (soft, dramatic, natural)
- **Style**: Photorealistic, digital art, illustration
- **Composition**: Camera angle, framing

### Example Good Prompt
```
A confident software developer sitting at a command center desk with
5 glowing terminal screens arranged in a semicircle, each showing
different code outputs. The developer has a calm, managerial posture
with arms crossed, observing rather than typing. Soft blue and purple
ambient lighting. Futuristic but realistic office setting. Cinematic
composition, shallow depth of field, photorealistic.
```

### Avoid
- Copyrighted characters or brands
- Specific real people's names
- Overly complex scenes with many elements
- Contradictory instructions

## Output

Generated images:
- Include SynthID watermark (invisible, identifies as AI-generated)
- PNG format by default
- Named based on prompt number or custom output path

## Troubleshooting

### "API key not found"
Set your environment variable:
```bash
export GEMINI_API_KEY="your-key-here"
```

### "Model not available"
Ensure your API key has access to Imagen models. Some models require billing enabled.

### "Image blocked by safety filter"
Modify your prompt to avoid potentially sensitive content. The API has built-in safety filters.

### Rate limits
If you hit rate limits, wait a few seconds between requests or use the `--delay` flag:
```bash
python generate_blog_images.py --prompts-file prompts.md --delay 2
```
