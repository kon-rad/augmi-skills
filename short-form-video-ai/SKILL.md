---
name: short-form-video-ai
description: |
  Generates professional short-form vertical videos (30-60 seconds) for YouTube Shorts, Instagram Reels,
  and TikTok with word-synced captions and highlighted current words. Takes a script.json input and
  produces 6 AI-generated scene images (9:16 portrait), converts them to video clips using Fal.ai Kling,
  adds Deepgram TTS narration (female voice with word timestamps), FAL.ai background music, and burns
  animated captions with per-word highlighting into the final video. Output: broadcast-ready MP4 with
  rounded font captions (70px), bright cyan current-word highlights, 8px black shadows.
---

# Short-Form Video AI Generator (Enhanced)

Generates professional short-form vertical videos (30-60 seconds) for YouTube Shorts, Instagram Reels, and TikTok.

**Key features:**
- ✅ 6 AI-generated images (Gemini Imagen 4 Fast, 9:16 portrait aspect ratio)
- ✅ Image-to-video animation (Fal.ai Kling, 5 seconds per scene)
- ✅ Female voice narration (Deepgram TTS - aura-luna-en by default)
- ✅ Word-level timestamps (extracted from TTS response)
- ✅ **Word-synced captions with current-word highlighting** (bright cyan)
- ✅ Large readable captions (70px rounded font, 8px shadow)
- ✅ Background music (FAL.ai Lyria2, auto-trimmed to duration)
- ✅ Burned-in captions (no external SRT needed)

## Prerequisites

### API Keys

Set the following environment variables:

- `DEEPGRAM_API_KEY` - Text-to-speech narration ([console.deepgram.com](https://console.deepgram.com))
- `GEMINI_API_KEY` or `GOOGLE_AI_API_KEY` - AI image generation ([aistudio.google.com/apikey](https://aistudio.google.com/apikey))
- `FAL_KEY` - Image-to-video and music generation ([fal.ai/dashboard/keys](https://fal.ai/dashboard/keys))

### System Dependencies

- `ffmpeg` (with libfreetype for text rendering) - `brew install ffmpeg`
- `python3` (3.10+)
- Mulish ExtraBold font (bundled at `fonts/Mulish-ExtraBold.ttf`)

### Python Dependencies

```bash
pip install requests google-genai pillow python-dotenv fal-client pydub
```

## Input Format: script.json

The skill expects a `script.json` file with this structure:

```json
{
  "title": "Video Title",
  "description": "Short description for captions",
  "targetDuration": 30,
  "style": "hype",
  "voice": "aura-luna-en",
  "orientation": "portrait",
  "config": {
    "musicPrompt": "Hard-hitting trap beat, intense energy...",
    "musicVolume": 0.15,
    "narrationVolume": 1.0,
    "font": "Mulish ExtraBold",
    "fontSize": 90,
    "highlightColor": "#00FFFF",
    "fontPath": ".claude/skills/short-form-video-ai/fonts/Mulish-ExtraBold.ttf"
  },
  "narration": {
    "text": "Full narration text for the entire video..."
  },
  "scenes": [
    {
      "sceneNumber": 1,
      "title": "Scene Title",
      "narration": "Narration for this 5-second scene...",
      "duration": 5,
      "imageGenPrompt": "Detailed image generation prompt (Gemini Imagen style)...",
      "videoPrompt": "Motion direction for Kling image-to-video (camera movement, zoom, etc)..."
    },
    // ... repeat for each of 6 scenes
  ]
}
```

## Image Preparation (REQUIRED before video generation)

All source images MUST be 9:16 portrait (1080x1920) before being sent to the image-to-video model. Blog post images and other source images are typically landscape or square — they must be cropped/converted first.

### Cropping Rules

**Portrait images (e.g., 1080x1350 carousel slides):**
- Create a 1080x1920 canvas with dark background (`#09090b`)
- Center the image vertically on the canvas
- The image fills the full width, black bars pad top and bottom

**Landscape images (e.g., 1408x768 blog images):**
- Create a 1080x1920 canvas
- Scale the original image to fill 1080px width (preserving aspect ratio)
- Create a blurred, darkened copy of the image as background fill (Gaussian blur radius 30, 60% dark overlay)
- Paste the blurred version as full canvas background
- Paste the sharp scaled image centered vertically
- Apply gradient fades (80px) at top and bottom edges of the sharp image to blend into the blurred background

**Square images (1:1):**
- Same approach as landscape — blurred dark background fill with sharp image centered

### Why crop first?

The fal.ai Kling image-to-video model accepts an `aspect_ratio` parameter but produces better results when the input image already matches 9:16. Sending a landscape image with `aspect_ratio: "9:16"` causes the model to crop unpredictably — pre-cropping gives you control over framing.

### Preserve originals

Source images (blog post images, etc.) must NEVER be modified in place. Always create copies in the short-video output directory (`short-video/images/scene-N.png`) and crop those.

## Pipeline

### Phase 1: Narration Generation

```bash
python3 scripts/tts-narration.py <script.json>
```

**Output:**
- `audio/narration.mp3` - MP3 audio file
- `audio/narration.json` - Word-level timestamps from Deepgram TTS:
  ```json
  {
    "duration_ms": 21200,
    "words": [
      {"word": "An", "start_ms": 0, "end_ms": 400},
      {"word": "AI", "start_ms": 400, "end_ms": 800},
      ...
    ]
  }
  ```

### Phase 2: Image Generation

```bash
python3 scripts/generate-images.py <script.json>
```

**Generates:**
- `images/scene-1.jpg` through `images/scene-6.jpg`
- All in 9:16 portrait aspect ratio (1080x1920 or similar proportion)
- Quality: JPEG high quality (95%)

### Phase 3: Video Clip Generation

```bash
python3 scripts/generate-video-clips.py <script.json>
```

**Generates:**
- `videos/scene-1.mp4` through `videos/scene-6.mp4`
- Each exactly 5 seconds
- 1080x1920 resolution (9:16 portrait)
- Uses Fal.ai Kling (cheapest tier: `fal-ai/kling-video/v2.1/standard/image-to-video`)
- Motion based on `videoPrompt` field

### Phase 4: Music Generation

```bash
python3 scripts/generate-music.py <script.json>
```

**Generates:**
- `audio/music.mp3` - Background music track
- Duration auto-matched to total narration duration
- Music volume: 0.15 relative to narration

### Phase 5: Caption Rendering

```bash
python3 scripts/render-captions.py <script.json>
```

**Creates:**
- `captions/captions.txt` - Frame-by-frame caption text with per-word colors
- Per-frame mapping: `frame_number -> (word_text, color, duration)`
- Implemented as FFmpeg drawtext filters (time-based color variable)

### Phase 6: Video Composition

```bash
python3 scripts/compose-final-video.py <script.json>
```

**Produces:**
- `final/<title>.mp4` - Final broadcast-ready video
- Resolution: 1080x1920 (9:16 portrait)
- Video: H.264 codec
- Audio: AAC, Deepgram narration (1.0) + background music (0.15) mixed
- Captions: Burned-in using FFmpeg drawtext filter
- Word-synced highlighting: Current word in bright cyan during its timestamp range

## Caption Styling

**Font specifications:**
- Font family: **Mulish ExtraBold** (bundled at `fonts/Mulish-ExtraBold.ttf`)
- Size: 90px (configurable via `config.fontSize`)
- Color: Bright cyan (#00FFFF)
- Outline: 8px black border
- Position: Center-bottom (440px from bottom edge)
- Alignment: Center

**Single-word display:**
- **One word at a time** — each word appears centered during its exact timestamp window
- Words are UPPERCASE for mobile readability
- Punctuation (periods, commas, etc.) is stripped from display
- Timestamps from Deepgram STT ensure precise audio sync

## Watermark

All videos include the Augmi brand watermark in the top-right corner.

**Watermark specifications:**
- Image: `public/augmi-w-transparent.png` (white logo on transparent background)
- Position: Top-right area, inset from edges
- Width: 320px (auto-scales height to preserve aspect ratio)
- Opacity: 40% (`0.4`)
- Margin: 100px from top and right edges

**Config options:**
```json
{
  "config": {
    "watermarkPath": "public/augmi-w-transparent.png",
    "watermarkOpacity": 0.4,
    "watermarkWidth": 320,
    "watermarkMargin": 100
  }
}
```

To disable watermark, set `"watermarkPath": ""` or remove the field.

## Usage Example

```bash
# With existing script.json:
python3 scripts/compose-final-video.py OUTPUT/20260306/ai-content-factory-ugc/videos/script.json

# Output:
# final/ai-content-factory-ugc.mp4 (21.2 seconds, 1080x1920, word-synced captions)
```

## Cost Estimation

| Component | Cost | Notes |
|-----------|------|-------|
| Deepgram TTS (word extraction) | $0.01-0.02 | Per 51 words |
| Gemini Imagen 4 Fast (6 images) | $0.06-0.10 | @$0.01-0.02/image |
| Fal.ai Kling (6 video clips) | $0.30-0.60 | @$0.05-0.10/clip |
| FAL.ai Lyria2 music | $0.05-0.10 | Per 30-second track |
| **Total** | **~$0.42-0.82** | Full production |

## Common Customizations

### Change Female Voice

Edit `config.voice` in script.json:
- `aura-luna-en` - Calm, pleasant (default)
- `aura-asteria-en` - Warm, clear
- `aura-athena-en` - Confident

### Adjust Caption Size

Edit `config.fontSize` (suggested: 80-100px for mobile, default: 90px)

### Change Music Style

Edit `config.musicPrompt`:
- "Hard-hitting trap beat" (default, hype)
- "Uplifting ambient electronic" (calm)
- "Pop upbeat rhythm" (energetic)

### Disable Music

Set `config.musicVolume` to `0.0`

## Troubleshooting

**No captions visible:**
- Check that FFmpeg has text rendering support: `ffmpeg -filters | grep drawtext`
- Verify font file path in scripts
- Try system font name instead of file path

**Video too short/long:**
- Adjust narration word count
- Captions always match narration timing (can't be longer)

**Music cuts off:**
- Music auto-trims to narration duration
- If too short, increase narration length

**Current word not highlighting:**
- Check `narration.json` has valid `start_ms`/`end_ms` values
- Verify highlight color is different from base color

## Style Guide Reference

See: `/content/short-form-style-guide.md` for complete specifications including:
- Resolution: 1080x1920 (9:16 portrait)
- Duration: 30-90 seconds
- Music volume: 0.15 relative to narration
- Caption font size: 70px
- Current word highlight: Bright cyan (#00FFFF)

## Files Generated

```
OUTPUT/{YYYYMMDD}/{project}/
├── videos/
│   ├── script.json                 # Input script
│   ├── images/                     # 6 AI-generated portrait images
│   │   ├── scene-1.jpg
│   │   ├── scene-2.jpg
│   │   ├── ... scene-6.jpg
│   ├── videos/                     # 6 animated video clips (5s each)
│   │   ├── scene-1.mp4
│   │   ├── scene-2.mp4
│   │   ├── ... scene-6.mp4
│   ├── audio/
│   │   ├── narration.mp3           # TTS narration
│   │   ├── narration.json          # Word timestamps
│   │   └── music.mp3               # Background music
│   ├── captions/
│   │   └── captions.txt            # Per-frame caption data
│   └── final/
│       └── {project}.mp4           # Final video with burned-in captions
```

---

## Social Media Posting Rules

- **NEVER shorten links.** Always use the full URL (e.g., `https://augmi.world/blog/ai-agents-taking-over-defi-agentic-era-crypto`). Link shorteners (bit.ly, t.co, etc.) do not work reliably on most platforms and get flagged as spam. Always paste the complete blog URL in captions.
- Always run `/humanizer` on caption text before posting.
- Always show content to user for approval before posting.

---

**Skill Status:** ✅ Ready for production
**Latest Update:** March 11, 2026
**API Providers:** Deepgram, Gemini Imagen 4, Fal.ai Kling + Lyria2
