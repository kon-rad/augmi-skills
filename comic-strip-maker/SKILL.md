---
name: comic-strip-maker
description: >
  Generates comic strips and manga-style cartoon pages using Google's Nano Banana 3
  model via Gemini API. IMPORTANT: Before generating, Claude MUST first interview the
  user about their story — ask about characters, themes, setting, mood, visual style,
  and any reference images. Develop the story collaboratively, confirm the concept with
  the user, and only then generate the comic. Creates multi-panel comic pages with
  consistent art style, speech bubbles, and dynamic compositions.
  Triggers on requests like "create a comic strip", "make a manga page",
  "generate a cartoon", or "draw a comic".
user_invocable:
  - name: create
    description: "Create a comic strip from a story prompt"
  - name: panels
    description: "Create a multi-panel comic page from a scene description"
  - name: strip
    description: "Create a horizontal comic strip (3-4 panels)"
---

# Comic Strip Maker Skill

Generate comic strips and manga-style cartoon pages from text prompts using Google's Nano Banana 3 model.

## Overview

This skill creates comic strips through a collaborative story development process. It:

1. **Interviews the user** about their story idea — asking about themes, characters, setting, mood, and visual style
2. **Develops the story** by crafting a detailed prompt based on the user's answers
3. **Confirms the story** with the user before generating anything
4. **Generates an optimized comic prompt** using Gemini to translate the story into visual panel descriptions
5. **Creates the comic** using Nano Banana 3, which excels at comic/manga panel layouts
6. **Outputs a single PNG image** in the current working directory and tells the user where it is

## Story Interview (IMPORTANT — Do This First)

**Before running the script, Claude MUST interview the user to develop the story.** Do NOT skip straight to generation. The interview ensures the comic matches what the user actually wants.

### Interview Questions

Ask the user these questions conversationally (not all at once — adapt based on their responses):

1. **Core Idea**: "What's the basic story or scene you want to capture? A joke, a dramatic moment, an action sequence?"
2. **Characters**: "Who are the main characters? Describe their appearance — hair, clothing, distinguishing features. Do you have reference images for any characters?"
3. **Setting**: "Where does this take place? What's the environment — city, nature, space, indoors? Any specific real-world location?"
4. **Themes & Mood**: "What themes do you want to explore? What's the emotional tone — funny, dramatic, mysterious, heartwarming, dark?"
5. **Visual Style**: "What art style are you going for? Any anime/manga/comic references? (e.g., Cowboy Bebop, Studio Ghibli, Marvel, etc.) Do you have a style reference image?"
6. **Color Palette**: "Any color preferences? Neon cyberpunk, warm sunset tones, pastel, dark and moody, vibrant?"
7. **Text & Dialogue**: "Should characters have speech bubbles? What language? Any specific lines of dialogue you want included?"
8. **Assets**: "Do you have any images to include — character face photos, logos, brand images, style reference images?"
9. **Layout**: "Do you prefer a horizontal strip (social media friendly), a full manga page, a 4-panel comic, or a grid layout?"

### After the Interview

Once you have enough information:

1. **Summarize the story** back to the user in a concise paragraph
2. **List the generation settings** you'll use (layout, style, panels, mood, aspect ratio)
3. **Confirm with the user**: "Does this capture what you're going for? Any changes before I generate?"
4. **Only after confirmation**, construct the prompt and run the script

### Tips for Building Good Prompts from Interview Answers

- **Be extremely specific** about character appearance in every panel description (hair color, clothing, accessories)
- **Describe each panel individually** with setting, action, and dialogue
- **Specify the color palette explicitly** (e.g., "deep blues, warm oranges, neon purple")
- **Include "FULL COLOR"** at the start if the user wants color (most do)
- **Add "ALL TEXT IN ENGLISH"** unless the user specifically wants Japanese text
- **Avoid sending reference images that could confuse the model** — if a character photo has artistic elements (pencils, swirls, etc.), describe the character in text instead
- **The cross/plus logo can be misinterpreted as Swiss flag** — describe logos in text rather than uploading if they contain crosses

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

## Commands

### /comic-strip-maker:create

Create a comic strip. Claude will **interview you first** about your story, characters, themes, and visual style before generating anything. You can provide a starting idea or let Claude guide you from scratch.

**Usage:**
```bash
# With a starting idea (Claude will ask follow-up questions)
/comic-strip-maker:create A cat discovers it can fly and surprises its owner

# With a detailed concept (Claude will confirm and refine)
/comic-strip-maker:create A cyberpunk story about a hacker in a tropical jungle school, Cowboy Bebop style

# From scratch (Claude will guide the story development)
/comic-strip-maker:create
```

### /comic-strip-maker:panels

Create a multi-panel comic page. Claude will discuss the story with you first, then generate a page with varied panel sizes for dramatic storytelling.

**Usage:**
```bash
/comic-strip-maker:panels A hero discovers a mysterious glowing sword in a cave, picks it up, and transforms
```

### /comic-strip-maker:strip

Create a horizontal comic strip (3-4 panels in a row), great for social media or blog posts. Claude will confirm the story and tone before generating.

**Usage:**
```bash
/comic-strip-maker:strip A developer explains recursion to a rubber duck, the duck starts recursing
```

## Script Usage

### Basic Usage - From Prompt

```bash
export $(grep -v '^#' .env.local | xargs) && python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "A cat accidentally becomes the captain of a spaceship" \
  --output comic.png
```

### With a Character Face

```bash
export $(grep -v '^#' .env.local | xargs) && python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "A hero discovers they have superpowers at the office" \
  --character my-face.jpg \
  --output hero-comic.png
```

### With Logo and Style Reference

```bash
export $(grep -v '^#' .env.local | xargs) && python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "A startup launches their product" \
  --logo company-logo.png \
  --style-ref watercolor-comic.jpg \
  --output launch-comic.png
```

### With Layout Options

```bash
export $(grep -v '^#' .env.local | xargs) && python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "Two robots discover what friendship means" \
  --layout manga \
  --panels 4 \
  --output manga-page.png
```

### From Story File

```bash
export $(grep -v '^#' .env.local | xargs) && python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --story-file my-story.md \
  --output comic.png
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--prompt` | Story/scene description for the comic | - |
| `--story-file` | Path to markdown file with story | - |
| `--output` | Output path for generated image | `comic-strip.png` |
| `--layout` | Panel layout style (see below) | `strip` |
| `--panels` | Number of panels (2-6) | `3` |
| `--aspect-ratio` | Image aspect ratio | `16:9` |
| `--style` | Art sub-style | `modern-anime` |
| `--mood` | Mood/tone override | Auto-detected |
| `--character` | Character/face reference image(s) | - |
| `--logo` | Logo image(s) to include in the comic | - |
| `--style-ref` | Style reference image(s) to match | - |
| `--verbose` | Show generated prompt details | `false` |

### Reference Images

You can pass images to guide the comic's look. These are sent to both the prompt generator (Gemini Flash) and the image generator (Nano Banana 3) so the output matches your references.

| Flag | What It Does | Example |
|------|-------------|---------|
| `--character` | Main character looks like this person (face, hair, features) | `--character photo.jpg` |
| `--logo` | This logo appears in the comic (on a shirt, sign, screen, etc.) | `--logo brand.png` |
| `--style-ref` | Match this art style instead of the preset | `--style-ref watercolor-sample.jpg` |

Each flag accepts one or more image paths (jpg, png, webp). Multiple images can be passed: `--character face1.jpg face2.jpg`

### Layout Styles

| Layout | Description | Best For |
|--------|-------------|----------|
| `strip` | Horizontal 3-4 equal panels (default) | Jokes, gags, social media |
| `manga` | Traditional manga page with varied panel sizes | Full stories, dramatic moments |
| `4-koma` | Vertical 4-panel comic (Japanese yonkoma style) | Comedy, slice-of-life |
| `splash` | Single large panel with inset detail panels | Action scenes, reveals |
| `grid` | Even grid layout (2x2 or 2x3) | Sequential events, tutorials |

### Art Sub-Styles

| Style | Description |
|-------|-------------|
| `modern-anime` | Clean lines, vibrant colors, Studio Ghibli-meets-modern aesthetic (default) |
| `shonen` | Bold, dynamic action style (Dragon Ball, Naruto) |
| `shoujo` | Soft, sparkly, emotional style (Sailor Moon) |
| `chibi` | Cute, super-deformed characters |
| `seinen` | Detailed, mature art style |
| `retro` | 80s/90s anime aesthetic |

## Workflow

### Step 1: Story Interview

Claude asks the user about their story idea. This is a conversation, not a form — adapt questions based on what the user shares. Some users arrive with a detailed vision; others need guidance.

**If user provides a detailed concept**: Confirm understanding, ask about visual style and any missing details (characters, setting, mood), then summarize.

**If user provides a vague idea**: Ask about themes, characters, setting, and mood to flesh it out. Suggest creative directions. Build the story together.

**If user provides no prompt**: Ask "What kind of story excites you?" and guide from there — offer genre options (comedy, sci-fi, drama, action, slice-of-life) and build collaboratively.

### Step 2: Confirm the Story

Before generating, present the user with:
- **Story summary**: 2-3 sentence description of what will be generated
- **Panel breakdown**: What happens in each panel
- **Settings**: Layout, style, panels, mood, aspect ratio
- **Assets**: Any character images, logos, or style references being used

Ask: "Ready to generate, or want to adjust anything?"

### Step 3: Generate the Comic

Only after user confirms, run the script:
```bash
export $(grep -v '^#' .env.local | xargs) && python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "The detailed story prompt built from the interview" \
  --layout strip \
  --panels 4 \
  --style modern-anime \
  --output my-comic.png
```

### Step 4: Review and Iterate

Show the user the generated image. Ask if they want to:
- **Adjust the story**: Change dialogue, setting, or character details
- **Try a different style**: Switch from modern-anime to chibi, seinen, etc.
- **Try a different layout**: Switch from strip to manga, grid, 4-koma, etc.
- **Regenerate**: Same prompt, new random result
- **Accept**: Done!

## How It Works

1. **Story Analysis**: Gemini analyzes the user's prompt and determines:
   - Key story beats (setup, action, punchline/resolution)
   - Character descriptions for consistency
   - Emotional tone and mood
   - Optimal panel arrangement

2. **Prompt Engineering**: Generates a detailed Nano Banana 3 prompt that includes:
   - Panel layout instructions (sizes, positions)
   - Per-panel scene descriptions
   - Character consistency cues
   - Speech bubble text and placement
   - Art style directives (line weight, shading, color palette)
   - Comic visual effects (speed lines, emotion marks, screen tones)

3. **Image Generation**: Nano Banana 3 renders the full comic page in a single generation, maintaining:
   - Consistent character designs across panels
   - Proper reading flow (left-to-right for strips, right-to-left for manga)
   - Dynamic compositions per panel
   - Appropriate comic visual effects

## Prompt Best Practices

### Good Prompts
- "A shy girl confesses her feelings under cherry blossoms, but a gust of wind blows her letter away, and a boy catches it"
- "A knight discovers the dragon they came to slay is actually tiny and adorable"
- "Two rival chefs have an epic cooking battle, but both make the same dish"

### Tips
- Include **characters** (who), **action** (what happens), and **twist/resolution**
- 2-3 sentences is ideal; the skill expands it into panel descriptions
- Mention **emotion** if important ("comedic", "dramatic", "heartwarming")
- For speech bubbles, you can include dialogue: `"Character says: 'Hello!'"`

### Avoid
- Overly complex plots (keep to 1-2 beats per page)
- More than 3-4 characters (hard to maintain consistency)
- Real people's names or copyrighted characters
- Explicit or violent content (will be blocked by safety filters)

## Examples

### Comedy Strip
```bash
python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "A programmer asks AI to write code, AI writes code that writes code, infinite loop of AIs writing code while programmer stares in horror" \
  --layout strip \
  --style chibi \
  --output ai-loop-strip.png
```

### Character Face in a Comic
```bash
python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "A developer wins a hackathon and celebrates with their team" \
  --character my-headshot.jpg \
  --layout strip \
  --output hackathon-comic.png
```

### Branded Comic with Logo
```bash
python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "A team ships a new feature and users love it" \
  --logo company-logo.png \
  --character ceo-photo.jpg \
  --style modern-anime \
  --output branded-comic.png
```

### Match a Specific Art Style
```bash
python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "A knight discovers the dragon is actually friendly" \
  --style-ref watercolor-manga-sample.jpg \
  --layout manga \
  --panels 4 \
  --output watercolor-comic.png
```

### Dramatic Manga Page
```bash
python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "A lone samurai stands at the edge of a cliff as the sun sets, remembers their fallen companions, then unsheathes their sword with determination" \
  --layout manga \
  --panels 5 \
  --style seinen \
  --mood dramatic \
  --output samurai-page.png
```

### Cute 4-Koma
```bash
python3 .claude/skills/comic-strip-maker/scripts/generate_comic_strip.py \
  --prompt "A cat tries to fit into progressively smaller boxes, ending with squeezing into a matchbox" \
  --layout 4-koma \
  --style chibi \
  --output cat-boxes-4koma.png
```

## Output

- **Format**: PNG, saved to the current working directory (or path specified with `--output`)
- **Quality**: High resolution suitable for web, social media, or print
- **Includes**: SynthID watermark (invisible, identifies as AI-generated)
- **Typical size**: 1-3 MB depending on detail level

After generation, the script prints the full path to the saved image.

## Cost

- ~$0.04 per image generation (Nano Banana Pro)
- ~$0.001 for prompt analysis (Gemini Flash)
- **Total: ~$0.04 per comic strip**

## Troubleshooting

### "API key not found"
Set your environment variable:
```bash
export GEMINI_API_KEY="your-key-here"
```

### "Model not available"
The Nano Banana model (`nano-banana-pro-preview`) requires API access. Ensure your API key has access to preview models at https://aistudio.google.com.

### "Image blocked by safety filter"
Modify your prompt to avoid potentially sensitive content. Try adding `--style chibi` for safer, more cartoonish outputs.

### Panels not well-defined
Some generations may blend panel boundaries. Tips:
- Use `--layout grid` for the most consistent panel separation
- Add explicit panel count with `--panels`
- Regenerate with a more specific prompt

### Characters look different across panels
This is a limitation of single-image generation. Tips:
- Describe characters distinctively (hair color, outfit, accessories)
- Use `--style chibi` for more consistent simplified characters
- Keep character count low (2-3 max)
