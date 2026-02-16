---
name: short-video-gen
description: |
  Generates short-form vertical videos (30-60 seconds) for YouTube Shorts, Instagram Reels,
  and TikTok. Features an interactive storyline refinement flow before generating. Supports
  three visual modes: web images only (free), AI-generated images via Gemini Imagen, or
  text-to-video clips via Fal.ai. Combines visuals with Deepgram TTS narration and Fal.ai
  background music into a vertical 9:16 MP4. Each scene is up to 5 seconds. This skill should
  be used when the user wants to create a short video, reel, YouTube Short, TikTok, or
  vertical video clip. Triggers on requests like "make a short about...", "create a reel",
  "generate a TikTok video", "make a YouTube Short".
---

# Short Video Generator

Generate 30-60 second vertical videos (9:16) for YouTube Shorts, Instagram Reels, and TikTok.
Features an interactive story development phase where Claude asks questions to refine the
storyline before generating. Supports three visual modes with cost estimation, Deepgram TTS
narration, and Fal.ai background music.

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

## Phase 1: Interactive Story Development

**This phase is mandatory.** Before generating anything, ask the user 2-3 clarifying questions:

1. **What's the core message?** "What single takeaway should viewers remember?"
2. **What's the tone/mood?** Present the style options:
   - `educational` - Informative, "Did you know..." hooks
   - `promotional` - Product-focused, punchy CTAs
   - `storytelling` - Narrative arc, emotional
   - `hype` - Fast-paced, bold, trending energy
3. **Visual preference?** Present options with cost estimates:

### Visual Mode Selection

Present this table to the user and ask which mode to use:

| Mode | Description | Cost Estimate | Best For |
|------|-------------|---------------|----------|
| **images-web** | Free stock photos from Pexels | Free ($0) | Quick drafts, testing |
| **images-ai** | AI-generated via Gemini Imagen | ~$0.04/image (~$0.24-0.48 total) | Custom visuals, branded |
| **video-ai** | AI video clips via Fal.ai Kling | ~$0.10/clip (~$0.60-1.20 total) | Premium, motion content |
| **mixed** | Web images + AI video for key scenes | ~$0.30-0.60 total | Balance of cost and quality |

**Cost breakdown per video (6-12 scenes at 5 seconds each):**
- Deepgram TTS: ~$0.01 (per narration)
- Fal.ai music: ~$0.05 (per soundtrack)
- Gemini Imagen: ~$0.04/image
- Fal.ai Kling video: ~$0.10/clip (cheapest tier)
- **Total range: $0.06 (web images) to $1.30 (all AI video)**

After answers, generate a 30-60 second script with:
- **Hook** (0-5s): Attention-grabbing opening
- **2-4 Key Points** (5s each): One idea per scene
- **Closer** (0-5s): CTA or takeaway

Present the script to the user for approval. Iterate until approved.

## Phase 2: Script Generation

### Phase 2a: From Topic (Interactive)

After user approves the storyline, generate `script.json`:

```json
{
  "title": "Short Title",
  "description": "Caption text with hashtags",
  "targetDuration": 30,
  "style": "educational",
  "visualMode": "mixed",
  "voice": "aura-asteria-en",
  "orientation": "portrait",
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
    },
    {
      "sceneNumber": 2,
      "title": "Key Point",
      "narration": "Here's why this matters...",
      "duration": 5,
      "visualType": "web",
      "imageSearchQuery": "AI software development",
      "imageGenPrompt": null,
      "videoPrompt": null
    }
  ]
}
```

#### Scene Rules

- **Each scene is exactly 5 seconds** (no longer)
- 6 scenes for 30s video, 12 scenes for 60s video
- Total narration: ~75 words (30s) or ~150 words (60s)
- Each scene narration: ~12 words (fits 5 seconds at 2.5 wps)
- All AI image prompts MUST include "vertical portrait composition, 9:16"

#### Visual Type Assignment by Mode

- `images-web`: All scenes get `visualType: "web"`
- `images-ai`: All scenes get `visualType: "generate"`
- `video-ai`: All scenes get `visualType: "video"`
- `mixed`: Hook + closer get `visualType: "video"`, middle scenes get `visualType: "web"`

### Phase 2b: From Deep-Research Script

When given a `youtube-script.md` from `/deep-research:full`, parse and condense:

```bash
python scripts/parse_script.py path/to/youtube-script.md --duration 30 --style educational --visual-mode mixed
```

The parser condenses the full script into 5-second scenes following the same rules above.

### Style-Specific Writing Guidelines

**educational:**
- Hook: "Did you know..." / "Most people don't realize..."
- Tone: Clear, authoritative, slightly surprised
- CTA: "Follow for more" / "Save this for later"

**promotional:**
- Hook: "Stop scrolling if you..." / "This changes everything"
- Tone: Confident, benefit-focused, urgent
- CTA: "Link in bio" / "Try it free"

**storytelling:**
- Hook: "I just discovered something..." / "Here's what happened when..."
- Tone: Personal, conversational, emotional
- CTA: "What do you think?" / "Share your experience"

**hype:**
- Hook: "This is INSANE" / "Nobody is talking about this"
- Tone: Fast, bold, exclamation-heavy, trending
- CTA: "Share this NOW" / "Tag someone who needs this"

## Phase 3: Image Acquisition

Based on `visualMode`, run the appropriate scripts:

```bash
# Web images (portrait orientation) - for scenes with visualType "web"
python scripts/search_images.py path/to/script.json

# AI-generated images (9:16 vertical) - for scenes with visualType "generate" or "video"
python scripts/generate_images.py path/to/script.json
```

- `search_images.py` uses Pexels API with `orientation=portrait`
- `generate_images.py` uses Gemini Imagen with `9:16` aspect ratio
- Images saved to `OUTPUT/{date}/{slug}/images/`

## Phase 4: Video Generation (video-ai and mixed modes only)

```bash
# Generate 5-second video clips from images
python scripts/generate_videos.py path/to/script.json
```

- Uses Fal.ai Kling Standard (cheapest image-to-video model)
- Takes generated/downloaded images and creates 5-second motion clips
- Uses `videoPrompt` from each scene for camera/motion direction
- Saves clips to `OUTPUT/{date}/{slug}/videos/`
- Skips scenes with `visualType: "web"` (those use Ken Burns in compose step)

## Phase 5: Audio Generation

### Narration

```bash
python scripts/generate_audio.py path/to/script.json
```

- Sends full narration to Deepgram TTS
- Voice auto-selected by style (or explicit override)
- Saves to `OUTPUT/{date}/{slug}/audio/narration.mp3`

#### Deepgram Voice Options

| Voice | Description | Best For |
|-------|-------------|----------|
| `aura-asteria-en` | Female, warm and clear | educational (default) |
| `aura-athena-en` | Female, confident | promotional |
| `aura-perseus-en` | Male, warm narrator | storytelling |
| `aura-arcas-en` | Male, energetic | hype |
| `aura-orion-en` | Male, deep | authoritative content |
| `aura-luna-en` | Female, calm | professional |

### Background Music

```bash
python scripts/generate_music.py path/to/script.json
```

- Uses Fal.ai CassetteAI music generator
- Auto-generates style-appropriate music prompt
- Trims to exact video duration
- Saves to `OUTPUT/{date}/{slug}/audio/music.mp3`

#### Style-to-Music Mapping

- `educational`: "Calm ambient electronic background, minimal, informative feel"
- `promotional`: "Upbeat modern pop instrumental, confident energy, rising build"
- `storytelling`: "Gentle acoustic guitar with soft piano, emotional, warm"
- `hype`: "Hard-hitting trap beat, bass-heavy, intense energy, trending sound"

## Phase 6: Video Composition

```bash
python scripts/compose_video.py path/to/script.json
```

Composites everything into the final vertical 9:16 MP4:

1. For `web` scenes: Creates Ken Burns zoom clips from still images (5s each)
2. For `video` scenes: Uses the AI-generated video clips directly
3. Concatenates all clips in scene order
4. Mixes audio: narration (volume 1.0) + music (volume 0.15)
5. Outputs final MP4 to `OUTPUT/{date}/{slug}/video/{slug}.mp4`

## Directory Structure

```
INPUT/{YYYYMMDD}/{topic-slug}/
  +-- research.md              # Quick research notes
  +-- script.json              # Scene script

OUTPUT/{YYYYMMDD}/{topic-slug}/
  +-- images/                  # Scene images (portrait)
  |   +-- scene-1.jpg
  |   +-- scene-2.jpg
  +-- videos/                  # AI video clips (if video-ai/mixed)
  |   +-- scene-1.mp4
  |   +-- scene-3.mp4
  +-- audio/
  |   +-- narration.mp3        # Deepgram TTS
  |   +-- music.mp3            # Fal.ai background music
  +-- video/
      +-- {slug}.mp4           # Final vertical video
```

## Troubleshooting

- **No portrait images**: Pexels may have fewer portrait results. Try broader queries.
- **Fal.ai timeout**: Video generation can take 30-60s per clip. Use `--delay 5` between clips.
- **Too long/short**: Each scene is 5s. Adjust scene count: 6 for 30s, 12 for 60s.
- **Wrong energy**: Change the `style` parameter and regenerate the script.
- **Cost too high**: Use `images-web` mode (free) or `mixed` mode (only key scenes as video).
- **Music too loud**: Adjust `musicVolume` in config (default 0.15, range 0.0-1.0).
