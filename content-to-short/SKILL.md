---
name: content-to-short
description: |
  Generates short-form vertical videos (30-90 seconds, 9:16) from any content input — blog posts,
  articles, stories, or topics. Features two modes: Interactive (with clarifying prompts) or
  Fully Automated (runs the entire pipeline with sensible defaults). Supports Deepgram Aura-2
  TTS with 40+ voice options, optional subtitle burning, web/AI images, AI video clips, and
  background music. This skill should be used when the user wants to turn content into a short
  video, reel, YouTube Short, or TikTok clip. Triggers on requests like "turn this blog post
  into a short video", "make a reel from this article", "create a TikTok from this content".
allowed-tools:
  - Bash(content-to-short:*)
---

# Content-to-Short Video Generator

Turn any content (blog posts, articles, stories, or topics) into 30-90 second vertical videos
(9:16) for YouTube Shorts, Instagram Reels, and TikTok.

## Prerequisites

### API Keys

Set the following environment variables (see `assets/.env.example`):

- `DEEPGRAM_API_KEY` - Text-to-speech narration ([console.deepgram.com](https://console.deepgram.com))
- `GEMINI_API_KEY` or `GOOGLE_AI_API_KEY` - AI image generation ([aistudio.google.com/apikey](https://aistudio.google.com/apikey))
- `PEXELS_API_KEY` - Web image search ([pexels.com/api](https://www.pexels.com/api/new/))
- `FAL_KEY` - Text-to-video and music generation ([fal.ai/dashboard/keys](https://fal.ai/dashboard/keys))

### System Dependencies

- `ffmpeg` - Video/audio composition (`brew install ffmpeg`)
- `python3` (3.10+)

### Python Dependencies

```bash
pip install requests google-genai pillow python-dotenv fal-client
```

## Phase 0: Mode Selection

**Ask the user at the very start:**

> How would you like to proceed?
> 1. **Interactive** — I'll ask clarifying questions about tone, visuals, duration, and voice before generating
> 2. **Automated** — I'll pick sensible defaults and run the full pipeline end-to-end

### Automated Mode Defaults

When automated mode is selected, use these defaults:
- **Duration**: 30 seconds (6 scenes)
- **Style**: `educational`
- **Visual mode**: `mixed` (hook + closer as AI video, middle scenes as web images)
- **Voice**: Auto-selected by style (see voice table below)
- **Subtitles**: Off
- **Music**: On (style-appropriate)

Skip all clarifying questions. Go straight from content parsing to final video output.

## Phase 1: Content Input

The user provides content in one of these forms:

1. **Pasted text** — blog post, article, or story pasted directly
2. **File path** — path to a markdown/text file
3. **Topic description** — a topic to generate content about from scratch

### From Content (File or Pasted Text)

```bash
# From a file
python scripts/content_to_script.py path/to/article.md --duration 30 --style educational --visual-mode mixed

# From stdin (pasted content)
echo "Your article text..." | python scripts/content_to_script.py --stdin --duration 60 --style hype
```

The content parser:
- Extracts title from first `#` heading or first sentence
- Splits into sections by `##` headings or paragraph breaks
- Selects the most impactful sections for hook, key points, and closer
- Condenses each to ~12 words per 5-second scene
- Generates image search queries and AI image prompts from each section
- Outputs `script.json`

### From Deep-Research Script

When given a `youtube-script.md` from `/deep-research:full`:

```bash
python scripts/parse_script.py path/to/youtube-script.md --duration 45 --style educational --visual-mode mixed
```

### From Topic (Interactive Only)

In interactive mode, Claude generates the script directly from a topic description.

## Phase 2: Interactive Story Development (Interactive Mode Only)

**Skip this in Automated Mode.**

Ask 2-3 clarifying questions:

1. **Duration?** Present options: 30s (6 scenes), 45s (9 scenes), 60s (12 scenes), 90s (18 scenes)
2. **Tone/Style?** Present the style options:
   - `educational` - Informative, "Did you know..." hooks
   - `promotional` - Product-focused, punchy CTAs
   - `storytelling` - Narrative arc, emotional
   - `hype` - Fast-paced, bold, trending energy
3. **Visual preference?** Present with cost estimates:

| Mode | Description | Cost Estimate | Best For |
|------|-------------|---------------|----------|
| **images-web** | Free stock photos from Pexels | Free ($0) | Quick drafts, testing |
| **images-ai** | AI-generated via Gemini Imagen | ~$0.04/image | Custom visuals, branded |
| **video-ai** | AI video clips via Fal.ai Kling | ~$0.10/clip | Premium, motion content |
| **mixed** | Web images + AI video for key scenes | ~$0.30-0.60 total | Balance of cost and quality |

4. **Voice?** Show top recommendations for their style, or `--list-voices` for all 40+
5. **Subtitles?** Yes/No (burned into the video)

Present the generated script for approval before proceeding.

## Phase 3: Script Generation

### script.json Schema

```json
{
  "title": "Short Title",
  "description": "Caption text with hashtags",
  "targetDuration": 30,
  "style": "educational",
  "visualMode": "mixed",
  "voice": "aura-2-asteria-en",
  "orientation": "portrait",
  "subtitles": false,
  "config": {
    "musicPrompt": "Upbeat electronic background music, energetic, modern",
    "musicVolume": 0.15,
    "narrationVolume": 1.0
  },
  "narration": {
    "text": "Full narration text concatenated from all scenes..."
  },
  "scenes": [
    {
      "sceneNumber": 1,
      "title": "Hook",
      "narration": "Did you know that AI agents can now...",
      "duration": 5,
      "visualType": "video",
      "imageSearchQuery": null,
      "imageGenPrompt": "A futuristic AI robot, neon lighting, vertical portrait, 9:16",
      "videoPrompt": "Camera slowly pushes in, neon lights flicker, subtle movement"
    }
  ]
}
```

#### Scene Rules

- **Each scene is exactly 5 seconds** (no longer)
- 6 scenes for 30s, 9 for 45s, 12 for 60s, 18 for 90s
- Total narration: ~75 words (30s), ~112 (45s), ~150 (60s), ~225 (90s)
- Each scene narration: ~12 words (fits 5 seconds at 2.5 wps)
- All AI image prompts MUST include "vertical portrait composition, 9:16"

#### Visual Type Assignment by Mode

- `images-web`: All scenes get `visualType: "web"`
- `images-ai`: All scenes get `visualType: "generate"`
- `video-ai`: All scenes get `visualType: "video"`
- `mixed`: Hook + closer get `visualType: "video"`, middle scenes get `visualType: "web"`

## Phase 4: Image Acquisition

```bash
# Web images (portrait orientation) — for images-web and mixed modes
python scripts/search_images.py path/to/script.json

# AI-generated images (9:16 vertical) — for images-ai, video-ai, and mixed modes
python scripts/generate_images.py path/to/script.json
python scripts/generate_images.py path/to/script.json --model imagen-4  # or imagen-4-fast, imagen-3
python scripts/generate_images.py path/to/script.json --skip-existing   # resume interrupted runs
```

**Important:** For `mixed` mode, run **both** `search_images.py` (for web scenes) **and** `generate_images.py` (for AI video scenes that need a source image).

## Phase 5: Video Generation (video-ai and mixed modes only)

```bash
python scripts/generate_videos.py path/to/script.json
python scripts/generate_videos.py path/to/script.json --model kling-pro  # higher quality
python scripts/generate_videos.py path/to/script.json --skip-existing    # resume interrupted runs
```

## Phase 6: Audio Generation

### Narration

```bash
python scripts/generate_audio.py path/to/script.json
python scripts/generate_audio.py path/to/script.json --voice aura-2-orion-en
python scripts/generate_audio.py --list-voices  # Show all 40+ voices
```

#### Deepgram Aura-2 Voice Options

**Female Voices:**

| Voice | Description | Best For |
|-------|-------------|----------|
| `aura-2-asteria-en` | Warm and clear | educational (default) |
| `aura-2-athena-en` | Confident and polished | promotional |
| `aura-2-luna-en` | Calm and professional | corporate, explainers |
| `aura-2-hera-en` | Authoritative | news, announcements |
| `aura-2-andromeda-en` | Warm and engaging | storytelling |
| `aura-2-cassiopeia-en` | Professional, neutral | business |
| `aura-2-clio-en` | Narrative, expressive | storytelling |
| `aura-2-electra-en` | Authoritative, powerful | speeches |
| `aura-2-harmonia-en` | Smooth, soothing | wellness, calm |
| `aura-2-io-en` | Casual, friendly | social media |
| `aura-2-lyra-en` | Bright, upbeat | marketing |
| `aura-2-nova-en` | Friendly, approachable | tutorials |
| `aura-2-pandora-en` | Expressive, dramatic | drama, stories |
| `aura-2-selene-en` | Soothing, gentle | meditation, ASMR |
| `aura-2-theia-en` | Powerful, dynamic | presentations |
| `aura-2-venus-en` | Elegant, refined | luxury brands |
| `aura-2-vesta-en` | Clear, articulate | education |

**Male Voices:**

| Voice | Description | Best For |
|-------|-------------|----------|
| `aura-2-orion-en` | Deep and authoritative | educational, news |
| `aura-2-arcas-en` | Energetic, fast-paced | hype (default) |
| `aura-2-perseus-en` | Warm narrator | storytelling (default) |
| `aura-2-orpheus-en` | Smooth, rich | luxury, premium |
| `aura-2-helios-en` | Professional, clear | corporate |
| `aura-2-zeus-en` | Commanding, powerful | announcements |
| `aura-2-arcturus-en` | Deep, resonant | documentaries |
| `aura-2-draco-en` | Energetic, bold | hype, gaming |
| `aura-2-mars-en` | Commanding, strong | action, military |
| `aura-2-neptune-en` | Narrative, calm | storytelling |
| `aura-2-pegasus-en` | Warm, friendly | tutorials |
| `aura-2-phoenix-en` | Dynamic, versatile | general |
| `aura-2-saturn-en` | Calm, measured | educational |
| `aura-2-sol-en` | Energetic, upbeat | marketing |
| `aura-2-titan-en` | Authoritative, deep | finance, tech |

#### Style-to-Voice Defaults

- `educational` → `aura-2-asteria-en` (female) or `aura-2-orion-en` (male)
- `promotional` → `aura-2-athena-en` (female) or `aura-2-sol-en` (male)
- `storytelling` → `aura-2-andromeda-en` (female) or `aura-2-perseus-en` (male)
- `hype` → `aura-2-lyra-en` (female) or `aura-2-arcas-en` (male)

### Background Music

```bash
python scripts/generate_music.py path/to/script.json
```

## Phase 7: Video Composition

```bash
# Without subtitles
python scripts/compose_video.py path/to/script.json

# With subtitles burned in
python scripts/compose_video.py path/to/script.json --subtitles

# No background music
python scripts/compose_video.py path/to/script.json --no-music
```

Subtitle burning:
- Auto-generates SRT from scene narrations with timestamps
- Burns white text with black outline at bottom of frame
- Uses FFmpeg `ass` filter for styled subtitles

## Directory Structure

```
INPUT/{YYYYMMDD}/{topic-slug}/
  +-- content.md              # Source content (if from file)
  +-- script.json             # Scene script

OUTPUT/{YYYYMMDD}/{topic-slug}/
  +-- images/                 # Scene images (portrait)
  +-- videos/                 # AI video clips (if video-ai/mixed)
  +-- audio/
  |   +-- narration.mp3       # Deepgram TTS
  |   +-- music.mp3           # Fal.ai background music
  +-- video/
      +-- {slug}.mp4          # Final vertical video
      +-- subtitles.srt       # Generated subtitles (if enabled)
```

## Cost Estimates

| Duration | images-web | images-ai | video-ai | mixed |
|----------|-----------|-----------|----------|-------|
| 30s (6 scenes) | $0.06 | $0.30 | $0.90 | $0.34 |
| 45s (9 scenes) | $0.06 | $0.42 | $1.32 | $0.34 |
| 60s (12 scenes) | $0.06 | $0.54 | $1.74 | $0.34 |
| 90s (18 scenes) | $0.06 | $0.78 | $2.58 | $0.34 |

*video-ai includes image generation for every scene ($0.04/image) plus video generation ($0.10/clip). mixed generates 2 AI video scenes (hook + closer) with web images for middle scenes.*

## One-Command Pipeline

Run the entire pipeline with a single command:

```bash
./scripts/run_pipeline.sh path/to/article.md --duration 45 --style hype --visual-mode mixed
./scripts/run_pipeline.sh path/to/article.md --skip-existing --subtitles
./scripts/run_pipeline.sh path/to/article.md --no-music
```

This runs all 7 steps in order: parse content, search images, generate AI images, generate video clips, narration, music, and compose.

## script.json State Evolution

The `script.json` file evolves as each pipeline step adds fields:

| After Step | Fields Added |
|------------|-------------|
| `content_to_script.py` | `title`, `scenes`, `narration.text`, `config`, `style`, `voice` |
| `search_images.py` | `scenes[].imagePath` (for web scenes) |
| `generate_images.py` | `scenes[].imagePath` (for generate/video scenes) |
| `generate_videos.py` | `scenes[].videoPath` (for video scenes) |
| `generate_audio.py` | `audioPath`, `voice` |
| `generate_music.py` | `musicPath` |
| `compose_video.py` | `outputVideo`, `actualDuration` |

## Troubleshooting

- **No portrait images**: Pexels may have fewer portrait results. Try broader queries.
- **Fal.ai timeout**: Video generation can take 30-60s per clip. Use `--delay 10`.
- **Wrong energy**: Change the `style` parameter and regenerate the script.
- **Cost too high**: Use `images-web` mode (free) or `mixed` mode.
- **Music too loud**: Adjust `musicVolume` in config (default 0.15).
- **Subtitles cut off**: The subtitle style auto-positions at bottom with margin.
- **Voice not found**: Run `--list-voices` to see all available Aura-2 voices.
